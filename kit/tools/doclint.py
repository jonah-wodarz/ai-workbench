#!/usr/bin/env python3
"""doclint: config-driven lint for Markdown documentation trees.

Usage (from the repository root):
    python tools/doclint.py              # run all checks
    python tools/doclint.py --map        # print the generated index (map) table
    python tools/doclint.py --quiet      # errors only (used by the pre-commit hook)
    python tools/doclint.py --verbose    # also list files missing front matter, plugin details
    python tools/doclint.py --config PATH  # use another config (default: tools/doclint.json)

Standard library only, Python 3.7+. The project's rules live in tools/doclint.json;
see the kit's CONFIG.md for every key. Files with front matter are "migrated" and
checked strictly; files without it get only the link and stale-term checks.
Project-specific checks are plugins: tools/doclint_plugins/<name>.py.
"""
import importlib.util
import json
import os
import re
import sys

__version__ = "0.1.0"

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "doclint.json")

EMOJI = re.compile("[☀-➿⬀-⯿\U0001F000-\U0001FAFF←-⇿⌀-⏿]")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
FIRST_PERSON = re.compile(r"\b(I'm|I've|I'd|I'll|[Mm]y|me)\b|\bI\s+[a-z]")
FENCE = re.compile(r"^(```|~~~)")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")

DEFAULTS = {
    "docs_dir": "docs",
    "skip_dirs": ["archive", "templates"],
    "codes": {"file": None, "pattern": r"`([A-Z]{3})`\s*\|\s*([^|]+?\.md)", "inline": {}},
    "code_path_prefixes": [""],
    "id_scheme": {"code": "[A-Z]{3}", "rule": "R", "question": "Q",
                  "decision_prefix": "D", "decision_digits": 3},
    "types": {},
    "enums": {},
    "date_fields": ["updated"],
    "depends_field": "depends_on",
    "unique_id_exempt_types": [],
    "sections": {},
    "tags": {},
    "prose": {"types": [], "checks": [], "patterns": []},
    "word_budget": {},
    "mirror": {},
    "decision_log_types": [],
    "history_line": r"^\s*-\s+\d{4}-\d{2}-\d{2}\s+—",
    "stale_terms": {"file": None, "retired_names": None,
                    "exempt": {"exclude": [], "include": []}},
    "refs": {"exempt": {"exclude": [], "include": []}},
    "index": {"file": None, "question_tags": []},
    "expect_front_matter": {"include": [], "exclude_regex": None},
    "map": {"columns": [], "sort": []},
    "plugins": [],
    "plugin_config": {},
}


# --------------------------------------------------------------------------- config

def load_config(path):
    with open(path, encoding="utf-8") as f:
        user = json.load(f)
    cfg = json.loads(json.dumps(DEFAULTS))
    for key, value in user.items():
        if key.startswith("_"):
            continue  # comments
        if isinstance(value, dict) and isinstance(cfg.get(key), dict):
            cfg[key].update(value)
        else:
            cfg[key] = value
    return cfg


# --------------------------------------------------------------------------- report

class Report:
    def __init__(self, root):
        self.root = root
        self.items = []

    def add(self, level, path, line, msg):
        self.items.append((level, os.path.relpath(path, self.root).replace(os.sep, "/"), line, msg))

    def error(self, path, line, msg):
        self.add("ERROR", path, line, msg)

    def warn(self, path, line, msg):
        self.add("WARN", path, line, msg)

    def count(self, level):
        return sum(1 for i in self.items if i[0] == level)

    def print(self, quiet=False):
        for level, path, line, msg in sorted(self.items, key=lambda i: (i[1], i[2], i[0])):
            if quiet and level != "ERROR":
                continue
            loc = "{}:{}".format(path, line) if line else path
            print("{:5} {}  {}".format(level, loc, msg))


