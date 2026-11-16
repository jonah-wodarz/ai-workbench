# Skill-trigger setup

Skills load reliably when a file or hook names them. Descriptions alone trigger unreliably.

| File | Purpose | Surface |
|---|---|---|
| `pointer-block.md` | Paste-ready text: harness location, language rule, "Skills in use" instruction | Cowork / claude.ai (Settings, project instructions); Claude Code (`~/.claude/CLAUDE.md`) |
| `claude-code/hooks/skills-in-use.py` | SessionStart: prints the `## Skills in use` table of `docs/CONVENTIONS.md` | Claude Code |
| `claude-code/hooks/skill-router.py` + `skill-router.json` | UserPromptSubmit: names up to two skills whose regex matches the prompt | Claude Code |
| `claude-code/settings.example.json` | `hooks` block wiring both scripts | Claude Code |
| `claude-code/tests/` | `test_hooks.py` (unit), `e2e_check.py` (real `claude -p` run) | Claude Code |

## Install: Claude Code

1. Clone `ai-workbench`; the scripts run from the clone.
2. Merge `settings.example.json` into `~/.claude/settings.json` (all projects) or `.claude/settings.json` (one project).
3. Replace `/ABSOLUTE/PATH/TO/ai-workbench` with the clone path. On Windows use forward slashes (`C:/Users/...`).
4. Set `command` to `python` on Windows and usually on Linux; use `python3` where only that exists (macOS, many Linux distributions).
5. Put the `## Skills in use` table at the top of each project's `docs/CONVENTIONS.md` (template: `skills/doc-kit/kit/templates/design/docs/CONVENTIONS.md`).
6. Edit `skill-router.json` to tune patterns; `SKILL_ROUTER_CONFIG` points to another file.

Run the tests from the repo root:

```
python -m unittest discover -s setup/claude-code/tests -v
python setup/claude-code/tests/e2e_check.py
```

## Install: Cowork / claude.ai

Hooks do not exist there. Paste block (a) and block (b) of `pointer-block.md` into Settings, personal preferences, and block (c) into each project's instructions. Keep the `Skills in use` table in the project's `docs/CONVENTIONS.md`.

## Limits

Hooks guarantee that the skill name reaches the model, not that the model loads the skill. In the end-to-end check (haiku, single runs) the model called the Skill tool for the named fixture skill. The router matches wording only; paraphrases without a pattern stay silent.

Hook schema: https://code.claude.com/docs/en/hooks (checked 2026-11-14).
