#!/usr/bin/env python3
"""SessionStart hook: print the project's "Skills in use" table as context.

Looks for docs/CONVENTIONS.md, then CONVENTIONS.md, in the project directory
and prints the "## Skills in use" section plus one instruction line.
Prints nothing when the file or the section is absent. Never fails the session.
"""
import json
import os
import re
import sys

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INSTRUCTION = "Load the named skill with the Skill tool before the matching work."


def project_dir(payload):
    return os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()


def find_conventions(root):
    for rel in (os.path.join("docs", "CONVENTIONS.md"), "CONVENTIONS.md"):
        path = os.path.join(root, rel)
        if os.path.isfile(path):
            return path
    return None


def extract_section(text, title="skills in use"):
    """Return the body of the level-2 section called `title`, or None."""
    lines = text.splitlines()
    start = None
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
            continue
        m = HEADING.match(line)
        if fence or not m:
            continue
        level, name = len(m.group(1)), m.group(2).strip().lower()
        if start is None:
            if level == 2 and name == title:
                start = i + 1
        elif level <= 2:
            return "\n".join(lines[start:i]).strip() or None
    if start is None:
        return None
    return "\n".join(lines[start:]).strip() or None


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        path = find_conventions(project_dir(payload))
        if not path:
            return 0
        with open(path, encoding="utf-8") as fh:
            section = extract_section(fh.read())
        if not section:
            return 0
        out = "Skills in use (from %s):\n\n%s\n\n%s\n" % (
            os.path.relpath(path, project_dir(payload)).replace(os.sep, "/"),
            section,
            INSTRUCTION,
        )
        sys.stdout.buffer.write(out.encode("utf-8"))
    except Exception:  # a context hook must never break the session
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
