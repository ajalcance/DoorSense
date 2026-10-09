# Local preparation

Status: Slice 2 backend/frontend resolution, installation and imports passed,
with one explicitly recorded MediaPipe wheel-metadata exception. Ollama, Qwen and
vision assets are acquired and their local bytes verified. Foreground Ollama
startup and exact local Qwen metadata checks passed in owner Terminal. No
extra runtime download is needed for the prepared owner checkout. Genuine camera inference
and four supported Qwen examples worked; full offline acceptance remains pending.

## Checkout and repository check

With Git installed and repository access, a new contributor can clone it:

```sh
git clone https://github.com/ajalcance/DoorSense.git
cd DoorSense
git status --short --branch
python3 scripts/check_docs.py
```

The owner's existing local workspace is `Hackathon/DoorSense` under the selected
Codex workspace. That checkout is independent of the parent workspace's Git repo.
GitHub connector authorisation and local `git`/`gh` authentication are separate.
Do not paste tokens into chat or store them in this repository.

## Recorded preflight and installed pins

The checked computer is a MacBook Air M1, 8 GB, macOS 14.1.2 ARM64. Existing
Python 3.12.13 and Homebrew Node 22.23.1 are selected without changing global
defaults. Approximately 9.4 GiB was available during preflight. Camera permission,
external display configuration and combined resource use need current acceptance.
Camera permission/inference subsequently worked in owner runs.

- Backend direct pins: [requirements.in](../backend/requirements.in). MediaPipe
  0.10.21, NumPy 1.26.4, one OpenCV provider (contrib 4.11.0.86), JAX/JAXlib 0.4.35,
  FastAPI 0.143.0, Uvicorn 0.54.0 and HTTPX 0.28.1. JAX is a declared MediaPipe
  dependency, not a DoorSense training feature. SQLite uses the Python standard library.
- Frontend direct pins: [package.json](../frontend/package.json), React/React DOM
  19.3.0, Vite 8.3.4 and React plugin 6.1.2. The console is implemented and builds locally.
- Assets: [runtime manifest](../assets/runtime-manifest.json), Ollama 0.40.1,
  Qwen3 0.6B and EfficientDet-Lite0 int8 version 1. Full local hashes and sizes
  are recorded only after acquisition. The Qwen publisher lists approximately 523 MB.

The installed set passes the source audit; live/offline acceptance is separate.
The online command produces
the full Python hash lock and npm integrity lock before installing, reuses existing
locks on subsequent runs, and refuses source builds and npm lifecycle scripts.
Python wheels are retained for offline reinstalls. npm dependencies/cache remain
local; reproducible offline npm reinstallation has not yet been tested. The owner
acquisition subsequently completed and both dependency locks now exist.

The owner command resolved and installed the backend successfully, then stopped
at `pip check`. The publisher's Python 3.12 universal2 MediaPipe wheel contains
the inconsistent internal tag `cp312-cp312-macosx_14_0_x86_64`. The main bindings
contain ARM64 code and the actual imports passed on this M1. `runtime_health.py`
retains the original package metadata and permits only this exact diagnostic,
only on macOS 14+ ARM64/Python 3.12, after checking the published archive SHA-256,
installed metadata/native bytes and bounded native-binding imports. Other pip
errors still block preparation. Raw `pip check` continues to report the mismatch;
the project check records the verified exception explicitly. Detector inference
has passed in owner camera runs; broader quality and offline checks remain pending.

MediaPipe 1.1.0 declares usage metrics. Version 0.10.21 is selected as a candidate
because an upstream reporter observed no outbound connections from that version.
This report is not a guarantee of no telemetry. Verify the installed bytes and
network behaviour during runtime acceptance before making that claim.

