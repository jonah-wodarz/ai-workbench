#!/usr/bin/env python3
"""Compare two result labels: `python3 compare.py before after`. Prints a per-skill table and regressions."""
import sys

import lib


def load(label):
    return lib.load_json(lib.EVALS / "results" / label / "summary.json")


def rate(n, d):
    return None if not d else n / d


def fmt(x):
    return "   -" if x is None else f"{100 * x:3.0f}%"


def delta(a, b, lower_is_better=False):
    if a is None or b is None:
        return "   "
    d = 100 * (b - a)
    if abs(d) < 0.5:
        return " = "
    good = (d < 0) == lower_is_better
    return f"{d:+.0f}{'+' if good else '!'}"


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    a, b = load(argv[1]), load(argv[2])
    print(f"before: {a['meta'].get('ref')} ({argv[1]})   after: {b['meta'].get('ref')} ({argv[2]})")
    ta, tb = a.get("trigger"), b.get("trigger")
    if ta and tb:
        print("\nTrigger (should-trigger rate / near-miss false-trigger rate; '!' = worse, '+' = better)")
        print(f"{'skill':30} {'should before':>13} {'after':>6} {'d':>5}   {'nearmiss before':>15} {'after':>6} {'d':>5}")
        for s in sorted(set(ta["skills"]) | set(tb["skills"])):
            x, y = ta["skills"].get(s), tb["skills"].get(s)
            if not x or not y:
                print(f"{s:30} (only in one run)")
                continue
            sa, sb = rate(x["should"]["hits"], x["should"]["n"]), rate(y["should"]["hits"], y["should"]["n"])
            na, nb = rate(x["near_miss"]["false_hits"], x["near_miss"]["n"]), rate(y["near_miss"]["false_hits"], y["near_miss"]["n"])
            print(f"{s:30} {fmt(sa):>13} {fmt(sb):>6} {delta(sa, sb):>5}   {fmt(na):>15} {fmt(nb):>6} {delta(na, nb, True):>5}")
        ua, ub = ta["unrelated"], tb["unrelated"]
        print(f"{'unrelated (false fires)':30} {ua['false_hits']}/{ua['n']:>10} {ub['false_hits']}/{ub['n']:>4}")
        qa = {q["id"]: q for q in ta["queries"]}
        reg = []
        for q in tb["queries"]:
            p = qa.get(q["id"])
            if p and q["kind"] == "should":
                ha, hb = p["outcomes"].count(q["skill"]), q["outcomes"].count(q["skill"])
                if hb < ha:
                    reg.append((q["skill"], ha, hb, q["outcomes"], q["query"]))
        if reg:
            print("\nShould-trigger queries that fire less often now:")
            for s, ha, hb, o, q in reg:
                print(f"  {s}: {ha} -> {hb} of {len(o)}  {q[:90]!r}")
    sa_, sb_ = a.get("scenarios"), b.get("scenarios")
    if sa_ and sb_:
        print("\nScenarios (assertions passed / total over all runs)")
        print(f"{'skill':30} {'before':>9} {'after':>9}  {'d':>4}")
        for s in sorted(set(sa_["skills"]) | set(sb_["skills"])):
            x, y = sa_["skills"].get(s), sb_["skills"].get(s)
            if not x or not y:
                print(f"{s:30} (only in one run)")
                continue
            d = y["passed"] - x["passed"]
            print(f"{s:30} {x['passed']:>4}/{x['total']:<4} {y['passed']:>4}/{y['total']:<4} {d:+4d}{'!' if d < 0 else ''}")
        print("\nAssertions with more failures now:")
        n = 0
        for s, y in sb_["skills"].items():
            x = sa_["skills"].get(s)
            if not x:
                continue
            for sc, ent in y["scenarios"].items():
                prev = {t["id"]: t for t in x["scenarios"].get(sc, {}).get("assertions", [])}
                for t in ent["assertions"]:
                    p = prev.get(t["id"])
                    if p and t["fails"] > p["fails"]:
                        n += 1
                        print(f"  {s}/{sc}/{t['id']}: failed {p['fails']}/{p['runs']} -> {t['fails']}/{t['runs']}: {t['desc'][:80]}")
                        for ev in t["failure_evidence"][:1]:
                            print(f"      {ev['why'][:160]}")
        if not n:
            print("  none")


if __name__ == "__main__":
    main(sys.argv)
