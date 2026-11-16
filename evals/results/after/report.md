# Eval report: after

Ref `WORKTREE` (WORKTREE), model trigger `sonnet`, scenario `sonnet`.

## Trigger

363 runs (3 per query), isolation violations: 0, errors: 0.

| Skill | Should-trigger | Near-miss false trigger | Confusion on should-trigger (other firing) |
|---|---|---|---|
| design-capture | 21/24 (88%) | 0/9 (0%) | tool:Bash x3 |
| doc-kit | 24/24 (100%) | 0/9 (0%) | - |
| fair-practice-questions | 24/24 (100%) | 0/9 (0%) | - |
| handoff | 7/24 (29%) | 0/9 (0%) | tool:Bash x14, tool:Artifact x3 |
| interrogate | 24/24 (100%) | 0/9 (0%) | - |
| layered-design-facilitation | 24/24 (100%) | 0/9 (0%) | - |
| playbook | 20/24 (83%) | 0/9 (0%) | tool:Bash x4 |
| report-style | 1/24 (4%) | 0/9 (0%) | tool:Bash x20, none x3 |
| setup-retro | 24/24 (100%) | 0/9 (0%) | - |
| structured-project-docs | 20/24 (83%) | 0/9 (0%) | doc-kit x3, tool:Bash x1 |

Unrelated queries: 0/30 fired one of the skills (none).

Explicit `/teach`: loaded 3/3.

## Scenarios

36 runs, isolation violations: 0, errors: 0.

| Skill | Scenario | Passed / total (all runs) |
|---|---|---|
| design-capture | conflict-quote | 14/16 |
| design-capture | tiers-history-rename | 16/16 |
| **design-capture** | all | **30/32** |
| doc-kit | new-design-project | 16/16 |
| **doc-kit** | all | **16/16** |
| fair-practice-questions | list-n-chain | 14/15 |
| fair-practice-questions | mc-set-german | 13/16 |
| **fair-practice-questions** | all | **27/31** |
| interrogate | articulate-mode | 11/14 |
| interrogate | decide-mode | 6/14 |
| **interrogate** | all | **17/28** |
| layered-design-facilitation | jump-ahead | 8/16 |
| layered-design-facilitation | open-new-system | 13/14 |
| **layered-design-facilitation** | all | **21/30** |
| playbook | follow-existing | 12/16 |
| playbook | new-workflow | 14/16 |
| **playbook** | all | **26/32** |
| report-style | bluf-summary | 12/16 |
| report-style | work-summary | 14/16 |
| **report-style** | all | **26/32** |
| setup-retro | inventory-classify | 15/16 |
| setup-retro | playbooks-and-stale | 10/12 |
| **setup-retro** | all | **25/28** |
| structured-project-docs | new-tree | 10/16 |
| structured-project-docs | split-monolith | 12/16 |
| **structured-project-docs** | all | **22/32** |
| teach | first-session | 12/12 |
| **teach** | all | **12/12** |

### Failing assertions

- `design-capture/conflict-quote` **reply-shape** (2/2 failed): The reply has four parts in order: a one-line state (system, layer, status), the rules recorded by ID with their text, reversals and conflicts, and what is needed from the user as questions sized to one decision.
  - run 1: **State:** Archery · L2 · drafting. Stamina · L1 · idea. The lint passes with 0 errors and 0 warnings.
  - run 2: **State:** Archery · L2 · drafting, and Stamina · L1 · idea. The lint passes with 0 errors and 0 warnings.
- `fair-practice-questions/list-n-chain` **no-leak** (1/2 failed): No task, option, hint or visible explanation reveals the answer to another task.
  - run 1: Task 2 option D's solution text states: "Das Phänomen heißt **Non-repeatable Read**" is only in solutions; but Task 4 stem says "Alle Sperren werden bis `COMMIT` oder `ROLLBACK` gehalten" and Task 3 lists S/S, IS/S compatible
- `fair-practice-questions/mc-set-german` **no-spoilers** (1/2 failed): No question stem, option or visible hint reveals the answer to another question.
  - run 1: Sicherungsschicht (Schicht 2), die Rahmen über physische Adressen zustellt
- `fair-practice-questions/mc-set-german` **no-verbal-echo** (2/2 failed): No distinctive word from a stem appears only in the correct option, and no stem agrees grammatically with only one option.
  - run 1: Die Ziel-MAC-Adresse im Ethernet-Header des Frames
  - run 2: B) UDP, weil kein Warten auf Neuübertragungen die Verzögerung gering hält
