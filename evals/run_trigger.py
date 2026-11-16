#!/usr/bin/env python3
"""Trigger test: does the right skill load for a realistic request?

Each run starts `claude -p <query>` in a fresh isolated project holding the full skill set of the
chosen ref and reads the stream. Two outcomes are recorded per run:
- first call: the first tool call decides: a Skill call (which skill), another tool, or text only.
- within window: with `--window N` the run continues until a Skill call, N tool calls, or the final
  answer, whichever comes first. The first Skill call inside the window decides; without one the
  first call decides as before. `--window 1` (default) is the first-call test.
"""
import argparse
import json
import re
import sys
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import lib


def run_once(query, skills_dir, expected, model, timeout, explicit=None, window=1):
    """Returns dict(first=..., calls=[...], skill_at=..., init_skills=..., isolation=[...], error=?, ms=int).

    first: decision at the first tool call (or text). calls: tool names seen, in order. skill_at:
    {"name", "idx"} of the first Skill call within the first `window` tool calls (idx is 1-based)."""
    t0 = time.time()
    with lib.Sandbox(skills_dir) as sb:
        state = {"init": None, "first": None, "text": 0, "blocks": {}, "result_err": None, "seen_text": "",
                 "calls": [], "ids": set(), "skill_at": None, "pending_skill": None, "stop": False}

        def set_first(d):
            if state["first"] is None:
                state["first"] = d

        def finish():
            state["stop"] = True
            return True

        def note_call(cid, name, inp=None):
            """Register a tool call once. Returns True when the run can stop."""
            if cid in state["ids"]:
                return False
            state["ids"].add(cid)
            state["calls"].append(name)
            idx = len(state["calls"])
            if name == "Skill":
                if inp is not None and inp.get("skill"):
                    return got_skill(idx, inp["skill"])
                state["pending_skill"] = idx
                return False
            set_first({"kind": "tool", "name": name, "input": json.dumps(inp)[:300] if inp else ""})
            return idx >= window

        def got_skill(idx, name):
            state["pending_skill"] = None
            set_first({"kind": "skill", "name": name})
            state["skill_at"] = {"name": name, "idx": idx}
            return True

        def on_event(ev):
            t = ev.get("type")
            if t == "system" and ev.get("subtype") == "init":
                state["init"] = ev.get("skills", [])
                return False
            if t == "result":
                if ev.get("is_error"):
                    state["result_err"] = str(ev.get("result"))[:300]
                else:
                    set_first({"kind": "text"})
                return True
            if t == "stream_event":
                se = ev.get("event", {})
                st = se.get("type")
                idx = se.get("index")
                if st == "message_start":
                    state["text"] = 0
                    state["blocks"] = {}
                elif st == "content_block_start":
                    cb = se.get("content_block", {})
                    if cb.get("type") == "tool_use":
                        state["blocks"][idx] = ""
                        if explicit:
                            state["calls"].append(cb.get("name"))
                        elif note_call(cb.get("id") or f"b{len(state['ids'])}", cb.get("name")):
                            return True
                elif st == "content_block_delta":
                    d = se.get("delta", {})
                    if d.get("type") == "input_json_delta" and idx in state["blocks"]:
                        state["blocks"][idx] += d.get("partial_json", "")
                        if explicit:
                            if explicit in state["blocks"][idx]:
                                set_first({"kind": "explicit-marker"})
                                return True
                            return False
                        m = re.search(r'"skill"\s*:\s*"([^"]+)"', state["blocks"][idx])
                        if m and state["pending_skill"] is not None:
                            return got_skill(state["pending_skill"], m.group(1))
                    elif d.get("type") == "text_delta":
                        state["text"] += len(d.get("text", ""))
                        state["seen_text"] += d.get("text", "")
                        if explicit:
                            if explicit in state["seen_text"]:
                                set_first({"kind": "explicit-marker"})
                                return True
                        if state["text"] > 600:
                            set_first({"kind": "text"})
                            return True
                elif st == "message_delta":
                    # a turn that ends without a tool call is the final answer
                    if se.get("delta", {}).get("stop_reason") not in (None, "tool_use"):
                        set_first({"kind": "text"})
                        return True
                elif st == "message_stop" and state["first"] is None and (not explicit or not state["blocks"]):
                    set_first({"kind": "text"})
                    return True
            if t == "assistant":
                for c in ev.get("message", {}).get("content", []):
                    if c.get("type") == "tool_use" and not explicit:
                        if note_call(c.get("id") or f"a{len(state['ids'])}", c.get("name"), c.get("input", {})):
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
        res["calls"] = state["calls"]
        res["skill_at"] = state["skill_at"]
    return res


def classify(first, skill_names):
    """Collapse the decision into a label: skill name | 'other-skill:x' | 'tool:x' | 'none'."""
    if first["kind"] == "skill":
        n = first["name"].split(":")[-1]
        return n if n in skill_names else f"other-skill:{first['name']}"
    if first["kind"] == "tool":
        return f"tool:{first['name']}"
    return "none"


