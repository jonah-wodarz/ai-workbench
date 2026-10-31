# ai-workbench

Skills, playbooks and tools for working with AI assistants: the results of an ongoing effort to make their output more structured, checkable and repeatable.

The skills use the open `SKILL.md` format, which several agents read (Claude, Claude Code, Codex, Gemini CLI, GitHub Copilot). They were built and tested with Claude; a few steps refer to Claude features (multiple-choice question cards, skill proposal cards, memory) and fall back to plain text elsewhere.

## Contents

| Folder | What it holds |
|---|---|
| [`skills/`](skills/) | Skills, one folder each. `doc-kit` carries scripts and tests, its own changelog and `doc-kit-v*` tags |
| [`playbooks/`](playbooks/) | Repeatable workflows with their run logs |
| [`tools/`](tools/) | doclint configured for this repo's playbook library |

## Skills

| Skill | Use it to |
|---|---|
| [`interrogate`](skills/interrogate/SKILL.md) | Get questioned in rounds until a plan is decided or a message's core is clear |
| [`layered-design-facilitation`](skills/layered-design-facilitation/SKILL.md) | Run open-ended design top-down through layers L0–L4, parking premature detail |
| [`design-capture`](skills/design-capture/SKILL.md) | Turn design talk into specs + decision history that stay consistent |
| [`structured-project-docs`](skills/structured-project-docs/SKILL.md) | Keep project docs a navigable tree of small single-topic files |
| [`report-style`](skills/report-style/SKILL.md) | Write deliverables bottom-line-first with consistent terms and fitting visuals |
| [`playbook`](skills/playbook/SKILL.md) | Capture a workflow as a playbook + run log while figuring it out |
| [`setup-retro`](skills/setup-retro/SKILL.md) | Review the Claude setup: skills, preferences, friction, playbooks ready to promote |
| [`fair-practice-questions`](skills/fair-practice-questions/SKILL.md) | Write practice questions that can't be answered by test-wiseness |
| [`doc-kit`](skills/doc-kit/SKILL.md) | Scaffold and lint a docs project with a config-driven lint (`doclint`) |

## Install

- **Claude (web, desktop):** zip a skill folder from `skills/` (`cd skills && zip -r <name>.zip <name>`) and upload it under Settings → Skills. See [package-skill-for-upload](playbooks/package-skill-for-upload.md).
- **Claude Code:** copy a skill folder to `~/.claude/skills/<name>/` (personal) or `.claude/skills/<name>/` (project).
- **Other agents:** most read `SKILL.md` folders from their own skills directory; see the agent's docs.

## Checks

- Playbooks: `python tools/doclint.py` from the repo root (Python 3.7+, standard library only).
- doc-kit: `python -m unittest discover -s skills/doc-kit/tests`.

## Credits

`interrogate` adapts the round-based questioning of [`grilling`](https://github.com/mattpocock/skills) by Matt Pocock (MIT). Several revisions follow ideas from his `writing-for-agents` and `wayfinder` skills.
