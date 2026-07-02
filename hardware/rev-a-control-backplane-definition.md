# GAS Rev A Control Backplane Definition

This file defines the preferred rev-A solution for the denser control groups.

The backplane is still fully analog in spirit:

- no MCU
- no digital audio
- no embedded computer

It only centralizes panel controls, passive control wiring, and simple relay-driver or mode-encoding support where that is cleaner than long direct runs to every audio board.

## Purpose

- land the dense front-panel controls
- decode mode selectors into the existing control nets
- keep passive control harnessing organized
- optionally reserve space for `ULN2003ADR` or similar future support if a later revision changes the harness to give the backplane real coil-drive or indicator ownership

## Recommended Active Content

- `U601` `ULN2003ADR`
  - optional reserve only
  - do not assume it is populated in the current fixed rev-A harness because the frozen inter-board interface carries only the two ext-mode outputs, not a dedicated expanded relay-driver bus
  - if the simple direct-drive rev-A strategy is retained, `CTL_EXT_MODE_A/B` themselves should be treated as the switched `+5VAUX` relay-control outputs

## Power

### P601 Backplane Power

- preferred connector: `JST VH` 4-position
- pins:
  - `1` `+5VAUX`
  - `2` `AGND`
  - `3` `+15VA`
  - `4` `-15VA`

Practical note:

- most of the control backplane only needs `+5VAUX` and `AGND`
- the split rails are included so the board can still serve as the common control landing board if local analog buffering or LED/reference support is later added

## Board-Side Control Connectors

### P610 I/O Controls

- preferred connector: `JST XH` 9-position
- carries:
  - `WD_L_HI`
  - `WD_L_WIPER`
  - `WD_L_LO`
  - `WD_R_HI`
  - `WD_R_WIPER`
  - `WD_R_LO`
  - `MONO_A`
  - `MONO_C`
  - `MONO_B`

### P611 Ext Routing Controls

- preferred connector: `JST XH` 10-position
- carries:
  - `EXTMIX_L_HI`
  - `EXTMIX_L_WIPER`
  - `EXTMIX_L_LO`
  - `EXTMIX_R_HI`
  - `EXTMIX_R_WIPER`
  - `EXTMIX_R_LO`
  - `+5VAUX`
  - `AGND`
  - `CTL_EXT_MODE_A`
  - `CTL_EXT_MODE_B`

### P612 Crossfade / Feedback Controls

- preferred connector: `JST XH` 10-position
- carries:
  - `XFD_L_HI`
  - `XFD_L_WIPER`
  - `XFD_L_LO`
  - `XFD_R_HI`
  - `XFD_R_WIPER`
  - `XFD_R_LO`
  - `FB_L_WIPER`
  - `FB_R_WIPER`
  - `CTL_FB_INV`
  - `AGND`

Practical note:

- if the feedback amount law ends up needing full six-wire raw dual-pot wiring instead of local bias endpoints on the crossfade board, split this into two connectors rather than overcompressing the harness

### P613 Filter / Clipper Controls A

- preferred connector: `JST XH` 12-position
- carries:
  - `DRV_HI`
  - `DRV_WIPER`
  - `DRV_LO`
  - `HPF_F_L_HI`
  - `HPF_F_L_WIPER`
  - `HPF_F_L_LO`
  - `HPF_F_R_HI`
  - `HPF_F_R_WIPER`
  - `HPF_F_R_LO`
  - `HPF_Q_L_WIPER`
  - `HPF_Q_R_WIPER`
  - `AGND`

### P614 Filter / Clipper Controls B

- preferred connector: `JST XH` 12-position
- carries:
  - `LPF_F_L_HI`
  - `LPF_F_L_WIPER`
  - `LPF_F_L_LO`
  - `LPF_F_R_HI`
  - `LPF_F_R_WIPER`
  - `LPF_F_R_LO`
  - `LPF_Q_L_WIPER`
  - `LPF_Q_R_WIPER`
  - `+5VAUX`
  - `CTL_CLIP_MODE_A`
  - `CTL_CLIP_MODE_B`
  - `AGND`

## Panel-Side Hardware

The backplane is the preferred landing point for:

- `J701` ext mode rotary
- `J702` clip mode rotary
- `VR701` wet/dry dual pot
- `VR702` ext amount dual pot
- `VR703` crossfade dual pot
- `VR704` feedback dual pot
- `VR705` drive pot
- `VR706` HPF cutoff dual pot
- `VR707` HPF Q dual pot
- `VR708` LPF cutoff dual pot
- `VR709` LPF Q dual pot
- `SW701` mono-to-stereo
- `SW702` feedback phase

## Encoding Rules

### Ext Mode

- `00` = `Off`
- `10` = `Series`
- `11` = `Parallel`
- `01` = reserved / off-equivalent service state

### Clip Mode

- `00` = `Clean`
- `01` = `Silicon`
- `10` = `LED`
- `11` = `Germanium`

## Why This Board Is Worth Keeping

Without it, rev A starts to accumulate:

- too many long passive control runs
- too many tiny inconsistent control headers
- avoidable front-panel wiring clutter

With it, the build package becomes easier to quote and easier to service while still staying fully within the analog-only project constraint.
