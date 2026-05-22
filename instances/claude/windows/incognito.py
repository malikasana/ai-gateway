"""
instances/claude/incognito.py

Claude Desktop — Incognito Mode Handler
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


def find_claude_app_id():
    # Use .env value if set
    app_id = os.getenv("CLAUDE_APP_ID")
    if app_id:
        print(f"  Using Claude App ID from .env: {app_id}")
        return app_id
    # Auto detect
    try:
        result = subprocess.run(
            ['powershell', '-Command',
             'Get-StartApps | Where-Object { $_.Name -like "*Claude*" } | Select-Object -ExpandProperty AppID'],
            capture_output=True, text=True
        )
        app_id = result.stdout.strip()
        if app_id:
            print(f"  Auto-detected Claude App ID: {app_id}")
            return app_id
    except:
        pass
    raise Exception(
        "Claude app not found!\n"
        "To fix: Open PowerShell and run:\n"
        "  Get-StartApps | Where-Object { $_.Name -like '*Claude*' }\n"
        "Copy the AppID value and add it to .env as:\n"
        "  CLAUDE_APP_ID=your_app_id_here"
    )


def is_claude_running():
    try:
        desktop = Desktop(backend="uia")
        wins = desktop.windows(class_name="Chrome_WidgetWin_1")
        for w in wins:
            if "Claude" in w.window_text():
                return True
        return False
    except:
        return False


def open_claude():
    if is_claude_running():
        print("  Claude already running...")
    else:
        print("  Opening Claude...")
        app_id = find_claude_app_id()
        subprocess.Popen(
            f'explorer.exe shell:appsFolder\\{app_id}',
            shell=True
        )
        time.sleep(6)


def get_claude_window():
    desktop = Desktop(backend="uia")
    wins = desktop.windows(class_name="Chrome_WidgetWin_1")
    for w in wins:
        if "Claude" in w.window_text():
            return w
    raise Exception("Claude window not found!")


def click_new_chat():
    print("  Opening new chat...")
    win = get_claude_window()
    win.set_focus()
    for btn in win.descendants(control_type="Button"):
        try:
            if "New chat" in btn.window_text():
                btn.click_input()
                time.sleep(2)
                return get_claude_window()
        except:
            pass
    raise Exception("New chat button not found!")


def enable_incognito():
    print("  Enabling incognito...")
    win = get_claude_window()
    win.set_focus()
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(2)
    print("  Incognito enabled!")


def disable_incognito():
    print("  Closing incognito...")
    win = get_claude_window()
    win.set_focus()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'shift', 'i')
    time.sleep(2)
    print("  Incognito closed!")


def find_input_box(win):
    PLACEHOLDERS = [
        "Write a message",
        "How can I help you today",
        "Type / for skills",
    ]
    for elem in win.descendants():
        try:
            name = elem.window_text()
            ctrl = elem.element_info.control_type
            if ctrl == "Edit":
                if name.strip() == "" or any(p.lower() in name.lower() for p in PLACEHOLDERS):
                    return elem
        except:
            pass
    return None


def find_send_button(win):
    for btn in win.descendants(control_type="Button"):
        try:
            if "Send" in btn.window_text():
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
            win = get_claude_window()
            for btn in win.descendants(control_type="Button"):
                try:
                    if btn.window_text() == "Use voice mode":
                        print("  Reply complete!")
                        time.sleep(1)
                        return get_claude_window()
                except:
                    pass
        except:
            pass
        time.sleep(1)


def scroll_to_bottom(win):
    win = get_claude_window()
    win.set_focus()
    time.sleep(0.5)
    while True:
        pyautogui.press('tab')
        time.sleep(0.3)
        win = get_claude_window()
        for elem in win.descendants():
            try:
                if elem.has_keyboard_focus():
                    if "Add files" in elem.window_text():
                        print("  Scrolling to bottom...")
                        pyautogui.press('end')
                        time.sleep(1.5)
                        return
            except:
                pass


def copy_last_reply(win):
    scroll_to_bottom(win)
    time.sleep(1)

    win = get_claude_window()
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


def run(query: str, **kwargs) -> str:
    """
    Entry point called by queue_manager.
    Receives query, returns reply as string.
    kwargs reserved for future use.
    """
    open_claude()
    win = click_new_chat()
    win.set_focus()
    time.sleep(1)

    enable_incognito()

    win = get_claude_window()
    send_query(win, query)
    win = wait_for_reply()
    reply = copy_last_reply(win)

    disable_incognito()

    return reply