def classify_window(r, skill_names):
    """Label for the within-window outcome: the first Skill call in the window, else the first call."""
    sa = r.get("skill_at")
    if sa:
        return classify({"kind": "skill", "name": sa["name"]}, skill_names)
    return classify(r["first"], skill_names)


def build_jobs(queries, meta, only, limit, sets):
    jobs = []
    auto = [s for s, m in meta.items() if m["auto"]]
    for s in auto:
        if only and s not in only:
            continue
        q = queries["skills"].get(s)
        if not q:
            continue
        groups = []
        if "train" in sets:
            groups.append(("train", q))
        if "holdout" in sets and q.get("holdout"):
            groups.append(("holdout", q["holdout"]))
        for sname, g in groups:
            for x in g.get("should", [])[:limit or None]:
                jobs.append({"kind": "should", "set": sname, "skill": s, "q": x["q"], "instead": None})
            for x in g.get("near_miss", [])[:limit or None]:
                jobs.append({"kind": "near_miss", "set": sname, "skill": s, "q": x["q"], "instead": x.get("instead")})
    if "train" in sets:
        if not only or "unrelated" in only:
            for x in queries["unrelated"][:limit or None]:
                jobs.append({"kind": "unrelated", "set": "train", "skill": None, "q": x, "instead": None})
        for s, x in queries.get("explicit", {}).items():
            if not only or s in only:
                jobs.append({"kind": "explicit", "set": "train", "skill": s, "q": x["q"], "marker": x["marker"], "instead": None})
    for j in jobs:
        j["id"] = lib.short_id(j["kind"], j["q"]) if j["set"] == "train" else lib.short_id(j["kind"], j["set"], j["q"])
    return jobs