# --------------------------------------------------------------------------- parsing

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def front_matter(text):
    """Return (dict or None, number of lines the front matter occupies).

    Supports the flat subset used in docs: `key: value` and `key: [a, b]`.
    """
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, 0
    data = {}
    for i in range(1, len(lines)):
        line = lines[i]
        if line.strip() == "---":
            return data, i + 1
        m = re.match(r"^([A-Za-z_]+):\s*(.*?)\s*(?:#.*)?$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if value.startswith("[") and value.endswith("]"):
            value = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        data[key] = value
    return None, 0


class Doc:
    """One Markdown file: path, docs-relative path, text, front matter."""

    def __init__(self, path, rel, text):
        self.path = path
        self.rel = rel
        self.text = text
        self.fm, self.fm_lines = front_matter(text)

    @property
    def migrated(self):
        return self.fm is not None

    def body(self):
        """Yield (line_number, line, in_fence) after the front matter.

        Fence delimiter lines themselves are reported with in_fence=True.
        """
        in_fence = False
        for n, line in enumerate(self.text.split("\n"), start=1):
            if n <= self.fm_lines:
                continue
            if FENCE.match(line.strip()):
                in_fence = not in_fence
                yield n, line, True
                continue
            yield n, line, in_fence

    def walk(self):
        """Yield (line_number, line, in_fence, section) where section is the
        lower-cased current `## ` heading ("" before the first one)."""
        section = ""
        for n, line, fence in self.body():
            if line.startswith("## "):
                section = line.strip().lower()
            yield n, line, fence, section


def scoped(rel, rules):
    """True if rel is covered by exempt-style rules {'exclude': [...], 'include': [...]}.

    An entry ending in '/' matches as a prefix; otherwise it must match exactly.
    'include' re-admits paths that 'exclude' would cover.
    """
    def hit(entries):
        return any(rel.startswith(e) if e.endswith("/") else rel == e for e in entries)
    return hit(rules.get("exclude", [])) and not hit(rules.get("include", []))


# --------------------------------------------------------------------------- project

class Project:
    def __init__(self, root, cfg):
        self.root = root
        self.cfg = cfg
        self.docs = os.path.join(root, cfg["docs_dir"])
        ids = cfg["id_scheme"]
        code = ids["code"]
        r, q, d, dd = ids["rule"], ids["question"], ids["decision_prefix"], ids["decision_digits"]
        self.rx_rule_line = re.compile(r"^\s*[-*]\s+\*\*(" + code + ")-" + r + r"(\d+)\*\*")
        self.rx_question_line = re.compile(r"^\s*[-*]\s+\*\*(" + code + ")-" + q + r"(\d+)\*\*")
        self.rx_decision_head = re.compile(r"^###\s+" + d + "-(" + code + r")-(\d{" + str(dd) + r"})\b")
        self.rx_ref = re.compile(r"\b(" + code + ")-([" + r + q + r"])(\d+)\b")
        self.rx_dec_ref = re.compile(r"\b" + d + "-(" + code + r")-(\d{" + str(dd) + r"})\b")
        self.rx_history = re.compile(cfg["history_line"]) if cfg.get("history_line") else None
        self.fmt_rule = "{}-" + r + "{}"
        self.fmt_question = "{}-" + q + "{}"
        self.fmt_decision = d + "-{}-{}"
        self.codes = self._codes()
        self.files = {}
        self.plugins = []
        self.extra = {}  # plugins may store results here (e.g. summary counts)

    # -- helpers
    def rel(self, path):
        return os.path.relpath(path, self.docs).replace(os.sep, "/")

    def is_history_line(self, line):
        return bool(self.rx_history and self.rx_history.match(line))

    def type_cfg(self, kind):
        return self.cfg["types"].get(kind, {})

    # -- discovery
    def _codes(self):
        spec = self.cfg["codes"]
        codes = dict(spec.get("inline") or {})
        if spec.get("file"):
            path = os.path.join(self.docs, spec["file"])
            if os.path.exists(path):
                rx = re.compile(spec["pattern"])
                for line in read(path).split("\n"):
                    for code, target in rx.findall(line):
                        codes[code] = target.strip().split(" ")[0]
        return codes

    def markdown_files(self):
        skip = set(self.cfg["skip_dirs"])
        for base, dirs, files in os.walk(self.root):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            rel = os.path.relpath(base, self.docs)
            if not rel.startswith("..") and rel.split(os.sep)[0] in skip:
                dirs[:] = []
                continue
            for f in sorted(files):
                if f.endswith(".md"):
                    yield os.path.join(base, f)

    def load(self):
        for path in self.markdown_files():
            path = os.path.normpath(path)
            self.files[path] = Doc(path, self.rel(path), read(path))

    def owner_path(self, rel):
        for prefix in self.cfg["code_path_prefixes"]:
            p = os.path.normpath(os.path.join(self.docs, prefix, rel))
            if os.path.exists(p):
                return p
        return None

    def defined_ids(self, doc, code):
        ids = set()
        for _, line, fence in doc.body():
            if fence:
                continue
            m = self.rx_rule_line.match(line)
            if m and m.group(1) == code:
                ids.add(self.fmt_rule.format(code, m.group(2)))
            m = self.rx_question_line.match(line)
            if m and m.group(1) == code:
                ids.add(self.fmt_question.format(code, m.group(2)))
            d = self.rx_decision_head.match(line)
            if d and d.group(1) == code:
                ids.add(self.fmt_decision.format(code, d.group(2)))
        return ids

    def build_index(self):
        """owners: code -> {path, migrated, ids}; decisions: code -> decision ids."""
        self.owners, self.decisions = {}, {}
        for code, rel in self.codes.items():
            path = self.owner_path(rel)
            if path is None or path not in self.files:
                continue
            doc = self.files[path]
            self.owners[code] = {"path": path, "migrated": doc.migrated,
                                 "ids": self.defined_ids(doc, code) if doc.migrated else set()}
        log_types = set(self.cfg["decision_log_types"])
        for doc in self.files.values():
            if doc.fm and doc.fm.get("type") in log_types and doc.fm.get("id"):
                self.decisions.setdefault(doc.fm["id"], set()).update(self.defined_ids(doc, doc.fm["id"]))


# --------------------------------------------------------------------------- checks

def stale_terms(project):
    spec = project.cfg["stale_terms"]
    terms = []
    if spec.get("file"):
        path = os.path.join(project.root, spec["file"])
        if os.path.exists(path):
            for raw in read(path).split("\n"):
                raw = raw.strip()
                if not raw or raw.startswith("#"):
                    continue
                pattern, _, hint = raw.partition("=>")
                terms.append((re.compile(pattern.strip()), hint.strip()))
    rn = spec.get("retired_names")
    if rn:
        terms += retired_names(project, rn)
    return terms


def retired_names(project, spec):
    """Parse a 'Retired | Use instead | Lint pattern' table into (pattern, hint) pairs."""
    path = os.path.join(project.docs, spec["file"])
    if not os.path.exists(path):
        return []
    text = read(path)
    start = text.find(spec.get("heading", "## Retired names"))
    if start == -1:
        return []
    use_col, pat_col = spec.get("use_column", 1), spec.get("pattern_column", 2)
    header = spec.get("header_first_cell", "Retired")
    terms = []
    for line in text[start:].split("\n")[1:]:
        if line.startswith("## "):
            break
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) <= max(use_col, pat_col) or cells[0] == header:
            continue
        m = re.fullmatch(r"`(.+)`", cells[pat_col])
        if not m:
            continue  # manual-checklist row
        pattern = m.group(1).replace("\\|", "|")
        terms.append((re.compile(pattern), "retired name; use: " + cells[use_col]))
    return terms


