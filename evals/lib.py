"""Shared helpers for the skill eval harness (stdlib only).

Isolation model: every run gets a fresh project dir with the skills under test in
`.claude/skills/` and a fresh, empty CLAUDE_CONFIG_DIR, so user-level skills,
synced plugin skills, memory and project context are not loaded.
"""
import difflib
from collections import Counter
import fcntl
import hashlib
import json
import os
import re
import select
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from pathlib import Path

EVALS = Path(__file__).resolve().parent
REPO = EVALS.parent
WORK = Path(os.environ.get("AIWB_EVAL_WORK", "/home/claude/run/work/evals"))
CLAUDE = os.environ.get("AIWB_EVAL_CLAUDE", "claude")

# Environment variables of the host session that would leak context into a test run.
DROP_ENV = [
    "CLAUDECODE", "CLAUDE_PROJECT_UUID", "CLAUDE_PROJECT_TOOL", "CCR_SKILL_OVERRIDES",
    "CLAUDE_CODE_POST_TURN_MEMORY", "CLAUDE_CODE_POST_TURN_MEMORY_CONFIG",
    "CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD", "CLAUDE_ADDITIONAL_DIRECTORIES",
]
LIMIT_RE = re.compile(r"rate.?limit|usage limit|hit your .{0,20}limit|limit reached|overloaded|\b429\b|\b529\b|too many requests|quota", re.I)


# ---------------------------------------------------------------- snapshots
def _git(*args, **kw):
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True, **kw)


def export_ref(ref, patches=()):
    """Export `skills/` at `ref` into a cached snapshot. Returns (skills_dir, sha_or_label).
    patches: 'skill/file::old text::new text' strings applied to a copy (diagnostics only)."""
    base, sha = _export_ref(ref)
    if not patches:
        return base, sha
    tag = hashlib.sha1("|".join(patches).encode()).hexdigest()[:8]
    dest = WORK / "snapshots" / f"{sha[:12]}-patch-{tag}"
    if not dest.exists():
        shutil.copytree(base, dest / "skills")
        for pt in patches:
            f, old, new = pt.split("::", 2)
            path = dest / "skills" / f
            txt = path.read_text()
            if old not in txt:
                raise SystemExit(f"patch text not found in {f}")
            path.write_text(txt.replace(old, new))
    return dest / "skills", f"{sha}+patch-{tag}"


def _export_ref(ref):
    if ref == "WORKTREE":
        dest = WORK / "snapshots" / f"worktree-{time.strftime('%Y%m%d-%H%M%S')}"
        dest.mkdir(parents=True)
        shutil.copytree(REPO / "skills", dest / "skills", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        return dest / "skills", "WORKTREE"
    sha = _git("rev-parse", "--verify", f"{ref}^{{commit}}").stdout.decode().strip()
    dest = WORK / "snapshots" / sha[:12]
    if not (dest / "skills").is_dir():
        dest.mkdir(parents=True, exist_ok=True)
        arc = _git("archive", sha, "skills").stdout
        subprocess.run(["tar", "-x", "-C", str(dest)], input=arc, check=True)
    return dest / "skills", sha


def skill_meta(skills_dir):
    """name -> {'auto': bool, 'description': str} from SKILL.md frontmatter."""
    out = {}
    for d in sorted(Path(skills_dir).iterdir()):
        f = d / "SKILL.md"
        if not f.is_file():
            continue
        m = re.match(r"---\n(.*?)\n---", f.read_text(), re.S)
        fm = m.group(1) if m else ""
        dis = re.search(r"^disable-model-invocation:\s*true", fm, re.M) is not None
        dm = re.search(r'^description:\s*"?(.*?)"?\s*$', fm, re.M)
        out[d.name] = {"auto": not dis, "description": dm.group(1) if dm else ""}
    return out


# ---------------------------------------------------------------- isolation
def isolated_env(cfg_dir):
    env = {k: v for k, v in os.environ.items() if k not in DROP_ENV}
    env["CLAUDE_CONFIG_DIR"] = str(cfg_dir)
    env["CLAUDE_CODE_SYNC_SKILLS"] = "0"
    env["CLAUDE_CODE_SYNC_PLUGINS"] = "0"
    # Local login (no env-based auth): carry the credential file into the temp config dir.
    real = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / ".credentials.json"
    if real.is_file():
        dst = Path(cfg_dir) / ".credentials.json"
        shutil.copyfile(real, dst)
        os.chmod(dst, 0o600)
    return env


class Sandbox:
    """Fresh project dir + empty config dir. Use as a context manager."""

    def __init__(self, skills_dir, keep=False):
        WORK.joinpath("tmp").mkdir(parents=True, exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="run-", dir=WORK / "tmp"))
        self.proj = self.root / "proj"
        self.cfg = self.root / "cfg"
        self.cfg.mkdir()
        (self.proj / ".claude").mkdir(parents=True)
        if skills_dir:
            shutil.copytree(skills_dir, self.proj / ".claude" / "skills", ignore=shutil.ignore_patterns("__pycache__"))
        self.keep = keep

    def env(self):
        return isolated_env(self.cfg)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        if not self.keep:
            shutil.rmtree(self.root, ignore_errors=True)


