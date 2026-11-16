#!/usr/bin/env python3
"""Scenario test: does a skill still produce the intended behaviour?

A scenario (scenarios/<skill>/<name>.json) holds a prompt, an optional fixture project and 4-8 assertions.
Each run executes `claude -p` headless in a fresh isolated project (tools allowed, turns capped), records
the transcript and a file diff, then grades every assertion: deterministic checks first, an LLM judge
(one call per run) for the rest.
"""
import argparse
import fnmatch
import json
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import lib
from checks import CUSTOM, get_target

TOOLS = "Bash,Read,Write,Edit,Glob,Grep,Skill,WebSearch,WebFetch"


def load_scenarios(only_skills, only_names, limit):
    out = []
    for f in sorted((lib.EVALS / "scenarios").glob("*/*.json")):
        sc = lib.load_json(f)
        sc["skill"], sc["name"] = f.parent.name, f.stem
        if only_skills and sc["skill"] not in only_skills:
            continue
        if only_names and sc["name"] not in only_names:
            continue
        out.append(sc)
    return out[:limit] if limit else out


def execute(sc, skills_dir, model, timeout):
    """Run one scenario once. Returns dict with transcript pieces, diff and info."""
    with lib.Sandbox(skills_dir) as sb:
        info = lib.build_fixture(sc.get("fixture"), skills_dir, sb.proj)
        before = lib.tree_state(sb.proj)
        ev = {"init": None, "assistant": [], "result": None, "tools": []}

        def on_event(e):
            t = e.get("type")
            if t == "system" and e.get("subtype") == "init":
                ev["init"] = e.get("skills", [])
            elif t == "assistant":
                for c in e.get("message", {}).get("content", []):
                    if c.get("type") == "text" and c.get("text", "").strip():
                        ev["assistant"].append({"text": c["text"]})
                    elif c.get("type") == "tool_use":
                        ev["tools"].append({"name": c["name"], "input": c.get("input", {}), "after_text": len(ev["assistant"])})
                        ev["assistant"].append({"tool": c["name"], "input": c.get("input", {})})
            elif t == "result":
                ev["result"] = e
            return False

        cmd = lib.base_cmd(model, ["--permission-mode", "acceptEdits", "--allowedTools", sc.get("tools", TOOLS),
                                   "--max-turns", str(sc.get("max_turns", 15))]) + ["-p", sc["prompt"]]
        t0 = time.time()
        reason, err = lib.stream_run(cmd, sb.proj, sb.env(), timeout, on_event)
        res = ev["result"] or {}
        out = {"seconds": int(time.time() - t0), "reason": reason, "subtype": res.get("subtype"),
               "turns": res.get("num_turns"), "cost": res.get("total_cost_usd", 0), "fixture": info}
        if res.get("is_error") and res.get("subtype") != "error_max_turns":
            out["error"] = str(res.get("result"))[:300]
        elif ev["result"] is None:
            out["error"] = f"no result event ({reason}) {err[-200:]}"
        texts = [a["text"] for a in ev["assistant"] if "text" in a]
        out["final"] = res.get("result") if isinstance(res.get("result"), str) and res.get("result") else (texts[-1] if texts else "")
        out["all_text"] = "\n\n".join(texts)
        out["tools"] = ev["tools"]
        out["trace"] = ev["assistant"]
        after = lib.tree_state(sb.proj)
        out["diff"], out["changed"] = lib.tree_diff(before, after)
        out["skills_dir"] = str(skills_dir)
        out["empty_dirs"] = sorted(str(d.relative_to(sb.proj)) for d in sb.proj.rglob("*")
                                   if d.is_dir() and d.relative_to(sb.proj).parts[0] not in (".claude", ".git")
                                   and "__pycache__" not in d.parts and not any(x.is_file() for x in d.rglob("*")))
        out["files"] = {k: v.decode(errors="replace") for k, v in after.items() if len(v) < 200000 and not k.startswith(".claude/")}
        out["before_files"] = {k: v.decode(errors="replace") for k, v in before.items() if len(v) < 200000 and not k.startswith(".claude/")}
        if ev["init"] is not None:
            probs, _ = lib.isolation_problems(ev["init"], list(lib.skill_meta(skills_dir)))
            out["isolation"] = probs
        # deterministic checks that need to run commands must do so inside the sandbox
        out["cmd_results"] = {}
        for a in sc["assertions"]:
            if a.get("check") in ("cmd", "lint"):
                rc, text = lib.run_cmd(a["cmd"], sb.proj)
                out["cmd_results"][a["id"]] = {"rc": rc, "out": text[-600:]}
        return out


def tool_text(t):
    i = t["input"]
    return f"{t['name']} " + json.dumps(i, ensure_ascii=False)[:400]