def check_links(project, doc, report):
    for n, line, fence in doc.body():
        if fence:
            continue
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            full = os.path.normpath(os.path.join(os.path.dirname(doc.path), target))
            if not os.path.exists(full):
                report.error(doc.path, n, "broken link: " + target)


def check_stale(project, doc, terms, report):
    if scoped(doc.rel, project.cfg["stale_terms"].get("exempt", {})):
        return
    for n, line, fence in doc.body():
        if fence or project.is_history_line(line) or "~~" in line:
            continue
        for pattern, hint in terms:
            if pattern.search(line):
                msg = "stale term /{}/".format(pattern.pattern) + (" -> " + hint if hint else "")
                (report.error if doc.migrated else report.warn)(doc.path, n, msg)


def check_refs(project, doc, report):
    """Every referenced rule, question or decision ID must exist in its owner."""
    if scoped(doc.rel, project.cfg["refs"].get("exempt", {})):
        return
    for n, line, fence in doc.body():
        if fence or project.is_history_line(line):
            continue
        refs = [(c, "{}-{}{}".format(c, k, num)) for c, k, num in project.rx_ref.findall(line)]
        refs += [(c, project.fmt_decision.format(c, num)) for c, num in project.rx_dec_ref.findall(line)]
        for code, ref in refs:
            if ref.startswith(project.cfg["id_scheme"]["decision_prefix"] + "-"):
                if code not in project.decisions:
                    if code in project.owners:
                        report.warn(doc.path, n, "{}: {} has no decision-history file yet".format(ref, code))
                elif ref not in project.decisions[code]:
                    report.error(doc.path, n, "dangling reference {}: no such decision entry".format(ref))
                continue
            owner = project.owners.get(code)
            if owner is None:
                continue  # not a known code (e.g. template placeholders)
            if not owner["migrated"]:
                report.warn(doc.path, n, "{} points into unmigrated {}".format(ref, project.rel(owner["path"])))
            elif ref not in owner["ids"]:
                report.error(doc.path, n, "dangling reference {}: not defined in {}".format(
                    ref, project.rel(owner["path"])))


