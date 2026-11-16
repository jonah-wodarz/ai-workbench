# Eval report: before

Ref `662e096` (662e096c880c), model trigger `sonnet`, scenario `sonnet`.

## Trigger

330 runs (3 per query), isolation violations: 0, errors: 0.

| Skill | Should-trigger | Near-miss false trigger | Confusion on should-trigger (other firing) |
|---|---|---|---|
| design-capture | 22/24 (92%) | 0/9 (0%) | tool:Bash x2 |
| doc-kit | 24/24 (100%) | 0/9 (0%) | - |
| fair-practice-questions | 24/24 (100%) | 0/9 (0%) | - |
| interrogate | 24/24 (100%) | 0/9 (0%) | - |
| layered-design-facilitation | 24/24 (100%) | 0/9 (0%) | - |
| playbook | 24/24 (100%) | 0/9 (0%) | - |
| report-style | 6/24 (25%) | 0/9 (0%) | tool:Bash x15, none x3 |
| setup-retro | 24/24 (100%) | 0/9 (0%) | - |
| structured-project-docs | 18/24 (75%) | 0/9 (0%) | tool:Bash x3, doc-kit x3 |

Unrelated queries: 0/30 fired one of the skills (none).

Explicit `/teach`: loaded 3/3.

## Scenarios

36 runs, isolation violations: 0, errors: 4.

| Skill | Scenario | Passed / total (all runs) |
|---|---|---|
| design-capture | conflict-quote | 14/16 |
| design-capture | tiers-history-rename | 14/16 |
| **design-capture** | all | **28/32** |
| doc-kit | new-design-project | 16/16 |
| **doc-kit** | all | **16/16** |
| fair-practice-questions | list-n-chain | 10/14 |
| fair-practice-questions | mc-set-german | 16/16 |
| **fair-practice-questions** | all | **26/30** |
| interrogate | articulate-mode | 11/14 |
| interrogate | decide-mode | 10/14 |
| **interrogate** | all | **21/28** |
| layered-design-facilitation | jump-ahead | 10/16 |
| layered-design-facilitation | open-new-system | 10/14 |
| **layered-design-facilitation** | all | **20/30** |
| playbook | follow-existing | 0/0 (2 run(s) errored, not counted) |
| playbook | new-workflow | 0/0 (2 run(s) errored, not counted) |
| **playbook** | all | **0/0** |
| report-style | bluf-summary | 12/16 |
| report-style | work-summary | 14/16 |
| **report-style** | all | **26/32** |
| setup-retro | inventory-classify | 15/16 |
| setup-retro | playbooks-and-stale | 10/12 |
| **setup-retro** | all | **25/28** |
| structured-project-docs | new-tree | 12/16 |
| structured-project-docs | split-monolith | 11/16 |
| **structured-project-docs** | all | **23/32** |
| teach | first-session | 12/12 |
| **teach** | all | **12/12** |

### Failing assertions

- `design-capture/conflict-quote` **records-nonconflicting** (1/2 failed): The armour decision is written into the archery spec as a numbered rule.
  - run 1: pattern 'ARC-R[4-9]\\*\\*[^\\n]*(break|heavy armour)' not found
- `design-capture/conflict-quote` **reply-shape** (1/2 failed): The reply has four parts in order: a one-line state (system, layer, status), the rules recorded by ID with their text, reversals and conflicts, and what is needed from the user as questions sized to one decision.
  - run 2: **State:** Archery · L2 · drafting. Stamina · L1 · idea. The lint is clean.
- `design-capture/tiers-history-rename` **no-raw-numbers** (1/2 failed): The archery spec carries none of the raw draw times (0.8, 1.2).
  - run 2: unwanted text present: '0.8'
- `design-capture/tiers-history-rename` **numbers-parked** (1/2 failed): The raw draw times are parked for L3.
  - run 2: pattern '0\\.8|1\\.2' not found
- `fair-practice-questions/list-n-chain` **no-leak** (2/2 failed): No task, option, hint or visible explanation reveals the answer to another task.
  - run 1: Nur SERIALIZABLE verhindert Phantom Reads. Alle drei schwächeren Levels erlauben sie nach der Standarddefinition.
  - run 2: Task 2 solution c) says 'Strict 2PL garantiert Serialisierbarkeit und Kaskadenfreiheit', and Task 4 stem mentions 'Wait-for-Graph' and 'Deadlock-Erkennung' hints; Task 3 option D is thus revealed.
