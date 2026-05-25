"""
instances/gemini/incognito.py

Gemini Web — Incognito-style Mode Handler
- Opens browser with existing signed-in Google session
- Sends query, waits for reply, copies, deletes chat, closes window

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

GEMINI_URL = "https://gemini.google.com/app"


def open_gemini():
    print("  Opening Gemini...")
    open_browser(GEMINI_URL)
    time.sleep(10)


def get_gemini_window():
    wins = Desktop(backend="uia").windows(class_name=get_window_class())
    for w in wins:
        if "Gemini" in w.window_text():
            return w
    raise Exception("Gemini window not found!")


def find_input_box(win):
    for elem in win.descendants(control_type="Edit"):
        try:
            if "ql-editor" in (elem.element_info.class_name or ""):
                return elem
        except:
            pass
    return None


def send_query(win, query):
    print(f"  Sending: {query[:60]}...")
    box = find_input_box(win)
    if not box:
        raise Exception("Could not find Gemini input box!")
    box.click_input()
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
    time.sleep(3)
    TIMEOUT = 120
    start = time.time()
    while time.time() - start < TIMEOUT:
        win = get_gemini_window()
        for btn in win.descendants(control_type="Button"):
            try:
                if btn.window_text().strip() == "Send message":
                    print("  Reply complete!")
                    time.sleep(1)
                    return get_gemini_window()
            except:
                pass
        time.sleep(0.8)
    raise Exception("Timeout: Gemini did not finish within 120 seconds")


def scroll_to_bottom():
    print("  Scrolling to bottom...")
    win = get_gemini_window()
    win.set_focus()
    time.sleep(0.5)
    win_rect = win.rectangle()
    cx = (win_rect.left + win_rect.right) // 2
    cy = (win_rect.top + win_rect.bottom) // 2
    pyautogui.click(cx, cy)
    time.sleep(1)
    pyautogui.press('end')
    time.sleep(2)


def copy_last_reply():
    print("  Looking for Copy button...")
    win = get_gemini_window()
    pyperclip.copy("")
    time.sleep(0.5)

    copy_buttons = []
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text().strip() == "Copy":
                copy_buttons.append(btn)
        except:
            pass

    print(f"  Found {len(copy_buttons)} Copy buttons")

    if not copy_buttons:
        return ""

    btn = copy_buttons[-1]
    rect = btn.rectangle()
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2
    pyautogui.moveTo(cx, cy, duration=0.5)
    time.sleep(0.8)
    pyautogui.click(cx, cy)
    time.sleep(1.5)

    result = pyperclip.paste()
    print(f"  Copied {len(result)} chars")
    return result


def delete_chat():
    print("  Deleting chat...")
    win = get_gemini_window()
    win.set_focus()
    time.sleep(0.5)

    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text().strip() == "Open menu for conversation actions.":
                btn.click_input()
                time.sleep(1)
                break
        except:
            pass

    win = get_gemini_window()
    for elem in win.descendants(control_type="MenuItem"):
        try:
            if elem.window_text().strip() == "Delete":
                elem.click_input()
                time.sleep(1)
                break
        except:
            pass

    win = get_gemini_window()
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text().strip() == "Delete":
                btn.click_input()
                time.sleep(1)
                print("  Chat deleted!")
                return
        except:
            pass


def close_gemini():
    print("  Closing Gemini...")
    win = get_gemini_window()
    win.close()
    time.sleep(1)


def run(query: str, **kwargs) -> str:
    pythoncom.CoInitialize()
    try:
        open_gemini()
        win = get_gemini_window()
        win.set_focus()
        time.sleep(1)

        send_query(win, query)
        wait_for_reply()

        scroll_to_bottom()
        reply = copy_last_reply()

        delete_chat()
        close_gemini()

        return reply

    finally:
        pythoncom.CoUninitialize()