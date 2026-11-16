"""Deterministic checks that need more than a regex. Each takes (run, assertion) and returns
(status, why) with status in 'pass' | 'fail' | 'skip'. `run` holds: final, all_text, diff, files (path -> text
after the run), before_files, changed {added, modified, deleted}, tools, empty_dirs, skills_dir."""
import fnmatch
import json
import posixpath
import re
from pathlib import Path

ENTRY_FILES = {"README", "PROJECT_STRUCTURE", "CONVENTIONS", "GLOSSARY", "MAP", "SYSTEM_MAP", "CHANGELOG", "NOTES", "MISSION", "RESOURCES", "INDEX"}


def glob_files(run, pattern):
    return sorted(m for m in run["files"] if fnmatch.fnmatch(m, pattern))


def get_target(run, name):
    """Text of a named target, or None when a file target matches nothing."""
    if name in ("final", "all_text", "diff"):
        return run[name]
    if name == "output":  # final answer plus any Markdown file the run added
        added = "\n\n".join(run["files"][f] for f in run["changed"]["added"] if f.endswith(".md") and f in run["files"])
        return added + "\n\n" + run["final"]
    if name == "playbook":
        ms = [m for m in glob_files(run, "docs/playbooks/*.md") if "/" not in m[len("docs/playbooks/"):]]
        return "\n".join(run["files"][m] for m in ms) if ms else None
    if name == "runlog":
        ms = glob_files(run, "docs/playbooks/runs/*.md")
        return "\n".join(run["files"][m] for m in ms) if ms else None
    if name.startswith("file:"):
        ms = glob_files(run, name[5:])
        return "\n".join(run["files"][m] for m in ms) if ms else None
    raise ValueError(f"unknown target {name}")


# ------------------------------------------------------------------ structure checks
def kebab_names(run, a):
    bad = []
    for f in run["changed"]["added"]:
        if not f.endswith(".md"):
            continue
        stem = Path(f).stem
        if stem in ENTRY_FILES or re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", stem) or re.fullmatch(r"\d{4}-[a-z0-9-]+", stem):
            continue
        bad.append(f)
    n = len([f for f in run["changed"]["added"] if f.endswith(".md")])
    if n == 0:
        return "fail", "no Markdown files were added"
    return ("pass" if not bad else "fail"), f"{n} added; not kebab-case: {bad[:5]}"


def links_resolve(run, a):
    broken, checked = [], 0
    names = set(run["files"])
    dirs = {posixpath.dirname(f) for f in names} | {""}
    for f, text in run["files"].items():
        if not f.endswith(".md"):
            continue
        for m in re.finditer(r"\]\(([^)\s]+)\)", text):
            href = m.group(1).split("#")[0]
            if not href or "<" in href or re.match(r"[a-z]+:", href):
                continue
            checked += 1
            tgt = posixpath.normpath(posixpath.join(posixpath.dirname(f), href))
            if tgt not in names and tgt not in dirs:
                broken.append(f"{f} -> {href}")
    if checked == 0:
        return "fail", "no relative links found"
    return ("pass" if not broken else "fail"), f"{checked} links, broken: {broken[:5]}"


def monolith_gone(run, a):
    notes = run["files"].get(a.get("path", "notes.md"))
    words = len(notes.split()) if notes else 0
    big = [f for f in run["changed"]["added"] if f.endswith(".md") and len(run["files"][f].split()) > a.get("max_new", 600)]
    if notes is not None and words > a.get("max_left", 80):
        return "fail", f"{a.get('path', 'notes.md')} still has {words} words"
    if big:
        return "fail", f"new files over {a.get('max_new', 600)} words: {big}"
    if not run["changed"]["added"]:
        return "fail", "nothing was split out"
    return "pass", f"original has {words} words left; {len(run['changed']['added'])} files added"


def no_empty_dirs(run, a):
    empty = run.get("empty_dirs", [])
    tiny = [f for f in run["changed"]["added"] if len(run["files"].get(f, "")) < 20 and not f.endswith(".keep")]
    if not run["changed"]["added"]:
        return "fail", "nothing was created"
    return ("pass" if not empty and not tiny else "fail"), f"empty dirs: {empty[:5]}; near-empty files: {tiny[:5]}"


def files_all(run, a):
    missing = [p for p in a["paths"] if not glob_files(run, p)]
    return ("pass" if not missing else "fail"), f"missing: {missing}"


def no_changes(run, a):
    ch = [f for k in ("added", "modified", "deleted") for f in run["changed"][k]]
    return ("pass" if not ch else "fail"), f"changed files: {ch[:6]}"


