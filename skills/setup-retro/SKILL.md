---
name: "setup-retro"
description: "Retrospective on the user's Claude setup: skills, preferences, plugins, playbooks and the friction log. Use when the user asks to review, audit, shorten, clean up or retro their skills, instructions or setup (\"retro\", \"review my skills\", \"why did the skill not fire\", \"which skills overlap\", \"Setup aufräumen\"), or to check one skill against the quality checklist. Boundary: promoting a playbook uses the playbook skill's criteria; the report follows report-style."
---

# Setup Retro

Find where the setup costs the user effort and turn each finding into the cheapest durable fix. **The user's own corrections are the primary evidence**; Claude's self-assessment of its skill use is a lead only.

## 1. Scope

Period: since the last retro (dated line at the end of the friction log), else the last 3 months. Surfaces: this app, plus Claude Code if used. Confirm in one line, then start.

## 2. Inventory

1. List enabled skills and plugins (ListSkills, ListPlugins). Built-in Anthropic skills are in scope only where one collides with a user skill.
2. Read every user skill's SKILL.md in full, plus account and memory preferences and the friction log.
3. List playbooks (central library and `docs/playbooks/`) with status, `runs`, `last_run`.

Done when every in-scope skill and playbook is listed with trigger (description) and job.

## 3. Evidence

1. Friction log entries since the last retro.
2. Chat mining: search past chats for corrections and re-asks ("actually", "no,", "I meant", "again", "that's not", "eigentlich", "nein", "nochmal", "gemeint") and read hits in context.
3. Project memory for stated frustrations; playbook run logs for recurring gotchas.
4. Per hit: which skill or instruction was involved (or none), what was corrected, how often.

Done when every hit is attributed to a finding or dismissed as a one-off.

## 4. Classify

Assign each finding a category and its cheapest fix from [finding-categories.md](references/finding-categories.md). For a skill under review also apply [skill-checklist.md](references/skill-checklist.md), starting with `scripts/check_skills.py`.

## 5. Report

Files when a folder is available (structured-project-docs), else a doc; the chat gets the summary. Contents:

- Decision table: item, verdict (keep / amend / merge / remove / new / promote), confidence, evidence link.
- Friction found, including what the log missed.
- Action plan by owner: **user** (toggle skills or plugins, paste preference lines) and **Claude** (skill proposal cards).
- Uncertainty next to the claim it affects.

Ask for decisions on ambiguous items before drafting changes (interrogate, decide mode).

## 6. Act

1. Removals and preference edits: the user applies them; give paste-ready text.
2. Skill changes: read the current SKILL.md in full, then propose the complete updated file as a card (max 3 per batch). Plugin skills cannot be edited; propose a renamed user skill.
3. Promotions: draft the skill from the playbook steps and run-log gotchas; after the user saves it, set the playbook to `deprecated` with a link.
4. Skills with scripts or references travel as a zip for Settings upload, not as cards.
5. Check each amended skill with writing-for-agents if installed.

## 7. Close

Append to the friction log: `- [YYYY-MM-DD] retro done — <n> findings, <n> fixed; open: <items>`.
