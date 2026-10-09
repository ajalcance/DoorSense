#!/usr/bin/env python3
"""Check prepared policy and gate; --installed also probes native enforcement."""

import argparse
import errno
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def prepared_checks():
    config = tomllib.loads((ROOT / "security/codex-config.toml").read_text())
    assert config["approval_policy"] == "never"
    assert config["default_permissions"] == "doorsense"
    profile = config["permissions"]["doorsense"]
    assert profile["network"]["enabled"] is False
    assert {path for path, mode in profile["filesystem"].items() if mode == "write"} == {
        str(ROOT), ":slash_tmp", ":tmpdir"
    }
    for name in (".git", ".codex", ".agents", ".aws"):
        assert profile["filesystem"][str(ROOT / name)] == "read"
    spec = importlib.util.spec_from_file_location("doorsense_gate", ROOT / "security/pre_tool_gate.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def event(command, tool="Bash"):
        return {"hook_event_name": "PreToolUse", "cwd": str(ROOT),
                "tool_name": tool, "tool_input": {"command": command}}

    cases = [
        (event("python3 scripts/check_docs.py"), False),
        (event("git status --short"), False),
        (event("/bin/rm -rf /Users/anymind/Documents"), True),
        (event("find . -delete"), True),
        (event("sudo anything"), True),
        (event("git reset --hard"), True),
        (event("git clean -fd"), True),
        (event("codex --yolo"), True),
        (event("*** Begin Patch\n*** Add File: backend/example.py\n+x\n*** End Patch", "apply_patch"), False),
        (event("*** Begin Patch\n*** Delete File: README.md\n*** End Patch", "apply_patch"), True),
        (event("*** Begin Patch\n*** Add File: ../outside.txt\n+x\n*** End Patch", "apply_patch"), True),
        (event("*** Begin Patch\n*** Update File: .codex/config.toml\n@@\n+x\n*** End Patch", "apply_patch"), True),
        ({"hook_event_name": "PermissionRequest"}, True),
        ({}, True),
    ]
    for payload, blocked in cases:
        assert bool(module.check(payload)) == blocked, payload
    escalation = event("true")
    escalation["tool_input"]["sandbox_permissions"] = "require_escalated"
    assert module.check(escalation)
    result = subprocess.run([sys.executable, str(ROOT / "security/pre_tool_gate.py")],
                            input="not-json", text=True, capture_output=True)
    assert result.returncode == 2
    print(f"PASS: prepared profile and {len(cases) + 2} gate cases. Hooks are not activated by this check.")


PROBE = r'''
import errno, os, pathlib, socket, sys, tempfile, uuid
root = pathlib.Path(sys.argv[1])
name = ".doorsense-probe-" + uuid.uuid4().hex
def allowed(path):
    with path.open("x") as handle:
        handle.write("disposable DoorSense sandbox probe")
    path.unlink()
def denied(path):
    try:
        with path.open("x") as handle:
            handle.write("unexpected write permitted")
    except OSError as exc:
        if exc.errno not in (errno.EPERM, errno.EACCES, errno.EROFS):
            raise RuntimeError("Inconclusive denial: " + str(exc))
        return
    path.unlink()  # Only this newly-created, exclusively-opened probe file.
    raise RuntimeError("Sandbox allowed an out-of-bound write: " + str(path))
allowed(root / name)
allowed(pathlib.Path(tempfile.gettempdir()) / name)
denied(root.parent / name)
denied(root / ".codex" / name)
denied(root / ".git" / name)
link = root / (name + "-link")
try:
    link.symlink_to(root.parent, target_is_directory=True)
    denied(link / name)
finally:
    if link.is_symlink():
        link.unlink()
connection = socket.socket()
connection.settimeout(1)
try:
    connection.connect(("192.0.2.1", 443)) # Reserved test address, no HTTP/data sent.
except OSError as exc:
    if exc.errno not in (errno.EPERM, errno.EACCES):
        raise RuntimeError("Network denial not proven: " + str(exc))
else:
    raise RuntimeError("Command networking unexpectedly permitted")
finally:
    connection.close()
print("PASS: native sandbox permits repo/temp writes; blocks parent, protected paths, symlink escape and network.")
'''


def installed_checks():
    target = ROOT / ".codex"
    for name, source in (("config.toml", "codex-config.toml"), ("pre_tool_gate.py", "pre_tool_gate.py")):
        assert (target / name).read_bytes() == (ROOT / "security" / source).read_bytes(), "Installed file drift"
    hooks = json.loads((target / "hooks.json").read_text())["hooks"]
    assert set(hooks) == {"PreToolUse", "PermissionRequest"}
    codex = shutil.which("codex")
    if not codex:
        bundled = Path("/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex")
        if bundled.is_file():
            codex = str(bundled)
    if not codex:
        raise SystemExit("STOP: Codex executable not found. No installation was attempted.")
    result = subprocess.run([
        codex, "sandbox", "-C", str(ROOT), "--permission-profile", "doorsense",
        "--include-managed-config", sys.executable, "-c", PROBE, str(ROOT)
    ], timeout=30)
    if result.returncode:
        raise SystemExit("BLOCKED: native sandbox check failed. Do not treat the boundary as verified.")
    print("Native profile verified for this probe. Hook trust and this desktop chat still need live verification.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed", action="store_true")
    args = parser.parse_args()
    prepared_checks()
    if args.installed:
        installed_checks()
