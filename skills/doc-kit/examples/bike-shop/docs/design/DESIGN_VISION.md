---
id: VIS
title: Design Vision
type: vision
updated: 2026-11-10
---
# Design Vision
> A small bike shop sells parts and repairs bikes. Counter, web shop and workshop work from one view of the stock.

## Pillars
- **VIS-P1** Staff never promise a part that is not available.
- **VIS-P2** A customer can learn the state of an order or a repair without calling the shop.

## Scope
In scope: one shop with a counter, a web shop and a workshop. Out of scope: accounting and staff scheduling.

## Systems
- [Inventory](sales/inventory.md) knows what is in stock and what is already promised.
- [Orders](sales/orders.md) takes what customers buy, at the counter and online.
- [Repairs](workshop/repairs.md) follows a bike through the workshop and the parts its repair uses.