def closing_tag(line, allowed):
    """Return the single allowed tag a line ends with, or None."""
    tags = re.findall(r"`(" + "|".join(map(re.escape, allowed)) + r")`", line)
    if len(tags) == 1 and line.rstrip().endswith("`{}`".format(tags[0])):
        return tags[0]
    return None


def check_front_matter(project, doc, report):
    """Validate front matter. Returns False if the type is unknown (skip body checks)."""
    fm, cfg = doc.fm, project.cfg
    kind = fm.get("type")
    if kind not in cfg["types"]:
        report.error(doc.path, 1, "front matter: unknown type '{}'".format(kind))
        return False
    tcfg = project.type_cfg(kind)
    for key in tcfg.get("required", []):
        if not fm.get(key):
            report.error(doc.path, 1, "front matter: missing '{}'".format(key))
    code = fm.get("id", "")
    if code and code not in project.codes:
        report.error(doc.path, 1, "front matter: id '{}' is not in the code table".format(code))
    always = set(tcfg.get("enums_always", []))
    for key, values in cfg["enums"].items():
        if key in fm or key in always:
            if fm.get(key) not in values:
                report.error(doc.path, 1, "front matter: unknown {} '{}'".format(key, fm.get(key)))
    for key in cfg["date_fields"]:
        if key in fm and not DATE.fullmatch(str(fm[key])):
            report.error(doc.path, 1, "front matter: '{}' must be YYYY-MM-DD".format(key))
    for dep in fm.get(cfg["depends_field"], []) or []:
        if dep not in project.codes:
            report.warn(doc.path, 1, "front matter: {} '{}' is not a known code".format(cfg["depends_field"], dep))
    if tcfg.get("id_matches_path") and code in project.codes:
        expected = project.codes[code]
        candidates = {doc.rel} | {doc.rel[len(p):] for p in cfg["code_path_prefixes"] if p and doc.rel.startswith(p)}
        if expected not in candidates:
            report.error(doc.path, 1, "front matter: id '{}' belongs to {}".format(code, expected))
    return True


