---
id: REP
title: Repairs
type: spec
domain: workshop
layer: L1
status: drafting
updated: 2026-11-10
depends_on: [INV]
---
# Repairs
> Follows a bike from drop-off to pick-up and reserves the parts its repair uses.

## Intent
Repairs lets the workshop plan with parts that are really there (VIS-P1) and shows the customer where the bike stands (VIS-P2).

## Interface
- **REP-I1** The state of a repair job: accepted, waiting for parts, in work, ready or closed.

## Rules
### Parts
- **REP-R1** A repair job reserves the parts it needs (INV-I2). `locked`
- **REP-R2** A repair job whose parts are not available waits for them. `locked`

## Parameters
None yet.

## Open questions
- **REP-Q1** Does the customer approve the cost before the work starts? `blocking`
- **REP-Q2** Can a mechanic move a reserved part from one repair job to another? `major`

## See also
- Decision history: [`../../decisions/workshop/repairs.md`](../../decisions/workshop/repairs.md)
