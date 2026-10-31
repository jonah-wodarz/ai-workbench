"""Regression: generic doclint + Wayfarer config must find what Wayfarer's original lint finds.

Usage: python regression_wayfarer.py <wayfarer-copy> <kit-dir>
For each mutation, a fresh copy of the tree is faulted, both lints run, and their
findings are compared as multisets of (level, file, line). Messages are shown side
by side when they differ, since some were deliberately made project-neutral.
"""
import collections
import os
import re
import shutil
import subprocess
import sys
import tempfile

LINE = re.compile(r"^(ERROR|WARN)\s+(\S+?)(?::(\d+))?\s{2}(.*)$")


def append(rel, text):
    def f(root):
        with open(os.path.join(root, rel), "a", encoding="utf-8") as fh:
            fh.write(text)
    return f


def replace(rel, old, new, count=1):
    def f(root):
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8") as fh:
            t = fh.read()
        assert old in t, (rel, old)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(t.replace(old, new, count))
    return f


def remove(rel):
    return lambda root: os.remove(os.path.join(root, rel))


def write(rel, text):
    def f(root):
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    return f


A = "docs/design/combat/archery.md"
FM_ARC = "id: ARC\ntitle: Archery\ntype: sdd"
MUTATIONS = {
    "clean": [],
    "broken link": [append(A, "\nSee [x](nope.md).\n")],
    "retired name": [append(A, "\n- Shield Breaking is mentioned.\n")],
    "stale fact": [append(A, "\nnetherite +2 here.\n")],
    "stale fact in unmigrated root file": [append("README.md", "\nnetherite +2 here.\n")],
    "rule without tag": [replace(A, "visual trail, so their arc can be read and learned. `locked`",
                                 "visual trail, so their arc can be read and learned.")],
    "rule with two tags": [replace(A, "repaired with string. `locked`", "repaired with string. `locked` `placeholder`")],
    "duplicate rule id": [append(A, "\n- **ARC-R1** Duplicate. `locked`\n")],
    "foreign rule code": [append(A, "\n- **CHA-R900** Wrong file. `locked`\n")],
    "leaning outside provisional": [replace(A, "repaired with string. `locked`", "repaired with string. `leaning`")],
    "provisional section problems": [append(A, "\n## Provisional rules\n- **ARC-R900** No cite. `leaning`\n"
                                            "- **ARC-R901** Bad cite (ARC-Q999). `leaning`\n"
                                            "- **ARC-R902** Wrong tag (ARC-Q1). `locked`\n")],
    "question without tag": [append(A, "\n## Open questions\n- **ARC-Q900** Untagged?\n")],
    "blocking question not indexed": [append(A, "\n## Open questions\n- **ARC-Q901** Blocks? `blocking`\n")],
    "duplicate question": [append(A, "\n## Open questions\n- **ARC-Q902** A? `minor`\n- **ARC-Q902** B? `minor`\n")],
    "dangling rule ref": [append("docs/design/combat/shields.md", "\nSee ARC-R999.\n")],
    "dangling decision ref": [append("docs/design/combat/shields.md", "\nSee D-ARC-999.\n")],
    "ref into GLO (no ids)": [append("docs/design/combat/shields.md", "\nSee GLO-R1.\n")],
    "decision ref without history": [append("docs/design/combat/shields.md", "\nSee D-VIS-001.\n")],
    "heading emoji/date/changelog": [append(A, "\n## Notes ✅\n## Update 2026-10-01\n## Changelog\n")],
    "star, strike, first person": [append(A, "\n★ key. ~~old~~ text. Not my idea.\n")],
    "capital My (new lint stricter)": [append(A, "\nMy idea here.\n")],
    "release scheduling": [append(A, "\nShips in v2 maybe, v2+ later.\n")],
    "working notes in settled": [append(A, "\n## Working notes\nfree text ★ v2\n- **ARC-R903** In notes.\n")],
    "migration inbox in migrated": [append(A, "\n## Migration inbox\n- **From CHA, 2026-10-01** — x.\n- bad entry\n")],
    "inbox in unmigrated file": [write("docs/design/combat/newfile.md",
                                       "# New\n## Migration inbox\n- **From ARC, 2026-10-01** — ok.\n- bad\n")],
    "unmigrated design file": [write("docs/design/combat/raw.md", "# Raw\nARC-R1 and ARC-R999.\n")],
    "fm missing key": [replace(A, "domain: combat\n", "")],
    "fm unknown status": [replace(A, "status: settled", "status: done")],
    "fm bad layer": [replace(A, "layer: L2", "layer: L9")],
    "fm missing layer": [replace(A, "layer: L2\n", "")],
    "fm bad updated": [replace(A, "updated: 2026-10-15", "updated: Oct 15")],
    "fm unknown depends": [replace(A, "depends_on: [CHA,", "depends_on: [ZZZ,")],
    "fm unknown id": [replace(A, "id: ARC", "id: ZZZ")],
    "fm id of other file": [replace(A, "id: ARC", "id: CHA")],
    "no mirror": [remove("docs/decisions/combat/archery.md")],
    "decision dup and wrong code": [append("docs/decisions/combat/archery.md",
                                           "\n### D-ARC-001 — Dup\n### D-CHA-500 — Wrong\n")],
    "word budget": [append(A, "\n" + ("word " * 1600) + "\n")],
    "legacy OQ": [append("docs/planning/OPEN_QUESTIONS.md", "\n- **X12** legacy\n")],
    "unknown type (old lint crashes)": [replace(A, "type: sdd", "type: spec")],
}


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    items = []
    for line in p.stdout.splitlines():
        m = LINE.match(line)
        if m:
            items.append((m.group(1), m.group(2), int(m.group(3) or 0), m.group(4)))
    crash = p.stderr.strip().splitlines()[-1:] if "Traceback" in p.stderr else []
    return p.returncode, items, crash


