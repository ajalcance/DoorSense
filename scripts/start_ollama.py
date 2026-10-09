#!/usr/bin/env python3
"""Owner Terminal foreground launcher. Ollama creates its own ~/.ollama identity keys."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="start the downloaded daemon explicitly")
    args = parser.parse_args()
    if not args.serve:
        print("Foreground plan: loopback 127.0.0.1:11434, cloud disabled, models in DoorSense. "
              "Ollama also creates identity keys in ~/.ollama. No Codex permission changes.")
        return 0
    receipt = json.loads((ROOT / ".runtime/assets-receipt.json").read_text())
    executable = (ROOT / receipt["ollama"]["executable"]).resolve()
    if not executable.is_relative_to(ROOT):
        raise ValueError("Executable escapes DoorSense")
    with executable.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != receipt["ollama"]["executable_sha256"]:
            raise ValueError("Ollama executable changed")
    models = (ROOT / "assets/models/ollama").resolve()
    if not models.is_relative_to(ROOT):
        raise ValueError("Model store escapes DoorSense")
    with socket.socket() as probe:
        try:
            probe.bind(("127.0.0.1", 11434))
        except OSError as error:
            raise ValueError("Port 11434 unavailable. Inspect the existing service; this launcher never stops it.") from error
    env = os.environ.copy()
    # Remove inherited Ollama options and proxy overrides; keep system HOME unchanged.
    for key in list(env):
        if key.startswith("OLLAMA_") or key.lower() in {"http_proxy", "https_proxy", "all_proxy", "no_proxy"}:
            env.pop(key)
    env.update({"OLLAMA_HOST": "127.0.0.1:11434", "OLLAMA_MODELS": str(models),
                "OLLAMA_NO_CLOUD": "1", "OLLAMA_NOHISTORY": "1", "OLLAMA_NOPRUNE": "1",
                "OLLAMA_CONTEXT_LENGTH": "2048", "OLLAMA_NUM_PARALLEL": "1",
                "OLLAMA_MAX_LOADED_MODELS": "1", "OLLAMA_KEEP_ALIVE": "60s"})
    print("Starting foreground Ollama; Ctrl+C stops it. Models stay in DoorSense; "
          "identity keys use ~/.ollama. Cloud disabled is a configuration, not a network firewall.", flush=True)
    os.execve(executable, [str(executable), "serve"], env)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as error:
        print(f"Ollama startup blocked: {error}", file=sys.stderr)
        raise SystemExit(1)
