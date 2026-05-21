import threading
import queue
import importlib
import os

# ── Single request queue — one at a time ──────────────────
_queue = queue.Queue()
_lock = threading.Lock()

def _get_handler(ai: str, mode: str):
    """
    Dynamically load the correct instance handler.
    Path: instances/{ai}/{mode}.py
    Each handler must implement: run(query, **kwargs) -> str
    """
    try:
        module = importlib.import_module(f"instances.{ai}.{mode}")
        return module.run
    except ModuleNotFoundError:
        raise Exception(f"No handler found for ai='{ai}' mode='{mode}'. "
                       f"Expected: instances/{ai}/{mode}.py")

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
