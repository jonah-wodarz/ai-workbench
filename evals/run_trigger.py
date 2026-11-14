#!/usr/bin/env python3
"""Trigger test: does the right skill load for a realistic request?

Each run starts `claude -p <query>` in a fresh isolated project holding the full skill set of the
chosen ref, reads the stream, and stops at the first tool call (or when the first assistant message
ends). The first call decides the outcome: a Skill call (which skill), another tool, or text only.
"""
import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import lib


def run_once(query, skills_dir, expected, model, timeout, explicit=None):
    """Returns dict(first=..., init_skills=..., isolation=[...], error=?, ms=int)."""
    t0 = time.time()
    with lib.Sandbox(skills_dir) as sb:
        state = {"init": None, "first": None, "text": 0, "blocks": {}, "result_err": None, "seen_text": ""}

        def on_event(ev):
            t = ev.get("type")
            if t == "system" and ev.get("subtype") == "init":
                state["init"] = ev.get("skills", [])
                return False
            if t == "result":
                if ev.get("is_error"):
                    state["result_err"] = str(ev.get("result"))[:300]
                elif state["first"] is None:
                    state["first"] = {"kind": "text"}
                return True
            if t == "stream_event":
                se = ev.get("event", {})
                st = se.get("type")
                idx = se.get("index")
                if st == "content_block_start":
                    cb = se.get("content_block", {})
                    if cb.get("type") == "tool_use":
                        if explicit:
                            state["blocks"][idx] = ""
                        elif cb.get("name") != "Skill":
                            state["first"] = {"kind": "tool", "name": cb.get("name")}
                            return True
                        state["blocks"][idx] = ""
                elif st == "content_block_delta":
                    d = se.get("delta", {})
                    if d.get("type") == "input_json_delta" and idx in state["blocks"]:
                        state["blocks"][idx] += d.get("partial_json", "")
                        if explicit:
                            if explicit in state["blocks"][idx]:
                                state["first"] = {"kind": "explicit-marker"}
                                return True
                            return False
                        m = re.search(r'"skill"\s*:\s*"([^"]+)"', state["blocks"][idx])
                        if m:
                            state["first"] = {"kind": "skill", "name": m.group(1)}
                            return True
                    elif d.get("type") == "text_delta":
                        state["text"] += len(d.get("text", ""))
                        state["seen_text"] += d.get("text", "")
                        if explicit:
                            if explicit in state["seen_text"]:
                                state["first"] = {"kind": "explicit-marker"}
                                return True
                        if state["text"] > 600:
                            state["first"] = {"kind": "text"}
                            return True
                elif st == "message_stop" and state["first"] is None and (not explicit or not state["blocks"]):
                    state["first"] = {"kind": "text"}
                    return True
            if t == "assistant" and state["first"] is None:
                for c in ev.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use":
                        if c.get("name") == "Skill":
                            state["first"] = {"kind": "skill", "name": c.get("input", {}).get("skill", "")}
                        else:
                            state["first"] = {"kind": "tool", "name": c.get("name"), "input": json.dumps(c.get("input"))[:300]}
                        return True
            return False

        cmd = lib.base_cmd(model, ["--include-partial-messages", "--permission-prompts", "none"]) + ["-p", query]
        reason, err = lib.stream_run(cmd, sb.proj, sb.env(), timeout, on_event)
    res = {"ms": int((time.time() - t0) * 1000), "init_n": len(state["init"] or [])}
    if state["init"] is not None:
        probs, extras = lib.isolation_problems(state["init"], expected)
        res["isolation"] = probs
        res["bundled_extras"] = extras
    else:
        res["isolation"] = ["no init event"]
    if state["result_err"]:
        res["error"] = state["result_err"]
    elif state["first"] is None:
        res["error"] = f"no decision ({reason}) {err[-200:]}"
    else:
        res["first"] = state["first"]
    return res


def classify(first, skill_names):
    """Collapse the decision into a label: skill name | 'other-skill:x' | 'tool:x' | 'none'."""
    if first["kind"] == "skill":
        n = first["name"].split(":")[-1]
        return n if n in skill_names else f"other-skill:{first['name']}"
    if first["kind"] == "tool":
        return f"tool:{first['name']}"
    return "none"


