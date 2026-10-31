# claude-workbench

Skills, playbooks and tools for working with Claude: the results of an ongoing effort to make Claude's output more structured, checkable and repeatable.

## Contents

| Folder | What it holds |
|---|---|
| [`skills/`](skills/) | Claude skills, one folder each |
| [`playbooks/`](playbooks/) | Repeatable workflows with their run logs |
| [`doc-kit/`](doc-kit/) | Config-driven docs lint (`doclint`), presets and templates; also a skill. Own changelog and `doc-kit-v*` tags |
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
| [`doc-kit`](doc-kit/SKILL.md) | Scaffold and lint a docs project |

## Install

- **Claude (web, desktop):** single-file skills: Settings → Skills → create from the SKILL.md. Skills with extra files (doc-kit): zip the folder (`zip -r doc-kit.zip doc-kit -x 'doc-kit/.git/*'`) and upload it. See [package-skill-for-upload](playbooks/package-skill-for-upload.md).
- **Claude Code:** copy a skill folder to `~/.claude/skills/<name>/` (personal) or `.claude/skills/<name>/` (project).

## Checks

- Playbooks: `python tools/doclint.py` from the repo root (Python 3.7+, standard library only).
- doc-kit: `python -m unittest discover -s doc-kit/tests`.

## Credits

`interrogate` adapts the round-based questioning of [`grilling`](https://github.com/mattpocock/skills) by Matt Pocock (MIT). Several revisions follow ideas from his `writing-for-agents` and `wayfinder` skills.
