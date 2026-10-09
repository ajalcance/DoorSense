"""Dependency check with one verified upstream wheel-metadata exception."""
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIAPIPE_WHEEL = "mediapipe-0.10.21-cp312-cp312-macosx_11_0_universal2.whl"
MEDIAPIPE_SHA256 = "a65508f8c0e28a73f519c8a717f95949b9d5b2fb3bf4a632b181cdb71224d62e"
EXPECTED_FAILURE = "mediapipe 0.10.21 is not supported on this platform"


def verified_mediapipe_exception():
    if platform.system() != "Darwin" or platform.machine() != "arm64" or sys.version_info[:2] != (3, 12):
        raise ValueError("MediaPipe exception only applies to macOS ARM64 / Python 3.12")
    if int(platform.mac_ver()[0].split(".")[0]) < 14:
        raise ValueError("Internal MediaPipe wheel metadata requires macOS 14+")
    distribution = importlib.metadata.distribution("mediapipe")
    if distribution.version != "0.10.21":
        raise ValueError("Unexpected MediaPipe version")
    wheel = (ROOT / ".runtime/wheels" / MEDIAPIPE_WHEEL).resolve()
    if not wheel.is_relative_to(ROOT):
        raise ValueError("Wheel path escapes DoorSense")
    with wheel.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != MEDIAPIPE_SHA256:
            raise ValueError("MediaPipe wheel is not the reviewed publisher artifact")
    with zipfile.ZipFile(wheel) as archive:
        metadata_path = "mediapipe-0.10.21.dist-info/WHEEL"
        metadata = archive.read(metadata_path)
        tags = [line for line in metadata.decode().splitlines() if line.startswith("Tag: ")]
        if tags != ["Tag: cp312-cp312-macosx_14_0_x86_64"]:
            raise ValueError("MediaPipe internal tag is not the known mismatch")
        paths = [metadata_path,
                 "mediapipe/python/_framework_bindings.cpython-312-darwin.so",
                 "mediapipe/tasks/cc/metadata/python/_pywrap_metadata_version.cpython-312-darwin.so",
                 "mediapipe/tasks/python/metadata/flatbuffers_lib/_pywrap_flatbuffers.cpython-312-darwin.so"]
        for relative in paths:
            installed = Path(distribution.locate_file(relative)).resolve()
            if not installed.is_relative_to((ROOT / ".venv").resolve()):
                raise ValueError("Installed MediaPipe is outside DoorSense's environment")
            if hashlib.sha256(installed.read_bytes()).digest() != hashlib.sha256(archive.read(relative)).digest():
                raise ValueError(f"Installed artifact differs from reviewed wheel: {relative}")
    # Import all three primary native bindings in a bounded subprocess. Success
    # proves the ARM64 loader accepts them; it does not prove detector inference.
    cache = (ROOT / ".runtime").resolve()
    if not cache.is_relative_to(ROOT):
        raise ValueError("Import cache escapes DoorSense")
    env = os.environ.copy()
    env.update({"MPLCONFIGDIR": str(cache / "matplotlib"), "XDG_CACHE_HOME": str(cache / "cache")})
    code = "; ".join("import " + name for name in (
        "mediapipe.python._framework_bindings",
        "mediapipe.tasks.cc.metadata.python._pywrap_metadata_version",
        "mediapipe.tasks.python.metadata.flatbuffers_lib._pywrap_flatbuffers"))
    subprocess.run([sys.executable, "-c", code], env=env, check=True, timeout=120)
    return {"status": "verified metadata exception", "wheel_sha256": MEDIAPIPE_SHA256,
            "note": "Published universal2 wheel has Intel-only internal tag; original metadata retained. "
                    "Installed primary bindings match the publisher artifact and load on ARM64. "
                    "Model inference remains unverified."}


def dependencies():
    cache = (ROOT / ".runtime/pip-cache").resolve()
    if not cache.is_relative_to(ROOT):
        raise ValueError("pip cache escapes DoorSense")
    result = subprocess.run([sys.executable, "-m", "pip", "--isolated", "--disable-pip-version-check",
                             "--cache-dir", str(cache), "check"], capture_output=True, text=True, timeout=30)
    if result.returncode == 0:
        return {"status": "passed", "pip_check": result.stdout.strip()}
    if result.returncode == 1 and result.stdout.strip() == EXPECTED_FAILURE and not result.stderr.strip():
        return verified_mediapipe_exception()
    raise ValueError("Dependency check failed: " + (result.stdout + result.stderr).strip())


if __name__ == "__main__":
    try:
        print(json.dumps(dependencies(), indent=2))
    except Exception as error:
        print(f"Dependency check blocked: {error}", file=sys.stderr)
        raise SystemExit(1)
