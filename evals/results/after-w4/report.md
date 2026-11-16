# Eval report: after-w4

Ref `WORKTREE` (WORKTREE), model trigger `sonnet`, scenario `-`.

## Trigger

363 runs (3 per query, window 4), isolation violations: 0, errors: 0.

First call: the first tool call is a Skill call for the expected skill. Within window: the skill loaded within the first 4 tool calls; `Load at` lists the tool-call index of the load (1 = first call).

| Skill | Should: first call | Should: within window | Load at | Near-miss: first call | Near-miss: within window | Other firing on should-trigger (within window) |
|---|---|---|---|---|---|---|
| design-capture | 21/24 (88%) | 21/24 (88%) | 1: 21 | 0/9 (0%) | 0/9 (0%) | tool:Bash x3 |
| doc-kit | 24/24 (100%) | 24/24 (100%) | 1: 24 | 0/9 (0%) | 0/9 (0%) | - |
| fair-practice-questions | 22/24 (92%) | 24/24 (100%) | 1: 22, 2: 2 | 0/9 (0%) | 0/9 (0%) | - |
| handoff | 6/24 (25%) | 10/24 (42%) | 1: 6, 2: 4 | 0/9 (0%) | 0/9 (0%) | tool:Bash x11, other-skill:artifact-diagramming x3 |
| interrogate | 24/24 (100%) | 24/24 (100%) | 1: 24 | 0/9 (0%) | 0/9 (0%) | - |
| layered-design-facilitation | 24/24 (100%) | 24/24 (100%) | 1: 24 | 0/9 (0%) | 0/9 (0%) | - |
| playbook | 19/24 (79%) | 22/24 (92%) | 1: 19, 2: 3 | 0/9 (0%) | 0/9 (0%) | tool:Bash x2 |
| report-style | 3/24 (12%) | 6/24 (25%) | 1: 3, 2: 3 | 0/9 (0%) | 0/9 (0%) | tool:Bash x15, none x3 |
| setup-retro | 24/24 (100%) | 24/24 (100%) | 1: 24 | 0/9 (0%) | 0/9 (0%) | - |
| structured-project-docs | 19/24 (79%) | 19/24 (79%) | 1: 19 | 0/9 (0%) | 0/9 (0%) | doc-kit x3, tool:Bash x2 |

Unrelated queries: 0/30 fired one of the skills (none); within window 0/30.

Explicit `/teach`: loaded 3/3.
