"""Verify production assets exclude obsolete synthetic presentation paths."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
assets = list((ROOT / 'frontend/dist/assets').glob('*.js'))
if not assets:
    raise SystemExit('Build frontend production assets first')
bundle = '\n'.join(path.read_text() for path in assets)
for text in ('UI fixture', 'Fixture detector reports', 'Show fixture answer',
             'Synthetic presentation', 'fixtureAnswer', 'UI fixture scenarios'):
    if text in bundle:
        raise SystemExit('Unexpected presentation-only content: ' + text)
for name in ('main.jsx', 'ConsoleView.jsx', 'session.js', 'contracts.js'):
    text = (ROOT / 'frontend/src' / name).read_text()
    if 'fixtures.js' in text or 'fixtureAnswer' in text:
        raise SystemExit('Obsolete fixture dependency: ' + name)
scripts = json.loads((ROOT / 'frontend/package.json').read_text())['scripts']
if 'fixtures.test.js' in scripts['test']:
    raise SystemExit('Test script still targets obsolete presentation module')
print('PASS: live production bundle has no synthetic presentation, canned answers or fixture imports.')
