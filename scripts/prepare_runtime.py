#!/usr/bin/env python3
"""Owner-run online acquisition. No camera, services, global installs or shell commands."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
MANIFEST = json.loads((ROOT / "assets/runtime-manifest.json").read_text())
MAX_ASSET_BYTES = 3 * 1024**3


def inside(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError(f"Destination escapes DoorSense: {path}")
    return path


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def request(url):
    if not url.startswith("https://"):
        raise ValueError("Acquisition requires HTTPS")
    response = urllib.request.urlopen(urllib.request.Request(url, headers={
        "User-Agent": "DoorSense-owner-preparation",
        "Accept": "application/json, application/vnd.docker.distribution.manifest.v2+json",
    }), timeout=90)
    if not response.url.startswith("https://"):
        response.close()
        raise ValueError("Non-HTTPS redirect rejected")
    return response


def fetch_json(url):
    with request(url) as response:
        raw = response.read(4 * 1024**2 + 1)
    if len(raw) > 4 * 1024**2:
        raise ValueError("Metadata is unexpectedly large")
    return json.loads(raw), raw


def download(url, path, expected=None, size=None):
    path = inside(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if not expected:
            raise ValueError(f"Existing unverified asset requires inspection: {path}")
        if digest(path) != expected or (size is not None and path.stat().st_size != size):
            raise ValueError(f"Existing asset fails integrity check: {path}")
        return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
                "sha256": expected, "source": url}
    if size is not None and not 0 < size <= MAX_ASSET_BYTES:
        raise ValueError("Asset exceeds preparation size limit")
    temporary = inside(path.with_name(path.name + ".part"))
    print(f"Downloading {path.name}" + (f" ({size / 1e6:.1f} MB)" if size else ""), flush=True)
    total = 0
    h = hashlib.sha256()
    with request(url) as response, temporary.open("wb") as output:
        while block := response.read(1024**2):
            total += len(block)
            if total > MAX_ASSET_BYTES:
                raise ValueError("Download exceeds preparation size limit")
            h.update(block)
            output.write(block)
    actual = h.hexdigest()
    if (expected and actual != expected) or (size is not None and total != size):
        raise ValueError(f"Downloaded asset fails integrity check: {path.name}")
    temporary.replace(path)
    return {"path": str(path.relative_to(ROOT)), "bytes": total,
            "sha256": actual, "source": url}


def safe_extract(archive, destination):
    destination = inside(destination)
    # Only a fresh directory is accepted; Python's data filter validates links,
    # special files and every member before writing outside this directory.
    destination.mkdir()
    with tarfile.open(archive, "r:gz") as source:
        source.extractall(destination, filter="data")


def run(args, env, cwd=ROOT):
    print("Running " + " ".join(str(arg) for arg in args), flush=True)
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, check=True)


def packages():
    inside(ROOT / ".venv")
    # resolve() points to the read-only existing base interpreter for a venv
    # symlink, so use its lexical path for execution and validate the venv itself.
    python = ROOT / ".venv/bin/python"
    node_dir = Path("/opt/homebrew/opt/node@22/bin")
    uv = Path("/opt/homebrew/bin/uv")
    if not uv.is_file() or not (node_dir / "node").is_file():
        raise ValueError("Existing uv / Node 22 is unavailable; no automatic runtime installation")
    for path in (RUNTIME, ROOT / "frontend/node_modules"):
        inside(path)
    env = os.environ.copy()
    for key in list(env):
        if key.startswith(("UV_", "PIP_")) or key.lower().startswith("npm_config_") or key == "NODE_OPTIONS":
            env.pop(key)
    env.update({"PATH": str(node_dir) + os.pathsep + env.get("PATH", ""),
                "UV_CACHE_DIR": str(RUNTIME / "uv-cache"),
                "UV_PYTHON_DOWNLOADS": "never", "PIP_DISABLE_PIP_VERSION_CHECK": "1",
                "PIP_CONFIG_FILE": os.devnull,
                "MPLCONFIGDIR": str(RUNTIME / "matplotlib"),
                "XDG_CACHE_HOME": str(RUNTIME / "cache")})
    lock = inside(ROOT / "backend/requirements.lock")
    if not lock.exists():
        pending = inside(lock.with_suffix(".pending"))
        run([uv, "--no-config", "pip", "compile", "backend/requirements.in",
             "--python", python, "--only-binary", ":all:", "--prerelease", "disallow",
             "--generate-hashes", "--format", "requirements.txt", "--output-file", pending,
             "--default-index", "https://pypi.org/simple"], env)
        pending.replace(lock)
    wheels = inside(RUNTIME / "wheels")
    wheels.mkdir(exist_ok=True)
    pip = [python, "-m", "pip", "--isolated", "--disable-pip-version-check",
           "--cache-dir", RUNTIME / "pip-cache"]
    run(pip + ["download", "--index-url", "https://pypi.org/simple", "--only-binary", ":all:",
               "--require-hashes", "-r", lock, "--dest", wheels], env)
    run(pip + ["install", "--no-index", "--find-links", wheels, "--only-binary", ":all:",
               "--require-hashes", "-r", lock], env)
    run([python, ROOT / "scripts/runtime_health.py"], env)
    # Ignore lifecycle scripts; use npm's ARM64 optional packages, then verify
    # actual imports. No application build is claimed at this checkpoint.
    for config in ("npm-user.conf", "npm-global.conf"):
        inside(RUNTIME / config).touch(exist_ok=True)
    npm = [node_dir / "npm", "--cache", RUNTIME / "npm-cache",
           "--userconfig", RUNTIME / "npm-user.conf", "--globalconfig", RUNTIME / "npm-global.conf",
           "--registry", "https://registry.npmjs.org", "--ignore-scripts", "--no-audit", "--no-fund",
           "--global=false", "--update-notifier=false"]
    frontend = ROOT / "frontend"
    inside(frontend / "package-lock.json")
    if not (frontend / "package-lock.json").exists():
        run(npm + ["install", "--package-lock-only"], env, frontend)
    run(npm + ["ci"], env, frontend)
    run([node_dir / "node", "--input-type=module", "-e",
         "await import('react'); await import('react-dom/client'); "
         "await import('vite'); await import('@vitejs/plugin-react'); "
         "console.log('Frontend imports passed');"], env, frontend)
    run([python, ROOT / "scripts/check_runtime.py", "--imports"], env)


def assets():
    receipt_path = inside(RUNTIME / "assets-receipt.json")
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    spec = MANIFEST["ollama"]
    release, _ = fetch_json(spec["release_api"])
    if release.get("tag_name") != "v" + spec["version"] or release.get("prerelease"):
        raise ValueError("Ollama release is not the pinned stable version")
    archive = next(a for a in release["assets"] if a["name"] == spec["archive"])
    checksum = archive.get("digest", "")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", checksum):
        raise ValueError("Pinned Ollama archive has no publisher SHA-256; inspection required")
    if spec.get("acquired_archive_sha256") and checksum[7:] != spec["acquired_archive_sha256"]:
        raise ValueError("Ollama release bytes changed from the acquired archive")
    record = download(archive["browser_download_url"], RUNTIME / spec["archive"],
                      checksum[7:], archive["size"])
    target = inside(RUNTIME / ("ollama-" + spec["version"]))
    if not target.exists():
        with tempfile.TemporaryDirectory(dir=RUNTIME) as stage:
            unpacked = Path(stage) / "unpacked"
            safe_extract(RUNTIME / spec["archive"], unpacked)
            unpacked.rename(target)
    executables = [p for p in target.rglob("ollama") if p.is_file() and os.access(p, os.X_OK)]
    if len(executables) != 1:
        raise ValueError("Expected one executable Ollama CLI in the official archive")
    record.update({"version": spec["version"], "licence": spec["licence"],
                   "executable": str(executables[0].relative_to(ROOT)),
                   "executable_sha256": digest(executables[0])})
    receipt["ollama"] = record
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

    vision = MANIFEST["vision"]
    previous = vision.get("acquired_sha256") or receipt.get("vision", {}).get("sha256")
    receipt["vision"] = download(vision["url"], ROOT / "assets/models" / vision["filename"], previous)
    receipt["vision"]["hash_status"] = "locally measured; no publisher checksum established"
    receipt["vision"]["licence_status"] = vision["licence_status"]
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")

    qwen = MANIFEST["qwen"]
    document, raw = fetch_json(qwen["manifest_url"])
    manifest_hash = hashlib.sha256(raw).hexdigest()
    if not manifest_hash.startswith(qwen["published_digest_prefix"]):
        raise ValueError("Qwen tag changed from the reviewed digest; refusing a different model")
    if qwen.get("acquired_manifest_sha256") and manifest_hash != qwen["acquired_manifest_sha256"]:
        raise ValueError("Qwen manifest differs from the acquired full digest")
    if "layers" not in document or "config" not in document:
        raise ValueError("Unexpected Qwen registry manifest format")
    records = []
    store = inside(ROOT / "assets/models/ollama")
    for layer in [document["config"], *document["layers"]]:
        identifier = layer["digest"]
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", identifier):
            raise ValueError("Invalid model layer digest")
        record = download("https://registry.ollama.ai/v2/library/qwen3/blobs/" + identifier,
                          store / "blobs" / identifier.replace(":", "-"), identifier[7:], layer["size"])
        record["media_type"] = layer["mediaType"]
        records.append(record)
    manifest_path = inside(store / "manifests/registry.ollama.ai/library/qwen3/0.6b")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(raw)
    receipt["qwen"] = {"name": qwen["name"], "manifest_sha256": manifest_hash,
                       "bytes": sum(r["bytes"] for r in records), "layers": records,
                       "licence": qwen["licence"], "source": qwen["source"]}
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true", help="acquire packages/assets in owner Terminal")
    parser.add_argument("--packages-only", action="store_true")
    parser.add_argument("--assets-only", action="store_true")
    args = parser.parse_args()
    if args.packages_only and args.assets_only:
        parser.error("Choose at most one partial preparation mode")
    if not args.online:
        print("Plan: hash-lock and install local Python/npm dependencies; download pinned Ollama, "
              "EfficientDet-Lite0 and Qwen. No services or camera. Use --online in owner Terminal.")
        return 0
    if platform.system() != "Darwin" or platform.machine() != "arm64" or sys.version_info[:2] != (3, 12):
        raise ValueError("This acquisition plan requires macOS ARM64 and Python 3.12")
    if Path(sys.prefix).resolve() != inside(ROOT / ".venv"):
        raise ValueError("Run with DoorSense .venv/bin/python, never a global interpreter")
    inside(RUNTIME).mkdir(exist_ok=True)
    if shutil.disk_usage(ROOT).free < 3 * 1024**3:
        raise ValueError("At least 3 GiB free required; inspect storage before downloading")
    if not args.assets_only:
        packages()
    if not args.packages_only:
        assets()
    print("ACQUISITION PASSED. Runtime startup, model compatibility and offline acceptance remain pending.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, StopIteration, subprocess.CalledProcessError) as error:
        print(f"Preparation stopped: {error}. Existing files retained; no cleanup outside DoorSense.", file=sys.stderr)
        raise SystemExit(1)
