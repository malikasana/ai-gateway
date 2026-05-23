"""
instances/deepseek/windows/incognito.py

DeepSeek Web — Incognito-style Mode Handler
- Opens Chrome with existing signed-in session
- Creates new chat for every request
- Sends query, gets reply, copies reply, deletes chat, closes window

Entry point: run(query, **kwargs) -> str
"""

import time
import re
import subprocess
import pyperclip
import pyautogui
import pythoncom
import os
from pywinauto import Desktop
from dotenv import load_dotenv

load_dotenv()

pyautogui.FAILSAFE = False

CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DEEPSEEK_URL = "https://chat.deepseek.com"


def open_deepseek():
    print("  Opening DeepSeek...")
    subprocess.Popen(f'"{CHROME_PATH}" --new-window {DEEPSEEK_URL}', shell=True)
    time.sleep(4)


def get_deepseek_window():
    wins = Desktop(backend="uia").windows(class_name="Chrome_WidgetWin_1")
    for w in wins:
        if "DeepSeek" in w.window_text():
            return w
    raise Exception("DeepSeek window not found!")


def find_input_box(win):
    for elem in win.descendants(control_type="Edit"):
        try:
            if "chat.deepseek" not in elem.window_text():
                return elem
        except:
            pass
    return None


def click_new_chat():
    print("  Opening new chat...")
    win = get_deepseek_window()
    win.set_focus()
    time.sleep(0.5)
    for elem in win.descendants(control_type="Text"):
        try:
            if elem.window_text().strip() == "New chat":
                elem.click_input()
                time.sleep(2)
                return get_deepseek_window()
        except:
            pass
    raise Exception("New chat button not found!")


def send_query(win, query):
    print(f"  Sending: {query[:60]}...")
    input_box = find_input_box(win)
    if not input_box:
        raise Exception("Could not find input box!")
    input_box.click_input()
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
        win = get_deepseek_window()
        title = win.window_text()
        if "Into the Unknown" not in title and "DeepSeek - Into" not in title:
            print("  Reply complete!")
            time.sleep(1)
            return get_deepseek_window()
        time.sleep(0.5)


def copy_reply():
    print("  Copying reply...")
    win = get_deepseek_window()
    pyperclip.copy("")
    time.sleep(0.3)

    # Find all nameless buttons with class db183363
    # Group by top value — highest top = last reply
    from collections import defaultdict
    groups = defaultdict(list)
    for btn in win.descendants(control_type="Button"):
        try:
            cls  = btn.element_info.class_name or ""
            name = btn.window_text().strip()
            if "db183363" in cls and name == "":
                rect = btn.rectangle()
                groups[rect.top].append((rect.left, btn))
        except:
            pass

    if not groups:
        print("  No copy buttons found!")
        return ""

    # Get the group with highest top — last reply
    last_top = max(groups.keys())
    buttons_in_group = sorted(groups[last_top], key=lambda x: x[0])

    # First button in group is always Copy
    copy_btn = buttons_in_group[0][1]
    rect = copy_btn.rectangle()
    cx = (rect.left + rect.right) // 2
    cy = (rect.top + rect.bottom) // 2

    print(f"  Clicking Copy at ({cx}, {cy})")
    pyautogui.moveTo(cx, cy, duration=0.5)
    time.sleep(0.8)
    pyautogui.click(cx, cy)
    time.sleep(1.5)

    result = pyperclip.paste()
    print(f"  Copied {len(result)} chars")
    return result


def delete_current_chat():
    print("  Deleting chat...")
    win = get_deepseek_window()
    win.set_focus()
    time.sleep(0.5)

    # Find active chat by unique class b64fb9ae
    for elem in win.descendants(control_type="Hyperlink"):
        try:
            cls = elem.element_info.class_name or ""
            if "b64fb9ae" in cls:
                rect = elem.rectangle()
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2
                pyautogui.moveTo(cx, cy, duration=0.5)
                time.sleep(1)

                # Click the three-dot button that appears on hover
                win = get_deepseek_window()
                for btn in win.descendants(control_type="Button"):
                    try:
                        b_rect = btn.rectangle()
                        if abs(b_rect.top - rect.top) < 20 and btn.window_text() == '':
                            btn.click_input()
                            time.sleep(1)
                            break
                    except:
                        pass

                # Click Delete in dropdown
                win = get_deepseek_window()
                for e in win.descendants(control_type="Text"):
                    try:
                        if e.window_text().strip() == 'Delete':
                            e.click_input()
                            time.sleep(1)
                            break
                    except:
                        pass

                # Confirm deletion
                win = get_deepseek_window()
                for btn in win.descendants(control_type="Button"):
                    try:
                        if btn.window_text().strip() == 'Delete chat':
                            btn.click_input()
                            time.sleep(1)
                            print("  Chat deleted!")
                            return
                    except:
                        pass
                break
        except:
            pass


def close_deepseek():
    print("  Closing DeepSeek...")
    win = get_deepseek_window()
    win.close()
    time.sleep(1)


def run(query: str, **kwargs) -> str:
    """
    Entry point called by queue_manager.
    Receives query, returns reply as string.
    """
    pythoncom.CoInitialize()
    try:
        open_deepseek()
        win = get_deepseek_window()
        win.set_focus()
        time.sleep(1)

        click_new_chat()

        win = get_deepseek_window()
        send_query(win, query)
        wait_for_reply()

        reply = copy_reply()

        delete_current_chat()
        close_deepseek()

        return reply

    finally:
        pythoncom.CoUninitialize()