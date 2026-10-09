#!/usr/bin/env python3
"""Owner-only loopback service; camera remains off until console Start."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
os.environ["MPLCONFIGDIR"] = str(ROOT / ".runtime/matplotlib")
os.environ["XDG_CACHE_HOME"] = str(ROOT / ".runtime/cache")
sys.path.insert(0, str(ROOT / "backend"))

if __name__ == "__main__":
    import uvicorn
    from doorsense.console import create_app
    print("DoorSense: http://127.0.0.1:8765 — camera OFF; Child safety mode OFF; no recording. Ctrl+C stops service.", flush=True)
    uvicorn.run(create_app(), host="127.0.0.1", port=8765, workers=1, access_log=False)