Sources: [MediaPipe release](https://pypi.org/project/mediapipe/0.10.21/),
[telemetry report](https://github.com/google-ai-edge/mediapipe/issues/6291),
[Vite requirements](https://vite.dev/guide/),
[vision model guide](https://developers.google.com/edge/mediapipe/solutions/vision/object_detector),
[Ollama release](https://github.com/ollama/ollama/releases/tag/v0.40.1).

## Owner online acquisition

Run this in macOS **Terminal**, while internet is available, from the owner's
existing checkout. The current Codex `doorsense` profile blocks command networking
and sandbox escalation; it is not changed by this preparation. Terminal commands
are outside Codex's sandbox.

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/prepare_runtime.py --online &&
.venv/bin/python scripts/check_runtime.py --imports --assets
```

The checked existing `uv` and Node 22 are expected under `/opt/homebrew/`.
The `.venv` was created from the existing Python 3.12.13; backend packages are
now installed there. No Homebrew/global package installations,
camera capture or service startup are performed. Downloads and tool caches are
placed under DoorSense; scripts do not modify user shell profiles or Codex settings.

The acquisition script obtains the pinned official Ollama CLI archive and requires
the release API's SHA-256. Extraction rejects archive path escapes. It obtains
Qwen's reviewed registry manifest directly, verifies the published digest prefix,
validates each layer against its full registry digest, and records the complete
manifest digest. This provisions the local store without starting Ollama or pulling
models at runtime. Store compatibility with the pinned daemon remains a live check.
The acquired full hashes are now tracked in the manifest and future acquisition
must match them. EfficientDet's SHA-256 is locally recorded; no independent publisher checksum or
asset-specific licence has yet been established. Its ignored weights are not redistributed.

Expected output: `ACQUISITION PASSED`, then `passed` for imports and asset-byte
checks. Full acquisition and those checks have passed. On error, stop and report the first
failure; the script does not remove existing files outside DoorSense. For diagnosis,
`--packages-only` or `--assets-only` can resume a separate acquisition stage.

Records are local and ignored: `.runtime/assets-receipt.json` and
`.runtime/runtime-checks.json`. Generated `backend/requirements.lock` and
`frontend/package-lock.json` are intended reproducibility files to review and commit
after successful acquisition. Both locks now exist.

## Explicit local Ollama startup and metadata check

After successful acquisition, run the following in a foreground Terminal:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/start_ollama.py --serve
```

**Ollama itself creates identity keys in `~/.ollama` at first startup.** This is
the known startup write outside DoorSense; its models remain in the repository.
The launcher does not change `HOME`, install an app, modify PATH, relax Codex's
sandbox, run model pulls, or stop any existing daemon. If port 11434 is occupied,
it refuses to proceed. Ctrl+C stops the foreground service.

The launcher sets `OLLAMA_HOST=127.0.0.1:11434`, `OLLAMA_NO_CLOUD=1`, short context,
one parallel request, one loaded model and no CLI history. Cloud disablement is
configuration, not an outbound firewall. Inspect the startup log for disabled
cloud configuration and verify listeners; do not infer network enforcement from it.

In a second Terminal, run:

```sh
cd "/Users/anymind/Documents/ChatGPT/Albert Space 2/Hackathon/DoorSense" &&
.venv/bin/python scripts/check_runtime.py --imports --assets --ollama
```

The check verifies the daemon version and exact acquired Qwen manifest digest.
It does not generate text, open the camera or call external services. Current
Codex commands may not reach even loopback under its network restriction, so these
checks run in owner Terminal. No policy change or Codex restart is required for
these owner commands. Genuine generation subsequently ran; disconnected restarts
remain a later acceptance checkpoint.

Owner startup/check evidence on 2026-10-09: all three checks passed; the daemon
reported version 0.40.1, exact acquired Qwen digest, cloud disabled and listening
on 127.0.0.1:11434. The loopback listener was independently observed in this chat.
Apple M1 Metal discovery was logged; this is not proof that inference ran on GPU.
The startup log's VRAM-based context default was 4096; future application requests
must explicitly set the planned 2048-token context instead of assuming a startup
setting determines the effective generation budget.

## Local assets and data

Record asset sources, licences and hashes in [disclosures](DISCLOSURES.md). Store
vision files and the Ollama store under ignored `assets/models/`. Keep reference PDFs under ignored
`private/reference/` and event state/recordings under ignored local-data directories.
Never auto-fetch missing assets at runtime.

## Application startup and acceptance

For a fresh Apple Silicon/macOS checkout, provide Python 3.12, existing Homebrew
Node 22 and `uv` first. The preparation script expects these runtimes and refuses
to install global tools. From the repository root, create the virtual environment
if absent, then provision dependencies and the required face asset online:

```sh
python3.12 -m venv .venv
.venv/bin/python scripts/prepare_runtime.py --online
.venv/bin/python scripts/prepare_scene_models.py --feature face --online
(cd frontend && /opt/homebrew/opt/node@22/bin/node node_modules/vite/bin/vite.js build)
.venv/bin/python scripts/check_runtime.py --imports --assets
```

The current owner checkout already has these dependencies and models. Do not
recreate its environment or reacquire weights for a routine restart. The build
command creates `frontend/dist/`; the checked stack is macOS ARM64, not a verified
cross-platform installer. Start prepared Ollama as above, then in another Terminal:

```sh
.venv/bin/python scripts/console.py
```

Open `http://127.0.0.1:8765`, refresh and click Start. Face analysis is enabled by
default; pose is not required. The camera and Child safety mode initially remain
off. Ctrl+C stops the service; enrollment survives restart.

The [camera spike](CAMERA_SPIKE.md) passed basic owner acceptance; the bounded
[Qwen spike](LLM_SPIKE.md) has four genuine supported results and an application
question guard. The face-recognition console is implemented. Follow the
[current startup and demo](FAMILY_REFERENCE.md); no routine spike repetition is
required. Existing Ollama may be left running, but verify its listener in a new
session. Owner commands operate outside the Codex sandbox. Then execute
[offline acceptance](DEMO_AND_ACCEPTANCE.md) with both application and Ollama
restarted without external network connections.
