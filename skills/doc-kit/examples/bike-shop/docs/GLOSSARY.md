---
id: GLO
title: Glossary
type: registry
updated: 2026-11-10
---
# Glossary

One canonical name per concept. Check here before naming anything; update this file in the same change as any new or renamed term. Rules: [`CONVENTIONS.md`](CONVENTIONS.md) §8. Definitions say what a thing is or does; the owner says how it behaves.

## Shop

| Term | Means | Owner | Not to be confused with |
|---|---|---|---|
| **Available quantity** | Stock of a part minus its reservations | [Inventory](design/sales/inventory.md) | Stock |
| **Reservation** | A hold on a part for one order or one repair job | [Inventory](design/sales/inventory.md) | Order |
| **Repair job** | One bike in the workshop, from drop-off to pick-up | [Repairs](design/workshop/repairs.md) | Order |

## Retired names

Read by `tools/doclint.py`: a pattern makes the old name a lint error in files with front matter. Rows without a pattern are a manual checklist. Escape pipes in patterns as `\|`.

| Retired | Use instead | Lint pattern |
|---|---|---|