- `fair-practice-questions/list-n-chain` **chain-self-contained** (1/2 failed): Task 4 builds on task 2 without stating task 2's answer in its stem; it is self-contained or applies the mechanism to a new case.
  - run 2: a) ... begründen Sie, ob sich der Wait-for-Graph hier zyklisch verhalten kann. (5 Punkte)
- `fair-practice-questions/list-n-chain` **hint-safe** (1/2 failed): Any hint narrows the reasoning without naming the answer or ruling out all but one option by form.
  - run 1: judge gave no evidence quote; verdict rejected
- `interrogate/articulate-mode` **no-recommendation** (1/2 failed): No question carries a recommended answer or a pick; the assistant does not favour one framing.
  - run 1: Examples might be reply with a yes or no, book a meeting, or give feedback on the idea. Which is closest, or is it something else?
- `interrogate/articulate-mode` **max-four** (2/2 failed): At most 4 questions in the round, one concept per question, none depending on another in the same round.
  - run 1: Is there a deadline, such as a registration date, the semester or an exam office rule? Do you know if she's the right person for this topic, or is that part of what you're unsure about?
  - run 2: **Constraints:** Please tell me any that apply.
   - Language (German or English)
   - Deadline, such as when you need to register the thesis or start writing
- `interrogate/decide-mode` **max-four** (2/2 failed): The first round asks at most 4 questions, and none of them depends on the answer to another in the same round.
  - run 1: If you pick b, I'll need to ask about a repeatable import. If you pick a, I'll skip it.
  - run 2: Where will you read the notes?
   - Options: VS Code or Obsidian locally, the GitHub web view, or a generated site.
- `interrogate/decide-mode` **recommendations** (2/2 failed): Each question carries a recommended answer, listed first, phrased so that 'yes' accepts it.
  - run 1: a) A new git repo in this folder, with the export moved into a clean structure (recommended)
  - run 2: Rendering: Where will you read the notes? - Options: VS Code or Obsidian locally, the GitHub web view, or a generated site.
- `layered-design-facilitation/jump-ahead` **offers-moves** (1/2 failed): The reply offers both park and probe.
  - run 2: pattern '(?=[\\s\\S]*\\bpark)(?=[\\s\\S]*\\bprobe)' not found
- `layered-design-facilitation/jump-ahead` **ordering** (1/2 failed): The tool ratings are restated as an ordering (crowbar above picks above bump key above drill, or equivalent) and the user is asked to confirm, with the raw ratings parked for L3.
  - run 2: **Ordering:** crowbar above picks, above bump key, above drill. "Higher is better" didn't say better at what
- `layered-design-facilitation/jump-ahead` **ideas-first** (2/2 failed): The reply asks for the user's ideas about the system before offering any proposals of its own, and offers no design proposals itself.
  - run 1: a crowbar ranking best at lockpicking is unusual. It might fit a loud, brute-force pillar, or it might mean the crowbar is a different kind of tool.
  - run 2: For example, a lock might exist to create a tense moment when the plan fails, or to be a puzzle in the plan itself.
- `layered-design-facilitation/jump-ahead` **one-decision-questions** (2/2 failed): Every question in the reply asks for a single decision answerable in a sentence or by choosing among named options.
  - run 1: Park the numbers, or probe them now as trial values to see how they feel?
  - run 2: Does the layer model above work for you, or would you change it? If you'd rather skip the scene and settle the layers first, say so.
- `layered-design-facilitation/open-new-system` **few-questions** (2/2 failed): At most 4 question marks in the reply.
  - run 1: count of '\\?' = 6 (allowed 0..4)
  - run 2: count of '\\?' = 5 (allowed 0..4)
- `layered-design-facilitation/open-new-system` **open-questions** (1/2 failed): Questions at this layer are open (about intent or feeling), not multiple-choice numeric options, and each asks for one decision.
  - run 1: For example: tension, panic, a decision about whether to push on or bail, or something else.
- `layered-design-facilitation/open-new-system` **confirms-shape** (1/2 failed): The reply asks the user to confirm or adjust the proposed layer shape before going on.
  - run 2: That's the standard five-layer stack. Heat is small enough to use all five without merging any. We'll go top-down and announce every layer change
