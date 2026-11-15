# ai-workbench

Skills, playbooks and tools for working with AI assistants: the results of an ongoing effort to make their output more structured, checkable and repeatable.

The skills use the open `SKILL.md` format, which several agents read (Claude, Claude Code, Codex, Gemini CLI, GitHub Copilot). They were built and tested with Claude; a few steps refer to Claude features (multiple-choice question cards, skill proposal cards, memory) and fall back to plain text elsewhere.

## Contents

| Folder | What it holds |
|---|---|
| [`skills/`](skills/) | Skills, one folder each. `doc-kit` carries scripts and tests, its own changelog and `doc-kit-v*` tags |
| [`playbooks/`](playbooks/) | Repeatable workflows with their run logs |
| [`tools/`](tools/) | doclint configured for this repo's playbook library; `export_public.py` and its deny list |
| [`publish/`](publish/) | Files that exist only in the public bundle repo [`creative-design`](https://github.com/jonah-wodarz/creative-design) |

## Skills

| Skill | Use it to |
|---|---|
| [`interrogate`](skills/interrogate/SKILL.md) | Get questioned in rounds until a plan is decided or a message's core is clear |
| [`layered-design-facilitation`](skills/layered-design-facilitation/SKILL.md) | Run open-ended design through layers L0–L4, top-down by default, with deliberate moves between layers (park, probe, ascend) |
| [`design-capture`](skills/design-capture/SKILL.md) | Turn design talk into specs + decision history that stay consistent |
| [`structured-project-docs`](skills/structured-project-docs/SKILL.md) | Keep project docs a navigable tree of small single-topic files |
| [`playbook`](skills/playbook/SKILL.md) | Capture a workflow as a playbook + run log while figuring it out |
| [`setup-retro`](skills/setup-retro/SKILL.md) | Review the Claude setup: skills, preferences, friction, playbooks ready to promote |
| [`fair-practice-questions`](skills/fair-practice-questions/SKILL.md) | Write practice questions that can't be answered by test-wiseness |
| [`doc-kit`](skills/doc-kit/SKILL.md) | Scaffold and lint a docs project with a config-driven lint (`doclint`); generates the system map page |
| [`handoff`](skills/handoff/SKILL.md) | Build an HTML page in place of a long report: overview, decision brief, explainer |

## Install

- **Claude (web, desktop):** zip a skill folder from `skills/` (`cd skills && zip -r <name>.zip <name>`) and upload it under Settings → Skills. See [package-skill-for-upload](playbooks/package-skill-for-upload.md).
- **Claude Code:** copy a skill folder to `~/.claude/skills/<name>/` (personal) or `.claude/skills/<name>/` (project).
- **Other agents:** most read `SKILL.md` folders from their own skills directory; see the agent's docs.

## Checks

- Playbooks: `python tools/doclint.py` from the repo root (Python 3.7+, standard library only).
- doc-kit: `python -m unittest discover -s skills/doc-kit/tests` (Python 3.8+ for the tests; the lint itself runs on 3.7+). Regression against a copy of the Wayfarer project: `python evals/regression/wayfarer/regression_wayfarer.py <wayfarer-copy> skills/doc-kit`.
- handoff: `python skills/handoff/scripts/build.py <template> skills/handoff/assets/examples/<template>.json --validate` per template; `python skills/handoff/scripts/sync_shared.py --check`.
- Skill folders: `python skills/setup-retro/scripts/check_skills.py skills`.
- Claude Code hooks: `python -m unittest discover -s setup/claude-code/tests`.

## Publishing the design bundle

`python tools/export_public.py <path-to-creative-design-clone>` copies the five design skills and the files in `publish/creative-design/` into the public repo folder and runs every check, including a deny list for personal terms. Skill text stays generic; personal trigger phrases live in the hook router's pattern file.

## Credits

`interrogate` adapts the round-based questioning of [`grilling`](https://github.com/mattpocock/skills) by Matt Pocock (MIT). Several revisions follow ideas from his `writing-for-agents` and `wayfinder` skills.

## License

[MIT](LICENSE). Third-party ideas credited above remain under their own licenses.
