#!/usr/bin/env python3
"""Owner-only acquisition of one optional model; no installs, services or capture."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 64 * 1024 * 1024


def inside(path):
    path = Path(path).resolve()
    root = ROOT.resolve()
    if not path.is_relative_to(root) or any(part in ('.git', '.codex', '.agents', '.aws') for part in path.relative_to(root).parts):
        raise ValueError('Destination escapes writable project files')
    return path


def verify_bundle(path):
    if not 0 < path.stat().st_size <= LIMIT:
        raise ValueError('Model bundle exceeds size limit or is empty')
    with zipfile.ZipFile(path) as archive:
        models = [info for info in archive.infolist() if info.filename.endswith('.tflite')]
        if len(models) < 2 or sum(info.file_size for info in archive.infolist()) > LIMIT:
            raise ValueError('Unexpected model bundle layout/expanded size')
        for info in models:
            with archive.open(info) as member:
                if member.read(8)[4:8] != b'TFL3':
                    raise ValueError('Invalid TensorFlow Lite member')


def acquire(name, online=False, import_file=None):
    spec = json.loads((ROOT / 'assets/scene-models.json').read_text())[name]
    destination = inside(ROOT / 'assets/models' / spec['filename'])
    receipt_path = inside(ROOT / '.runtime/scene-assets.json')
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    if destination.exists():
        record = receipt.get(name, {})
        if record.get('url') != spec['url'] or record.get('sha256') != hashlib.sha256(destination.read_bytes()).hexdigest() or record.get('bytes') != destination.stat().st_size:
            raise ValueError('Existing model has no matching receipt; preserve it and inspect manually')
        verify_bundle(destination)
        return record
    if not online and not import_file:
        raise ValueError('Explicit owner --online or --import-file required; runtime never acquires models')
    destination.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='scene-', suffix='.pending') as pending:
        if import_file:
            source = Path(import_file).open('rb')
        else:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            source = opener.open(spec['url'], timeout=90)
            if not source.url.startswith('https://storage.googleapis.com/mediapipe-models/'):
                source.close()
                raise ValueError('Unexpected acquisition redirect')
        size = 0
        with source:
            while block := source.read(1024 * 1024):
                size += len(block)
                if size > LIMIT:
                    raise ValueError('Acquisition exceeds model size limit')
                pending.write(block)
        pending.flush()
        verify_bundle(Path(pending.name))
        data = Path(pending.name).read_bytes()
        # Exclusive creation never replaces an existing local asset.
        with destination.open('xb') as output:
            output.write(data)
    record = dict(url=spec['url'], path=str(destination.relative_to(ROOT.resolve())), bytes=size,
                  sha256=hashlib.sha256(data).hexdigest(), acquired_at=datetime.now(timezone.utc).isoformat(),
                  hash_status='Locally measured acquisition hash; no independent publisher checksum established.',
                  licence_status=spec['licence_status'], acquisition='offline transfer' if import_file else 'owner HTTPS acquisition')
    receipt[name] = record
    with tempfile.NamedTemporaryFile(mode='w', dir=receipt_path.parent, prefix='scene-receipt-', delete=False) as temporary:
        json.dump(receipt, temporary, indent=2)
        temporary.write('\n')
    Path(temporary.name).replace(receipt_path)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feature', choices=('face', 'pose'), required=True)
    parser.add_argument('--online', action='store_true')
    parser.add_argument('--import-file', type=Path)
    args = parser.parse_args()
    if args.online and args.import_file:
        parser.error('Choose online acquisition or offline transfer')
    if not args.online and not args.import_file:
        print('PLAN ONLY: '+args.feature+' optional model. Add --online in owner Terminal or --import-file PATH. No action taken.')
        return 0
    print(json.dumps(acquire(args.feature, args.online, args.import_file), indent=2))
    print('Local bytes recorded. Genuine inference, feature quality, resource fit and asset licence remain separate checks.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit('Preparation stopped: '+str(error))
