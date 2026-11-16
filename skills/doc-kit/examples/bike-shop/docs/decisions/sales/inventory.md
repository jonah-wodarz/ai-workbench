---
id: INV
title: Inventory — decision history
type: decisions
domain: sales
updated: 2026-11-10
---
# Inventory — decision history
Current state: [`../../design/sales/inventory.md`](../../design/sales/inventory.md). Entries record pivotal decisions only, are immutable, and run newest at the bottom.

### D-INV-001 — A reservation lowers the available quantity at once
2026-11-10 · accepted · rules INV-R2
**Decision:** A part counts as taken from the moment it is reserved, not from the moment it is paid.
**Why:** Two customers must never be promised the last part (VIS-P1).
**Rejected:** Lowering the quantity at payment — simpler, but the web shop and the counter can sell the same part twice.
