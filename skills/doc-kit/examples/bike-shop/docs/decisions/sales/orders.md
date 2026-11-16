---
id: ORD
title: Orders — decision history
type: decisions
domain: sales
updated: 2026-11-10
---
# Orders — decision history
Current state: [`../../design/sales/orders.md`](../../design/sales/orders.md). Entries record pivotal decisions only, are immutable, and run newest at the bottom.

### D-ORD-001 — Orders only for available parts
2026-11-10 · accepted · rules ORD-R1
**Decision:** A part that is not available cannot be ordered.
**Why:** The shop does not know supplier delivery times well enough to promise a date.
**Rejected:** Backorders — more sales, but a promise the shop cannot keep.
