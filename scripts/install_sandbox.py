#!/usr/bin/env python3
"""Owner-run installer: writes only the project's protected .codex directory."""

import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = Path("/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense")


def main():
    if ROOT != EXPECTED:
        raise SystemExit("STOP: this configuration is tied to the owner's DoorSense path.")
    target = ROOT / ".codex"
    if target.is_symlink():
        raise SystemExit("STOP: .codex must not be a symlink.")
    config = (ROOT / "security/codex-config.toml").read_bytes()
    parsed = tomllib.loads(config.decode())
    if parsed["default_permissions"] != "doorsense" or parsed["approval_policy"] != "never":
        raise SystemExit("STOP: unexpected sandbox defaults.")
    gate = (ROOT / "security/pre_tool_gate.py").read_bytes()
    compile(gate, "pre_tool_gate.py", "exec")
    hooks = {"hooks": {
        "PreToolUse": [{"matcher": "^(Bash|apply_patch|Edit|Write)$", "hooks": [{
            "type": "command",
            "command": '/usr/bin/python3 "' + str(target / "pre_tool_gate.py") + '"',
            "timeout": 5,
            "statusMessage": "Checking DoorSense safety gate"
        }]}],
        "PermissionRequest": [{"matcher": "*", "hooks": [{
            "type": "command",
            "command": '/usr/bin/python3 "' + str(target / "pre_tool_gate.py") + '"',
            "timeout": 5
        }]}]
    }}
    files = {
        "config.toml": config,
        "hooks.json": (json.dumps(hooks, indent=2) + "\n").encode(),
        "pre_tool_gate.py": gate,
    }
    # Preflight all conflicts before changing anything. Re-running is idempotent.
    for name, content in files.items():
        path = target / name
        if path.is_symlink() or (path.exists() and path.read_bytes() != content):
            raise SystemExit(f"STOP: {path} already exists with different contents; nothing overwritten.")
    target.mkdir(exist_ok=True)
    for name, content in files.items():
        path = target / name
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(content)
            path.chmod(0o600)
    print("INSTALLED: DoorSense profile and hook files. Existing session unchanged.")
    print("NEXT: restart Codex, select the doorsense permission profile, and trust the hook once.")
    print("CLI hook trust: open Codex in this repo, enter /hooks, and trust these two hook definitions.")
    print("Do not use full access. Ask this chat to verify the active profile before implementation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