def base_cmd(model, extra=()):
    return [CLAUDE, "--model", model, "--output-format", "stream-json", "--verbose",
            "--no-session-persistence", "--setting-sources", "project", "--strict-mcp-config",
            "--no-chrome", *extra]


def isolation_problems(init_skills, expected):
    """Problems visible in the init event's skill list. Returns (problems, bundled_extras)."""
    probs = []
    missing = [s for s in expected if s not in init_skills]
    if missing:
        probs.append(f"missing from run: {missing}")
    foreign = [s for s in init_skills if ":" in s]
    if foreign:
        probs.append(f"namespaced (plugin/synced) skills visible: {foreign[:5]}")
    extras = [s for s in init_skills if s not in expected and ":" not in s]
    return probs, extras


# ---------------------------------------------------------------- process streaming
def stream_run(cmd, cwd, env, timeout, on_event, stdin_text=None):
    """Run cmd, feed parsed JSON lines to on_event(event) -> True to stop. Returns (reason, stderr_tail).
    reason: 'stopped' | 'exit' | 'timeout'."""
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    try:
        if stdin_text is not None:
            proc.stdin.write(stdin_text.encode())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = []
    threading.Thread(target=lambda: err.append(proc.stderr.read()), daemon=True).start()
    buf, start, reason = b"", time.time(), "exit"
    try:
        while True:
            if time.time() - start > timeout:
                reason = "timeout"
                break
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if not ready:
                if proc.poll() is not None:
                    break
                continue
            chunk = os.read(proc.stdout.fileno(), 65536)
            if not chunk:
                break
            buf += chunk
            stop = False
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if on_event(ev):
                    stop = True
                    break
            if stop:
                reason = "stopped"
                break
    finally:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.wait()
    time.sleep(0.05)
    return reason, (err[0].decode(errors="replace")[-500:] if err else "")


class RateGate:
    """Shared back-off: when one worker hits a limit, all wait."""

    def __init__(self):
        self.until = 0.0
        self.lock = threading.Lock()

    def wait(self):
        while True:
            d = self.until - time.time()
            if d <= 0:
                return
            time.sleep(min(d, 5))

    def trip(self, seconds):
        with self.lock:
            self.until = max(self.until, time.time() + seconds)


GATE = RateGate()


def reset_wait(msg):
    """Seconds until the reset time named in a usage-limit message ('resets 8:40am (Europe/Berlin)'), else None."""
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    m = re.search(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*\(([^)]+)\)", msg, re.I)
    if not m:
        return None
    try:
        tz = ZoneInfo(m.group(4))
    except Exception:
        return None
    h = int(m.group(1)) % 12 + (12 if m.group(3).lower() == "pm" else 0)
    now = datetime.now(tz)
    t = now.replace(hour=h, minute=int(m.group(2) or 0), second=0, microsecond=0)
    if t <= now:
        t += timedelta(days=1)
    return (t - now).total_seconds() + 120


def with_retry(fn, attempts=4, base=60, max_wait=None):
    """fn() -> dict with optional 'error'. Limit-type errors wait (until the stated reset time if given)
    and retry; other errors retry once. With max_wait (seconds), a limit whose reset lies further away
    returns the result with 'limit_abort' set instead of waiting."""
    res, tries, waits = None, 0, 0
    while True:
        GATE.wait()
        res = fn()
        err = res.get("error")
        if not err:
            return res
        if LIMIT_RE.search(err):
            waits += 1
            if waits > 6:
                return res
            wait = min(reset_wait(err) or base * (2 ** min(waits, 5)), 6 * 3600)
            if max_wait is not None and wait > max_wait:
                res["limit_abort"] = True
                return res
            GATE.trip(wait)
            res["retries"] = waits
            continue
        tries += 1
        if tries >= 2:
            return res
        res["retries"] = tries
        time.sleep(5)


