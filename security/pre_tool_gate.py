#!/usr/bin/env python3
"""Supplementary accident guard. The OS sandbox enforces filesystem access."""

import json
from pathlib import Path
import shlex
import sys

ROOT = Path("/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense")
PROTECTED = {".git", ".codex", ".agents", ".aws"}


def check(event):
    if not isinstance(event, dict):
        return "Invalid hook event."
    if event.get("hook_event_name") == "PermissionRequest":
        return "DoorSense does not permit sandbox escapes or network exceptions."
    if event.get("hook_event_name") != "PreToolUse":
        return "Unexpected hook event."
    cwd = event.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).resolve().is_relative_to(ROOT):
        return "DoorSense gate requires the DoorSense working directory."
    args = event.get("tool_input")
    if not isinstance(args, dict):
        return "Invalid tool input."
    if args.get("sandbox_permissions") == "require_escalated":
        return "Sandbox escalation is blocked."
    command = args.get("command", args.get("cmd"))
    if not isinstance(command, str) or not command.strip():
        return "Missing command or patch."

    tool = event.get("tool_name")
    if tool in {"apply_patch", "Edit", "Write"}:
        headers = ("*** Add File: ", "*** Update File: ", "*** Move to: ")
        found = False
        for line in command.splitlines():
            if line.startswith("*** Delete File: "):
                return "File deletion is blocked by the DoorSense gate."
            for header in headers:
                if line.startswith(header):
                    found = True
                    path = (Path(cwd) / line[len(header):]).resolve()
                    if not path.is_relative_to(ROOT):
                        return "Patch destination is outside DoorSense."
                    relative = path.relative_to(ROOT)
                    if not relative.parts or relative.parts[0] in PROTECTED:
                        return "Patch destination is protected."
        return None if found else "Unrecognised patch format."

    if tool != "Bash":
        return "Unrecognised gated tool."
    tokens = shlex.split(command, posix=True)
    # Deliberately conservative. This detects common commands, not arbitrary
    # program behaviour, shell expansion, interactive input, or obfuscation.
    names = {Path(token).name for token in tokens}
    if names.intersection({"rm", "rmdir", "unlink", "shred", "sudo"}):
        return "Deletion commands and sudo are blocked by the DoorSense gate."
    if "-delete" in tokens:
        return "find -delete is blocked."
    if "git" in names and any(token in {"clean", "reset", "restore", "checkout"} for token in tokens):
        return "Destructive Git worktree commands are blocked; use an owner Terminal."
    if any(token in {"--yolo", "--dangerously-bypass-approvals-and-sandbox",
                     "--dangerously-bypass-hook-trust"} for token in tokens):
        return "Safety bypass flags are blocked."
    return None


def main():
    try:
        reason = check(json.load(sys.stdin))
    except Exception:
        reason = "DoorSense gate could not validate this request."
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
