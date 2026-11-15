---
id: LMP
title: Lamp
type: spec
domain: keeper
layer: L2
status: settled
updated: 2026-11-10
depends_on: [WEA]
---
# Lamp
> Turns oil into beam reach. The players decide each night how much oil to burn.

## Intent
The lamp is the players' only tool, so each night's choice stays legible (VIS-P2).

## Interface
- **LMP-I1** The beam reach of the current night: short, middle or long.

## Rules
### Burning
- **LMP-R1** The players choose a burn level at dusk and cannot change it during the night. `locked`
- **LMP-R2** A higher burn level gives a longer beam reach and uses more oil. `locked`
- **LMP-R3** A worse visibility tier (WEA-I1) shortens the beam reach of every burn level. `locked`

## Provisional rules
- **LMP-R4** Unused oil carries over to the next night. (LMP-Q1) `leaning`

## Parameters
None yet.

## Open questions
- **LMP-Q1** Does oil carry over without a limit, or does the tank cap it? `major`

## See also
- Decision history: [`../../decisions/keeper/lamp.md`](../../decisions/keeper/lamp.md)
