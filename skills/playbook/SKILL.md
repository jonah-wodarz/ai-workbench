---
name: "playbook"
description: "Keep a playbook (repeatable step-by-step guide) and a run log while working through a task that is likely to recur and needs trial and error, research or clarification; follow and refine an existing playbook on later runs. Use at the start of any non-trivial task, especially one with the same shape as an earlier task (same kind of data, tool or setup, new instance), when a first attempt fails, and when the user says \"playbook this\", \"do it like last time\", \"how did we do this before\" or \"schreib das als Playbook auf\". Boundary: a stable, frequently used procedure becomes a skill (setup-retro finds candidates); doc structure and naming follow structured-project-docs."
---

# Playbook

Capture a workflow the first time it is figured out, so the next run starts from the answer.

| File | Holds | Read when |
|---|---|---|
| **Playbook** | Current best procedure: steps with done-conditions, gotchas, verification | Doing the task again |
| **Run log** | Dated runs: attempts, results, reasons | Asking "why this way?" or debugging a step |

## 1. Look first

At the start of every non-trivial task, search `docs/playbooks/` and the central library by title and keywords. Match on shape too: an earlier task with the same kind of input, tool or setup counts. If a playbook exists, follow it; this run refines it.

## 2. Decide to keep one

Keep a playbook when **both** hold: figuring out is happening or ahead (an attempt failed, research or clarification was needed), and the task is likely to recur (it has the shape of an earlier task, or the user says so). A one-off, or a task an existing skill fully covers, gets none.

Announce in one line, then continue: "Keeping a playbook for this (say 'no playbook' to skip)." A decline ends it for this task.

## 3. During the run

Append a row to the run log as each attempt happens: tried, result, why or lesson. Dead ends stay in; they are the thought process.

## 4. Finish

1. Create or edit the playbook from the doc-kit template (`docs/templates/playbook.md` in the project; `doc-kit/kit/templates/basic/docs/templates/playbook.md` otherwise). Keep its sections and front matter keys unchanged.
2. **Steps** follow the path that worked, imperative, one action each, each ending `Done when: <checkable condition>`.
3. **Gotchas**: every failure that cost time as symptom, cause, fix.
4. **Generalize**: instance details become placeholders such as `<project>`; specifics stay in the run log.
5. Update front matter: `runs` +1, `last_run`, `updated`; `status: draft` after run 1, `current` once a later run followed it successfully.
6. Close the run-log entry with **Outcome** (done or partial, what the playbook gained).
7. Run the lint: `python tools/doclint.py` in a doc-kit project, until 0 errors. Without doc-kit, compare headings and front matter with the template by hand.
8. End the reply with: "Playbook updated: <name> (run <n>)."

Done when someone holding only the playbook could repeat the task.

## Writing rules

- **Language**: playbooks and run logs are English, even when the task content is German. Learner-facing or deliverable content keeps its own language.
- Playbook: current state, no author voice, one term per concept (structured-project-docs).
- Run log: free narrative, first person allowed.
- Credentials and personal data stay out; note where they are kept.

## Location

| Workflow belongs to | Playbook | Run log |
|---|---|---|
| One project | `docs/playbooks/<name>.md` | `docs/playbooks/runs/<name>.md` |
| No project, or several | `<library>/<name>.md` | `<library>/runs/<name>.md` |

The central library location is a user fact in memory. If unknown, ask once; until a folder exists, write into the session's outputs.

## Promotion

A `current` playbook with 3+ runs and stable steps is a skill candidate. setup-retro lists candidates and drafts the skill; the playbook then gets status `deprecated` with a link to the skill.

## Troubleshooting

- **Skill did not fire on a repeat-shaped task**: run step 1 at task start, before planning.
- **Playbook drifted from the template or came out in German**: restart from the template file; apply the language rule.
- **Lint skipped**: step 4.7 is part of done.
