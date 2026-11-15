#!/usr/bin/env python3
"""Check skill folders against the mechanical audit rules.

Usage: python check_skills.py <skills-dir> [skill-name ...] [--deny FILE]

Checks per skill: front matter parses, name equals folder name, description
present, under 1,024 characters and free of angle brackets, SKILL.md word
count (warning above 1,000, error above 5,000), local links in SKILL.md
resolve, no README.md in the folder. With --deny FILE, every text file in the
skill folder is also searched for the file's patterns (one regex per line,
"#" starts a comment); a match is an error. Use it before publishing to keep
personal terms out. Prints one line per finding; exit code 1 if any error was
found. Stdlib only.
"""
import re
import sys
from pathlib import Path


def parse_front_matter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        km = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not km:
            continue
        value = km.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
        elif len(value) >= 2 and value[0] == value[-1] == "'":
            value = value[1:-1]
        data[km.group(1)] = value
    return data


def check(skill_dir):
    findings = []  # (level, message)
    md = skill_dir / "SKILL.md"
    if not md.is_file():
        return [("error", "SKILL.md missing")]
    text = md.read_text(encoding="utf-8")
    fm = parse_front_matter(text)
    if fm is None:
        return [("error", "front matter block not found")]
    if fm.get("name") != skill_dir.name:
        findings.append(("error", f"name {fm.get('name')!r} != folder {skill_dir.name!r}"))
    desc = fm.get("description", "")
    if not desc:
        findings.append(("error", "description missing"))
    if len(desc) >= 1024:
        findings.append(("error", f"description is {len(desc)} chars (limit 1,023)"))
    if "<" in desc or ">" in desc:
        findings.append(("error", "description contains angle brackets"))
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else text
    words = len(body.split())
    if words > 5000:
        findings.append(("error", f"{words} words in body (cap 5,000)"))
    elif words > 1000:
        findings.append(("warn", f"{words} words in body (target about 700-1,000)"))
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
        if re.match(r"[a-z]+:", target):
            continue
        if not (skill_dir / target).exists():
            findings.append(("error", f"link does not resolve: {target}"))
    if (skill_dir / "README.md").exists():
        findings.append(("error", "README.md inside skill folder"))
    return findings


def load_deny(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [re.compile(l.strip()) for l in lines if l.strip() and not l.lstrip().startswith("#")]


def check_deny(skill_dir, patterns):
    findings = []
    for f in sorted(skill_dir.rglob("*")):
        if not f.is_file() or "__pycache__" in f.parts:
            continue
        try:
            lines = f.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            for rx in patterns:
                m = rx.search(line)
                if m:
                    findings.append(("error", f"{f.relative_to(skill_dir).as_posix()}:{n}: denied term '{m.group(0)}'"))
    return findings


def main(argv):
    deny = []
    if "--deny" in argv:
        i = argv.index("--deny")
        if i + 1 >= len(argv):
            print(__doc__)
            return 2
        deny = load_deny(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(__doc__)
        return 2
    names = argv[2:] or sorted(p.name for p in root.iterdir() if p.is_dir())
    errors = 0
    for name in names:
        for level, msg in check(root / name) + (check_deny(root / name, deny) if deny else []):
            print(f"{level.upper():5} {name}: {msg}")
            errors += level == "error"
    print(f"{len(names)} skills checked, {errors} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
