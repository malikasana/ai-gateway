"""
instances/browser.py

Shared browser launcher utility.
All instances import from here instead of hardcoding Chrome.
Auto-detects OS — user only needs to touch .env if Chrome
is not in the default installation path.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

BROWSER = os.getenv("BROWSER", "chrome").lower()

if sys.platform == "win32":
    DEFAULT_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
elif sys.platform == "darwin":
    DEFAULT_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
else:
    DEFAULT_PATH = "google-chrome"

BROWSER_PATH = os.getenv("BROWSER_PATH", DEFAULT_PATH)

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