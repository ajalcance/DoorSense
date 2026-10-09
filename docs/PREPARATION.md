# Local preparation

Status: repository setup only. No runtime dependencies or models installed by this
step; no application startup command exists yet.

## Checkout and repository check

With Git installed, a new contributor can clone the public repository:

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

## Runtime preflight, before implementation

Confirm macOS, Python compatibility, camera permissions and external display.
Select and pin compatible packages and small vision model bundles after the
camera spike. The proposed stack is Python/FastAPI/OpenCV/MediaPipe/SQLite and
React/Vite. There is no verified dependency lockfile yet.

## Qwen provisioning plan

Install Ollama from its official distribution before disconnecting. Once installed,
provision the selected model while internet is available:

```sh
ollama pull qwen3:0.6b
```

This command is a preparation instruction and has not been executed by this
repository setup. Record actual model digest, licence, runtime version and size.
The publisher's listed quantized download is 523 MB; total RAM use is larger.

For offline runtime, stop any existing Ollama daemon and restart one instance with
`OLLAMA_NO_CLOUD=1`; keep the service on loopback. Verify the effective configuration,
local model availability and `think: false` on actual application requests. Do not
run simultaneous app-managed and terminal-managed Ollama servers on port 11434.
The application adapter will use `http://127.0.0.1:11434/api/chat` and bounded calls.

## Local assets and data

Record asset sources, licences and hashes in [disclosures](DISCLOSURES.md). Store
manually acquired model files under ignored `assets/models/`; Ollama-managed
weights stay in Ollama's store. Keep reference PDFs under ignored
`private/reference/` and event state/recordings under ignored local-data directories.
Never auto-fetch missing assets at runtime.

## Application startup and acceptance

Pending implementation. Replace this section with tested install/build/start
commands once the application runs. Then execute [offline acceptance](DEMO_AND_ACCEPTANCE.md)
with both application and Ollama restarted without external network connections.
