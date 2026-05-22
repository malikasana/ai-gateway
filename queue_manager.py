import threading
import queue
import importlib
import os
import platform

# ── Single request queue — one at a time ──────────────────
_queue = queue.Queue()
_lock = threading.Lock()

def _get_handler(ai: str, mode: str):
    """
    Dynamically load the correct instance handler.
    Path: instances/{ai}/{os}/{mode}.py
    Each handler must implement: run(query, **kwargs) -> str
    """
    os_name = "windows" if platform.system() == "Windows" else "mac"
    try:
        module = importlib.import_module(f"instances.{ai}.{os_name}.{mode}")
        return module.run
    except ModuleNotFoundError:
        raise Exception(f"No handler found for ai='{ai}' mode='{mode}' os='{os_name}'. "
                       f"Expected: instances/{ai}/{os_name}/{mode}.py")

def process_request(ai: str, mode: str, query: str, **kwargs) -> str:
    """
    Thread-safe request processor.
    Acquires lock so only one request runs at a time.
    """
    with _lock:
        print(f"\n[Queue] Processing: ai={ai} mode={mode}")
        print(f"[Queue] Query: {query[:60]}...")
        handler = _get_handler(ai, mode)
        reply = handler(query, **kwargs)
        print(f"[Queue] Done: {len(reply)} chars")
        return reply