---
id: GLO
title: Glossary
type: registry
updated: 2026-11-10
---
# Glossary

One canonical name per concept. Check here before naming anything; update this file in the same change as any new or renamed term. Rules: [`CONVENTIONS.md`](CONVENTIONS.md) §8. Definitions say what a thing is or does; the owner says how it behaves.

## World

| Term | Means | Owner | Not to be confused with |
|---|---|---|---|
| **Visibility tier** | How far a light or a ship can be seen: clear, hazy or blind | [Weather](design/world/weather.md) | Beam reach |
| **Beam reach** | How far the lamp's light carries in the current visibility tier | [Lamp](design/keeper/lamp.md) | Visibility tier |
| **Passage** | One ship's attempt to pass the reef during a night | [Ships](design/world/ships.md) | Night |

## Retired names

Read by `tools/doclint.py`: a pattern makes the old name a lint error in files with front matter. Rows without a pattern are a manual checklist. Escape pipes in patterns as `\|`.

| Retired | Use instead | Lint pattern |
|---|---|---|
