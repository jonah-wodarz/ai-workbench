---
name: "playbook"
description: "Keep a playbook (repeatable step-by-step guide) and a run log while working through a likely-to-recur task that needs trial and error, research or clarification; follow and refine an existing playbook on later runs. Use automatically when such a task starts or turns out to need figuring out, and when the user says \"playbook this\" or asks how something was done last time."
---

# Playbook

The first time a workflow is figured out, capture it so the next run starts from the answer, and so the user can see how it was found. Two files per workflow, the same split as spec and decision history:

| File | Holds | Read when |
|---|---|---|
| **Playbook** | The current best procedure: steps with done-conditions, gotchas, verification | Doing the task again |
| **Run log** | Dated runs: what was tried, what happened, why the steps are what they are | Asking "why this way?" or debugging a step |

## 1. Start

Start when **both** hold:
- **Figuring out** is happening or clearly ahead: an attempt failed, research was needed, or a requirement had to be clarified.
- **Likely to recur**: a setup, process, tool or data workflow; a kind of task the user has done before; or the user says so.

One-off questions and tasks an existing skill fully covers stay without a playbook.

Announce in one line, then continue the task: *"Keeping a playbook for this (say 'no playbook' to skip)."* If the user declines, stop for this task.

**Look first.** Search the project's `docs/playbooks/` and the central library for an existing playbook on this workflow (titles, then keywords). If one exists, follow it, and treat this run as a refinement.

## 2. During the run

Append to the run log **as things happen**, one table row per attempt: tried · result · why/lesson. Rows written in the moment are the thought process the user wants to see; a reconstruction at the end loses the dead ends.

## 3. Finish

Update the playbook from the run:

1. **Steps** follow the path that worked, in order, each ending on `Done when: <checkable condition>`.
2. **Gotchas** list every failure that cost time: symptom · cause · fix.
3. **Generalize**: instance details (this project's paths, names, dates) become placeholders like `<project>`; the specifics stay in the run log.
4. **Front matter**: `runs` +1, `last_run`, `updated`; status `draft` after the first run, `current` once a later run followed it successfully.
5. Close the run-log entry with **Outcome**: done or partial, and what the playbook gained.
6. Run the lint if the project has doc-kit.

Done when someone with only the playbook could repeat the task without the run log.

Report in one line at the end of the reply: *"Playbook updated: <name> (run <n>)."*

## Location

| Workflow belongs to | Playbook | Run log |
|---|---|---|
| One project | `docs/playbooks/<name>.md` | `docs/playbooks/runs/<name>.md` |
| No project, or several | Central library: `<library>/<name>.md` | `<library>/runs/<name>.md` |

- The central library's location is a user fact in memory. If none is known, ask once where it should live; until there is a folder, write into the session's outputs and send the files.
- Templates: **doc-kit** `docs/templates/playbook.md` and `run-log.md`; structure and naming follow **structured-project-docs**. Link related docs, skills and tools from the playbook's *See also*.

## Writing

- **Playbook**: the persistent-doc rules of structured-project-docs apply: current state, no author voice, one term per concept. Steps are imperative ("Stage the files"), one action each.
- **Run log**: free narrative is fine, first person included; it is the record of thinking.
- Credentials and personal data stay out of both; write where they are kept instead.

## Promotion to a skill

A playbook is a skill candidate when it is `current`, has 3+ runs, and its steps stopped changing. **setup-retro** lists candidates; after the user agrees, the skill is drafted from the playbook (the run log supplies the gotchas), and the playbook gets status `deprecated` with a link to the skill.