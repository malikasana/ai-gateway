"""
instances/deepseek/incognito.py

DeepSeek Web — Incognito-style Mode Handler
- Opens Chrome with existing signed-in session
- Creates new chat for every request
- Sends query, gets reply, deletes chat, closes window

Entry point: run(query, **kwargs) -> str
"""

import time
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

IGNORE = [
    'New chat', 'Ctrl + J', 'Today', '7 Days', '30 Days',
    '2026-04', '2026-03', '2026-02', '2026-01',
    'Instant', 'Expert', 'DeepThink', 'Search',
    'AI-generated, for reference only',
    'This response is AI-generated, for reference only.',
    'Muhammad Ali Kasana'
]


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


def delete_current_chat():
    print("  Deleting chat...")
    win = get_deepseek_window()
    win.set_focus()
    time.sleep(0.5)

    for elem in win.descendants(control_type="Hyperlink"):
        try:
            name = elem.window_text().strip()
            if name and "deepseek" not in name.lower() and len(name) > 3:
                rect = elem.rectangle()
                cx = (rect.left + rect.right) // 2
                cy = (rect.top + rect.bottom) // 2
                pyautogui.moveTo(cx, cy, duration=0.5)
                time.sleep(1)

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

                win = get_deepseek_window()
                for e in win.descendants(control_type="Text"):
                    try:
                        if e.window_text().strip() == 'Delete':
                            e.click_input()
                            time.sleep(1)
                            break
                    except:
                        pass

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


def get_reply(win, query):
    win = get_deepseek_window()

    text_elems = []
    for elem in win.descendants(control_type="Text"):
        try:
            name = elem.window_text().strip()
            if name and name not in IGNORE and len(name) > 5:
                text_elems.append(name)
        except:
            pass

    # Skip title and user query, everything after is the reply
    reply_parts = []
    found_query = False
    for t in text_elems:
        if not found_query:
            if query[:20] in t or t in query:
                found_query = True
            continue
        reply_parts.append(t)

    reply = '\n\n'.join(reply_parts)
    print(f"  Copied {len(reply)} chars")
    return reply


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
        win = wait_for_reply()

        reply = get_reply(win, query)

        delete_current_chat()
        close_deepseek()

        return reply

    finally:
        pythoncom.CoUninitialize()