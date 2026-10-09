#!/usr/bin/env python3
"""Local source/asset readiness inventory; no network, Git mutations or live claims."""
import hashlib
import json
from pathlib import Path
import sys

from check_runtime import assets

ROOT = Path(__file__).resolve().parents[1]


def source_files(root=ROOT):
    # Explicit allowlist excludes private history/media, model weights, caches,
    # installed packages, runtime reports, credentials and obsolete UI fixtures.
    files = [root/name for name in ('README.md', 'WORKING_PLAN.md', 'CONTRIBUTING.md',
                                  '.gitignore', '.gitattributes', '.editorconfig',
                                  '.github/pull_request_template.md', 'backend/README.md',
                                  'frontend/README.md', 'hardware/README.md',
                                  'security/codex-config.toml', 'security/pre_tool_gate.py')]
    for directory, pattern in (('docs', '*.md'), ('demo', '*.md'), ('backend/doorsense', '*.py'),
                               ('scripts', '*.py'), ('frontend/src', '*'), ('frontend/scripts', '*.mjs')):
        files.extend((root/directory).glob(pattern))
    files.extend(root/name for name in ('backend/requirements.in', 'backend/requirements.lock',
        'frontend/package.json', 'frontend/package-lock.json', 'frontend/index.html', 'frontend/vite.config.js',
        'assets/runtime-manifest.json', 'assets/scene-models.json', 'assets/README.md'))
    return sorted({file for file in files if file.is_file() and file.name not in ('fixtures.js', 'fixtures.test.js', 'console_preview.py')})


def inventory(root=ROOT):
    output = []
    for path in source_files(root):
        resolved = path.resolve()
        if not resolved.is_relative_to(root.resolve()):
            raise ValueError('Reproduction source escapes project: '+str(path))
        output.append(dict(path=str(path.relative_to(root)), bytes=path.stat().st_size,
                           sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    return output


def main():
    blockers = []
    try:
        assets()
    except Exception as error:
        blockers.append('Initial model/runtime bytes: '+str(error))
    sys.path.insert(0, str(ROOT/'backend'))
    # Avoid importing MediaPipe or constructing models for inventory.
    specs = json.loads((ROOT/'assets/scene-models.json').read_text())
    receipt_path = ROOT/'.runtime/scene-assets.json'
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    # Only face analysis is enabled in the current demo; pose is historical/optional.
    for name in ('face',):
        spec = specs[name]
        path = ROOT/'assets/models'/spec['filename']
        record = receipt.get(name, {})
        if not path.is_file() or record.get('url') != spec['url'] or record.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest() or record.get('bytes') != path.stat().st_size:
            blockers.append(name+' model missing/unverified')
    if not (ROOT/'frontend/dist/index.html').is_file():
        blockers.append('Production frontend build missing')
    report = dict(scope='Local source/asset inventory only; not genuine inference, clean-machine reproduction or offline acceptance.',
                  files=inventory(), blockers=blockers, source_assets_ready=not blockers,
                  exclusions='Private data/media, models, runtime reports, dependencies, credentials and protected metadata.',
                  outstanding='Asset-specific licences, owner live/offline acceptance, actual recording, public repository, social post, organiser eligibility and submission.')
    path = ROOT/'.runtime/reproduction-inventory.json'
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Inventory destination escapes project')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'files'}, indent=2))
    print(str(len(report['files']))+' source fingerprints recorded; no files published.')
    return 0 if not blockers else 1


if __name__ == '__main__':
    raise SystemExit(main())
