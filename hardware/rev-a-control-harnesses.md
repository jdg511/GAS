# GAS Rev A Control Harnesses

This file defines the rev-A front-panel control wiring in a way that can actually be captured and built.

It exists because several rev-A controls are stereo dual-gang parts, and those cannot be represented honestly as vague one-net control abstractions if the first hardware pass uses passive panel controls.

## Control Wiring Strategy

Rev A supports two valid implementations:

1. board-mounted controls where a board sits directly behind the panel
2. a power/control/backplane board that lands the panel controls and routes them to the audio boards

For the denser stereo-control groups, option `2` is preferred.

## Raw Control Pin Convention

For passive panel controls, use these labels:

### Single Pot

- `HI`
- `WIPER`
- `LO`

### Dual-Gang Pot

- `L_HI`
- `L_WIPER`
- `L_LO`
- `R_HI`
- `R_WIPER`
- `R_LO`

### SPDT Toggle

- `A`
- `C`
- `B`

### Encoded Mode Switch

For mode selectors that are decoded into logic-like control lines on the control backplane:

- `+5VAUX`
- `AGND`
- `CTL_*_A`
- `CTL_*_B`

## Harness Set

### H21 Wet / Dry Control

- from: panel dual-gang pot
- to: I/O board `P5` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `WD_L_HI`
  - `WD_L_WIPER`
  - `WD_L_LO`
  - `WD_R_HI`
  - `WD_R_WIPER`
  - `WD_R_LO`

### H22 Mono Source To Stereo

- from: panel SPDT toggle
- to: I/O board `P6` or control backplane landing
- preferred connector: `JST XH` 3-position
- conductors:
  - `MONO_A`
  - `MONO_C`
  - `MONO_B`

### H23 Ext Reverb Tanks Amount

- from: panel dual-gang pot
- to: ext-routing board analog-control input or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `EXTMIX_L_HI`
  - `EXTMIX_L_WIPER`
  - `EXTMIX_L_LO`
  - `EXTMIX_R_HI`
  - `EXTMIX_R_WIPER`
  - `EXTMIX_R_LO`

### H24 Ext Reverb Tanks Mode

- from: panel mode rotary
- to: ext-routing board or control backplane logic landing
- preferred connector: `JST XH` 4-position
- conductors:
  - `+5VAUX`
  - `AGND`
  - `CTL_EXT_MODE_A`
  - `CTL_EXT_MODE_B`

Encoding:

- `00` = `Off`
- `10` = `Series`
- `11` = `Parallel`
- `01` = reserved / off-equivalent service state

### H25 Crossfade Amount

- from: panel dual-gang pot
- to: crossfade / feedback / wet board `P307` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `XFD_L_HI`
  - `XFD_L_WIPER`
  - `XFD_L_LO`
  - `XFD_R_HI`
  - `XFD_R_WIPER`
  - `XFD_R_LO`

### H26 Feedback Amount

- from: panel dual-gang pot
- to: crossfade / feedback / wet board `P307` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `FB_L_HI`
  - `FB_L_WIPER`
  - `FB_L_LO`
  - `FB_R_HI`
  - `FB_R_WIPER`
  - `FB_R_LO`

### H27 Feedback Phase

- from: panel SPDT toggle or backplane-encoded control
- to: crossfade / feedback / wet board `P307`
- preferred connector: `JST XH` 4-position if encoded
- conductors:
  - `+5VAUX`
  - `AGND`
  - `CTL_FB_INV`
  - `SPARE`

Preferred implementation note:

- if the phase inversion is executed by a local relay or analog switch on the crossfade board, this encoded harness is preferred
- if the phase switch itself is mounted directly on the crossfade board, no separate harness is needed

### H28 Drive

- from: panel single-gang pot
- to: filter / clipper board `P403` or control backplane landing
- preferred connector: `JST XH` 3-position
- conductors:
  - `DRV_HI`
  - `DRV_WIPER`
  - `DRV_LO`

### H29 HPF Cutoff

- from: panel dual-gang pot
- to: filter / clipper board `P403` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `HPF_F_L_HI`
  - `HPF_F_L_WIPER`
  - `HPF_F_L_LO`
  - `HPF_F_R_HI`
  - `HPF_F_R_WIPER`
  - `HPF_F_R_LO`

### H30 HPF Q

- from: panel dual-gang pot
- to: filter / clipper board `P405` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `HPF_Q_L_HI`
  - `HPF_Q_L_WIPER`
  - `HPF_Q_L_LO`
  - `HPF_Q_R_HI`
  - `HPF_Q_R_WIPER`
  - `HPF_Q_R_LO`

### H31 LPF Cutoff

- from: panel dual-gang pot
- to: filter / clipper board `P403` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `LPF_F_L_HI`
  - `LPF_F_L_WIPER`
  - `LPF_F_L_LO`
  - `LPF_F_R_HI`
  - `LPF_F_R_WIPER`
  - `LPF_F_R_LO`

### H32 LPF Q

- from: panel dual-gang pot
- to: filter / clipper board `P405` or control backplane landing
- preferred connector: `JST XH` 6-position
- conductors:
  - `LPF_Q_L_HI`
  - `LPF_Q_L_WIPER`
  - `LPF_Q_L_LO`
  - `LPF_Q_R_HI`
  - `LPF_Q_R_WIPER`
  - `LPF_Q_R_LO`

### H33 Clip Mode

- from: panel rotary selector
- to: filter / clipper board `P405` or control backplane landing
- preferred connector: `JST XH` 4-position
- conductors:
  - `+5VAUX` — **source is the panel 5V bus, NOT the filter board.**
    The filter board's `P405` pin 9 is a spare with no on-board 5V feed
    (its power input H13/`P404` is ±15V only). Feed the clip rotary common
    from the same +5VAUX bus that feeds the ext-mode rotary common
    (arrives at the panel on ext board `P206` pin 7, sourced from
    power-backplane `P506.4` via `P207.4`). One short panel jumper wire
    between the two rotary commons is the rev-A wiring.
    Do not wire `P405` pin 9 as the 5V source — the clip relays would
    never energize. (Found in the 2026-07-04 pre-order review; a 4-pin
    `P404`/`P504` power feed is the recorded rev-B fix.)
  - `AGND`
  - `CTL_CLIP_MODE_A`
  - `CTL_CLIP_MODE_B`

Encoding:

- `00` = `Clean`
- `01` = `Silicon`
- `10` = `LED`
- `11` = `Germanium`

## Practical Result

This wiring map makes two important rev-A implications explicit:

1. `Wet / Dry`, `Ext Amount`, `Crossfade`, `Feedback`, `HPF Cutoff`, `HPF Q`, `LPF Cutoff`, and `LPF Q` are all better treated as real 6-wire stereo controls if they are off-board.
2. a control-backplane or locally board-mounted controls are cleaner than pretending all of these can be handled by a few tiny generic control headers.