def no_added(run, a):
    ad = [f for f in run["changed"]["added"] if fnmatch.fnmatch(f, a["path"])]
    return ("pass" if not ad else "fail"), f"added under {a['path']}: {ad[:5]}"


def equals_preset(run, a):
    src = Path(run["skills_dir"]) / "doc-kit" / "kit" / "presets" / a.get("preset", "design.json")
    got = run["files"].get("tools/doclint.json")
    if got is None:
        return "fail", "tools/doclint.json missing"
    try:
        same = json.loads(got) == json.loads(src.read_text())
    except ValueError:
        return "fail", "doclint.json is not valid JSON"
    return ("pass" if same else "fail"), "doclint.json equals the preset" if same else "doclint.json differs from the preset"


def no_placeholders(run, a):
    pat = re.compile(a["pattern"])
    hits = []
    for f, t in run["files"].items():
        if f.endswith(".md") and "templates" not in Path(f).parts and pat.search(t):
            hits.append(f)
    return ("pass" if not hits else "fail"), f"files with placeholders: {hits[:6]}"


# ------------------------------------------------------------------ tool-trace checks
def read_all_skills(run, a):
    names = sorted(d.name for d in Path(run["skills_dir"]).iterdir() if (d / "SKILL.md").is_file())
    seen = set()
    for t in run["tools"]:
        if t["name"] not in ("Read", "Bash", "Grep"):
            continue
        blob = json.dumps(t["input"])
        if "SKILL.md" not in blob:
            continue
        if re.search(r"\*/SKILL\.md|skills/\*", blob):
            seen.update(names)
        seen.update(n for n in names if n in blob)
    ok = len(seen) >= a.get("min", 9)
    return ("pass" if ok else "fail"), f"{len(seen)} skill files read: {sorted(seen)}"


def first_convert_ok(run, a):
    for t in run["tools"]:
        if t["name"] == "Bash" and "convert.py" in t["input"].get("command", ""):
            cmd = t["input"]["command"]
            ok = "OUT_DIR" in cmd and re.search(r"latin|encoding|iso-8859", cmd, re.I) is not None
            return ("pass" if ok else "fail"), f"first convert call: {cmd[:160]}"
    return "fail", "convert.py was never run"


# ------------------------------------------------------------------ text checks
def sentences(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"(?m)^\s*\|.*$", " ", text)       # tables
    text = re.sub(r"(?m)^#+.*$", " ", text)           # headings
    text = re.sub(r"`[^`]*`", "X", text)
    text = re.sub(r"(?m)^\s*([-*]|\d+\.)\s+", "", text)
    parts = re.split(r"(?<=[.!?:;])\s+|\n{1,}", text)
    return [p for p in (x.strip() for x in parts) if len(p.split()) >= 3]


def sentence_length(run, a):
    txt = get_target(run, a["target"])
    if txt is None:
        return "fail", f"no text for {a['target']}"
    ss = sentences(txt)
    if len(ss) < 4:
        return "fail", f"only {len(ss)} sentences found"
    ok = sum(len(s.split()) <= a.get("words", 25) for s in ss)
    frac = ok / len(ss)
    long_ = [s[:90] for s in ss if len(s.split()) > a.get("words", 25)][:2]
    return ("pass" if frac >= a.get("min_frac", 0.85) else "fail"), f"{ok}/{len(ss)} sentences within {a.get('words', 25)} words; longest examples: {long_}"


def no_new_numbers(run, a):
    allowed = {str(x) for x in a.get("allowed", [])} | {"0", "1", "2", "3", "4"}
    txt = re.sub(r"\bL[0-4]\b", " ", run["final"])
    txt = re.sub(r"(?m)^\s*\d+[.)]\s", " ", txt)
    found = re.findall(r"\d+(?:[.,]\d+)?", txt)
    extra = sorted({f for f in found if f.replace(",", ".") not in allowed})
    return ("pass" if not extra else "fail"), f"numbers beyond the user's own: {extra}"


GERMAN = {"und", "der", "die", "das", "ist", "nicht", "ein", "eine", "mit", "für", "von", "wird", "bei", "auf", "den", "dem"}


def german(run, a):
    words = re.findall(r"[a-zäöüß]+", (get_target(run, "output") or "").lower())
    hits = sum(w in GERMAN for w in words)
    return ("pass" if hits >= a.get("min", 25) else "fail"), f"{hits} German function words in {len(words)} words"


