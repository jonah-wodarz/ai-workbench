#!/usr/bin/env python3
"""UserPromptSubmit hook: name the skill that matches the prompt.

Reads skill-router.json (next to this script, or the path in
SKILL_ROUTER_CONFIG): {"max_skills": 2, "skills": {"<skill>": ["<regex>", ...]}}.
Patterns are case-insensitive. On a match it prints
"Load the `<skill>` skill before answering." for up to max_skills skills,
ranked by the number of matching patterns, then by config order.
Prints nothing when nothing matches. Never fails the session.
"""
import json
import os
import re
import sys

DEFAULT_MAX = 2


def load_config():
    path = os.environ.get("SKILL_ROUTER_CONFIG") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "skill-router.json"
    )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def match_skills(prompt, config):
    limit = int(config.get("max_skills", DEFAULT_MAX))
    hits = []
    for order, (skill, patterns) in enumerate(config.get("skills", {}).items()):
        count = 0
        for pattern in patterns:
            try:
                if re.search(pattern, prompt, re.IGNORECASE):
                    count += 1
            except re.error:
                continue
        if count:
            hits.append((-count, order, skill))
    hits.sort()
    return [skill for _, _, skill in hits[:limit]]


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        prompt = payload.get("prompt") or ""
        skills = match_skills(prompt, load_config())
        out = "".join("Load the `%s` skill before answering.\n" % s for s in skills)
        if out:
            sys.stdout.buffer.write(out.encode("utf-8"))
    except Exception:  # a routing hint must never break the session
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