def build_jobs(queries, meta, only, limit):
    jobs = []
    auto = [s for s, m in meta.items() if m["auto"]]
    for s in auto:
        if only and s not in only:
            continue
        q = queries["skills"].get(s)
        if not q:
            continue
        for x in q["should"][:limit or None]:
            jobs.append({"kind": "should", "skill": s, "q": x["q"], "instead": None})
        for x in q["near_miss"][:limit or None]:
            jobs.append({"kind": "near_miss", "skill": s, "q": x["q"], "instead": x.get("instead")})
    if not only or "unrelated" in only:
        for x in queries["unrelated"][:limit or None]:
            jobs.append({"kind": "unrelated", "skill": None, "q": x, "instead": None})
    for s, x in queries.get("explicit", {}).items():
        if not only or s in only:
            jobs.append({"kind": "explicit", "skill": s, "q": x["q"], "marker": x["marker"], "instead": None})
    for j in jobs:
        j["id"] = lib.short_id(j["kind"], j["q"])
    return jobs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="git ref of the skills to test, or WORKTREE")
    ap.add_argument("--label", required=True, help="results folder name under evals/results/")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=3, help="runs per query")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=90, help="seconds per run")
    ap.add_argument("--skills", default="", help="comma list: only these skills (plus 'unrelated')")
    ap.add_argument("--limit", type=int, default=0, help="max queries per group (sanity checks)")
    ap.add_argument("--keep-raw", action="store_true", help="always write raw traces (default: yes)")
    ap.add_argument("--patch", action="append", default=[], help="diagnostics: 'skill/FILE::old::new' text replacement on the snapshot")
    args = ap.parse_args()

    skills_dir, sha = lib.export_ref(args.ref, args.patch)
    meta = lib.skill_meta(skills_dir)
    queries = lib.load_json(lib.EVALS / "trigger" / "queries.json")
    only = set(filter(None, args.skills.split(",")))
    jobs = build_jobs(queries, meta, only, args.limit)
    names = set(meta)
    expected = list(meta)
    print(f"ref {args.ref} -> {sha[:12]}; {len(jobs)} queries x {args.runs} runs, model {args.model}", flush=True)

    raw_dir = lib.EVALS / "results" / args.label / "raw" / "trigger"
    raw_dir.mkdir(parents=True, exist_ok=True)

    def work(job, i):
        def once():
            return run_once(job["q"], skills_dir, expected, args.model, args.timeout, job.get("marker"))
        r = lib.with_retry(once)
        return job, i, r

    results = defaultdict(list)
    t0 = time.time()
    done = 0
    with ThreadPoolExecutor(args.parallel) as ex:
        futs = [ex.submit(work, j, i) for j in jobs for i in range(args.runs)]
        for f in as_completed(futs):
            job, i, r = f.result()
            results[job["id"]].append(r)
            done += 1
            lab = classify(r["first"], names) if "first" in r else f"ERROR {r.get('error', '')[:60]}"
            print(f"[{done}/{len(futs)}] {job['kind']:9} {job['skill'] or '-':28} -> {lab}", flush=True)

    # ---- aggregate
    skills_out = {}
    unrelated = {"n": 0, "false_hits": 0, "by_skill": Counter()}
    explicit = {}
    qrecs, iso_viol, errors, extras_seen = [], 0, 0, set()
    for j in jobs:
        outs = []
        for r in results[j["id"]]:
            if r.get("isolation"):
                iso_viol += 1
            extras_seen.update(r.get("bundled_extras", []))
            if "first" not in r:
                errors += 1
                outs.append("error")
            else:
                outs.append(classify(r["first"], names))
        qrecs.append({"id": j["id"], "kind": j["kind"], "skill": j["skill"], "instead": j["instead"],
                      "query": j["q"], "outcomes": outs})
        valid = [o for o in outs if o != "error"]
        if j["kind"] in ("should", "near_miss"):
            s = skills_out.setdefault(j["skill"], {
                "should": {"n": 0, "hits": 0, "confusion": Counter()},
                "near_miss": {"n": 0, "false_hits": 0, "instead_hits": 0, "instead_n": 0, "fired": Counter()}})
            if j["kind"] == "should":
                s["should"]["n"] += len(valid)
                for o in valid:
                    if o == j["skill"]:
                        s["should"]["hits"] += 1
                    else:
                        s["should"]["confusion"][o] += 1
            else:
                nm = s["near_miss"]
                nm["n"] += len(valid)
                for o in valid:
                    if o == j["skill"]:
                        nm["false_hits"] += 1
                    elif o in names or o.startswith("other-skill"):
                        nm["fired"][o] += 1
                    if j["instead"]:
                        nm["instead_n"] += 1
                        nm["instead_hits"] += o == j["instead"]
        elif j["kind"] == "unrelated":
            unrelated["n"] += len(valid)
            for o in valid:
                if o in names:
                    unrelated["false_hits"] += 1
                    unrelated["by_skill"][o] += 1
        else:
            e = explicit.setdefault(j["skill"], {"n": 0, "hits": 0})
            for r in results[j["id"]]:
                if "first" in r:
                    e["n"] += 1
                    e["hits"] += r["first"]["kind"] == "explicit-marker" or (
                        r["first"]["kind"] == "skill" and r["first"]["name"].split(":")[-1] == j["skill"])
    for s in skills_out.values():
        s["should"]["confusion"] = dict(s["should"]["confusion"])
        s["near_miss"]["fired"] = dict(s["near_miss"]["fired"])
    unrelated["by_skill"] = dict(unrelated["by_skill"])
    n_runs = sum(len(v) for v in results.values())
    summary = {"runs_per_query": args.runs, "n_runs": n_runs, "isolation_violations": iso_viol, "errors": errors,
               "bundled_skills_visible": sorted(extras_seen), "skills": dict(sorted(skills_out.items())),
               "unrelated": unrelated, "explicit": explicit, "queries": qrecs,
               "seconds": int(time.time() - t0)}
    (raw_dir / "results.json").write_text(json.dumps({j["id"]: results[j["id"]] for j in jobs}, indent=1))
    d = lib.update_summary(args.label, "trigger", summary,
                           {"label": args.label, "ref": args.ref, "sha": sha, "trigger_model": args.model})
    print(f"wrote {d}/summary.json ({n_runs} runs, {summary['seconds']}s, errors {errors}, isolation violations {iso_viol})")


if __name__ == "__main__":
    sys.exit(main())
