"""
instances/grok/incognito.py

Grok Web — Private Chat Mode Handler
- Opens browser with existing signed-in session
- Enables private chat via Ctrl+Shift+J
- Sends query, waits for reply, copies it, closes window

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

GROK_URL = "https://grok.com"


def open_grok():
    print("  Opening Grok...")
    open_browser(GROK_URL)
    time.sleep(4)


def get_grok_window():
    wins = Desktop(backend="uia").windows(class_name=get_window_class())
    for w in wins:
        if "Grok" in w.window_text():
            return w
    raise Exception("Grok window not found!")


def enable_private_chat():
    print("  Enabling private chat...")
    win = get_grok_window()
    win.set_focus()
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(1)
    print("  Private chat enabled!")


def send_query(win, query):
    print(f"  Sending: {query[:60]}...")
    win.set_focus()
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.2)
    pyautogui.press('delete')
    time.sleep(0.3)
    pyperclip.copy(query)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    pyautogui.press('enter')
    print("  Sent! Waiting for reply...")


def wait_for_reply():
    time.sleep(2)
    while True:
        try:
            win = get_grok_window()
            for btn in win.descendants(control_type="Button"):
                try:
                    if btn.window_text() == "Regenerate":
                        print("  Reply complete!")
                        time.sleep(1)
                        return get_grok_window()
                except:
                    pass
        except:
            pass
        time.sleep(0.5)


def scroll_to_bottom(win):
    win = get_grok_window()
    win.set_focus()
    time.sleep(0.5)
    rect = win.rectangle()
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    pyautogui.click(cx, cy)
    time.sleep(0.5)
    pyautogui.press('end')
    time.sleep(1.5)


def copy_last_reply(win):
    scroll_to_bottom(win)
    time.sleep(1)

    win = get_grok_window()
    pyperclip.copy("")
    time.sleep(0.3)

    copy_buttons = []
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text() == "Copy":
                copy_buttons.append(btn)
        except:
            pass

    print(f"  Found {len(copy_buttons)} Copy buttons")

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


def close_grok():
    print("  Closing Grok...")
    win = get_grok_window()
    win.close()
    time.sleep(1)


def run(query: str, **kwargs) -> str:
    pythoncom.CoInitialize()
    try:
        open_grok()
        win = get_grok_window()
        win.set_focus()
        time.sleep(1)

        enable_private_chat()

        win = get_grok_window()
        send_query(win, query)
        win = wait_for_reply()
        reply = copy_last_reply(win)

        close_grok()
        return reply

    finally:
        pythoncom.CoUninitialize()