def check_mirror(project, doc, report):
    spec = project.cfg["mirror"]
    if not spec or doc.fm.get("type") not in spec.get("types", []):
        return
    src, dst = spec["from"], spec["to"]
    if doc.rel.startswith(src):
        mirror = os.path.join(project.docs, dst, doc.rel[len(src):])
        if not os.path.exists(mirror):
            report.warn(doc.path, 0, "no decision-history file at " +
                        os.path.relpath(mirror, project.root).replace(os.sep, "/"))


def check_decision_log(project, doc, report):
    code = doc.fm.get("id", "")
    seen = {}
    for n, line, fence in doc.body():
        if fence:
            continue
        m = project.rx_decision_head.match(line)
        if not m:
            continue
        did = project.fmt_decision.format(m.group(1), m.group(2))
        if m.group(1) != code:
            report.error(doc.path, n, "decision {} does not match file code {}".format(did, code))
        if did in seen:
            report.error(doc.path, n, "duplicate decision id {} (first at line {})".format(did, seen[did]))
        seen.setdefault(did, n)


def check_body(project, doc, report):
    """Section, prose, rule and question checks. Returns [(line, question_id, tag)] for indexing."""
    cfg = project.cfg
    kind = doc.fm.get("type")
    status = doc.fm.get("status")
    code = doc.fm.get("id", "")
    prose = cfg["prose"]
    prose_on = kind in prose.get("types", [])
    checks = set(prose.get("checks", []))
    patterns = [(re.compile(p["regex"]), p.get("level", "warn"), p["message"]) for p in prose.get("patterns", [])]
    sections = cfg["sections"]
    exempt_sections = {s["heading"] for s in sections.values() if s.get("exempt")}
    rule_tags = cfg["tags"].get("rule", {})
    q_tags = cfg["tags"].get("question", {})
    rule_tag_on = kind in rule_tags.get("types", [])
    q_tag_on = kind in q_tags.get("types", [])
    section_tag = {k.lower(): v for k, v in rule_tags.get("section_only", {}).items()}  # heading -> tag
    tag_section = {v: k for k, v in section_tag.items()}
    seen_rules, seen_questions, tagged_questions = {}, {}, []
    words = 0
    for n, line, fence, section in doc.walk():
        if line.startswith("## "):
            for s in sections.values():
                if section == s["heading"] and "allowed_status" in s and status not in s["allowed_status"]:
                    report.error(doc.path, n, s.get("message", "section not allowed with status '{}'".format(status)))
        if prose_on and line.startswith("#"):
            if "heading_emoji" in checks and (EMOJI.search(line) or "★" in line):
                report.error(doc.path, n, "heading contains emoji or symbols")
            if "heading_date" in checks and DATE.search(line):
                report.error(doc.path, n, "heading contains a date")
            if "changelog_heading" in checks and re.search(r"(?i)changelog", line):
                report.error(doc.path, n, "changelog section; history belongs in the decision history")
        if section in exempt_sections or fence:
            continue
        words += len(re.findall(r"\w+", line))
        if prose_on:
            if "star" in checks and "★" in line:
                report.error(doc.path, n, "'★' is not used in specs")
            if "strikethrough" in checks and "~~" in line:
                report.error(doc.path, n, "strikethrough; replace superseded text instead")
            if "first_person" in checks and FIRST_PERSON.search(line):
                report.error(doc.path, n, "first person in spec text")
            for rx, level, msg in patterns:
                if rx.search(line):
                    (report.error if level == "error" else report.warn)(doc.path, n, msg)
        m = project.rx_rule_line.match(line)
        if m:
            rid = project.fmt_rule.format(m.group(1), m.group(2))
            if m.group(1) != code:
                report.error(doc.path, n, "rule {} does not match file code {}".format(rid, code))
            if rid in seen_rules:
                report.error(doc.path, n, "duplicate rule id {} (first at line {})".format(rid, seen_rules[rid]))
            seen_rules.setdefault(rid, n)
            if rule_tag_on:
                values = rule_tags["values"]
                tag = closing_tag(line, values)
                if tag is None:
                    report.error(doc.path, n, "rule {} must end with exactly one tag: {}".format(rid, ", ".join(values)))
                elif section in section_tag:
                    if tag != section_tag[section]:
                        report.error(doc.path, n, "rule {} in this section must be tagged `{}`".format(
                            rid, section_tag[section]))
                elif tag in tag_section:
                    report.error(doc.path, n, "rule {}: `{}` is only allowed under {}".format(
                        rid, tag, tag_section[tag].lstrip("# ").capitalize()))
        q = project.rx_question_line.match(line)
        if q and q.group(1) == code:
            qid = project.fmt_question.format(code, q.group(2))
            if qid in seen_questions:
                report.error(doc.path, n, "duplicate question id {} (first at line {})".format(qid, seen_questions[qid]))
            seen_questions.setdefault(qid, n)
            if q_tag_on:
                values = q_tags["values"]
                tag = closing_tag(line, values)
                if tag is None:
                    report.error(doc.path, n, "question {} must end with exactly one tag: {}".format(qid, ", ".join(values)))
                else:
                    tagged_questions.append((n, qid, tag))
    budget = cfg["word_budget"].get(kind)
    if budget and words > budget:
        report.warn(doc.path, 0, "{} words exceeds the ~{}-word budget; consider splitting".format(words, budget))
    return tagged_questions


