---
id: WEA
title: Weather
type: spec
domain: world
layer: L2
status: settled
updated: 2026-11-10
depends_on: []
---
# Weather
> Sets the visibility tier of each night and announces it one night ahead.

## Intent
Weather is the opponent (VIS-P1). It makes nights differ and gives the players a forecast to plan with.

## Interface
- **WEA-I1** The visibility tier of the current night: clear, hazy or blind.
- **WEA-I2** The forecast: the visibility tier of the next night.

## Rules
### Nights
- **WEA-R1** Each night has exactly one visibility tier. `locked`
- **WEA-R2** The forecast is revealed at dusk and is always correct. `locked`
- **WEA-R3** Blind nights are rarer than hazy nights, and hazy nights are rarer than clear nights. `locked`

## Parameters
None yet.

## Open questions
- **WEA-Q1** Does the season end on a fixed storm night? `minor`

## See also
- Decision history: [`../../decisions/world/weather.md`](../../decisions/world/weather.md)