def new_skill_stats():
    return {"should": {"n": 0, "hits": 0, "confusion": Counter(), "win_hits": 0, "win_confusion": Counter(), "skill_at": []},
            "near_miss": {"n": 0, "false_hits": 0, "instead_hits": 0, "instead_n": 0, "fired": Counter(),
                          "win_false_hits": 0, "win_fired": Counter()}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True, help="git ref of the skills to test, or WORKTREE")
    ap.add_argument("--label", required=True, help="results folder name under evals/results/")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--runs", type=int, default=3, help="runs per query")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--timeout", type=int, default=0, help="seconds per run (default 90, or 60 + 45 per window step)")
    ap.add_argument("--window", type=int, default=1,
                    help="stop after a Skill call, N tool calls or the final answer; 1 = first call only")
    ap.add_argument("--set", dest="qset", choices=["train", "holdout", "all"], default="train",
                    help="train = should/near_miss, holdout = the held-out queries, all = both")
    ap.add_argument("--skills", default="", help="comma list: only these skills (plus 'unrelated')")
    ap.add_argument("--limit", type=int, default=0, help="max queries per group (sanity checks)")
    ap.add_argument("--max-wait", type=int, default=1200,
                    help="seconds: wait for a usage-limit reset only if it is this close, else stop and write partial results")
    ap.add_argument("--keep-raw", action="store_true", help="always write raw traces (default: yes)")
    ap.add_argument("--patch", action="append", default=[], help="diagnostics: 'skill/FILE::old::new' text replacement on the snapshot")
    args = ap.parse_args()
    window = max(1, args.window)
    timeout = args.timeout or (90 if window == 1 else 60 + 45 * window)
    sets = {"train", "holdout"} if args.qset == "all" else {args.qset}

    skills_dir, sha = lib.export_ref(args.ref, args.patch)
    meta = lib.skill_meta(skills_dir)
    queries = lib.load_json(lib.EVALS / "trigger" / "queries.json")
    only = set(filter(None, args.skills.split(",")))
    jobs = build_jobs(queries, meta, only, args.limit, sets)
    names = set(meta)
    expected = list(meta)
    # skills with queries that the ref does not contain (for example a skill added later)
    missing = sorted(s for s in queries["skills"] if s not in meta and (not only or s in only))
    print(f"ref {args.ref} -> {sha[:12]}; {len(jobs)} queries x {args.runs} runs, model {args.model}, "
          f"window {window}, set {args.qset}" + (f"; not in ref (skipped): {', '.join(missing)}" if missing else ""), flush=True)

    raw_dir = lib.EVALS / "results" / args.label / "raw" / "trigger"
    raw_dir.mkdir(parents=True, exist_ok=True)

    aborted = threading.Event()

    def work(job, i):
        if aborted.is_set():
            return job, i, {"error": "aborted: usage limit", "aborted": True}

        def once():
            return run_once(job["q"], skills_dir, expected, args.model, timeout, job.get("marker"), window)
        r = lib.with_retry(once, max_wait=args.max_wait)
        if r.get("limit_abort"):
            aborted.set()
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
            if done % 40 == 0:
                (raw_dir / "results.json").write_text(json.dumps(results))
            lab = classify(r["first"], names) if "first" in r else f"ERROR {r.get('error', '')[:60]}"
            wl = f" | window: {classify_window(r, names)}" if window > 1 and "first" in r else ""
            print(f"[{done}/{len(futs)}] {job['kind']:9} {job['skill'] or '-':28} -> {lab}{wl}", flush=True)

    # ---- aggregate
    skills_out = {"train": {}, "holdout": {}}
    unrelated = {"n": 0, "false_hits": 0, "win_false_hits": 0, "by_skill": Counter()}
    explicit = {}
    qrecs, iso_viol, errors, extras_seen = [], 0, 0, set()
    for j in jobs:
        outs, wouts, at = [], [], []
        if aborted.is_set():
            results[j["id"]] = [r for r in results[j["id"]] if not (r.get("aborted") or r.get("limit_abort"))]
            if not results[j["id"]]:
                continue
        for r in results[j["id"]]:
            if r.get("isolation"):
                iso_viol += 1
            extras_seen.update(r.get("bundled_extras", []))
            if "first" not in r:
                errors += 1
                outs.append("error")
                wouts.append("error")
                at.append(None)
            else:
                outs.append(classify(r["first"], names))
                wouts.append(classify_window(r, names))
                at.append(r["skill_at"]["idx"] if r.get("skill_at") else None)
        qrecs.append({"id": j["id"], "set": j["set"], "kind": j["kind"], "skill": j["skill"], "instead": j["instead"],
                      "query": j["q"], "outcomes": outs, "window_outcomes": wouts, "skill_at": at})
        valid = [(o, w, a) for o, w, a in zip(outs, wouts, at) if o != "error"]
        if j["kind"] in ("should", "near_miss"):
            s = skills_out[j["set"]].setdefault(j["skill"], new_skill_stats())
            if j["kind"] == "should":
                sh = s["should"]
                sh["n"] += len(valid)
                for o, w, a in valid:
                    if o == j["skill"]:
                        sh["hits"] += 1
                    else:
                        sh["confusion"][o] += 1
                    if w == j["skill"]:
                        sh["win_hits"] += 1
                        sh["skill_at"].append(a)
                    else:
                        sh["win_confusion"][w] += 1
            else:
                nm = s["near_miss"]
                nm["n"] += len(valid)
                for o, w, a in valid:
                    if o == j["skill"]:
                        nm["false_hits"] += 1
                    elif o in names or o.startswith("other-skill"):
                        nm["fired"][o] += 1
                    if w == j["skill"]:
                        nm["win_false_hits"] += 1
                    elif w in names or w.startswith("other-skill"):
                        nm["win_fired"][w] += 1
                    if j["instead"]:
                        nm["instead_n"] += 1
                        nm["instead_hits"] += o == j["instead"]
        elif j["kind"] == "unrelated":
            unrelated["n"] += len(valid)
            for o, w, a in valid:
                if o in names:
                    unrelated["false_hits"] += 1
                    unrelated["by_skill"][o] += 1
                if w in names:
                    unrelated["win_false_hits"] += 1
        else:
            e = explicit.setdefault(j["skill"], {"n": 0, "hits": 0})
            for r in results[j["id"]]:
                if "first" in r:
                    e["n"] += 1
                    e["hits"] += r["first"]["kind"] == "explicit-marker" or (
                        r["first"]["kind"] == "skill" and r["first"]["name"].split(":")[-1] == j["skill"])
    for grp in skills_out.values():
        for s in grp.values():
            for k in ("confusion", "win_confusion"):
                s["should"][k] = dict(s["should"][k])
            for k in ("fired", "win_fired"):
                s["near_miss"][k] = dict(s["near_miss"][k])
    unrelated["by_skill"] = dict(unrelated["by_skill"])
    n_runs = sum(len(results[j["id"]]) for j in jobs)
    summary = {"runs_per_query": args.runs, "window": window, "sets": sorted(sets), "n_runs": n_runs,
               "isolation_violations": iso_viol, "errors": errors,
               "bundled_skills_visible": sorted(extras_seen), "skills": dict(sorted(skills_out["train"].items())),
               "holdout_skills": dict(sorted(skills_out["holdout"].items())), "not_in_ref": missing,
               "aborted": "usage limit reached; partial results" if aborted.is_set() else "",
               "unrelated": unrelated, "explicit": explicit, "queries": qrecs,
               "seconds": int(time.time() - t0)}
    (raw_dir / "results.json").write_text(json.dumps({j["id"]: results[j["id"]] for j in jobs if results[j["id"]]}, indent=1))
    d = lib.update_summary(args.label, "trigger", summary,
                           {"label": args.label, "ref": args.ref, "sha": sha, "trigger_model": args.model})
    print(f"wrote {d}/summary.json ({n_runs} runs, {summary['seconds']}s, errors {errors}, isolation violations {iso_viol})")


if __name__ == "__main__":
    sys.exit(main())
