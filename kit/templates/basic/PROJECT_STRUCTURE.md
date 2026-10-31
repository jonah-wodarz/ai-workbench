# Project Structure

How the project is organized and where new work goes.

```
<project>/
├─ README.md               ← overview + entry points
├─ PROJECT_STRUCTURE.md    ← this file
├─ docs/
│  ├─ MAP.md               ← generated index of every doc
│  ├─ GLOSSARY.md          ← canonical names (check before naming anything)
│  ├─ CONVENTIONS.md       ← how docs are structured and written (binding)
│  ├─ parking-lot.md       ← ideas not yet placed
│  ├─ <area>/              ← one folder per topic area
│  └─ archive/             ← finished point-in-time docs
└─ tools/                  ← doclint.py, doclint.json, stale-terms.txt, hooks/
```

## Rules
All structure and writing rules live in [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md). Check them with `python tools/doclint.py`.

## Where does X go?
- A new topic → its own file in the matching `docs/<area>/`, front matter from CONVENTIONS §3.
- A new or renamed term → `docs/GLOSSARY.md`, in the same change.
- An idea not yet worth a doc → one line in `docs/parking-lot.md`.
- A finished review, audit or log → `docs/archive/`.
