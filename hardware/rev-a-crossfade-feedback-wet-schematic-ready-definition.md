# GAS Rev A Crossfade / Feedback / Wet Schematic-Ready Definition

This file is the direct electrical definition for the rev-A crossfade / feedback / wet board.

It is more specific than [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1) and [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1), but it still leaves room for loop-gain tuning against the real tanks.

Use this file when:

- promoting the current KiCad `crossfade-feedback-wet.kicad_sch` page from single-unit placeholder capture to a true multi-unit schematic
- freezing the first-pass crossfade and feedback topology before the eventual KiCad wiring pass
- checking that the wet return back to the I/O board and the feedback reinjection path remain clearly separable

## 1. Assumed First-Pass Circuit Strategy

This definition freezes the first-pass topology as:

- passive stereo crossfade pot landing on `P307`, with one dual track per channel
- `U301A` and `U301B` used as left and right inverting crossfade summers that drive the filter board
- `FILTCLIP_OUT_L/R` returning from the filter board as the authoritative post-tone/clip wet path
- direct final wet handoff back to the I/O board through small output isolators
- one inverting feedback-driver stage per channel using `U301C` and `U301D`
- feedback phase selection happening only in the feedback send path, never in the direct wet return

Important note:

- the currently checked-in `P307` 10-pin grouped header is a placeholder that is sufficient for crossfade plus feedback-phase capture, but it is still compressed for a fully passive off-board stereo feedback pot
- if the feedback amount control is kept as a true off-board dual-gang passive control, the later KiCad pass must either promote the control header or move the feedback pot physically onto a control-backplane PCB that owns the missing endpoints

## 2. Required KiCad Multi-Unit Promotion

The checked-in `crossfade-feedback-wet.kicad_sch` still has only one symbol unit placed for `U301`. The real capture pass should promote the sheet to this exact unit set:

| Ref | Unit | Job |
| --- | --- | --- |
| `U301` | `1` | `U301A` left crossfade summer |
| `U301` | `2` | `U301B` right crossfade summer |
| `U301` | `3` | `U301C` left feedback driver |
| `U301` | `4` | `U301D` right feedback driver |
| `U301` | `5` | power pins |

## 3. Header Pin Ownership

### P301 `JTR-XFADE`

| Pin | Net |
| --- | --- |
| `1` | `TANK_MIX_L` |
| `2` | `AGND` |
| `3` | `TANK_MIX_R` |

### P302 `JXF-FILT`

| Pin | Net |
| --- | --- |
| `1` | `XFADE_OUT_L` |
| `2` | `AGND` |
| `3` | `XFADE_OUT_R` |

### P303 `JFILT-WET`

| Pin | Net |
| --- | --- |
| `1` | `FILTCLIP_OUT_L` |
| `2` | `AGND` |
| `3` | `FILTCLIP_OUT_R` |

### P304 `JIO-WETRET`

| Pin | Net |
| --- | --- |
| `1` | `WET_SUM_L` |
| `2` | `AGND` |
| `3` | `WET_SUM_R` |

### P305 `JFB-INJ`

| Pin | Net |
| --- | --- |
| `1` | `FB_RET_L` |
| `2` | `AGND` |
| `3` | `FB_RET_R` |

### P306 `JXFD-PWR`

| Pin | Net |
| --- | --- |
| `1` | `+15VA` |
| `2` | `AGND` |
| `3` | `-15VA` |

### P307 Control Landing

Keep the currently captured pin ownership below for the first real KiCad pass:

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `XFD_L_HI` | left crossfade top end |
| `2` | `XFD_L_WIPER` | left crossfade wiper |
| `3` | `XFD_L_LO` | left crossfade bottom end |
| `4` | `XFD_R_HI` | right crossfade top end |
| `5` | `XFD_R_WIPER` | right crossfade wiper |
| `6` | `XFD_R_LO` | right crossfade bottom end |
| `7` | `FB_L_WIPER` | compressed left feedback control landing |
| `8` | `FB_R_WIPER` | compressed right feedback control landing |
| `9` | `CTL_FB_INV` | feedback phase invert control |
| `10` | `AGND` | local control reference |

## 4. Internal Audio Nodes

Use these node names when drawing the final KiCad page:

| Node | Meaning |
| --- | --- |
| `XFADE_L_SRC_A` | left-side source end of the left crossfade track |
| `XFADE_L_SRC_B` | right-side source end of the left crossfade track |
| `XFADE_R_SRC_A` | right-side source end of the right crossfade track |
| `XFADE_R_SRC_B` | left-side source end of the right crossfade track |
| `XFADE_SUM_L` | left crossfade-summer output from `U301A` |
| `XFADE_SUM_R` | right crossfade-summer output from `U301B` |
| `WET_POST_L` | left post-filter wet source from `P303 pin 1` |
| `WET_POST_R` | right post-filter wet source from `P303 pin 3` |
| `FB_INV_L` | left inverted feedback-drive output from `U301C` |
| `FB_INV_R` | right inverted feedback-drive output from `U301D` |
| `FB_SEL_L` | left post-phase-select feedback send |
| `FB_SEL_R` | right post-phase-select feedback send |

## 5. Exact First-Pass Passive Map

### Crossfade Pot Landing

Wire the raw crossfade landing as:

- `XFD_L_HI` from `TANK_MIX_L`
- `XFD_L_LO` from `TANK_MIX_R`
- `XFD_R_HI` from `TANK_MIX_R`
- `XFD_R_LO` from `TANK_MIX_L`

This gives the two-gang control a mirrored stereo role:

- one track moves the left filter send between left and right tank blends
- the other track moves the right filter send between right and left tank blends

### Crossfade Summers

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R301` | `20k` | `XFD_L_WIPER` | `U301A-` | left crossfade entry |
| `R302` | `20k` | `XFD_R_WIPER` | `U301B-` | right crossfade entry |
| `R309` | `20k` | `U301A out` | `U301A-` | left unity-gain feedback |
| `R310` | `20k` | `U301B out` | `U301B-` | right unity-gain feedback |
| `R311` | `100R` | `U301A out` | `P302 pin 1` | left filter-send isolator |
| `R312` | `100R` | `U301B out` | `P302 pin 3` | right filter-send isolator |

Wire the non-inverting inputs as:

- `U301A+` to `AGND`
- `U301B+` to `AGND`

### Final Wet Return

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R341` | `100R` | `FILTCLIP_OUT_L` | `P304 pin 1` | left final wet isolator |
| `R342` | `100R` | `FILTCLIP_OUT_R` | `P304 pin 3` | right final wet isolator |

The direct wet return to the I/O board should remain:

- sourced from `FILTCLIP_OUT_L/R`
- unaffected by `CTL_FB_INV`
- unaffected by the feedback amount control except through any sonic change caused by the loop itself

### Feedback Driver Stages

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R321` | `20k` | `FILTCLIP_OUT_L` | `U301C-` | left feedback-driver input |
| `R322` | `20k` | `FILTCLIP_OUT_R` | `U301D-` | right feedback-driver input |
| `R323` | `20k`, trim-friendly | `FB_L_WIPER network` | `U301C-` | left adjustable feedback return path |
| `R324` | `20k`, trim-friendly | `FB_R_WIPER network` | `U301D-` | right adjustable feedback return path |
| `R325` | `10k` | `U301C out` | `U301C-` | left minimum loop-floor feedback |
| `R326` | `10k` | `U301D out` | `U301D-` | right minimum loop-floor feedback |
| `C321` | `47 pF`, DNP default | `U301C out` | `U301C-` | left stability footprint |
| `C322` | `47 pF`, DNP default | `U301D out` | `U301D-` | right stability footprint |

Wire the non-inverting inputs as:

- `U301C+` to `AGND`
- `U301D+` to `AGND`

### Feedback Phase Selection

Use `CTL_FB_INV` only to choose which left/right source reaches `P305`:

- normal phase: `FB_SEL_L` from `FILTCLIP_OUT_L`, `FB_SEL_R` from `FILTCLIP_OUT_R`
- inverted phase: `FB_SEL_L` from `U301C out`, `FB_SEL_R` from `U301D out`

Reserve these output parts:

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R331` | `100R` | phase-selected left feedback source | `P305 pin 1` | left feedback-send isolator |
| `R332` | `100R` | phase-selected right feedback source | `P305 pin 3` | right feedback-send isolator |

## 6. Functional Wiring Summary By Stage

### Crossfade Path

- `TANK_MIX_L/R` arrive at `P301`
- the dual crossfade control at `P307` creates `XFD_L_WIPER` and `XFD_R_WIPER`
- `U301A/B` convert those wiper positions into low-impedance `XFADE_OUT_L/R`
- `P302` hands those signals to the filter/clipper board

### Wet Return Path

- `FILTCLIP_OUT_L/R` return at `P303`
- `R341/R342` pass them directly to `P304` as `WET_SUM_L/R`

### Feedback Path

- `FILTCLIP_OUT_L/R` also feed the inverting feedback drivers `U301C/D`
- `CTL_FB_INV` selects between direct post-filter phase and inverted-driver phase
- the selected feedback signals leave on `P305` as `FB_RET_L/R`

## 7. Local Decoupling Intent

Reserve `C391-C399` for local rail decoupling.

First-pass intent:

- one `100 nF` from `+15VA` to `AGND` near the `U301` power unit
- one `100 nF` from `-15VA` to `AGND` near the `U301` power unit
- one local `10 uF` to `22 uF` bulk footprint per rail pair is acceptable because these are power-path parts

## 8. Verification Gate For The Later KiCad Pass

When this definition is translated into the final multi-unit KiCad page, verify all of the following:

1. `U301` has all four signal units plus its power unit instantiated.
2. `P302`, `P304`, and `P305` all keep the frozen `signal / AGND / signal` pin order from the harness map.
3. `CTL_FB_INV` only affects the feedback send path and does not flip the direct wet return polarity.
4. `WET_SUM_L/R` are sourced from the post-filter wet path, not from the pre-filter crossfade outputs.
5. The feedback path remains visually and electrically distinct from the direct wet-return path.

## 9. Explicitly Deferred Items

These are intentionally deferred:

- the exact mechanical implementation of the feedback amount control if the final build keeps it as an off-board passive dual-gang control
- any later decision to promote `P307` to a larger header or split control landing for a more honest raw passive harness
- whether the loop-gain range around `R323/R324` stays near unity or needs more aggressive gain after the first real tank session
