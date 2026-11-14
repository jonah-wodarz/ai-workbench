#!/usr/bin/env python3
"""Build a handoff page: inject a data JSON into a template after validating it.

Usage: build.py <template> <data.json> -o <out.html> [--artifact] [--validate]
  template   decision-brief | system-map | change-report | explainer (or a path)
  --artifact write page content without the html/head/body wrappers (for the Artifact tool)
  --validate check the data only
Exit 0 ok, 1 invalid data (messages say how to fix), 2 usage error.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
DEFAULT_STATUSES = [
    {"id": "idea", "label": "Idea", "tone": "muted"},
    {"id": "drafting", "label": "Drafting", "tone": "warn"},
    {"id": "settled", "label": "Settled", "tone": "good"},
    {"id": "validated", "label": "Validated", "tone": "info"},
    {"id": "locked", "label": "Locked", "tone": "info"},
    {"id": "deferred", "label": "Deferred", "tone": "muted"},
]
KINDS = ["added", "changed", "removed", "reversed", "conflict"]


# ---- minimal schema kit -------------------------------------------------
class Ctx:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, path, msg):
        self.errors.append(f"{path}: {msg}")


class Str:
    def __init__(self, max=200, ident=False):
        self.max, self.ident = max, ident

    def check(self, c, v, p):
        if not isinstance(v, str) or not v.strip():
            return c.err(p, "needs a non-empty string")
        if len(v) > self.max:
            c.err(p, f"{len(v)} characters, limit {self.max}. Shorten it; the page shows short units")
        if self.ident and not ID_RE.match(v):
            c.err(p, f"'{v}' is not a valid id. Use letters, digits, '-', '_' or '.', starting with a letter or digit")


class Int:
    def __init__(self, lo=0, hi=9999):
        self.lo, self.hi = lo, hi

    def check(self, c, v, p):
        if isinstance(v, bool) or not isinstance(v, int) or not self.lo <= v <= self.hi:
            c.err(p, f"needs an integer from {self.lo} to {self.hi}")


class Num:
    def check(self, c, v, p):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            c.err(p, "needs a number")


class Bool:
    def check(self, c, v, p):
        if not isinstance(v, bool):
            c.err(p, "needs true or false")


class Enum:
    def __init__(self, *vals):
        self.vals = vals

    def check(self, c, v, p):
        if v not in self.vals:
            c.err(p, f"'{v}' is not allowed; use one of: {', '.join(self.vals)}")


class List:
    def __init__(self, item, lo=0, hi=100):
        self.item, self.lo, self.hi = item, lo, hi

    def check(self, c, v, p):
        if not isinstance(v, list):
            return c.err(p, "needs a list")
        if not self.lo <= len(v) <= self.hi:
            fix = "Split the content across two pages or cut items" if len(v) > self.hi else "Add the missing items"
            c.err(p, f"has {len(v)} items, needs {self.lo} to {self.hi}. {fix}")
        for i, x in enumerate(v):
            self.item.check(c, x, f"{p}[{i}]")


class Obj:
    def __init__(self, req=None, opt=None):
        self.req, self.opt = req or {}, opt or {}

    def check(self, c, v, p):
        if not isinstance(v, dict):
            return c.err(p, "needs an object")
        for k, spec in self.req.items():
            if k not in v:
                c.err(p, f"missing required key '{k}'")
            else:
                spec.check(c, v[k], f"{p}.{k}")
        for k, x in v.items():
            if k in self.req:
                continue
            if k in self.opt:
                self.opt[k].check(c, x, f"{p}.{k}")
            else:
                allowed = ", ".join(list(self.req) + list(self.opt))
                c.err(p, f"unknown key '{k}'. Allowed keys: {allowed}")


def head_req():
    return {"title": Str(60), "date": Str(24), "source": Str(140), "bottom_line": Str(260)}


# ---- templates: schema + cross-checks ------------------------------------
def unique(c, items, path, key="id"):
    seen = set()
    for i, x in enumerate(items):
        k = x.get(key) if isinstance(x, dict) else None
        if k in seen:
            c.err(f"{path}[{i}].{key}", f"duplicate id '{k}'. Ids must be unique")
        seen.add(k)
    return seen


def decision_brief():
    opt = Obj({"id": Str(10, True), "label": Str(70)},
              {"summary": Str(160), "pros": List(Str(110), 0, 3), "cons": List(Str(110), 0, 3)})
    dec = Obj({"id": Str(10, True), "question": Str(170), "context": Str(300), "options": List(opt, 2, 4)},
              {"recommended": Str(10), "reason": Str(260), "affects": List(Str(16), 0, 6), "tag": Str(16)})
    req = head_req()
    req["decisions"] = List(dec, 1, 12)
    schema = Obj(req, {"ask": Str(220)})

    def cross(c, d):
        if not isinstance(d.get("decisions"), list):
            return
        unique(c, d["decisions"], "$.decisions")
        for i, x in enumerate(d["decisions"]):
            if not isinstance(x, dict) or not isinstance(x.get("options"), list):
                continue
            p = f"$.decisions[{i}]"
            ids = unique(c, x["options"], f"{p}.options")
            for j, o in enumerate(x["options"]):
                if isinstance(o, dict) and not (o.get("pros") or o.get("cons")):
                    c.err(f"{p}.options[{j}]", "needs at least one entry in 'pros' or 'cons' so the reader sees a trade-off")
            rec = x.get("recommended")
            if rec is not None and rec not in ids:
                c.err(f"{p}.recommended", f"'{rec}' is not an option id here. Options: {', '.join(sorted(map(str, ids)))}")
            if rec is not None and "reason" not in x:
                c.err(p, "has 'recommended' but no 'reason'. Add one line that says why")
            if rec is None and "reason" in x:
                c.err(p, "has 'reason' but no 'recommended'. Add 'recommended' or drop 'reason'")
    return schema, cross


def system_map():
    node = Obj({"id": Str(10, True), "label": Str(40), "layer": Str(20), "status": Str(20)},
               {"group": Str(20), "summary": Str(240), "open": Int(0, 999)})
    edge = Obj({"from": Str(10), "to": Str(10)}, {"note": Str(120)})
    lab = Obj({"id": Str(20, True), "label": Str(32)})
    status = Obj({"id": Str(20, True), "label": Str(24), "tone": Enum("good", "warn", "bad", "info", "muted")})
    req = head_req()
    req.update({"layers": List(lab, 1, 8), "nodes": List(node, 1, 60), "edges": List(edge, 0, 300)})
    schema = Obj(req, {"ask": Str(220), "groups": List(lab, 1, 10), "statuses": List(status, 1, 10),
                       "columns": Enum("layer", "group"), "fan_out_warn": Int(1, 99)})

    def cross(c, d):
        if not isinstance(d.get("nodes"), list):
            return
        ids = unique(c, d["nodes"], "$.nodes")
        layers = {x.get("id") for x in d.get("layers", []) if isinstance(x, dict)}
        groups = {x.get("id") for x in d.get("groups", []) if isinstance(x, dict)}
        sts = {x.get("id") for x in d.get("statuses", DEFAULT_STATUSES) if isinstance(x, dict)}
        for i, n in enumerate(d["nodes"]):
            if not isinstance(n, dict):
                continue
            if n.get("layer") not in layers:
                c.err(f"$.nodes[{i}].layer", f"'{n.get('layer')}' is not in 'layers'. Known: {', '.join(sorted(map(str, layers)))}")
            if n.get("status") not in sts:
                c.err(f"$.nodes[{i}].status", f"'{n.get('status')}' is not a status. Known: {', '.join(sorted(map(str, sts)))}")
            if "group" in n and n["group"] not in groups:
                c.err(f"$.nodes[{i}].group", f"'{n['group']}' is not in 'groups'. Add it or fix the id")
            if d.get("columns") == "group" and "group" not in n:
                c.err(f"$.nodes[{i}]", "columns is 'group' but this node has no 'group'")
        seen = set()
        for i, e in enumerate(d.get("edges", [])):
            if not isinstance(e, dict):
                continue
            for k in ("from", "to"):
                if e.get(k) not in ids:
                    c.err(f"$.edges[{i}].{k}", f"'{e.get(k)}' is not a node id. Add the node or remove the edge")
            if e.get("from") == e.get("to"):
                c.err(f"$.edges[{i}]", "points from a node to itself; remove it")
            key = (e.get("from"), e.get("to"))
            if key in seen:
                c.err(f"$.edges[{i}]", f"duplicate edge {key[0]} -> {key[1]}")
            seen.add(key)
        if d.get("columns") == "group" and not groups:
            c.err("$.columns", "is 'group' but 'groups' is missing. Add 'groups' or use 'layer'")
    return schema, cross


def change_report():
    item = Obj({"id": Str(10, True), "area": Str(20), "kind": Enum(*KINDS), "title": Str(100)},
               {"why": Str(220), "before": Str(700), "after": Str(700), "ref": Str(30), "review": Bool(),
                "before_label": Str(22), "after_label": Str(22)})
    area = Obj({"id": Str(20, True), "label": Str(40)})
    req = head_req()
    req.update({"checkpoint": Str(140), "areas": List(area, 1, 12), "items": List(item, 1, 60)})
    schema = Obj(req, {"ask": Str(220)})
    need = {"added": ["after"], "removed": ["before"], "changed": ["before", "after"],
            "reversed": ["before", "after"], "conflict": ["before", "after"]}

    def cross(c, d):
        if not isinstance(d.get("items"), list):
            return
        unique(c, d["items"], "$.items")
        areas = {x.get("id") for x in d.get("areas", []) if isinstance(x, dict)}
        used = set()
        for i, x in enumerate(d["items"]):
            if not isinstance(x, dict):
                continue
            used.add(x.get("area"))
            if x.get("area") not in areas:
                c.err(f"$.items[{i}].area", f"'{x.get('area')}' is not in 'areas'. Known: {', '.join(sorted(map(str, areas)))}")
            for k in need.get(x.get("kind"), []):
                if k not in x:
                    c.err(f"$.items[{i}]", f"kind '{x['kind']}' needs '{k}' text so the page can show the change")
            if x.get("kind") == "added" and "before" in x:
                c.err(f"$.items[{i}]", "kind 'added' has no 'before' text; remove it")
            if x.get("kind") == "removed" and "after" in x:
                c.err(f"$.items[{i}]", "kind 'removed' has no 'after' text; remove it")
        for a in sorted(areas - used):
            c.warnings.append(f"area '{a}' has no items; remove it")
    return schema, cross


def explainer():
    step = Obj({"label": Str(44)}, {"note": Str(100)})
    layer = Obj({"label": Str(32), "note": Str(150)}, {"tag": Str(20)})
    series = Obj({"name": Str(30), "values": List(Num(), 2, 12)})
    blocks = {
        "callout": Obj({"type": Enum("callout"), "kind": Enum("definition", "pitfall", "example"), "text": Str(420)}, {"title": Str(50)}),
        "flow": Obj({"type": Enum("flow"), "steps": List(step, 2, 7)}, {"loop": Str(110), "caption": Str(140)}),
        "table": Obj({"type": Enum("table"), "columns": List(Str(32), 2, 6), "rows": List(List(Str(100), 2, 6), 1, 10)}, {"caption": Str(140)}),
        "chart": Obj({"type": Enum("chart"), "kind": Enum("bar", "line"), "labels": List(Str(24), 2, 12), "series": List(series, 1, 3)},
                     {"title": Str(80), "unit": Str(14), "caption": Str(140)}),
        "layers": Obj({"type": Enum("layers"), "layers": List(layer, 2, 8)}, {"title": Str(80), "direction": Str(40), "caption": Str(140)}),
        "list": Obj({"type": Enum("list"), "items": List(Str(170), 2, 8)}, {"ordered": Bool(), "title": Str(60)}),
    }

    class Block:
        def check(self, c, v, p):
            if not isinstance(v, dict) or v.get("type") not in blocks:
                return c.err(p, f"needs an object with 'type' one of: {', '.join(blocks)}")
            blocks[v["type"]].check(c, v, p)
            if v["type"] == "table" and isinstance(v.get("rows"), list) and isinstance(v.get("columns"), list):
                for i, r in enumerate(v["rows"]):
                    if isinstance(r, list) and len(r) != len(v["columns"]):
                        c.err(f"{p}.rows[{i}]", f"has {len(r)} cells but there are {len(v['columns'])} columns")
            if v["type"] == "chart" and isinstance(v.get("labels"), list):
                for i, s in enumerate(v.get("series", [])):
                    if isinstance(s, dict) and isinstance(s.get("values"), list) and len(s["values"]) != len(v["labels"]):
                        c.err(f"{p}.series[{i}].values", f"has {len(s['values'])} values but there are {len(v['labels'])} labels")

    check = Obj({"q": Str(190), "options": List(Str(130), 2, 4), "answer": Int(0, 3), "explain": Str(240)})
    sec = Obj({"id": Str(10, True), "heading": Str(70), "idea": Str(210)},
              {"body": List(Str(620), 0, 4), "blocks": List(Block(), 0, 5), "check": List(check, 0, 3)})
    req = head_req()
    req["sections"] = List(sec, 1, 10)
    schema = Obj(req, {"ask": Str(220)})

    def cross(c, d):
        if not isinstance(d.get("sections"), list):
            return
        unique(c, d["sections"], "$.sections")
        for i, s in enumerate(d["sections"]):
            if not isinstance(s, dict):
                continue
            for j, q in enumerate(s.get("check", [])):
                if isinstance(q, dict) and isinstance(q.get("options"), list) and isinstance(q.get("answer"), int) \
                        and q["answer"] >= len(q["options"]):
                    c.err(f"$.sections[{i}].check[{j}].answer", f"index {q['answer']} is outside the {len(q['options'])} options (0-based)")
    return schema, cross


BUILDERS = {"decision-brief": decision_brief, "system-map": system_map,
            "change-report": change_report, "explainer": explainer}


def validate(name, data):
    c = Ctx()
    if not isinstance(data, dict):
        c.err("$", "the data must be one JSON object")
        return c
    schema, cross = BUILDERS[name]()
    schema.check(c, data, "$")
    try:
        cross(c, data)
    except (AttributeError, TypeError, KeyError):
        if not c.errors:
            raise
    if len(str(data.get("title", "")).split()) > 6:
        c.warnings.append("title has more than 6 words; a 2 to 4 word name works better as the page title")
    return c


def normalize(name, data):
    if name == "system-map":
        data.setdefault("statuses", DEFAULT_STATUSES)
        data.setdefault("columns", "layer")
        data.setdefault("fan_out_warn", 8)
    return data


def artifact_form(text):
    text = re.sub(r"<!doctype html>\s*", "", text, flags=re.I)
    text = re.sub(r"</?(html|head|body)\b[^>]*>\s*", "", text, flags=re.I)
    text = re.sub(r'<meta (charset|name="viewport")[^>]*>\s*', "", text)
    return text.lstrip()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("template")
    ap.add_argument("data")
    ap.add_argument("-o", "--out")
    ap.add_argument("--artifact", action="store_true")
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args(argv)
    name = Path(a.template).stem
    if name not in BUILDERS:
        print(f"unknown template '{a.template}'. Use one of: {', '.join(BUILDERS)}", file=sys.stderr)
        return 2
    if not a.validate and not a.out:
        print("give -o <out.html> or --validate", file=sys.stderr)
        return 2
    try:
        data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"cannot read {a.data} as JSON: {e}. Fix the JSON syntax (quotes, commas, brackets)", file=sys.stderr)
        return 1
    c = validate(name, data)
    for w in c.warnings:
        print("warning: " + w, file=sys.stderr)
    if c.errors:
        print(f"{len(c.errors)} problem(s) in {a.data} for template '{name}':", file=sys.stderr)
        for e in c.errors:
            print("  " + e, file=sys.stderr)
        print(f"Schema: references/{name}.md", file=sys.stderr)
        return 1
    if a.validate:
        print("data valid")
        return 0
    tpl = (TEMPLATES / f"{name}.html").read_text(encoding="utf-8")
    payload = json.dumps(normalize(name, data), ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    pat = re.compile(r'(<script type="application/json" id="handoff-data">).*?(</script>)', re.S)
    out = pat.sub(lambda m: m.group(1) + payload + m.group(2), tpl, count=1)
    out = re.sub(r"<title>.*?</title>", lambda m: "<title>" + html.escape(data["title"]) + "</title>", out, count=1)
    if a.artifact:
        out = artifact_form(out)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(out, encoding="utf-8", newline="\n")
    print(f"built {a.out} ({len(out) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