# ---------------------------------------------------------------- judge
def run_json_claude(prompt, model="sonnet", timeout=300):
    """One no-tool claude call in an empty isolated dir; returns the result text."""
    with Sandbox(None) as sb:
        cmd = [CLAUDE, "-p", "--model", model, "--output-format", "json", "--tools", "",
               "--no-session-persistence", "--setting-sources", "project", "--strict-mcp-config", "--no-chrome"]
        p = subprocess.run(cmd, cwd=sb.proj, env=sb.env(), input=prompt.encode(), capture_output=True, timeout=timeout)
        out = p.stdout.decode(errors="replace")
        try:
            ev = json.loads(out)
            if ev.get("is_error"):
                return {"error": str(ev.get("result"))[:300]}
            return {"text": ev.get("result", ""), "cost": ev.get("total_cost_usd", 0)}
        except ValueError:
            return {"error": (out + p.stderr.decode(errors="replace"))[-300:]}


def parse_json_block(text):
    m = re.search(r"\{.*\}|\[.*\]", text, re.S)
    if not m:
        raise ValueError("no JSON in judge output")
    return json.loads(m.group(0))


def norm(s):
    """Alphanumerics only, lower case: quotes survive markdown, list markers and quote style."""
    return re.sub(r"[\W_]+", "", s).lower()


def judge(items, pack, model="sonnet"):
    """items: [{'id','desc','negative'}]; pack: dict of named text sections. Returns {id: {...}}."""
    sections = "\n\n".join(f"=== {k} ===\n{v}" for k, v in pack.items())
    lines = "\n".join(f"- id={i['id']}: {i['desc']}" for i in items)
    prompt = (
        "You grade the behaviour of an AI assistant in a recorded session against assertions. "
        "Judge only from the recorded material below. Be strict: partial or implied compliance fails.\n\n"
        f"{sections}\n\n=== ASSERTIONS ===\n{lines}\n\n"
        "Reply with JSON only, no prose and no code fence: "
        '{"verdicts":[{"id":"<id>","pass":true|false,"evidence":"<one verbatim quote of at most 200 characters '
        'copied from the recorded material that supports the verdict; empty string only when the assertion '
        'requires the absence of something>"}]}'
    )
    haystack = norm(" ".join(pack.values()))
    last = None
    for attempt in range(2):
        r = with_retry(lambda: run_json_claude(prompt, model))
        if r.get("error"):
            last = r["error"]
            continue
        try:
            data = parse_json_block(r["text"])
            verdicts = data["verdicts"] if isinstance(data, dict) else data
            out = {}
            for v in verdicts:
                it = next((i for i in items if i["id"] == v.get("id")), None)
                if not it:
                    continue
                ok, ev = bool(v.get("pass")), str(v.get("evidence", ""))
                note = ""
                frags = [norm(x) for x in re.split(r"\.\.\.|…|\[\.\.\.\]", ev) if len(norm(x)) >= 8]
                if ok and ev and not all(f in haystack for f in frags):
                    ok, note = False, "judge evidence quote not found in transcript; verdict rejected"
                if ok and not ev and not it.get("negative"):
                    ok, note = False, "judge gave no evidence quote; verdict rejected"
                out[it["id"]] = {"pass": ok, "evidence": ev[:300], "note": note, "cost": r.get("cost", 0)}
            if any(it["id"] not in out for it in items) and attempt == 0:
                last = "incomplete verdicts"
                continue
            for it in items:
                out.setdefault(it["id"], {"pass": False, "evidence": "", "note": "judge returned no verdict"})
            return out
        except (ValueError, KeyError, TypeError) as e:
            last = f"unparseable judge output: {e}: {r.get('text', '')[:200]}"
    return {i["id"]: {"pass": False, "evidence": "", "note": f"judge failed: {last}"} for i in items}


# ---------------------------------------------------------------- file snapshots / diffs
def tree_state(root):
    st = {}
    for p in sorted(Path(root).rglob("*")):
        rel = p.relative_to(root)
        if rel.parts[0] == ".git" or "__pycache__" in rel.parts or p.is_dir():
            continue
        if rel.parts[0] == ".claude" and rel.parts[1:2] != ("skills",):
            continue
        try:
            st[str(rel)] = p.read_bytes()
        except OSError:
            pass
    return st


