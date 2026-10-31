# Project Structure

How the project is organized and where new work goes.

```
<project>/
├─ README.md                 ← overview + entry points
├─ PROJECT_STRUCTURE.md      ← this file
├─ docs/
│  ├─ SYSTEM_MAP.md          ← START HERE: systems × layer × status (generated)
│  ├─ GLOSSARY.md            ← canonical names (check before naming anything)
│  ├─ CONVENTIONS.md         ← how every doc is structured and written (binding)
│  ├─ design/                ← current state: vision, parking lot, <domain>/ specs
│  ├─ decisions/             ← decision history mirroring design/
│  ├─ templates/             ← spec · decisions · data · playbook · run-log
│  ├─ playbooks/             ← repeatable workflow guides; runs/ holds their run logs
│  ├─ research/              ← sourced external knowledge
│  ├─ planning/              ← OPEN_QUESTIONS, roadmaps, audits
│  └─ archive/               ← finished point-in-time docs
└─ tools/                    ← doclint.py, doclint.json, stale-terms.txt, hooks/
```

## Rules
All structure, format and writing rules live in [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md). Check them with `python tools/doclint.py`.

## Where does X go?
- A workflow worked out by trial and error → `docs/playbooks/<name>.md` (steps) + `docs/playbooks/runs/<name>.md` (what was tried and why). Templates: `docs/templates/`.
- A rule, question or parameter for a system → its spec in `docs/design/` (or `parking-lot.md` if the system isn't open yet).
- Why something was decided, or what was rejected → the mirror file in `docs/decisions/`.
- Notes from outside sources → `docs/research/`.
- A question spanning systems or blocking a phase → `docs/planning/OPEN_QUESTIONS.md`.
- A new or renamed term → `docs/GLOSSARY.md`, in the same change.
