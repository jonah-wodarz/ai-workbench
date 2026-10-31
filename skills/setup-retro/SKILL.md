---
name: "setup-retro"
description: "Retrospective on the user's Claude setup: skills, preferences, plugins and the friction log. Use when the user asks to review, audit, clean up or retro their skills, instructions or setup."
---

# Setup Retro

Find where the setup costs the user effort, and turn each finding into the cheapest durable fix: a deterministic check, a sharper skill, a preference line, or a removal. **The user's own corrections are the primary evidence**; Claude's self-assessment of its skill use is unreliable and counts only as a lead.

## 1. Scope

- Period: since the last retro (dated line at the end of the friction log), else the last ~3 months.
- Surfaces: this app; add Claude Code once the user uses it.
- Confirm scope in one line, then start.

## 2. Inventory

1. List enabled skills and plugins (ListSkills, ListPlugins). Built-in Anthropic skills are out of scope unless one collides with a user skill.
2. Read **every user skill's SKILL.md in full**, plus account preferences and memory preferences.
3. Read the friction log in memory.
4. List playbooks (central library and project `docs/playbooks/`) with status, `runs` and `last_run`.

Done when every in-scope skill is read in full and listed with its trigger (description) and job, and every playbook is listed.

## 3. Evidence

1. **Friction log** entries since the last retro.
2. **Chat mining**: search past chats for corrections and re-asks: "actually", "no,", "I meant", "again", "that's not", "eigentlich", "nein", "nochmal", "gemeint". Read the hits in context.
3. **Project memory** for stated frustrations with docs, workflow or output.
4. **Playbook run logs** since the last retro: gotchas that recur across playbooks, steps a skill or check could absorb.
5. For each hit: which skill or instruction was involved (or none), what the user corrected, how often.

Done when every hit is either attributed to a finding or dismissed as one-off.

## 4. Classify

| Category | Signal | Cheapest fix |
|---|---|---|
| **Mechanical rule in prose** | User corrected a pattern a script could catch | Deterministic check (doc-kit lint pattern, script) |
| **Trigger** | Skill fired when it shouldn't, or stayed silent when it should | Rewrite the description's trigger branches |
| **Overlap** | Two skills claim the same request, or give conflicting rules | Merge, or assign one owner and point the other to it |
| **Steering bloat** | Long always-loaded preferences or descriptions | Move detail into a skill body or a doc behind a pointer |
| **No-op** | Instruction the model follows by default | Delete the sentence |
| **Negation-only rule** | Rule phrased only as "don't X" | State the positive target; keep the prohibition only as a paired guardrail |
| **Stale** | References to removed skills, files, tools or product features | Update or delete; verify product facts by search |
| **Information access** | A needed file, folder, connector or tool was missing | Suggest the connection or folder |
| **Tool economy** | Repeated expensive calls for bulk data | A script that processes data outside the context |
| **Gap** | Same request repeated, no skill covers it | New skill (or preference line if one sentence suffices) |
| **Ripe playbook** | Playbook `current`, 3+ runs, steps unchanged in the last runs | Promote to a skill (playbook skill, *Promotion*) |
| **Stale playbook** | No run in ~6 months, or its tools changed | Re-verify on next use, or deprecate |

## 5. Report

Write the review as files when a folder is available (structured-project-docs), else a doc; chat gets the summary (report-style):

- Decision table: item · verdict (keep / amend / merge / remove / new / promote) · confidence · evidence link.
- Friction found, including what the log missed.
- Action plan split by owner: **user** (toggle skills/plugins, paste preference lines) and **Claude** (skill proposal cards).
- Uncertainties flagged next to the claim they affect.

Ask the user for decisions on anything ambiguous before drafting changes (interrogate's decide mode fits).

## 6. Act

- Removals and preference edits: the user does them; give paste-ready text.
- Skill changes: read the current SKILL.md in full, then propose the complete updated file as a card (max 3 per batch). Plugin skills can't be edited; propose a renamed user skill instead.
- Promotions: draft the skill from the playbook's steps and the run logs' gotchas; after the user saves it, set the playbook to `deprecated` with a link to the skill.
- Skills with scripts can't travel as cards: package a zip for Settings upload.
- Check each amended skill against **writing-for-agents** if installed.

## 7. Close

Append one dated line to the friction log: `- [YYYY-MM-DD] retro done — <n> findings, <n> fixed; open: <items>`. The next retro mines from that date.