def check_index(project, listed, report):
    spec = project.cfg["index"]
    if not spec.get("file"):
        return
    path = os.path.join(project.docs, spec["file"])
    text = read(path) if os.path.exists(path) else ""
    for qpath, n, qid in listed:
        if not re.search(r"\b" + re.escape(qid) + r"\b", text):
            report.error(qpath, n, "{} question {} is not listed in {}".format(
                "/".join(spec["question_tags"]), qid, spec["file"]))


def build_map(project):
    """Index table. source 'codes': one row per code-table entry (shows missing/unmigrated owners).
    source 'files': one row per file with front matter."""
    spec = project.cfg["map"]
    columns = spec["columns"]  # [[header, field], ...]; fields: code, link, or any front-matter key
    sort_keys = spec.get("sort", ["code"])
    rows = []
    if spec.get("source", "codes") == "files":
        if not project.files:
            project.load()
        for doc in project.files.values():
            if not doc.migrated or doc.rel.startswith(".."):
                continue
            values = {"code": doc.fm.get("id", "—"), "link": doc.rel}
            for key in [f for _, f in columns] + list(sort_keys):
                values.setdefault(key, doc.fm.get(key, "—"))
            rows.append(values)
        return _render_map(columns, sort_keys, rows)
    for code, rel in project.codes.items():
        path = project.owner_path(rel)
        fm = front_matter(read(path))[0] if path else None
        link = project.rel(path) if path else rel
        values = {"code": code, "link": link}
        if fm:
            for _, field in columns:
                if field not in values:
                    values[field] = fm.get(field, "—")
            for key in sort_keys:
                values.setdefault(key, fm.get(key, "—"))
        else:
            status_field = spec.get("status_field", "status")
            title_field = spec.get("title_field", "title")
            for _, field in columns:
                values.setdefault(field, "—")
            for key in sort_keys:
                values.setdefault(key, "—")
            values[title_field] = rel
            values[status_field] = "not migrated" if path else "missing"
        rows.append(values)
    return _render_map(columns, sort_keys, rows)


