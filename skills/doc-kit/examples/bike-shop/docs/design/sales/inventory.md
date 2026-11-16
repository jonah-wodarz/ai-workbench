---
id: INV
title: Inventory
type: spec
domain: sales
layer: L2
status: settled
updated: 2026-11-10
depends_on: []
---
# Inventory
> Knows how many of each part are in stock and how many are already promised.

## Intent
Inventory is the one view of the stock that the counter, the web shop and the workshop share (VIS-P1).

## Interface
- **INV-I1** The available quantity of a part: its stock minus its reservations.
- **INV-I2** A reservation: a hold on a part for one order or one repair job.

## Rules
### Stock
- **INV-R1** Every part has exactly one stock record. `locked`
- **INV-R2** A reservation lowers the available quantity at once. `locked`
- **INV-R3** A reservation ends when its order or repair job is completed or cancelled. `locked`

## Parameters
None yet.

## Open questions
- **INV-Q1** Is stock counted for the whole shop or per shelf? `minor`

## See also
- Decision history: [`../../decisions/sales/inventory.md`](../../decisions/sales/inventory.md)
