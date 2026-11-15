---
id: SHP
title: Ships
type: spec
domain: world
layer: L1
status: drafting
updated: 2026-11-10
depends_on: [WEA, LMP]
---
# Ships
> Ships attempt a passage each night. The players win by bringing enough of them past the reef.

## Intent
Ships give the oil a purpose and score the night. Each lost ship points back to that night's burn level (VIS-P2).

## Interface
- **SHP-I1** The number of passages attempted in the current night.

## Rules
### Passages
- **SHP-R1** A passage succeeds when the beam reach (LMP-I1) covers the ship's lane. `locked`
- **SHP-R2** More ships attempt a passage on a clear night than on a blind night (WEA-I1). `locked`

## Parameters
None yet.

## Open questions
- **SHP-Q1** Do the players see how many ships are coming before they choose the burn level? `blocking`
- **SHP-Q2** Can a lost ship be rescued by a later action? `major`

## See also
- Decision history: [`../../decisions/world/ships.md`](../../decisions/world/ships.md)