def grade_det(a, run, sc):
    """Returns (status, why) with status in pass|fail|skip."""
    c = a["check"]
    files = run["files"]

    def target(name):
        return get_target(run, name)

    flags = re.I if "i" in a.get("flags", "") else 0
    flags |= re.M if "m" in a.get("flags", "") else 0
    if c == "regex":
        txt = target(a["target"])
        if txt is None:
            return ("fail" if a.get("expect", True) else "pass"), f"no file matches {a['target']}"
        m = re.search(a["pattern"], txt, flags | re.S if "s" in a.get("flags", "") else flags)
        want = a.get("expect", True)
        ok = (m is not None) == want
        if ok:
            return "pass", "ok"
        return "fail", (f"pattern {a['pattern'][:80]!r} not found" if want else f"unwanted text present: {m.group(0)[:120]!r}")
    if c == "count":
        txt = target(a["target"]) or ""
        n = len(re.findall(a["pattern"], txt, flags))
        ok = a.get("min", 0) <= n <= a.get("max", 10 ** 9)
        return ("pass" if ok else "fail"), f"count of {a['pattern']!r} = {n} (allowed {a.get('min', 0)}..{a.get('max', 'inf')})"
    if c in ("file_exists", "file_absent"):
        ms = [m for m in files if fnmatch.fnmatch(m, a["path"])]
        ok = bool(ms) == (c == "file_exists")
        return ("pass" if ok else "fail"), f"{a['path']}: {len(ms)} match(es) {ms[:4]}"
    if c == "file_unchanged":
        ch = [f for k in ("added", "modified", "deleted") for f in run["changed"][k] if fnmatch.fnmatch(f, a["path"])]
        return ("pass" if not ch else "fail"), f"changed under {a['path']}: {ch[:5]}"
    if c == "tool_used":
        pat = re.compile(a.get("input_regex", ""), re.S)
        hit = [t for t in run["tools"] if t["name"] in a["tools"] and pat.search(json.dumps(t["input"]))]
        ok = len(hit) >= a.get("min", 1)
        return ("pass" if ok else "fail"), f"{len(hit)} matching call(s) of {a['tools']}"
    if c == "order":
        def first(spec):
            for i, t in enumerate(run["tools"]):
                if t["name"] in spec["tools"] and re.search(spec.get("input_regex", ""), json.dumps(t["input"]), re.S):
                    return i
            return None
        x, y = first(a["first"]), first(a["then"])
        if y is None:
            return "skip", "second event never happened"
        return ("pass" if x is not None and x < y else "fail"), f"index first={x} then={y}"
    if c == "cmd":
        r = run["cmd_results"][a["id"]]
        return ("pass" if r["rc"] == 0 else "fail"), f"exit {r['rc']}: {r['out'][-200:]}"
    if c == "lint":
        r = run["cmd_results"][a["id"]]
        if r["rc"] == 0:
            return "pass", "lint exit 0"
        if run["fixture"].get("fixture_lint_exit", 0) != 0:
            return "skip", f"fixture itself fails lint at this ref ({run['fixture'].get('fixture_lint_tail')})"
        return "fail", f"lint exit {r['rc']}: {r['out'][-250:]}"
    if c == "py":
        return CUSTOM[a["fn"]](run, a)
    raise ValueError(f"unknown check {c}")


def pack_for_judge(run, sc):
    trace = []
    for x in run["trace"]:
        if "text" in x:
            trace.append(x["text"])
        else:
            trace.append(f"[tool call: {x['tool']} {json.dumps(x['input'], ensure_ascii=False)[:300]}]")
    return {
        "USER PROMPT": sc["prompt"],
        "FINAL ANSWER": run["final"][:12000],
        "SESSION IN ORDER (assistant text and tool calls)": "\n\n".join(trace)[:24000],
        "FILE CHANGES (unified diff vs start)": run["diff"] or "(no files changed)",
    }


