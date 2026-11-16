#!/usr/bin/env python3
"""Export the design bundle to the public repository folder and check it.

Usage: python tools/export_public.py <creative-design-folder>

Replaces <folder>/skills with the bundle's skill folders, copies the files in
publish/creative-design/ over the folder (README, changelog, plugin manifest)
and the LICENSE, then runs the checks: skill rules with the deny list
(tools/public-deny.txt), doc-kit tests, handoff example data and template sync.
Everything else in the folder, including .git, is left alone. Exit code 1 if a
check fails. Stdlib only.
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUNDLE = ["layered-design-facilitation", "design-capture", "structured-project-docs", "doc-kit", "handoff"]
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "CHANGELOG.md", ".gitignore")


def run(label, cmd, cwd):
    p = subprocess.run(cmd, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding="utf-8")
    tail = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    print("{:4} {}: {}".format("ok" if p.returncode == 0 else "FAIL", label, tail))
    if p.returncode:
        print(p.stdout)
    return p.returncode == 0


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    dest = Path(argv[1]).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if (dest / "skills").exists():
        shutil.rmtree(dest / "skills")
    for name in BUNDLE:
        shutil.copytree(REPO / "skills" / name, dest / "skills" / name, ignore=SKIP)
    shutil.copytree(REPO / "publish" / "creative-design", dest, dirs_exist_ok=True)
    shutil.copy(REPO / "LICENSE", dest / "LICENSE")
    py = sys.executable
    ok = [
        run("skill rules and deny list", [py, str(REPO / "skills/setup-retro/scripts/check_skills.py"), "skills", "--deny", str(REPO / "tools/public-deny.txt")], dest),
        run("doc-kit tests", [py, "-m", "unittest", "discover", "-s", "skills/doc-kit/tests"], dest),
        run("handoff template sync", [py, "skills/handoff/scripts/sync_shared.py", "--check"], dest),
    ]
    for tpl in sorted((dest / "skills/handoff/assets/examples").glob("*.json")):
        ok.append(run("handoff example " + tpl.stem, [py, "skills/handoff/scripts/build.py", tpl.stem, str(tpl), "--validate"], dest))
    print("exported to {}".format(dest) if all(ok) else "export has failures; do not publish")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