- `interrogate/articulate-mode` **maps-the-tree** (1/2 failed): The questions cover at least three of: intent, audience, the one key point, what the reader should do or think afterwards, constraints (tone, length, channel).
  - run 2: 3. **The ask:** What do you want from this first email?
- `interrogate/articulate-mode` **max-four** (2/2 failed): At most 4 questions in the round, one concept per question, none depending on another in the same round.
  - run 1: Also, what does "frameworks" mean here? Are you thinking of conceptual or process models, software or tooling frameworks, or an evaluation framework?
  - run 2: 2. **Topic stage:** How developed is "frameworks for AI-assisted design work" right now?
- `interrogate/decide-mode` **names-mode** (2/2 failed): The first round names the mode (Decide).
  - run 1: pattern '\\bdecide\\b' not found
  - run 2: pattern '\\bdecide\\b' not found
- `interrogate/decide-mode` **max-four** (2/2 failed): The first round asks at most 4 questions, and none of them depends on the answer to another in the same round.
  - run 1: Should I keep one file per subject ... and move them to `notes/<subject>.md`, with images in `notes/images/`? Or do you want a different structure
  - run 2: **Where should the repo live?** I recommend turning this project directory into the repo, with `git init` here and the notes at the top level.
- `interrogate/decide-mode` **recommendations** (2/2 failed): Each question carries a recommended answer, listed first, phrased so that 'yes' accepts it.
  - run 1: *(Recommended: yes, `git init` here.)*
  - run 2: Alternatives are a flat `notes/` folder with a shared `images/` folder (the current layout), or a layout by course or semester. Which one?
- `interrogate/decide-mode` **no-discoverable-facts** (1/2 failed): No question asks for something visible in the export (number of notebooks, whether images exist, file format).
  - run 1: Should this be a new git repo, with the current folder as its root? The folder isn't a git repo yet.
- `interrogate/decide-mode` **judgments-only** (1/2 failed): The questions are judgments or preferences (for example sync, search, image handling, structure), not fact lookups.
  - run 1: Should this be a new git repo, with the current folder as its root? The folder isn't a git repo yet.
- `layered-design-facilitation/jump-ahead` **offers-moves** (2/2 failed): The reply offers both park and probe.
  - run 1: pattern '(?=[\\s\\S]*\\bpark)(?=[\\s\\S]*\\bprobe)' not found
  - run 2: pattern '(?=[\\s\\S]*\\bpark)(?=[\\s\\S]*\\bprobe)' not found
- `layered-design-facilitation/jump-ahead` **ordering** (2/2 failed): The tool ratings are restated as an ordering (crowbar above picks above bump key above drill, or equivalent) and the user is asked to confirm, with the raw ratings parked for L3.
  - run 1: **Tool ranking:** crowbar > picks > bump key > drill. I need to know what "better" means here.
  - run 2: Tool ordering: crowbar > picks > bump key > drill. I need to check what the axis is. Is it overall effectiveness, or something narrower like speed or reliability?
