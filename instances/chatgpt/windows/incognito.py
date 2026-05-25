"""
instances/chatgpt/incognito.py

ChatGPT Web — Temporary Chat Mode Handler
- Opens chatgpt.com in browser with existing signed-in session
- Enables temporary chat, sends query, copies reply, closes window

Entry point: run(query, **kwargs) -> str
"""

import time
import pyperclip
import pyautogui
import pythoncom
from pywinauto import Desktop
from dotenv import load_dotenv
from instances.browser import open_browser, get_window_class

load_dotenv()

pyautogui.FAILSAFE = False

CHATGPT_URL = "https://chatgpt.com"
BOTTOM_FOCUS_TARGETS = ["Copy message", "Edit message", "Add files and more", "Start dictation", "Start Voice"]


def open_chatgpt():
    print("  Opening ChatGPT...")
    open_browser(CHATGPT_URL)
    time.sleep(5)


def get_chatgpt_window():
    wins = Desktop(backend="uia").windows(class_name=get_window_class())
    for w in wins:
        if "ChatGPT" in w.window_text():
            return w
    raise Exception("ChatGPT window not found!")


def enable_temporary_chat():
    print("  Enabling temporary chat...")
    win = get_chatgpt_window()
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text() == "Turn on temporary chat":
                btn.click_input()
                time.sleep(1)
                rect = win.rectangle()
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2
                pyautogui.moveTo(cx, cy, duration=0.3)
                time.sleep(0.5)
                print("  Temporary chat enabled!")
                return
        except:
            pass
    print("  WARNING: not found — may already be on")


def send_query(query):
    print(f"  Sending: {query[:60]}...")
    time.sleep(0.5)
    pyautogui.press('a')
    time.sleep(0.2)
    pyautogui.press('backspace')
    time.sleep(0.2)
    pyperclip.copy(query)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    print("  Sent! Waiting for reply...")


def wait_for_reply():
    time.sleep(2)
    while True:
        try:
            win = get_chatgpt_window()
            for btn in win.descendants(control_type="Button"):
                try:
                    if btn.window_text() == "Start Voice":
                        print("  Reply complete!")
                        time.sleep(1)
                        return get_chatgpt_window()
                except:
                    pass
        except:
            pass
        time.sleep(1)


def scroll_to_bottom():
    win = get_chatgpt_window()
    win.set_focus()
    time.sleep(0.5)
    while True:
        pyautogui.press('tab')
        time.sleep(0.3)
        win = get_chatgpt_window()
        for elem in win.descendants():
            try:
                if elem.has_keyboard_focus():
                    if any(t in elem.window_text() for t in BOTTOM_FOCUS_TARGETS):
                        print(f"  Bottom reached — pressing End...")
                        pyautogui.press('end')
                        time.sleep(2.5)
                        return
            except:
                pass


def copy_last_reply():
    scroll_to_bottom()
    time.sleep(1)

    win = get_chatgpt_window()
    pyperclip.copy("")
    time.sleep(0.3)

    copy_buttons = []
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text() == "Copy response":
                copy_buttons.append(btn)
        except:
            pass

    print(f"  Found {len(copy_buttons)} Copy response buttons")

    if copy_buttons:
        btn = copy_buttons[-1]
        rect = btn.rectangle()
        cx = (rect.left + rect.right) // 2
        cy = (rect.top + rect.bottom) // 2
        pyautogui.moveTo(cx, cy, duration=0.5)
        time.sleep(0.8)
        pyautogui.click(cx, cy)
        time.sleep(1)
        result = pyperclip.paste()
        print(f"  Copied {len(result)} chars")
        return result

    return ""


def close_chatgpt():
    print("  Closing ChatGPT...")
    win = get_chatgpt_window()
    win.close()
    time.sleep(1)


def run(query: str, **kwargs) -> str:
    """
    Entry point called by queue_manager.
    Receives query, returns reply as string.
    """
    pythoncom.CoInitialize()
    try:
        open_chatgpt()
        enable_temporary_chat()
        send_query(query)
        wait_for_reply()
        reply = copy_last_reply()
        close_chatgpt()
        return reply

    finally:
        pythoncom.CoUninitialize()