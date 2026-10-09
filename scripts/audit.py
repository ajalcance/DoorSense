#!/usr/bin/env python3
"""Repeat source regression/build checks; no installs, downloads, services or capture."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NODE = '/opt/homebrew/opt/node@22/bin/node'


def main():
    env = os.environ.copy()
    env.update(MPLCONFIGDIR=str(ROOT/'.runtime/matplotlib'), XDG_CACHE_HOME=str(ROOT/'.runtime/cache'))
    steps = (
        ('backend_regression', ROOT, [sys.executable, '-m', 'unittest', 'discover', '-s', 'scripts', '-p', 'test_*.py']),
        ('frontend_regression', ROOT, [NODE, '--test', 'frontend/src/session.test.js']),
        ('production_build', ROOT/'frontend', [NODE, 'node_modules/vite/bin/vite.js', 'build']),
        ('static_render_build', ROOT/'frontend', [NODE, 'node_modules/vite/bin/vite.js', 'build', '--ssr', 'src/ConsoleView.jsx', '--outDir', '.runtime/console-render']),
        ('static_markup', ROOT/'frontend', [NODE, 'scripts/check_console_markup.mjs']),
        ('live_bundle', ROOT, [sys.executable, 'scripts/check_live_bundle.py']),
        ('documentation_links', ROOT, [sys.executable, 'scripts/check_docs.py']),
    )
    results = []
    for name, cwd, command in steps:
        print('Checking '+name, flush=True)
        try:
            result = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
            output = result.stdout + result.stderr
            passed = result.returncode == 0
        except (OSError, subprocess.TimeoutExpired) as error:
            output, passed = str(error), False
        results.append(dict(name=name, passed=passed, output=output[-16000:]))
        print(('PASS' if passed else 'FAIL')+' '+name, flush=True)
        if not passed:
            print(output[-3000:])
    sources = [*list((ROOT/'backend/doorsense').glob('*.py')), *list((ROOT/'frontend/src').glob('*'))]
    report = dict(generated_at=datetime.now(timezone.utc).isoformat(),
                  scope='Automated source/injected regression, production build and static markup. No rendered browser, genuine camera/new-model or offline acceptance.',
                  checks=results, passed=all(row['passed'] for row in results),
                  source_sha256={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sources if path.is_file()})
    path = ROOT/'.runtime/source-audit.json'
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Audit output escapes project')
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, indent=2)+'\n')
    print('Evidence saved to '+str(path))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