def tree_diff(before, after, max_chars=24000):
    parts, changed = [], {"added": [], "modified": [], "deleted": []}
    for f in sorted(set(before) | set(after)):
        a, b = before.get(f), after.get(f)
        if a == b:
            continue
        kind = "added" if a is None else "deleted" if b is None else "modified"
        changed[kind].append(f)
        try:
            ta = (a or b"").decode()
            tb = (b or b"").decode()
        except UnicodeDecodeError:
            parts.append(f"--- {f} (binary, {kind})")
            continue
        d = "".join(difflib.unified_diff(ta.splitlines(True), tb.splitlines(True), f"a/{f}", f"b/{f}", n=2))
        parts.append(d or f"--- {f} ({kind}, empty)")
    text = "\n".join(parts)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n[diff truncated]"
    return text, changed


# ---------------------------------------------------------------- summary files
def update_summary(label, key, value, meta=None):
    d = EVALS / "results" / label
    d.mkdir(parents=True, exist_ok=True)
    f = d / "summary.json"
    with open(d / ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        data = json.loads(f.read_text()) if f.is_file() else {}
        data[key] = value
        data["meta"] = {**data.get("meta", {}), **(meta or {})}
        f.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        (d / "report.md").write_text(render_report(data))
    return d


def pct(n, d):
    return "-" if not d else f"{100 * n / d:.0f}%"


def render_report(data):
    m = data.get("meta", {})
    o = [f"# Eval report: {m.get('label', '?')}", "",
         f"Ref `{m.get('ref', '?')}` ({m.get('sha', '?')[:12]}), model trigger `{m.get('trigger_model', '-')}`, "
         f"scenario `{m.get('scenario_model', '-')}`.", ""]
    t = data.get("trigger")
    if t:
        w = t.get("window", 1)
        o += ["## Trigger", "",
              f"{t['n_runs']} runs ({t['runs_per_query']} per query, window {w}), isolation violations: "
              f"{t['isolation_violations']}, errors: {t['errors']}.", ""]
        if t.get("aborted"):
            o += [f"**Incomplete: {t['aborted']}.**", ""]
        if w > 1:
            o += [f"First call: the first tool call is a Skill call for the expected skill. Within window: the skill "
                  f"loaded within the first {w} tool calls; `Load at` lists the tool-call index of the load "
                  f"(1 = first call).", ""]
        for title, key in (("Train set", "skills"), ("Hold-out set", "holdout_skills")):
            grp = t.get(key)
            if not grp:
                continue
            if t.get("holdout_skills"):
                o += [f"### {title}", ""]
            if w > 1:
                o += ["| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | "
                      "Near-miss: within window | Other firing on should-trigger (within window) |",
                      "|---|---|---|---|---|---|---|"]
            else:
                o += ["| Skill | Should-trigger | Near-miss false trigger | Confusion on should-trigger (other firing) |",
                      "|---|---|---|---|"]
            for s, r in grp.items():
                sh, nm = r["should"], r["near_miss"]
                conf = ", ".join(f"{k} x{v}" for k, v in sorted(sh["confusion"].items(), key=lambda x: -x[1])) or "-"
                if w > 1:
                    wc = ", ".join(f"{k} x{v}" for k, v in sorted(sh["win_confusion"].items(), key=lambda x: -x[1])) or "-"
                    at = Counter(sh["skill_at"])
                    ats = ", ".join(f"{k}: {v}" for k, v in sorted(at.items(), key=lambda x: (x[0] is None, x[0]))) or "-"
                    o.append(f"| {s} | {sh['hits']}/{sh['n']} ({pct(sh['hits'], sh['n'])}) | "
                             f"{sh['win_hits']}/{sh['n']} ({pct(sh['win_hits'], sh['n'])}) | {ats} | "
                             f"{nm['false_hits']}/{nm['n']} ({pct(nm['false_hits'], nm['n'])}) | "
                             f"{nm['win_false_hits']}/{nm['n']} ({pct(nm['win_false_hits'], nm['n'])}) | {wc} |")
                else:
                    o.append(f"| {s} | {sh['hits']}/{sh['n']} ({pct(sh['hits'], sh['n'])}) | "
                             f"{nm['false_hits']}/{nm['n']} ({pct(nm['false_hits'], nm['n'])}) | {conf} |")
            for s in t.get("not_in_ref", []):
                o.append(f"| {s} | n/a (skill not in this ref) | | | | | |" if w > 1 else f"| {s} | n/a (skill not in this ref) | | |")
            o.append("")
        u = t["unrelated"]
        if u["n"]:
            o += [f"Unrelated queries: {u['false_hits']}/{u['n']} fired one of the skills "
                  f"({', '.join(f'{k} x{v}' for k, v in u['by_skill'].items()) or 'none'})"
                  + (f"; within window {u.get('win_false_hits', 0)}/{u['n']}" if w > 1 else "") + ".", ""]
        for k, v in t.get("explicit", {}).items():
            o.append(f"Explicit `/{k}`: loaded {v['hits']}/{v['n']}.")
        o.append("")
    s = data.get("scenarios")
    if s:
        o += ["## Scenarios", "",
              f"{s['n_runs']} runs, isolation violations: {s['isolation_violations']}, errors: {s['errors']}.", "",
              "| Skill | Scenario | Passed / total (all runs) |", "|---|---|---|"]
        for sk, r in s["skills"].items():
            for sc, x in r["scenarios"].items():
                err = f" ({x['errored_runs']} run(s) errored, not counted)" if x.get("errored_runs") else ""
                o.append(f"| {sk} | {sc} | {x['passed']}/{x['total']}{err} |")
            o.append(f"| **{sk}** | all | **{r['passed']}/{r['total']}** |")
        o += ["", "### Failing assertions", ""]
        any_fail = False
        for sk, r in s["skills"].items():
            for sc, x in r["scenarios"].items():
                for a in x["assertions"]:
                    if a["fails"]:
                        any_fail = True
                        o.append(f"- `{sk}/{sc}` **{a['id']}** ({a['fails']}/{a['runs']} failed): {a['desc']}")
                        for ev in a["failure_evidence"][:2]:
                            o.append(f"  - run {ev['run']}: {ev['why']}")
        if not any_fail:
            o.append("None.")
        o.append("")
    return "\n".join(o)


def load_json(path):
    return json.loads(Path(path).read_text())


def short_id(*parts):
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:8]