- `report-style/bluf-summary` **one-term** (2/2 failed): Each concept has one term throughout (for example the same word for the cache policies, for the delay measure and for memory use).
  - run 1: Memory is taken as the per-node figure in `results.csv` (unverified: the file does not state the unit's scope).
  - run 2: Memory budget / "Memory (MB)" column vs "needs 768 MB"; "p95 latency" vs "fastest (42 ms)"; also "policy" vs "policies" fine, but "the slowest of the three" and "fastest" shift away from latency term.
- `report-style/bluf-summary` **takeaway** (2/2 failed): After the table, one sentence states its takeaway without repeating the table's rows.
  - run 1: arc has the best hit rate and a better p95 than lfu, but it needs 68 MB more than the budget allows. That rules it out at 700 MB.
  - run 2: | arc | 86.2 | 44 | 768 | **no** (68 MB over) |

## Reasoning
- `report-style/work-summary` **next-steps** (2/2 failed): The summary ends with next steps.
  - run 1: pattern 'next steps?' not found
  - run 2: pattern 'next steps?' not found
- `setup-retro/inventory-classify` **uses-categories** (1/2 failed): Findings are classified with the retro's categories (for example Negation-only rule, No-op, Trigger, Overlap, Steering bloat, Mechanical rule in prose) and each has a cheapest fix.
  - run 2: | 2026-10-08 | doc-kit | "run the lint" again | Mechanical rule in prose | Three skills say "run the lint" (doc-kit, design-capture 0, structured-project-docs).
- `setup-retro/playbooks-and-stale` **lists-all** (1/2 failed): Every playbook is listed with its status, runs and last_run.
  - run 2: Playbook `ocr-scans` | promote | medium | It is `current` with 4 runs, and its steps have been unchanged since run 2.
- `setup-retro/playbooks-and-stale` **promotion-path** (1/2 failed): The promotion path is stated: the skill is drafted from the playbook's steps and the run log's gotchas after the user agrees, and the playbook then becomes deprecated with a link to the skill. The assistant does not promote on its own.
  - run 2: Promote `ocr-scans` to a skill, or turn it into a script?
- `structured-project-docs/new-tree` **proposal-first** (2/2 failed): Before creating files, the assistant proposes the tree and says why it fits this project.
  - run 1: Scaffold and lint config are in place. Next I'm writing the thesis-specific entry files and folder indexes.
  - run 2: Setting up the thesis docs tree. I'm restoring two templates I removed by mistake, then filling in the map and running the lint.
- `structured-project-docs/new-tree` **sized** (1/2 failed): Every created folder holds real content (no empty folders or near-empty files).
  - run 2: empty dirs: ['docs/chapters', 'docs/experiments', 'docs/literature', 'docs/playbooks', 'docs/playbooks/runs']; near-empty files: []
- `structured-project-docs/new-tree` **kebab** (1/2 failed): Added Markdown files use kebab-case names (entry files may be upper case).
  - run 1: 15 added; not kebab-case: ['docs/chapters/INDEX.md', 'docs/experiments/INDEX.md', 'docs/literature/INDEX.md']
- `structured-project-docs/split-monolith` **proposal-first** (2/2 failed): Before moving any content, the assistant states the target file tree and the reasoning for it in its text.
  - run 1: Notes.md is small (22 lines), so I'm using a light tree. The two release rules contradict each other, and the 2026-10-07 ruling is newer, so it wins. I'm writing the files now.
  - run 2: Reorganizing is nearly done: the lint reports 0 errors. I'm removing the old `notes.md` (everything in it now lives in the new files), then generating the map and re-running the lint.
- `structured-project-docs/split-monolith` **links-resolve** (1/2 failed): Every relative Markdown link in the tree resolves to an existing file.
  - run 2: 28 links, broken: ['docs/templates/playbook.md -> runs/<file>.md', 'docs/templates/run-log.md -> ../<file>.md']
- `structured-project-docs/split-monolith` **single-topic** (2/2 failed): Each resulting file covers one distinct topic with a descriptive name.
  - run 1: judge evidence quote not found in transcript; verdict rejected `docs/setup.md`, `docs/architecture.md`, `docs/troubleshooting.md`, `docs/release-process.md`, `docs/decisions/` one record per meeting decision
  - run 2: judge evidence quote not found in transcript; verdict rejected `docs/guides/setup.md` | Setup steps; `docs/guides/troubleshooting.md` | Expired session and stalled downloads; `docs/product/release-process.md` | No releases on Fridays
