# DoorSense development sandbox

Prepared and owner-installed on 2026-10-09. The hook is active in the desktop chat.
The exact DoorSense profile and direct live boundary checks are verified.
This is development-tool protection, not a sandbox for the future DoorSense app.

Live checks after restart: the gate blocked a no-argument `/bin/rm` and denied
an escalation request for the no-op `/usr/bin/true`. A direct current-session
probe permitted repo/temp writes and denied parent-directory, protected-path,
symlink-escape writes and command networking. Nested sandbox probes were blocked
by macOS and were not counted as passes. After the owner selected `doorsense`,
session metadata confirmed only DoorSense/temp write grants and approval policy
`never`; the visualization directory no longer has a write grant. Direct native
checks and the harmless deletion-command gate check passed again in that profile.

## Small setup

The named `doorsense` Codex permission profile grants writes only to the exact
DoorSense directory and OS temporary directories. Other files remain readable.
`.git`, `.codex`, `.agents`, and `.aws` inside the repository remain read-only.
Command networking is disabled. `approval_policy = "never"` rejects requests
to escape the active sandbox instead of asking for approval. It does not mean
full access. Model/chat networking is separate from command networking.

A `PreToolUse` command hook also rejects common deletion commands, `sudo`,
destructive Git worktree commands, patch deletions, out-of-repository patches,
protected-path patches, and common safety-bypass flags. `PermissionRequest`
rejects exceptions if that event is reached. These are conservative accident
guards, not a parser for every possible shell script or program.

The prepared files are under [security](../security/codex-config.toml), with a
[gate script](../security/pre_tool_gate.py). The installer copies them into the
protected project `.codex` folder and refuses conflicting existing files.
It does not install dependencies, edit global settings, or change `/etc`.

## Owner activation

In the Mac Terminal, from DoorSense:

```sh
python3 scripts/check_sandbox.py
python3 scripts/install_sandbox.py
python3 scripts/check_sandbox.py --installed
```

Python 3.11+ is needed by the installer/checker for standard-library TOML support.
The currently detected `python3` is 3.14.7; no installation is needed on this Mac.
The system Python runs the installed gate and only needs Python 3.9+.

Quit and reopen Codex. Select the `doorsense` permission profile in a fresh
session. Project settings only load when the project is trusted; this project's
trust entry was present during preparation. Existing chats or app-selected
permission presets may retain their old settings. Ask the assistant to verify
the effective roots, network policy, approval policy, and hook activation before
application implementation. Do not switch to full access to resolve failures.

Codex requires one-time trust of each non-managed hook's exact definition.
Open Codex CLI in this directory, enter `/hooks`, and trust the two DoorSense
hook definitions. A changed hook needs trust again. CLI hook trust alone does
not certify that this desktop chat loaded the hook; verify it here after restart.

The installed check makes and removes uniquely named disposable probe files.
It tests repo/temp writes, parent-directory write denial, protected metadata,
symlink escape, and OS rejection of a connection to a reserved test address.
Timeouts and unreachable networks are inconclusive, not successful denial proof.
It does not delete or modify existing personal files.

## Limits and recovery

Project configuration supplies defaults, not an immutable administrator policy.
Manually selecting full access, overriding configuration, disabling hooks, or
running commands in an ordinary Terminal can bypass these project defaults.
Hooks must be loaded and trusted; unsupported tool paths, interactive input,
hook launch failures and timeouts can bypass hook checks. The OS sandbox is the
primary protection against writes outside DoorSense, including from Python or
other programs that do not use a deletion command.

Web search, browser/computer control and connectors have separate permissions.
This setup does not sandbox them. It does not protect arbitrary files inside the
repo from all programmatic deletion, and temporary directories remain writable.
Dependencies/downloads or future local Ollama/HTTP access require a separately
reviewed workflow; networking must not be silently broadened.

For rollback, use an ordinary owner Terminal to move `.codex` to a backup name
inside DoorSense, then restart Codex. Do not remove shared global or system policy.

Official references:

- [Permission profiles](https://learn.chatgpt.com/docs/permissions)
- [Hooks and coverage limits](https://learn.chatgpt.com/docs/hooks)
- [Sandbox and approval modes](https://learn.chatgpt.com/docs/sandboxing)