# ---------------------------------------------------------------- fixtures
FIXTURES = EVALS / "scenarios" / "fixtures"


def run_cmd(cmd, cwd, timeout=60):
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def build_design_project(skills_dir, proj):
    """Scaffold doc-kit's design template (New project steps 3-5 of its SKILL.md) plus the two-spec overlay."""
    kit = Path(skills_dir) / "doc-kit" / "kit"
    shutil.copytree(kit / "templates" / "design", proj, dirs_exist_ok=True)
    shutil.copytree(kit / "tools", proj / "tools", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(kit / "presets" / "design.json", proj / "tools" / "doclint.json")
    shutil.copytree(FIXTURES / "design-project", proj, dirs_exist_ok=True)
    for p in proj.rglob("*.md"):
        if "templates" in p.parts:
            continue
        s = p.read_text()
        s = (s.replace("YYYY-MM-DD", "2026-10-05").replace("<OWNER>", "Jonah")
             .replace("# <Project name>", "# Hollowreach")
             .replace("<One or two sentences: what this is and why.>", "A first-person survival game about scarcity."))
        p.write_text(s)
    conv = proj / "docs" / "CONVENTIONS.md"
    s = conv.read_text()
    s = s.replace("| `MAP` | SYSTEM_MAP.md |\n",
                  "| `MAP` | SYSTEM_MAP.md |\n| `ARC` | design/combat/archery.md |\n| `STA` | design/survival/stamina.md |\n")
    conv.write_text(s)
    rc, table = run_cmd(["python3", "tools/doclint.py", "--map"], proj)
    mp = proj / "docs" / "SYSTEM_MAP.md"
    mp.write_text(mp.read_text().replace("<generated table>", table.strip()))
    rc, out = run_cmd(["python3", "tools/doclint.py"], proj)
    return {"fixture_lint_exit": rc, "fixture_lint_tail": out.strip().splitlines()[-1:] if out.strip() else []}


def build_fixture(fx, skills_dir, proj):
    """fx: {'builder': 'design-project'} and/or {'dir': 'name'} (copied over proj). Returns info dict."""
    info = {}
    if not fx:
        return info
    if fx.get("builder") == "design-project":
        info.update(build_design_project(skills_dir, proj))
    for d in ([fx["dir"]] if isinstance(fx.get("dir"), str) else fx.get("dir", [])):
        shutil.copytree(FIXTURES / d, proj, dirs_exist_ok=True)
    return info
