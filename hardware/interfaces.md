# Shared Interfaces

These are the working inter-board signal names for the analog build. The goal is to keep board boundaries stable before schematic capture.

## Audio Nets

- `IN_L`, `IN_R`
  - Local single-ended audio after the balanced input receiver
- `DRY_L`, `DRY_R`
  - Dry split taken from the input board before spring-tank processing
- `WET_SEND_L`, `WET_SEND_R`
  - Main wet-path feeds leaving the input board toward the tank system
- `PRI_RET_L`, `PRI_RET_R`
  - Recovered audio returning from the primary `4AB1C1B` tanks
- `SEC_RET_L`, `SEC_RET_R`
  - Recovered audio returning from the secondary `9EB2C1B` / `9EB3C1B` tanks
- `TANK_MIX_L`, `TANK_MIX_R`
  - Output of the tank-routing board before stereo crossfade
- `XFADE_OUT_L`, `XFADE_OUT_R`
  - Output of the stereo crossfade stage
- `FILTCLIP_OUT_L`, `FILTCLIP_OUT_R`
  - Output of the filter and clipping board
- `FB_SEND_L`, `FB_SEND_R`
  - Signals entering the feedback loop
- `FB_RET_L`, `FB_RET_R`
  - Feedback return signals summed into the wet path
- `WET_SUM_L`, `WET_SUM_R`
  - Final wet signal presented to the output mix stage
- `OUT_L`, `OUT_R`
  - Local single-ended audio before the balanced output driver

## Control Nets

- `CTL_EXT_MODE_A`, `CTL_EXT_MODE_B`
  - Two-bit ext-routing control pair
  - first-pass decode is `00 = Off`, `10 = Series`, `11 = Parallel`, `01 = reserved`
- `CTL_CLIP_MODE_A`, `CTL_CLIP_MODE_B`
  - Selects Clean / Silicon / LED / Germanium clipping topology
- `CTL_FB_INV`
  - Feedback polarity invert

Practical note:

- rev A now prefers raw passive control nets at the board boundaries rather than abstract one-net control names for stereo pots
- the actual raw control naming lives in [rev-a-control-harnesses.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-harnesses.md:1) and [rev-a-control-backplane-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-definition.md:1)

## Power Nets

- `+15VA`, `-15VA`
  - Preferred starting assumption for the main analog rails
- `+5VAUX`
  - Optional auxiliary rail for relay coils, LEDs, or analog-switch housekeeping
- `AGND`
  - Audio ground / star ground reference
- `CHASSIS`
  - Chassis / enclosure ground, bonded at controlled points only

## Current Assumptions

- Default design target is stereo throughout.
- External I/O uses combo `XLR / TRS` jacks.
- Main analog stages should preserve enough headroom to survive tank recovery peaks and clipping-mode level changes.
- Board-to-board links should use locking headers or JST/Molex style connectors rather than hardwired point-to-point only.
- If tank interface impedances force shielded cabling, the tank driver/recovery board owns that connectorization.
