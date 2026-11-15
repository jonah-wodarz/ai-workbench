---
id: MAP
title: System Map
type: registry
updated: 2026-11-10
---
# System Map
Every system, its type, depth and status, generated from front matter. Regenerate the table with `python tools/doclint.py --map`; only this introduction is written by hand. Open questions: [`planning/OPEN_QUESTIONS.md`](planning/OPEN_QUESTIONS.md).

## Working discipline
1. Know which system and layer a session is on; never drop two layers at once.
2. Finish or deliberately bound a layer before descending.
3. Record decisions in the owning spec and its decision history.
4. Ideas from another system or a deeper layer go to the [parking lot](design/parking-lot.md).
5. Check the [glossary](GLOSSARY.md) before naming anything.

## Systems
| Code | System | Type | Layer | Status | File |
|---|---|---|---|---|---|
| `LMP` | Lamp | spec | L2 | settled | [`design/keeper/lamp.md`](design/keeper/lamp.md) |
| `SHP` | Ships | spec | L1 | drafting | [`design/world/ships.md`](design/world/ships.md) |
| `WEA` | Weather | spec | L2 | settled | [`design/world/weather.md`](design/world/weather.md) |
| `GLO` | Glossary | registry | — | — | [`GLOSSARY.md`](GLOSSARY.md) |
| `MAP` | System Map | registry | — | — | [`SYSTEM_MAP.md`](SYSTEM_MAP.md) |
| `PRK` | Parking Lot | ideas | — | — | [`design/parking-lot.md`](design/parking-lot.md) |
| `VIS` | Design Vision | vision | — | — | [`design/DESIGN_VISION.md`](design/DESIGN_VISION.md) |
