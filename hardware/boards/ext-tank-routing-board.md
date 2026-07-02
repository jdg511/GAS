# Ext Reverb Tanks Off / Series / Parallel Board

## Purpose

This board controls how the secondary tanks are inserted into the signal path. It implements the real-hardware version of the plugin's `Ext Reverb Tanks` mode and `Ext Reverb Tanks Amount` control.

## Functions

- Secondary tanks completely bypassed in `Off`
- Secondary tanks inserted after the primary path in `Series`
- Secondary tanks blended alongside the primary path in `Parallel`
- Adjustable secondary-tank amount
- Left and right channels remain distinct:
  - secondary left tank is `9EB2C1B`
  - secondary right tank is `9EB3C1B`

## Software Features Mapped Here

- `Ext Reverb Tanks`: Off / Series / Parallel
- `Ext Reverb Tanks Amount`

## Hardware Interpretation

- `Off`
  - Only the primary `4AB1C1B` tank returns feed the downstream path
- `Series`
  - Primary tank recovery feeds the secondary tank path
  - The resulting secondary path is blended with the primary according to the amount control
- `Parallel`
  - The wet source is split so primary and secondary tank systems run side by side
  - Secondary path level is blended against the primary according to the amount control

## Recommended Analog Blocks

1. Routing selector
   - 3-position rotary switch, latching relays, or analog-switch IC matrix
   - No MCU-controlled logic
2. Buffering around routing nodes
   - Prevent loading changes between Off / Series / Parallel modes
3. Secondary amount control
   - Dual-ganged level control or active blend stage
4. Summing amplifiers
   - Blend primary and secondary returns where required
5. Optional makeup gain trim
   - Especially useful if series mode needs recovery after cascading through the extra tank path

## Proposed Connectors

- `P201` wet input from I/O board: `WET_SEND_L`, `AGND`, `WET_SEND_R`
- `P202` primary tank interface to tank driver/recovery board
- `P203` secondary tank interface to tank driver/recovery board
- `P204` routed output to crossfade stage: `TANK_MIX_L`, `AGND`, `TANK_MIX_R`
- `P205` feedback reinjection input: `FB_RET_L`, `AGND`, `FB_RET_R`
- `P206` controls: raw stereo ext amount plus `CTL_EXT_MODE_A`, `CTL_EXT_MODE_B`, or panel-backplane equivalent
- `P207` power: `+15VA`, `AGND`, `-15VA`, `+5VAUX`

## Preferred Rev A Direction

- Use a hard analog selector first, not a soft-control system that assumes future firmware.
- Keep mode switching electrically obvious and easy to debug on the bench.
- If analog switches are used, verify headroom and distortion margins against recovered tank peaks.
- If relays are used, keep coils and flyback currents away from sensitive recovery nodes.

## Risks

- Tank recovery nodes may be high gain and sensitive to switch leakage or crosstalk.
- Parallel mode can make gain structure drift if primary and secondary return paths are not normalized carefully.
- Series mode may need dedicated trim so it does not collapse in level compared to parallel or off.

## Rev A Schematic Checklist

- Decide between relay routing and analog-switch routing
- Define summing gains for Off / Series / Parallel
- Define the exact insertion point of feedback return relative to this board
- Verify that the amount control means the same thing in series and parallel modes