def _render_map(columns, sort_keys, rows):
    rows.sort(key=lambda v: tuple(str(v.get(k, "")) for k in sort_keys))
    out = ["| " + " | ".join(h for h, _ in columns) + " |",
           "|" + "---|" * len(columns)]
    for v in rows:
        cells = []
        for _, field in columns:
            if field == "code":
                cells.append("`{}`".format(v["code"]))
            elif field == "link":
                cells.append("[`{0}`]({0})".format(v["link"]))
            else:
                cells.append(str(v.get(field, "—")))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# --------------------------------------------------------------------------- plugins

def load_plugins(project):
    plugin_dir = os.path.join(HERE, "doclint_plugins")
    for name in project.cfg["plugins"]:
        path = os.path.join(plugin_dir, name + ".py")
        spec = importlib.util.spec_from_file_location("doclint_plugin_" + name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.CONFIG = project.cfg["plugin_config"].get(name, {})
        project.plugins.append(module)


def call_plugins(project, hook, *args):
    results = []
    for plugin in project.plugins:
        fn = getattr(plugin, hook, None)
        if fn:
            results.append(fn(project, *args))
    return results


# --------------------------------------------------------------------------- main

def run(project, report):
    """Run all checks; returns (migrated count, list of files missing front matter)."""
    cfg = project.cfg
    project.load()
    project.build_index()
    terms = stale_terms(project)
    expect = cfg["expect_front_matter"]
    expect_rx = re.compile(expect["exclude_regex"]) if expect.get("exclude_regex") else None
    index_tags = set(cfg["index"].get("question_tags", []))
    migrated, missing, listed, seen_ids = 0, [], [], {}
    exempt_unique = set(cfg["unique_id_exempt_types"])
    for path, doc in sorted(project.files.items()):
        check_links(project, doc, report)
        check_stale(project, doc, terms, report)
        check_refs(project, doc, report)
        call_plugins(project, "check_any", doc, report)
        if not doc.migrated:
            if not doc.rel.startswith("..") and any(doc.rel.startswith(p) for p in expect.get("include", [])) and not (
                    expect_rx and expect_rx.search(doc.rel)):
                missing.append(doc.rel)
            continue
        migrated += 1
        if doc.fm.get("type") not in exempt_unique and doc.fm.get("id"):
            if doc.fm["id"] in seen_ids:
                report.error(doc.path, 1, "id '{}' already used by {}".format(doc.fm["id"], seen_ids[doc.fm["id"]]))
            seen_ids.setdefault(doc.fm["id"], doc.rel)
        if not check_front_matter(project, doc, report):
            continue
        if doc.fm.get("type") in cfg["decision_log_types"]:
            check_decision_log(project, doc, report)
            continue
        check_mirror(project, doc, report)
        for n, qid, tag in check_body(project, doc, report):
            if tag in index_tags:
                listed.append((doc.path, n, qid))
        call_plugins(project, "check_migrated", doc, report)
    check_index(project, listed, report)
    call_plugins(project, "check_project", report)
    return migrated, missing


def main(argv):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    config_path = DEFAULT_CONFIG
    if "--config" in argv:
        config_path = argv[argv.index("--config") + 1]
    if "--version" in argv:
        print("doclint " + __version__)
        return 0
    cfg = load_config(config_path)
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(config_path)), cfg.get("root", "..")))
    project = Project(root, cfg)
    load_plugins(project)
    if "--map" in argv:
        print(build_map(project))
        return 0
    report = Report(root)
    migrated, missing = run(project, report)
    report.print(quiet="--quiet" in argv)
    print()
    parts = ["{} errors, {} warnings".format(report.count("ERROR"), report.count("WARN")),
             "{} migrated, {} not yet migrated".format(migrated, len(missing))]
    for extra in call_plugins(project, "summary"):
        if extra:
            parts.append(extra)
    print(" · ".join(parts))
    if "--verbose" in argv and missing:
        print("Not yet migrated:\n  " + "\n  ".join(sorted(missing)))
    if "--verbose" in argv:
        for text in call_plugins(project, "verbose"):
            if text:
                print(text)
    return 1 if report.count("ERROR") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
