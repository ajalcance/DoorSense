#!/usr/bin/env python3
"""Explicit local checks; never install, pull a model, capture frames or start services."""
import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
import urllib.request
from runtime_health import dependencies

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "assets/runtime-manifest.json").read_text())


def sha(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def verify_record(record):
    path = (ROOT / record["path"]).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("Receipt path escapes DoorSense")
    if path.stat().st_size != record["bytes"] or sha(path) != record["sha256"]:
        raise ValueError(f"Integrity mismatch: {record['path']}")


def imports():
    dependency_status = dependencies()
    versions = {}
    for line in (ROOT / "backend/requirements.in").read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        name, expected = line.split("==")
        actual = importlib.metadata.version(name)
        if actual != expected:
            raise ValueError(f"{name}: expected {expected}, found {actual}")
        versions[name] = actual
    # Avoid user-home Matplotlib cache writes during the MediaPipe import.
    if not (ROOT / ".runtime").resolve().is_relative_to(ROOT):
        raise ValueError("Cache destination escapes DoorSense")
    os.environ["MPLCONFIGDIR"] = str(ROOT / ".runtime/matplotlib")
    os.environ["XDG_CACHE_HOME"] = str(ROOT / ".runtime/cache")
    for name in ("fastapi", "uvicorn", "httpx", "cv2", "mediapipe", "numpy", "jax", "jaxlib", "sqlite3"):
        importlib.import_module(name)
    for name in ("opencv-python", "opencv-python-headless", "opencv-contrib-python-headless"):
        try:
            importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            continue
        raise ValueError(f"Multiple cv2 providers: unexpected {name}")
    installed = []
    for distribution in importlib.metadata.distributions():
        metadata = distribution.metadata
        installed.append({"name": metadata["Name"], "version": distribution.version,
                          "licence": metadata.get("License-Expression") or metadata.get("License") or "not declared",
                          "source": metadata.get_all("Project-URL", [])})
    frontend = ROOT / "frontend/package-lock.json"
    npm_licences = []
    if frontend.exists():
        for path, package in json.loads(frontend.read_text()).get("packages", {}).items():
            if path:
                npm_licences.append({"path": path, "version": package.get("version"),
                                     "licence": package.get("license", "not declared"),
                                     "integrity": package.get("integrity")})
    return {"direct_pins": versions, "dependency_check": dependency_status,
            "installed_python_metadata": installed,
            "npm_lock_metadata": npm_licences,
            "licence_note": "metadata inventory only; missing declarations need review"}


def assets():
    receipt = json.loads((ROOT / ".runtime/assets-receipt.json").read_text())
    for name in ("ollama", "vision"):
        verify_record(receipt[name])
    if receipt["ollama"]["sha256"] != MANIFEST["ollama"]["acquired_archive_sha256"]:
        raise ValueError("Ollama receipt differs from the tracked archive hash")
    if receipt["vision"]["sha256"] != MANIFEST["vision"]["acquired_sha256"]:
        raise ValueError("Vision receipt differs from the tracked acquired hash")
    if receipt["vision"]["path"] != "assets/models/" + MANIFEST["vision"]["filename"]:
        raise ValueError("Vision file is not at the configured model path")
    executable = (ROOT / receipt["ollama"]["executable"]).resolve()
    if not executable.is_relative_to(ROOT) or sha(executable) != receipt["ollama"]["executable_sha256"]:
        raise ValueError("Ollama executable integrity mismatch")
    raw = (ROOT / "assets/models/ollama/manifests/registry.ollama.ai/library/qwen3/0.6b").read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != receipt["qwen"]["manifest_sha256"] or not actual.startswith(MANIFEST["qwen"]["published_digest_prefix"]):
        raise ValueError("Qwen manifest mismatch")
    if actual != MANIFEST["qwen"]["acquired_manifest_sha256"]:
        raise ValueError("Qwen receipt differs from the tracked manifest hash")
    document = json.loads(raw)
    expected_layers = [document["config"], *document["layers"]]
    if len(expected_layers) != len(receipt["qwen"]["layers"]):
        raise ValueError("Qwen layer inventory is incomplete")
    for expected, layer in zip(expected_layers, receipt["qwen"]["layers"]):
        identifier = expected["digest"]
        expected_path = "assets/models/ollama/blobs/" + identifier.replace(":", "-")
        if layer["sha256"] != identifier[7:] or layer["bytes"] != expected["size"] or layer["path"] != expected_path:
            raise ValueError("Qwen layer receipt differs from the pinned registry manifest")
        verify_record(layer)
    return {name: "local bytes verified" for name in ("ollama", "vision", "qwen")}


def local_json(path):
    # Ignore ambient HTTP proxy settings: these are explicitly loopback-only checks.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open("http://127.0.0.1:11434" + path, timeout=10) as response:
        return json.load(response)


def ollama():
    version = local_json("/api/version")
    if version.get("version") != MANIFEST["ollama"]["version"]:
        raise ValueError("Ollama daemon is not the pinned runtime")
    receipt = json.loads((ROOT / ".runtime/assets-receipt.json").read_text())
    model = next(m for m in local_json("/api/tags")["models"] if m["name"] == MANIFEST["qwen"]["name"])
    if model["digest"] != receipt["qwen"]["manifest_sha256"]:
        raise ValueError("Served Qwen digest differs from acquired model")
    return {"version": version["version"], "name": model["name"], "digest": model["digest"],
            "note": "metadata only; no generation, cloud or offline acceptance test"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--imports", action="store_true")
    parser.add_argument("--assets", action="store_true")
    parser.add_argument("--ollama", action="store_true", help="owner Terminal; requires foreground local daemon")
    args = parser.parse_args()
    report = {"python": platform.python_version(), "architecture": platform.machine(),
              "scope": "preparation checks; no camera, model inference or offline acceptance"}
    failed = False
    for name, requested, check in (("imports", args.imports, imports), ("assets", args.assets, assets),
                                    ("ollama", args.ollama, ollama)):
        if requested:
            try:
                report[name] = {"status": "passed", "details": check()}
            except Exception as error:
                failed = True
                report[name] = {"status": "blocked", "reason": str(error)}
    display = json.loads(json.dumps(report))
    if display.get("imports", {}).get("status") == "passed":
        details = display["imports"]["details"]
        for key in ("installed_python_metadata", "npm_lock_metadata"):
            details[key] = f"{len(details[key])} records saved in .runtime/runtime-checks.json"
    print(json.dumps(display, indent=2))
    if any((args.imports, args.assets, args.ollama)):
        destination = (ROOT / ".runtime").resolve()
        if not destination.is_relative_to(ROOT):
            raise ValueError("Report destination escapes DoorSense")
        destination.mkdir(exist_ok=True)
        report_path = destination / "runtime-checks.json"
        if not report_path.resolve().is_relative_to(ROOT):
            raise ValueError("Report path escapes DoorSense")
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