# ------------------------------------------------------------------ multiple-choice parsing
def parse_mc(text):
    """Returns (questions, key). questions: list of {'n','stem','opts':{letter:text}}; key: {n: letter}."""
    qs, cur = [], None
    opt_re = re.compile(r"^\s*(?:[-*]\s*)?\**\(?([A-Da-d])[).:]\**\s+(.+?)\s*$")
    q_re = re.compile(r"^\s*(?:#+\s*)?\**(?:Frage|Aufgabe|Question|Q)?\s*(\d+)\s*[.):]?\**(?:\s|$)", re.I)
    key_start = re.search(r"(?im)^#+\s*.*(l[öo]sung|schl[üu]ssel|antwort|answer|key).*$", text)
    body = text[:key_start.start()] if key_start else text
    for line in body.splitlines():
        mo = opt_re.match(line)
        if mo and cur is not None:
            cur["opts"][mo.group(1).upper()] = re.sub(r"[*_`]", "", mo.group(2))
            continue
        mq = q_re.match(line)
        if mq and not mo:
            cur = {"n": int(mq.group(1)), "stem": line.strip(), "opts": {}}
            qs.append(cur)
    qs = [q for q in qs if len(q["opts"]) >= 2]
    key = {}
    if key_start:
        for m in re.finditer(r"(?m)^[^\n]*?\b(\d+)\b[\s.):|*-]*\**\s*\(?([A-Da-d])\b", text[key_start.start():]):
            key.setdefault(int(m.group(1)), m.group(2).upper())
    if not key:
        for q, m in zip(qs, re.finditer(r"(?i)(?:richtige antwort|correct answer|l[öo]sung|answer)\W{0,6}\**\s*\(?([A-D])\b", body)):
            key[q["n"]] = m.group(1).upper()
    return qs, key


def mc_shape(run, a):
    qs, key = parse_mc(get_target(run, "output") or "")
    if not qs:
        return "skip", "no multiple-choice questions could be parsed"
    bad = [q["n"] for q in qs if len(q["opts"]) != a.get("options", 4)]
    ok = len(qs) == a["questions"] and not bad
    return ("pass" if ok else "fail"), f"parsed {len(qs)} questions (want {a['questions']}); wrong option counts: {bad}"


def mc_positions(run, a):
    qs, key = parse_mc(get_target(run, "output") or "")
    letters = [key[q["n"]] for q in qs if q["n"] in key]
    if len(letters) < 3:
        return "skip", f"answer key not parsed ({len(letters)} entries)"
    distinct, top = len(set(letters)), max(letters.count(x) for x in set(letters))
    ok = distinct >= a.get("min_distinct", 3) and top <= a.get("max_same", 3)
    return ("pass" if ok else "fail"), f"key letters {''.join(letters)}: {distinct} distinct, most frequent x{top}"


def mc_length_parity(run, a):
    qs, key = parse_mc(get_target(run, "output") or "")
    rows = []
    for q in qs:
        k = key.get(q["n"])
        if k and k in q["opts"] and len(q["opts"]) >= 3:
            c = len(q["opts"][k])
            others = [len(v) for l, v in q["opts"].items() if l != k]
            rows.append((c, sum(others) / len(others), c > 1.15 * max(others)))
    if len(rows) < 3:
        return "skip", f"answer key not parsed ({len(rows)} usable questions)"
    avg = sum(c / o for c, o, _ in rows) / len(rows)
    standouts = sum(x for _, _, x in rows)
    ok = avg <= 1.25 and standouts <= max(1, len(rows) // 3)
    return ("pass" if ok else "fail"), f"correct/mean-distractor length {avg:.2f}; correct option clearly longest in {standouts}/{len(rows)}"


def solutions_after_tasks(run, a):
    txt = get_target(run, "output") or ""
    sol = re.search(r"(?im)^#+\s*(?!aufgabe|frage)[^\n]*(l[öo]sung|schl[üu]ssel)", txt)
    if not sol:
        return "fail", "no solutions heading found"
    before = re.findall(r"(?im)^#+\s*(?:aufgabe|frage)\s*\d", txt[:sol.start()])
    n = a.get("tasks", 4)
    return ("pass" if len(before) >= n else "fail"), f"{len(before)} task headings before the solutions heading (want {n})"


CUSTOM = {f.__name__: f for f in (
    kebab_names, links_resolve, monolith_gone, no_empty_dirs, files_all, no_changes, no_added, equals_preset,
    no_placeholders, read_all_skills, first_convert_ok, sentence_length, no_new_numbers, german, mc_shape,
    mc_positions, mc_length_parity, solutions_after_tasks)}
