#!/usr/bin/env python3
"""Copy assets/shared/base.css and base.js into the marked blocks of every template.

Usage: sync_shared.py [--check]
--check exits 1 when a template is out of sync (no files change).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BLOCKS = {"CSS": ASSETS / "shared" / "base.css", "JS": ASSETS / "shared" / "base.js"}


def sync(text: str) -> str:
    for name, src in BLOCKS.items():
        body = src.read_text(encoding="utf-8").rstrip("\n")
        pattern = re.compile(rf"(/\*@@BASE_{name}_START\*/\n).*?(/\*@@BASE_{name}_END\*/)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"marker BASE_{name} missing in template")
        text = pattern.sub(lambda m: m.group(1) + body + "\n" + m.group(2), text)
    return text


def main() -> int:
    check = "--check" in sys.argv
    stale = []
    for tpl in sorted((ASSETS / "templates").glob("*.html")):
        old = tpl.read_text(encoding="utf-8")
        new = sync(old)
        if new != old:
            stale.append(tpl.name)
            if not check:
                tpl.write_text(new, encoding="utf-8", newline="\n")
    if check and stale:
        print("out of sync: " + ", ".join(stale) + " (run scripts/sync_shared.py)")
        return 1
    print("templates in sync" if check or not stale else "updated: " + ", ".join(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
