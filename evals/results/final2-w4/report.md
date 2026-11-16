# Eval report: final2-w4

Ref `WORKTREE` (WORKTREE), model trigger `sonnet`, scenario `-`.

## Trigger

189 runs (3 per query, window 4), isolation violations: 0, errors: 0.

First call: the first tool call is a Skill call for the expected skill. Within window: the skill loaded within the first 4 tool calls; `Load at` lists the tool-call index of the load (1 = first call).

### Train set

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| doc-kit | 27/27 (100%) | 27/27 (100%) | 1: 27 | 0/9 (0%) | 0/9 (0%) | - |
| handoff | 27/36 (75%) | 29/36 (81%) | 1: 27, 2: 2 | 0/15 (0%) | 0/15 (0%) | tool:Bash x6, other-skill:artifact-diagramming x1 |
| structured-project-docs | 25/33 (76%) | 27/33 (82%) | 1: 25, 2: 2 | 0/15 (0%) | 0/15 (0%) | none x3, doc-kit x3 |

### Hold-out set

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| doc-kit | 12/12 (100%) | 12/12 (100%) | 1: 12 | 0/6 (0%) | 0/6 (0%) | - |
| handoff | 4/12 (33%) | 5/12 (42%) | 1: 4, 2: 1 | 0/6 (0%) | 0/6 (0%) | tool:Bash x4, none x3 |
| structured-project-docs | 8/12 (67%) | 9/12 (75%) | 1: 8, 2: 1 | 0/6 (0%) | 0/6 (0%) | tool:Bash x3 |

