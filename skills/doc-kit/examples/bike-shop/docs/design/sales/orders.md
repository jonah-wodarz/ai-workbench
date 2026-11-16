---
id: ORD
title: Orders
type: spec
domain: sales
layer: L2
status: settled
updated: 2026-11-10
depends_on: [INV]
---
# Orders
> Takes a customer's order for parts or bikes, at the counter or online.

## Intent
Orders turns a purchase into a promise the shop can keep (VIS-P1) and that the customer can follow (VIS-P2).

## Interface
- **ORD-I1** The state of an order: open, paid, handed over or cancelled.

## Rules
### Placing an order
- **ORD-R1** An order can be placed only for parts that are available (INV-I1). `locked`
- **ORD-R2** Placing an order reserves its parts (INV-I2). `locked`
- **ORD-R3** A cancelled order releases its reservations. `locked`

## Provisional rules
- **ORD-R4** An online order that stays unpaid is cancelled after a waiting period. (ORD-Q1) `leaning`

## Parameters
None yet.

## Open questions
- **ORD-Q1** Is the waiting period for an unpaid online order counted in hours or in days? `major`

## See also
- Decision history: [`../../decisions/sales/orders.md`](../../decisions/sales/orders.md)