def main(src, kit):
    total_ok = True
    for name, steps in MUTATIONS.items():
        tmp = tempfile.mkdtemp()
        root = os.path.join(tmp, "w")
        shutil.copytree(src, root)
        tools = os.path.join(root, "tools")
        shutil.copy(os.path.join(kit, "kit", "tools", "doclint.py"), os.path.join(tools, "doclint2.py"))
        shutil.copy(os.path.join(kit, "examples", "wayfarer", "doclint.json"), os.path.join(tools, "doclint.json"))
        os.makedirs(os.path.join(tools, "doclint_plugins"), exist_ok=True)
        shutil.copy(os.path.join(kit, "examples", "wayfarer", "doclint_plugins", "wayfarer.py"),
                    os.path.join(tools, "doclint_plugins", "wayfarer.py"))
        for step in steps:
            step(root)
        old_rc, old, old_err = run([sys.executable, "tools/doclint.py"], root)
        new_rc, new, new_err = run([sys.executable, "tools/doclint2.py"], root)
        ko = collections.Counter(i[:3] for i in old)
        kn = collections.Counter(i[:3] for i in new)
        same = ko == kn and old_rc == new_rc
        if "(new lint stricter)" in name and ko < kn:
            print("EXPECTED  {:38} old={:>2} new={:>2}  new lint catches more".format(name, len(old), len(new)))
            shutil.rmtree(tmp)
            continue
        if "(new lint stricter)" in name and ko < kn:
            print("EXPECTED  {:38} old={:>2} new={:>2}  new lint catches more".format(name, len(old), len(new)))
            shutil.rmtree(tmp)
            continue
        crashed = bool(old_err)
        status = "OK  " if same else ("OLD CRASH" if crashed else "DIFF")
        if not same and not crashed:
            total_ok = False
        print("{:9} {:38} old={:>2} new={:>2} rc {}/{}".format(status, name, len(old), len(new), old_rc, new_rc))
        if crashed:
            print("          old: " + old_err[0])
            for i in new:
                print("          new: {} {}:{} {}".format(*i))
        elif not same:
            for k in sorted((ko - kn).elements()):
                print("          only old:", k)
            for k in sorted((kn - ko).elements()):
                print("          only new:", k)
        if same:  # report reworded messages, pairing findings per location
            by_old, by_new = collections.defaultdict(list), collections.defaultdict(list)
            for i in old:
                by_old[i[:3]].append(i[3])
            for i in new:
                by_new[i[:3]].append(i[3])
            for k in by_old:
                for a, b in zip(sorted(set(by_old[k]) - set(by_new[k])), sorted(set(by_new[k]) - set(by_old[k]))):
                    print("          reworded: {!r} -> {!r}".format(a, b))
        shutil.rmtree(tmp)
    # --map equivalence
    print("map identical:", subprocess.run([sys.executable, "tools/doclint.py", "--map"], cwd=src,
                                           stdout=subprocess.PIPE, universal_newlines=True).stdout ==
          map_new(src, kit))
    return 0 if total_ok else 1


def map_new(src, kit):
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "w")
    shutil.copytree(src, root)
    tools = os.path.join(root, "tools")
    shutil.copy(os.path.join(kit, "kit", "tools", "doclint.py"), os.path.join(tools, "doclint2.py"))
    shutil.copy(os.path.join(kit, "examples", "wayfarer", "doclint.json"), os.path.join(tools, "doclint.json"))
    os.makedirs(os.path.join(tools, "doclint_plugins"), exist_ok=True)
    shutil.copy(os.path.join(kit, "examples", "wayfarer", "doclint_plugins", "wayfarer.py"),
                os.path.join(tools, "doclint_plugins", "wayfarer.py"))
    out = subprocess.run([sys.executable, "tools/doclint2.py", "--map"], cwd=root,
                         stdout=subprocess.PIPE, universal_newlines=True).stdout
    shutil.rmtree(tmp)
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
