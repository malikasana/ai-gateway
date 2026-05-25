"""
instances/browser.py

Shared browser launcher utility.
All instances import from here instead of hardcoding Chrome.
"""

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

BROWSER_PATH = os.getenv("BROWSER_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
BROWSER = os.getenv("BROWSER", "chrome").lower()

WINDOW_CLASS = {
    "chrome": "Chrome_WidgetWin_1",
    "edge": "Chrome_WidgetWin_1",
    "firefox": "MozillaWindowClass",
}


def open_browser(url: str):
    """Open a new browser window at the given URL."""
    subprocess.Popen(f'"{BROWSER_PATH}" --new-window {url}', shell=True)


def get_window_class() -> str:
    """Get the pywinauto window class for the configured browser."""
    return WINDOW_CLASS.get(BROWSER, "Chrome_WidgetWin_1")