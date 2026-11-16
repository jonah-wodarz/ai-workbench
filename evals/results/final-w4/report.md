# Eval report: final-w4

Ref `WORKTREE` (WORKTREE), model trigger `sonnet`, scenario `-`.

## Trigger

153 runs (3 per query, window 4), isolation violations: 0, errors: 0.

First call: the first tool call is a Skill call for the expected skill. Within window: the skill loaded within the first 4 tool calls; `Load at` lists the tool-call index of the load (1 = first call).

### Train set

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| design-capture | 24/24 (100%) | 24/24 (100%) | 1: 24 | 0/9 (0%) | 0/9 (0%) | - |
| handoff | 23/24 (96%) | 23/24 (96%) | 1: 23 | 0/9 (0%) | 0/9 (0%) | tool:Artifact x1 |
| structured-project-docs | 18/24 (75%) | 18/24 (75%) | 1: 18 | 0/9 (0%) | 0/9 (0%) | doc-kit x3, none x3 |

### Hold-out set

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| design-capture | 12/12 (100%) | 12/12 (100%) | 1: 12 | 0/6 (0%) | 0/6 (0%) | - |
| handoff | 6/12 (50%) | 6/12 (50%) | 1: 6 | 0/6 (0%) | 0/6 (0%) | tool:Bash x6 |
| structured-project-docs | 8/12 (67%) | 8/12 (67%) | 1: 8 | 0/6 (0%) | 0/6 (0%) | none x3, tool:Bash x1 |