def grade(sc, run):
    if run.get("error"):
        return [{"id": a["id"], "status": "skip", "why": "run errored: " + run["error"][:120]} for a in sc["assertions"]]
    results, llm_items = [], []
    for a in sc["assertions"]:
        if a["check"] == "llm":
            llm_items.append({"id": a["id"], "desc": a["desc"], "negative": a.get("negative", False)})
    verdicts = lib.judge(llm_items, pack_for_judge(run, sc), sc.get("judge_model", "sonnet")) if llm_items and not run.get("error") else {}
    for a in sc["assertions"]:
        if a["check"] == "llm":
            v = verdicts.get(a["id"], {"pass": False, "evidence": "", "note": "not judged (run error)"})
            results.append({"id": a["id"], "status": "pass" if v["pass"] else "fail", "why": (v["note"] + " " + v["evidence"]).strip()})
        else:
            try:
                st, why = grade_det(a, run, sc)
            except Exception as e:  # a broken check is a harness bug; surface it
                st, why = "fail", f"check error: {e!r}"
            results.append({"id": a["id"], "status": st, "why": why})
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--parallel", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--skills", default="")
    ap.add_argument("--scenarios", default="", help="comma list of scenario names")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--patch", action="append", default=[], help="diagnostics: 'skill/FILE::old::new' text replacement on the snapshot")
    args = ap.parse_args()

    skills_dir, sha = lib.export_ref(args.ref, args.patch)
    scs = load_scenarios(set(filter(None, args.skills.split(","))), set(filter(None, args.scenarios.split(","))), args.limit)
    print(f"ref {args.ref} -> {sha[:12]}; {len(scs)} scenarios x {args.runs} runs, model {args.model}", flush=True)
    raw = lib.EVALS / "results" / args.label / "raw" / "scenarios"

    def work(sc, i):
        run = lib.with_retry(lambda: execute(sc, skills_dir, args.model, args.timeout))
        run["grades"] = grade(sc, run)
        d = raw / sc["skill"] / sc["name"] / f"run{i + 1}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "final.md").write_text(run["final"])
        (d / "diff.patch").write_text(run["diff"])
        (d / "trace.json").write_text(json.dumps({k: run[k] for k in ("trace", "tools", "grades", "changed", "fixture", "seconds", "turns", "subtype", "cost")}
                                                 | {"error": run.get("error")}, indent=1, ensure_ascii=False))
        return sc, i, run

    runs = defaultdict(list)
    t0 = time.time()
    with ThreadPoolExecutor(args.parallel) as ex:
        futs = [ex.submit(work, sc, i) for sc in scs for i in range(args.runs)]
        for n, f in enumerate(as_completed(futs), 1):
            sc, i, run = f.result()
            g = run["grades"]
            p = sum(x["status"] == "pass" for x in g)
            t = sum(x["status"] != "skip" for x in g)
            print(f"[{n}/{len(futs)}] {sc['skill']}/{sc['name']} run{i + 1}: {p}/{t} ({run['seconds']}s, {run.get('turns')} turns"
                  f"{', ERROR ' + run['error'][:80] if run.get('error') else ''})", flush=True)
            runs[(sc["skill"], sc["name"])].append((i, run))

    skills_out, iso, errors, total_cost = {}, 0, 0, 0.0
    for sc in scs:
        sk = skills_out.setdefault(sc["skill"], {"passed": 0, "total": 0, "scenarios": {}})
        rr = sorted(runs[(sc["skill"], sc["name"])], key=lambda x: x[0])
        ent = {"passed": 0, "total": 0, "errored_runs": 0, "assertions": [], "runs": []}
        for a in sc["assertions"]:
            ar = {"id": a["id"], "desc": a.get("desc", a["id"]), "runs": 0, "fails": 0, "skips": 0, "failure_evidence": []}
            for i, run in rr:
                g = next(x for x in run["grades"] if x["id"] == a["id"])
                if g["status"] == "skip":
                    ar["skips"] += 1
                    continue
                ar["runs"] += 1
                if g["status"] == "fail":
                    ar["fails"] += 1
                    ar["failure_evidence"].append({"run": i + 1, "why": " ".join(g["why"].split())[:300]})
            ent["assertions"].append(ar)
            ent["passed"] += ar["runs"] - ar["fails"]
            ent["total"] += ar["runs"]
        for i, run in rr:
            iso += bool(run.get("isolation"))
            errors += bool(run.get("error"))
            total_cost += run.get("cost") or 0
            ent["errored_runs"] += bool(run.get("error"))
            ent["runs"].append({"run": i + 1, "seconds": run["seconds"], "turns": run.get("turns"), "subtype": run.get("subtype"),
                                "error": run.get("error"), "passed": sum(x["status"] == "pass" for x in run["grades"]),
                                "total": sum(x["status"] != "skip" for x in run["grades"])})
        sk["scenarios"][sc["name"]] = ent
        sk["passed"] += ent["passed"]
        sk["total"] += ent["total"]
    summary = {"runs_per_scenario": args.runs, "n_runs": sum(len(v) for v in runs.values()), "isolation_violations": iso,
               "errors": errors, "cost_usd_reported": round(total_cost, 2), "seconds": int(time.time() - t0),
               "skills": dict(sorted(skills_out.items()))}
    d = lib.update_summary(args.label, "scenarios", summary,
                           {"label": args.label, "ref": args.ref, "sha": sha, "scenario_model": args.model})
    print(f"wrote {d}/summary.json ({summary['n_runs']} runs, {summary['seconds']}s, errors {errors})")


if __name__ == "__main__":
    sys.exit(main())
