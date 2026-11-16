# Skill evals

Tests the skills in `skills/` through the real Claude Code CLI (`claude -p`), Python 3 stdlib only.

- **Trigger test** (`run_trigger.py`): does the right skill load for a realistic query? Queries are in `trigger/queries.json` (8 should-trigger and 3 near-miss per auto-invocable skill, plus unrelated queries and an explicit `/teach` check). Each run stops early: at the first tool call (`--window 1`, default) or, with `--window N`, at the first `Skill` call, after N tool calls or at the final answer. Queries sit in `train` (`should`, `near_miss`) and `holdout` sets.
- **Scenario test** (`run_scenarios.py`): a headless session per scenario in `scenarios/<skill>/<name>.json`, graded by deterministic checks (`checks.py`, regex, files, tool trace, lint) and one LLM-judge call per run.

## Run

```
python3 evals/run_trigger.py   --ref 662e096 --label before     # 3 runs per query, parallel 4, model sonnet
python3 evals/run_scenarios.py --ref 662e096 --label before     # 2 runs per scenario, parallel 3
python3 evals/run_trigger.py   --ref WORKTREE --label after-w4 --window 4 --set all   # window and hold-out set
python3 evals/compare.py before after
```

`--ref` is a git ref or `WORKTREE` (copies the current `skills/`). Skills are always exported to a snapshot under the work directory first (`AIWB_EVAL_WORK`), never read from the live tree. Useful flags: `--skills a,b`, `--limit N`, `--runs N`, `--model`, `--scenarios name,name`.

Trigger flags:

- `--window N` (default 1): a run counts as triggered when the expected skill is loaded within the first N tool calls. The run continues until a `Skill` call, N tool calls or the final answer; the first `Skill` call inside the window decides, else the first call decides. Work requests often start with a look at the project (Bash, Read) before the skill loads, so window 4 gives the fairer rate. Summary and report show both "first call" and "within window" rates plus the tool-call index of each load (`skill_at`, 1 = first call). Window runs execute read-only tool calls in the throwaway project; prompts are denied.
- `--set train|holdout|all` (default train): `train` is the `should`/`near_miss` lists; `holdout` is each skill's `holdout` lists, written before the descriptions were tuned and run only for a final check, never tuned on; `all` runs both and reports them in separate tables.
- A skill that has queries but is missing from the ref (for example a skill added later) is skipped and listed as n/a in the report.

## Output

`results/<label>/summary.json` and `report.md` (commit these); raw transcripts under `results/<label>/raw/` (ignored by git).

## Isolation

Each run uses a fresh project whose `.claude/skills/` holds the snapshot, plus a fresh empty `CLAUDE_CONFIG_DIR`, `CLAUDE_CODE_SYNC_SKILLS=0`, `CLAUDE_CODE_SYNC_PLUGINS=0`, `--setting-sources project` and host project variables removed. Every run checks the init event and counts violations in the summary. Bundled CLI skills (about 23, none sharing a name with these skills) stay visible.

## Limits

A usage limit pauses all workers until the stated reset time. Scenario fixtures derive from the ref under test (design project from doc-kit's design template); a template change can need an overlay update in `scenarios/fixtures/design-project/`.
