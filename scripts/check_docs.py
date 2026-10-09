#!/usr/bin/env python3
"""Check local Markdown link targets using the standard library."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".runtime", "node_modules", ".venv", "private", "data", "recordings", "dist"}
LINK = re.compile(r"\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")


def main():
    errors = []
    links = 0
    documents = 0
    for path in sorted(ROOT.rglob("*.md")):
        parts = path.relative_to(ROOT).parts
        if SKIP.intersection(parts) or parts[:2] == ("assets", "models"):
            continue
        documents += 1
        for raw in LINK.findall(path.read_text(encoding="utf-8")):
            target = raw.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            links += 1
            if not destination.is_relative_to(ROOT) or not destination.exists():
                errors.append(f"{path.relative_to(ROOT)}: invalid local target {target}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {documents} Markdown files, {links} local links resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
