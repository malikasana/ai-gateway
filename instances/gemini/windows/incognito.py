"""
instances/gemini/incognito.py

Gemini Web — Incognito-style Mode Handler
- Opens Chrome with existing signed-in Google session
- Sends query, waits for reply, extracts text
- Deletes chat, closes window

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
GEMINI_URL  = "https://gemini.google.com/app"

IGNORE = [
    "Conversation with Gemini",
    "Gemini said",
    "Gemini is AI and can make mistakes.",
    "Ask Gemini",
]


def open_gemini():
    print("  Opening Gemini...")
    subprocess.Popen(f'"{CHROME_PATH}" --new-window {GEMINI_URL}', shell=True)
    time.sleep(10)


def get_gemini_window():
    wins = Desktop(backend="uia").windows(class_name="Chrome_WidgetWin_1")
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


def get_reply(win, query):
    win = get_gemini_window()

    text_elems = []
    for elem in win.descendants(control_type="Text"):
        try:
            name = elem.window_text().strip()
            cls  = elem.element_info.class_name or ""
            # Skip UI chrome and user query bubbles
            if not name:
                continue
            if name in IGNORE:
                continue
            if len(name) <= 5:
                continue
            if "query-text" in cls:
                continue
            text_elems.append(name)
        except:
            pass

    # Only keep text inside model-response-message-content groups
    reply_parts = []
    for elem in win.descendants(control_type="Group"):
        try:
            aid = elem.element_info.automation_id or ""
            if aid.startswith("model-response-message-content"):
                for child in elem.descendants(control_type="Text"):
                    try:
                        name = child.window_text().strip()
                        if name and len(name) > 1:
                            reply_parts.append(name)
                    except:
                        pass
        except:
            pass

    # Fallback to text_elems if model-response extraction got nothing
    if not reply_parts:
        reply_parts = text_elems

    reply = '\n\n'.join(reply_parts)
    print(f"  Extracted {len(reply)} chars")
    return reply


def delete_chat():
    print("  Deleting chat...")
    win = get_gemini_window()
    win.set_focus()
    time.sleep(0.5)

    # Click conversation actions menu
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text().strip() == "Open menu for conversation actions.":
                btn.click_input()
                time.sleep(1)
                break
        except:
            pass

    # Click Delete menu item
    win = get_gemini_window()
    for elem in win.descendants(control_type="MenuItem"):
        try:
            if elem.window_text().strip() == "Delete":
                elem.click_input()
                time.sleep(1)
                break
        except:
            pass

    # Confirm deletion in dialog
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
    """
    Entry point called by queue_manager.
    Receives query, returns reply as string.
    """
    pythoncom.CoInitialize()
    try:
        open_gemini()
        win = get_gemini_window()
        win.set_focus()
        time.sleep(1)

        send_query(win, query)
        win = wait_for_reply()

        reply = get_reply(win, query)

        delete_chat()
        close_gemini()

        return reply

    finally:
        pythoncom.CoUninitialize()