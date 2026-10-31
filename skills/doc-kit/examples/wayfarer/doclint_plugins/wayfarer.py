"""Wayfarer-only checks for doclint: migration inbox, provisional-rule citations,
legacy X-numbered open-question entries. See Wayfarer docs/CONVENTIONS.md §6, §8.4, §10.

Plugin hooks (all optional): check_any(project, doc, report),
check_migrated(project, doc, report), check_project(project, report),
summary(project) -> str, verbose(project) -> str. CONFIG is set by doclint.
"""
import os
import re

CONFIG = {}

INBOX_HEAD = "## migration inbox"
PROVISIONAL_HEAD = "## provisional rules"
NOTES_HEAD = "## working notes"
RULE_TAGS = ("locked", "leaning", "placeholder")
INBOX_LINE = re.compile(r"^- \*\*From ([A-Z]{3}), \d{4}-\d{2}-\d{2}\*\* — \S")
LEGACY_OQ = re.compile(r"^\s*-\s+\*\*X\d+", re.M)


def _closing_tag(line, allowed):
    tags = re.findall(r"`(" + "|".join(allowed) + r")`", line)
    if len(tags) == 1 and line.rstrip().endswith("`{}`".format(tags[0])):
        return tags[0]
    return None


def check_any(project, doc, report):
    """Validate migration-inbox entries in every file; count pending ones in unmigrated files."""
    in_inbox, count = False, 0
    for n, line, fence in doc.body():
        if line.startswith("## "):
            in_inbox = line.strip().lower() == INBOX_HEAD
            continue
        if not in_inbox or fence or not line.startswith("- "):
            continue
        count += 1
        m = INBOX_LINE.match(line)
        if not m or m.group(1) not in project.codes:
            report.warn(doc.path, n, "inbox entry must start with '- **From <CODE>, YYYY-MM-DD** — '")
    if count and not doc.migrated:
        project.extra.setdefault("pending", {})[doc.rel] = count


def check_migrated(project, doc, report):
    code = doc.fm.get("id", "")
    status = doc.fm.get("status")
    is_sdd = doc.fm.get("type") == "sdd"
    provisional, questions = [], set()
    for n, line, fence, section in doc.walk():
        if line.startswith("## ") and section == INBOX_HEAD:
            report.error(doc.path, n, "migration inbox in a migrated file; integrate it (CONVENTIONS §10)")
        if section == NOTES_HEAD or fence or not is_sdd:
            continue
        q = project.rx_question_line.match(line)
        if q and q.group(1) == code:
            questions.add(project.fmt_question.format(code, q.group(2)))
        m = project.rx_rule_line.match(line)
        if m and section == PROVISIONAL_HEAD and _closing_tag(line, RULE_TAGS):
            rid = project.fmt_rule.format(m.group(1), m.group(2))
            cite = re.search(r"\((" + re.escape(code) + r"-Q\d+)\)", line)
            provisional.append((n, rid, cite.group(1) if cite else None))
    for n, rid, qid in provisional:
        if qid is None:
            report.error(doc.path, n, "provisional rule {} must cite an open question of this file, e.g. ({}-Q1)".format(rid, code))
        elif qid not in questions:
            report.error(doc.path, n, "provisional rule {} cites {}, which is not an open question in this file".format(rid, qid))
    if provisional and status in ("settled", "locked"):
        report.warn(doc.path, 0, "{} provisional rule(s) in a {} file; lock or resolve them".format(len(provisional), status))


def check_project(project, report):
    rel = project.cfg["index"].get("file")
    if not rel:
        return
    path = os.path.join(project.docs, rel)
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        legacy = len(LEGACY_OQ.findall(f.read()))
    if legacy:
        report.warn(path, 0, "{} legacy X-numbered entries; convert them as their owners migrate".format(legacy))


def summary(project):
    return "{} inbox entries pending".format(sum(project.extra.get("pending", {}).values()))


def verbose(project):
    pending = project.extra.get("pending", {})
    if not pending:
        return ""
    return "Pending migration inboxes:\n  " + "\n  ".join("{} ({})".format(p, c) for p, c in sorted(pending.items()))
