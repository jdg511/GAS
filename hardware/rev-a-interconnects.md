# GAS Rev A Interconnects

This file turns the board briefs into concrete board-to-board connector intent.

## Grounding Rules

- `AGND` is the signal reference shared by all audio boards
- `CHASSIS` is bonded to enclosure metalwork
- bond `AGND` to `CHASSIS` at one controlled star point near the power-entry area
- tank return cable shields should terminate to the recovery-side ground strategy, not randomly at multiple board points

## Power Distribution

Source:

- external `+24 VDC` wall adapter into the power-backplane board
- on-board conversion to:
  - `+15VA`
  - `-15VA`
  - `+5VAUX`
  - `AGND`

Distribution rails:

- `+15VA`
- `-15VA`
- `+5VAUX`
- `AGND`
- `CHASSIS`

## External Audio Nets

- `IN_BAL_L_P`, `IN_BAL_L_N`
  - external balanced left input pair from the left combo `XLR / TRS` jack
- `IN_BAL_R_P`, `IN_BAL_R_N`
  - external balanced right input pair from the right combo `XLR / TRS` jack
- `OUT_BAL_L_P`, `OUT_BAL_L_N`
  - external balanced left output pair to the left combo `XLR / TRS` jack
- `OUT_BAL_R_P`, `OUT_BAL_R_N`
  - external balanced right output pair to the right combo `XLR / TRS` jack

## Board Connectors

### JIO-PWR

Power into the Input / Output board

1. `+15VA`
2. `AGND`
3. `-15VA`

Preferred connector family:

- `JST VH`

### JIO-WETSEND

Wet send from Input / Output board to the tank-routing board

1. `WET_SEND_L`
2. `AGND`
3. `WET_SEND_R`

Preferred connector family:

- `JST XH`

### JIO-DRY

Dry feed retained for final mix on the Input / Output board

1. `DRY_L`
2. `AGND`
3. `DRY_R`

Preferred connector family:

- `JST XH`

### JIO-WETRET

Final wet return from Crossfade / Feedback / Wet Summing board back to Input / Output board

1. `WET_SUM_L`
2. `AGND`
3. `WET_SUM_R`

Preferred connector family:

- `JST XH`

### JTR-PRI

Primary tank send / return bundle between Tank Routing board and Tank Driver / Recovery board

1. `PRI_SEND_L`
2. `PRI_RET_L`
3. `AGND`
4. `PRI_SEND_R`
5. `PRI_RET_R`
6. `AGND`

Preferred connector family:

- `JST XH`

### JTR-SEC

Secondary tank send / return bundle between Tank Routing board and Tank Driver / Recovery board

1. `SEC_SEND_L`
2. `SEC_RET_L`
3. `AGND`
4. `SEC_SEND_R`
5. `SEC_RET_R`
6. `AGND`

Preferred connector family:

- `JST XH`

### JTR-XFADE

Output of routing board into crossfade board

1. `TANK_MIX_L`
2. `AGND`
3. `TANK_MIX_R`

Preferred connector family:

- `JST XH`

### JXF-FILT

Crossfade board output into filter / clipping board

1. `XFADE_OUT_L`
2. `AGND`
3. `XFADE_OUT_R`

Preferred connector family:

- `JST XH`

### JFILT-WET

Filter / clipping board output back to crossfade / feedback / wet summing board

1. `FILTCLIP_OUT_L`
2. `AGND`
3. `FILTCLIP_OUT_R`

Preferred connector family:

- `JST XH`

### JFB-INJ

Feedback reinjection from the crossfade / feedback board to the tank-routing board

1. `FB_RET_L`
2. `AGND`
3. `FB_RET_R`

Preferred connector family:

- `JST XH`

### JEXT-PWR

Power into the ext-routing board

1. `+15VA`
2. `AGND`
3. `-15VA`
4. `+5VAUX`

Preferred connector family:

- `JST VH`

## Control Hardware Allocation

### Input / Output board

- Wet/Dry
- Mono-input to stereo switch

### Tank Routing board

- Ext Reverb Tanks mode
- Ext Reverb Tanks amount

### Crossfade / Feedback board

- Crossfade amount
- Feedback amount
- Feedback phase invert

### Filter / Clipping board

- Drive
- HPF frequency
- HPF Q
- LPF frequency
- LPF Q
- Clip mode

## Practical Wiring Guidance

- External I/O is balanced line-level; internal inter-board audio is single-ended unless noted otherwise.
- Use shielded cable for tank send and tank return runs
- Use twisted pair plus local ground for low-level audio between boards
- Keep relay coil wiring away from tank recovery inputs
- Do not run DC power-entry wiring in the same bundle or channel as tank recovery wiring
- For the exact rev-A harness pin assignments, use [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
