"""End-to-end check: real `claude -p` run with both hooks wired (stdlib only).

Builds a temp project with a fixture skill, a fixture CONVENTIONS.md and
.claude/settings.json, runs the CLI on haiku and reads the stream-json events.
Passes when (1) the SessionStart hook output is in the events, (2) the router
line appears for a matching prompt, (3) the model calls the Skill tool for the
fixture skill. Needs the `claude` CLI and network access; costs a few cents.

Run: python setup/claude-code/tests/e2e_check.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.abspath(os.path.join(HERE, "..", "hooks")).replace("\\", "/")
SKILL = "zebra-fixture"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build(root):
    write(os.path.join(root, "docs", "CONVENTIONS.md"),
          "# Conventions\n\n## Skills in use\n\n| When | Skill |\n|---|---|\n"
          "| Fixture work | `%s` |\n\n## Other\n" % SKILL)
    write(os.path.join(root, ".claude", "skills", SKILL, "SKILL.md"),
          "---\nname: %s\ndescription: Fixture skill for hook tests.\n---\n"
          "Begin your answer with ZEBRA-LOADED.\n" % SKILL)
    hook = lambda name: [{"hooks": [{"type": "command", "command": "python",
                                     "args": ["%s/%s" % (HOOKS, name)], "timeout": 10}]}]
    write(os.path.join(root, ".claude", "settings.json"), json.dumps(
        {"hooks": {"SessionStart": hook("skills-in-use.py"),
                   "UserPromptSubmit": hook("skill-router.py")}}, indent=2))


def events(root, prompt):
    proc = subprocess.run(
        ["claude", "-p", prompt, "--model", "haiku", "--output-format", "stream-json",
         "--verbose"], cwd=root, stdin=subprocess.DEVNULL, capture_output=True, timeout=180)
    return [json.loads(x) for x in proc.stdout.decode("utf-8").splitlines() if x.startswith("{")]


def hook_out(evs, event):
    return [e.get("stdout", "") for e in evs
            if e.get("subtype") == "hook_response" and e.get("hook_event") == event]


def main():
    with tempfile.TemporaryDirectory() as root:
        build(root)
        evs = events(root, "grill me briefly on the fixture work, then say hello.")
    session = "".join(hook_out(evs, "SessionStart"))
    router = "".join(hook_out(evs, "UserPromptSubmit"))
    skills = [c["input"].get("skill") for e in evs if e.get("type") == "assistant"
              for c in e["message"]["content"] if c.get("type") == "tool_use" and c["name"] == "Skill"]
    checks = {
        "SessionStart output carries the fixture skill": SKILL in session,
        "router names interrogate": "Load the `interrogate` skill before answering." in router,
        "model calls the Skill tool for the fixture skill": SKILL in skills,
    }
    for name, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
