"""
instances/chatgpt/incognito.py

ChatGPT Desktop — Temporary Chat Mode Handler
- One query in, one reply out
- No chat history saved
- Independent of server and other instances

Entry point: run(query, **kwargs) -> str
"""

import time
import subprocess
import pyperclip
import pyautogui
from pywinauto import Desktop
from dotenv import load_dotenv
import os

load_dotenv()

pyautogui.FAILSAFE = False

BOTTOM_FOCUS_TARGETS = ["Copy message", "Edit message", "Add files and more", "Start dictation", "Start Voice"]


def find_chatgpt_app_id():
    app_id = os.getenv("CHATGPT_APP_ID")
    if app_id:
        print(f"  Using ChatGPT App ID from .env: {app_id}")
        return app_id
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             'Get-StartApps | Where-Object { $_.Name -like "*ChatGPT*" -or $_.Name -like "*OpenAI*" } | Select-Object -ExpandProperty AppID'],
            capture_output=True, text=True
        )
        app_id = result.stdout.strip()
        if app_id:
            print(f"  Auto-detected ChatGPT App ID: {app_id}")
            return app_id
    except:
        pass
    raise Exception(
        "ChatGPT app not found!\n"
        "To fix: Open PowerShell and run:\n"
        "  Get-StartApps | Where-Object { $_.Name -like '*ChatGPT*' }\n"
        "Copy the AppID value and add it to .env as:\n"
        "  CHATGPT_APP_ID=your_app_id_here"
    )


def is_chatgpt_running():
    try:
        desktop = Desktop(backend="uia")
        wins = desktop.windows(class_name="Chrome_WidgetWin_1")
        for w in wins:
            if "ChatGPT" in w.window_text():
                return True
        return False
    except:
        return False


def open_chatgpt():
    if is_chatgpt_running():
        print("  ChatGPT already running...")
    else:
        print("  Opening ChatGPT...")
        app_id = find_chatgpt_app_id()
        subprocess.Popen(
            f'explorer.exe shell:appsFolder\\{app_id}',
            shell=True
        )
        time.sleep(6)


def get_chatgpt_window():
    desktop = Desktop(backend="uia")
    wins = desktop.windows(class_name="Chrome_WidgetWin_1")
    for w in wins:
        if "ChatGPT" in w.window_text():
            return w
    raise Exception("ChatGPT window not found!")


def click_new_chat():
    print("  Opening new chat...")
    win = get_chatgpt_window()
    win.set_focus()
    for elem in win.descendants(control_type="Hyperlink"):
        try:
            if "New chat" in elem.window_text():
                elem.click_input()
                time.sleep(2)
                return get_chatgpt_window()
        except:
            pass
    raise Exception("New chat hyperlink not found!")


def enable_temporary_chat():
    print("  Enabling temporary chat...")
    win = get_chatgpt_window()
    win.set_focus()
    time.sleep(0.5)
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text() == "Turn on temporary chat":
                btn.click_input()
                time.sleep(1)
                print("  Temporary chat enabled!")
                return
        except:
            pass
    print("  WARNING: 'Turn on temporary chat' not found — may already be on")


def find_input_box(win):
    for elem in win.descendants(control_type="Edit"):
        return elem  # first Edit is always the input box
    return None


def find_send_button(win):
    for btn in win.descendants(control_type="Button"):
        try:
            if btn.window_text() == "Send prompt":
                return btn
        except:
            pass
    return None


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
    input_box.type_keys("^v")
    time.sleep(0.5)
    send_btn = find_send_button(win)
    if not send_btn:
        raise Exception("Could not find send button!")
    send_btn.click_input()
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


def scroll_to_bottom(win):
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
                    if any(target in elem.window_text() for target in BOTTOM_FOCUS_TARGETS):
                        print(f"  Reached bottom area (focused: '{elem.window_text()}') — pressing End...")
                        pyautogui.press('end')
                        time.sleep(2.5)
                        return
            except:
                pass


def copy_last_reply(win):
    scroll_to_bottom(win)
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


def run(query: str, **kwargs) -> str:
    """
    Entry point called by queue_manager.
    Receives query, returns reply as string.
    kwargs reserved for future use.
    """
    open_chatgpt()
    click_new_chat()
    enable_temporary_chat()

    win = get_chatgpt_window()
    send_query(win, query)
    win = wait_for_reply()
    reply = copy_last_reply(win)

    click_new_chat()  # cleans up temporary chat

    return reply