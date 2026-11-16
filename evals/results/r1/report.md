# Eval report: r1

Ref `WORKTREE` (WORKTREE), model trigger `sonnet`, scenario `-`.

## Trigger

108 runs (2 per query, window 4), isolation violations: 0, errors: 0.

**Incomplete: usage limit reached; partial results.**

First call: the first tool call is a Skill call for the expected skill. Within window: the skill loaded within the first 4 tool calls; `Load at` lists the tool-call index of the load (1 = first call).

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| design-capture | 16/16 (100%) | 16/16 (100%) | 1: 16 | 0/6 (0%) | 0/6 (0%) | - |
| doc-kit | 16/16 (100%) | 16/16 (100%) | 1: 16 | 0/6 (0%) | 0/6 (0%) | - |
| handoff | 14/16 (88%) | 16/16 (100%) | 1: 14, 2: 2 | 0/6 (0%) | 0/6 (0%) | - |
| report-style | 8/16 (50%) | 10/16 (62%) | 1: 8, 2: 2 | 0/6 (0%) | 0/6 (0%) | tool:Bash x4, none x2 |
| structured-project-docs | 14/16 (88%) | 14/16 (88%) | 1: 14 | 0/4 (0%) | 0/4 (0%) | doc-kit x2 |