- `layered-design-facilitation/jump-ahead` **ideas-first** (2/2 failed): The reply asks for the user's ideas about the system before offering any proposals of its own, and offers no design proposals itself.
  - run 1: **Proposed layers** (the default stack, in your game's terms):
  - run 2: Proposed layers for this game
- `layered-design-facilitation/jump-ahead` **one-decision-questions** (2/2 failed): Every question in the reply asks for a single decision answerable in a sentence or by choosing among named options.
  - run 1: Does that fit, or do you want to add or rename layers?
  - run 2: Do you want to use this layer model? If you'd rather stay on lockpicking, tell me and I'll note it as an override.
- `layered-design-facilitation/open-new-system` **confirms-shape** (1/2 failed): The reply asks the user to confirm or adjust the proposed layer shape before going on.
  - run 1: Heat starts at **L0**. Anything about numbers, meters or specific police behavior goes in the parking lot until we descend. I'll flag it if I drift, and you can flag me too.
- `playbook/follow-existing` **reads-first** (2/2 failed): The existing playbook was read before convert.py was first run.
  - run 1: index first=1 then=1
  - run 2: index first=1 then=1
- `playbook/follow-existing` **first-try-right** (2/2 failed): The first convert.py call already has OUT_DIR and the encoding flag.
  - run 1: first convert call: cd /home/claude/run/work/evals/tmp/run-b2z5antl/proj; ls docs/playbooks docs/playbooks/runs docs/templates tools data out 2>&1; head -5 data/export.csv; sed -n
  - run 2: first convert call: cd /home/claude/run/work/evals/tmp/run-0ibniq3o/proj; ls docs/playbooks docs/playbooks/runs docs/templates tools data out 2>&1; head -5 data/export.csv; sed -n
- `playbook/new-workflow` **generalized** (2/2 failed): The playbook uses placeholders instead of this run's file name.
  - run 1: pattern '<[a-z_-]+>' not found
  - run 2: pattern '<[a-z_-]+>' not found
- `report-style/bluf-summary` **one-term** (2/2 failed): Each concept has one term throughout (for example the same word for the cache policies, for the delay measure and for memory use).
  - run 1: Memory use is labeled "Memory per node (MB)" in the table, "700 MB memory budget" in the lead, and "budget" elsewhere; latency is "p95 latency" throughout but "faster" is used in trade-offs.
  - run 2: The 1.3-point gap between arc and lfu may be within run-to-run noise (unverified).
- `report-style/bluf-summary` **takeaway** (2/2 failed): After the table, one sentence states its takeaway without repeating the table's rows.
  - run 1: *Table: benchmark results per eviction policy. Lower is better for latency and memory, higher for hit rate.*
  - run 2: Hit rate is the share of requests served from the cache. p95 latency is the response time that 95% of requests stay under.
- `report-style/work-summary` **next-steps** (2/2 failed): The summary ends with next steps.
  - run 1: pattern 'next steps?' not found
  - run 2: pattern 'next steps?' not found
- `setup-retro/inventory-classify` **evidence-from-corrections** (1/2 failed): Findings cite the user's corrections in the friction log (by date or quote) as the primary evidence.
  - run 2: | 6 | `README.md` in doc-kit | Stale / checklist | Move its content to `CHANGELOG.md` or the SKILL.md, or delete | static |
- `setup-retro/playbooks-and-stale` **lists-all** (1/2 failed): Every playbook is listed with its status, runs and last_run.
  - run 1: `vm-image` playbook | amend, or deprecate | high | One run, last used 2026-02-01 (9 months ago), pinned to Ubuntu 22.04.
- `setup-retro/playbooks-and-stale` **promotion-path** (1/2 failed): The promotion path is stated: the skill is drafted from the playbook's steps and the run log's gotchas after the user agrees, and the playbook then becomes deprecated with a link to the skill. The assistant does not promote on its own.
  - run 2: **After you save the skill:** Set the playbook to `deprecated` with a link to it.
- `structured-project-docs/new-tree` **proposal-first** (2/2 failed): Before creating files, the assistant proposes the tree and says why it fits this project.
  - run 1: You said to go ahead, so I skipped the usual "propose the tree first" step.
  - run 2: Setting up the thesis tree now: the entry files and lint are copied in, and I'm adding the thesis-specific doc types (literature note, chapter, experiment log).
- `structured-project-docs/new-tree` **sized** (2/2 failed): Every created folder holds real content (no empty folders or near-empty files).
  - run 1: empty dirs: ['docs/archive', 'docs/chapters', 'docs/experiments', 'docs/literature', 'docs/playbooks']; near-empty files: []
  - run 2: empty dirs: ['docs/archive', 'docs/chapters', 'docs/experiments', 'docs/literature', 'docs/playbooks']; near-empty files: []
- `structured-project-docs/new-tree` **kebab** (2/2 failed): Added Markdown files use kebab-case names (entry files may be upper case).
  - run 1: 12 added; not kebab-case: ['CLAUDE.md']
  - run 2: 13 added; not kebab-case: ['CLAUDE.md']
- `structured-project-docs/split-monolith` **proposal-first** (2/2 failed): Before moving any content, the assistant states the target file tree and the reasoning for it in its text.
  - run 1: 
  - run 2: Next I'll paste the generated map into the map file, remove the old `notes.md`, and run the lint.
- `structured-project-docs/split-monolith` **single-topic** (1/2 failed): Each resulting file covers one distinct topic with a descriptive name.
  - run 2: | Sync loop, retries, cache, second-factor login | `docs/architecture.md` |
- `structured-project-docs/split-monolith` **where-does-x-go** (1/2 failed): PROJECT_STRUCTURE.md has a 'Where does X go?' list.
  - run 1: no file matches file:PROJECT_STRUCTURE.md
