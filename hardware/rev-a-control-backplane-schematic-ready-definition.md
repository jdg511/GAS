# GAS Rev A Control Backplane Schematic-Ready Definition

This file is the direct electrical definition for the rev-A control backplane layer.

It is the practical companion to [rev-a-control-backplane-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-definition.md:1), [rev-a-control-harnesses.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-harnesses.md:1), and [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1).

Use this file when:

- deciding whether the current rev-A control strategy stays as a distinct backplane or collapses into direct panel wiring
- translating the dense-control wiring into a future KiCad page or a later expansion of the current `power-backplane.kicad_sch`
- checking that the panel control layer stays analog-only and honest about which controls are raw passive landings versus encoded mode selectors

## 1. Assumed First-Pass Control-Backplane Strategy

This definition freezes the first-pass control-backplane role as:

- no audio signal processing on the backplane
- passive landing and redistribution for off-board pots and switches
- local generation of the encoded mode pairs for ext-routing and clip mode
- optional future reserve for simple coil or indicator support, but not relied on by the current frozen inter-board harness

Important note:

- the current rev-A harness contract between the control layer and the ext-routing board carries only `CTL_EXT_MODE_A` and `CTL_EXT_MODE_B`
- because of that, a `ULN2003ADR` on the control backplane cannot directly drive the ext-routing relay coils without changing the frozen inter-board interface
- if rev A keeps the simplest direct-drive relay strategy, those two exported mode lines should be interpreted as the switched `+5VAUX` outputs themselves, not as separate logic-only sense lines
- therefore `U601` should be treated as a reserve-only symbol for now, not a required populated rev-A part

## 2. First-Pass Electrical Boundary

The control backplane should remain fully compatible with the current project constraints:

- no MCU
- no programmable logic
- no digital audio
- no computer-style control plane

The only active behavior currently justified here is:

- switch-to-bit encoding for mode selectors
- optional passive or transistorized indicator/relay support if the inter-board interface later grows to support it

## 3. Board-Side Connector Ownership

### P601 Backplane Power

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `+5VAUX` | main control logic-high rail |
| `2` | `AGND` | control reference |
| `3` | `+15VA` | reserve split rail |
| `4` | `-15VA` | reserve split rail |

Practical rule:

- the current rev-A passive control scheme should assume only `+5VAUX` and `AGND` are required on the backplane
- `+15VA` and `-15VA` remain reserved for later analog buffer or indicator support and should not be assumed by the base passive wiring

### P610 I/O Controls

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `WD_L_HI` | left wet/dry pot dry end |
| `2` | `WD_L_WIPER` | left wet/dry wiper |
| `3` | `WD_L_LO` | left wet/dry pot wet end |
| `4` | `WD_R_HI` | right wet/dry pot dry end |
| `5` | `WD_R_WIPER` | right wet/dry wiper |
| `6` | `WD_R_LO` | right wet/dry pot wet end |
| `7` | `MONO_A` | mono switch throw A |
| `8` | `MONO_C` | mono switch common |
| `9` | `MONO_B` | mono switch throw B |

### P611 Ext Routing Controls

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `EXTMIX_L_HI` | left ext-amount top end |
| `2` | `EXTMIX_L_WIPER` | left ext-amount wiper |
| `3` | `EXTMIX_L_LO` | left ext-amount low end |
| `4` | `EXTMIX_R_HI` | right ext-amount top end |
| `5` | `EXTMIX_R_WIPER` | right ext-amount wiper |
| `6` | `EXTMIX_R_LO` | right ext-amount low end |
| `7` | `+5VAUX` | mode-encoding high rail |
| `8` | `AGND` | mode-encoding reference |
| `9` | `CTL_EXT_MODE_A` | ext-mode encoded bit A |
| `10` | `CTL_EXT_MODE_B` | ext-mode encoded bit B |

### P612 Crossfade / Feedback Controls

Keep the current rev-A grouped landing below, but treat it as a consciously compressed interface:

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `XFD_L_HI` | left crossfade top end |
| `2` | `XFD_L_WIPER` | left crossfade wiper |
| `3` | `XFD_L_LO` | left crossfade low end |
| `4` | `XFD_R_HI` | right crossfade top end |
| `5` | `XFD_R_WIPER` | right crossfade wiper |
| `6` | `XFD_R_LO` | right crossfade low end |
| `7` | `FB_L_WIPER` | left feedback control wiper only |
| `8` | `FB_R_WIPER` | right feedback control wiper only |
| `9` | `CTL_FB_INV` | feedback invert control |
| `10` | `AGND` | control reference |

Practical rule:

- this is sufficient for the current placeholder capture
- it is not yet a fully honest raw passive dual-gang feedback-pot interface
- before final PCB release, either:
  - promote this into a larger raw-feedback header set, or
  - make the feedback pot local to the control backplane and explicitly generate the missing endpoint references there

### P613 Filter / Clipper Controls A

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `DRV_HI` | drive-pot top end |
| `2` | `DRV_WIPER` | drive-pot wiper |
| `3` | `DRV_LO` | drive-pot low end |
| `4` | `HPF_F_L_HI` | left HPF cutoff top end |
| `5` | `HPF_F_L_WIPER` | left HPF cutoff wiper |
| `6` | `HPF_F_L_LO` | left HPF cutoff low end |
| `7` | `HPF_F_R_HI` | right HPF cutoff top end |
| `8` | `HPF_F_R_WIPER` | right HPF cutoff wiper |
| `9` | `HPF_F_R_LO` | right HPF cutoff low end |
| `10` | `HPF_Q_L_WIPER` | left HPF-Q wiper only |
| `11` | `HPF_Q_R_WIPER` | right HPF-Q wiper only |
| `12` | `AGND` | control reference |

### P614 Filter / Clipper Controls B

| Pin | Net | Meaning |
| --- | --- | --- |
| `1` | `LPF_F_L_HI` | left LPF cutoff top end |
| `2` | `LPF_F_L_WIPER` | left LPF cutoff wiper |
| `3` | `LPF_F_L_LO` | left LPF cutoff low end |
| `4` | `LPF_F_R_HI` | right LPF cutoff top end |
| `5` | `LPF_F_R_WIPER` | right LPF cutoff wiper |
| `6` | `LPF_F_R_LO` | right LPF cutoff low end |
| `7` | `LPF_Q_L_WIPER` | left LPF-Q wiper only |
| `8` | `LPF_Q_R_WIPER` | right LPF-Q wiper only |
| `9` | `+5VAUX` | clip-mode encoding high rail |
| `10` | `CTL_CLIP_MODE_A` | clip-mode encoded bit A |
| `11` | `CTL_CLIP_MODE_B` | clip-mode encoded bit B |
| `12` | `AGND` | control reference |

Practical rule:

- `P613` and `P614` are sufficient for the current grouped-control placeholder strategy
- the `HPF_Q_*` and `LPF_Q_*` entries are still compressed relative to a fully raw passive stereo pot landing
- before final PCB release, either:
  - promote those Q controls into fuller raw passive interfaces, or
  - make the Q controls local to the control backplane and explicitly generate the missing endpoint references there

## 4. Panel-Side Hardware Ownership

Use these panel refs as the first-pass control-backplane ownership map:

| Ref | Type | Function |
| --- | --- | --- |
| `VR701` | dual pot | wet/dry |
| `VR702` | dual pot | ext amount |
| `VR703` | dual pot | crossfade |
| `VR704` | dual pot | feedback |
| `VR705` | single pot | drive |
| `VR706` | dual pot | HPF cutoff |
| `VR707` | dual pot | HPF Q |
| `VR708` | dual pot | LPF cutoff |
| `VR709` | dual pot | LPF Q |
| `SW701` | SPDT or 3-state source switch | mono/stereo |
| `SW702` | SPDT | feedback invert |
| `J701` | rotary mode switch | ext mode |
| `J702` | rotary mode switch | clip mode |

## 5. Raw Passive Wiring Ownership

### Wet / Dry

`VR701` should wire directly to `P610`:

- left track to `WD_L_HI`, `WD_L_WIPER`, `WD_L_LO`
- right track to `WD_R_HI`, `WD_R_WIPER`, `WD_R_LO`

### Ext Amount

`VR702` should wire directly to `P611`:

- left track to `EXTMIX_L_HI`, `EXTMIX_L_WIPER`, `EXTMIX_L_LO`
- right track to `EXTMIX_R_HI`, `EXTMIX_R_WIPER`, `EXTMIX_R_LO`

### Crossfade

`VR703` should wire directly to `P612`:

- left track to `XFD_L_HI`, `XFD_L_WIPER`, `XFD_L_LO`
- right track to `XFD_R_HI`, `XFD_R_WIPER`, `XFD_R_LO`

### Feedback

`VR704` is not yet fully represented as a raw passive interface in the frozen 10-pin grouping.

Therefore the current schematic-ready interpretation is:

- `FB_L_WIPER` and `FB_R_WIPER` are the only mandatory frozen boundary nets today
- the exact local endpoint generation for the feedback dual pot remains a later design choice

### Drive

`VR705` should wire directly to `P613`:

- `DRV_HI`, `DRV_WIPER`, `DRV_LO`

### HPF Cutoff

`VR706` should wire directly to `P613`:

- left track to `HPF_F_L_HI`, `HPF_F_L_WIPER`, `HPF_F_L_LO`
- right track to `HPF_F_R_HI`, `HPF_F_R_WIPER`, `HPF_F_R_LO`

### HPF Q

`VR707` is only partially represented in the current grouped interface:

- mandatory frozen nets today are `HPF_Q_L_WIPER` and `HPF_Q_R_WIPER`
- the endpoint strategy remains deferred unless the interface is promoted

### LPF Cutoff

`VR708` should wire directly to `P614`:

- left track to `LPF_F_L_HI`, `LPF_F_L_WIPER`, `LPF_F_L_LO`
- right track to `LPF_F_R_HI`, `LPF_F_R_WIPER`, `LPF_F_R_LO`

### LPF Q

`VR709` is only partially represented in the current grouped interface:

- mandatory frozen nets today are `LPF_Q_L_WIPER` and `LPF_Q_R_WIPER`
- the endpoint strategy remains deferred unless the interface is promoted

## 6. Encoded Mode Ownership

### SW701 Mono Switch

`SW701` should remain the raw 3-wire switch landing:

| Switch Terminal | Net |
| --- | --- |
| `A` | `MONO_A` |
| `C` | `MONO_C` |
| `B` | `MONO_B` |

### SW702 Feedback Invert

The first-pass interpretation should stay simple:

- `CTL_FB_INV` is asserted or grounded by `SW702`
- `AGND` is the low state
- if needed, a pull-up or pull-down can live locally on the target board rather than on the backplane

### J701 Ext Mode

Freeze `J701` as a two-pole three-position rotary or functionally equivalent discrete analog switch arrangement.

Required bit map:

| User Position | `CTL_EXT_MODE_A` | `CTL_EXT_MODE_B` |
| --- | --- | --- |
| `Off` | `0` | `0` |
| `Series` | `1` | `0` |
| `Parallel` | `1` | `1` |

The unused `01` state should remain unselected by the panel hardware.

### J702 Clip Mode

Freeze `J702` as a two-pole four-position rotary or functionally equivalent discrete analog switch arrangement.

Required bit map:

| User Position | `CTL_CLIP_MODE_A` | `CTL_CLIP_MODE_B` |
| --- | --- | --- |
| `Clean` | `0` | `0` |
| `Silicon` | `0` | `1` |
| `LED` | `1` | `0` |
| `Germanium` | `1` | `1` |

## 7. `U601` Reserve Policy

`U601` `ULN2003ADR` should remain a reserve-only footprint or symbol unless the inter-board control contract changes.

Reason:

- the current frozen ext-routing interface carries encoded mode lines, not direct coil-drive lines
- without additional coil-drive nets in the harness, the backplane cannot directly own relay sinking

Therefore the current rev-A policy is:

1. do not treat `U601` as required
2. keep it absent from any fixed populated BOM unless the harness contract changes
3. if a later revision moves relay sinking to the backplane, update:
   - `rev-a-interconnect-pin-map.md`
   - `rev-a-board-connector-schedule.csv`
   - `rev-a-ext-routing-schematic-ready-definition.md`
   - the KiCad manifests

## 8. Current KiCad Capture Relationship

The checked-in `power-backplane.kicad_sch` currently captures:

- `J500`
- `F500`
- `D500`
- `TVS500`
- `C500`
- `PS500`
- `PS501`
- `FB500`
- `FB501`
- `P501-P506`
- `P601`

It does not yet instantiate:

- `P610-P614`
- `U601`

That is acceptable for the present phase, but it means the control-backplane layer remains a definition-level artifact rather than a real KiCad-wired page today.

## 9. Verification Gate For The Later KiCad Pass

When this definition is translated into the later real KiCad control-backplane pass, verify all of the following:

1. `P601` keeps the frozen `+5VAUX / AGND / +15VA / -15VA` order.
2. `P610` and `P611` remain fully honest raw passive or encoded interfaces and are not compressed further.
3. `J701` and `J702` cannot select illegal intermediate states in normal panel use.
4. `U601` is only populated if the harness definition is updated to support real coil-drive ownership from the backplane.
5. Any remaining compressed grouped headers are called out explicitly on the schematic notes instead of being mistaken for fully raw passive harnesses.

## 10. Explicitly Deferred Items

These are intentionally deferred:

- whether the control-backplane remains a distinct PCB or is folded into an expanded power/backplane board
- the final endpoint strategy for the off-board feedback, HPF-Q, and LPF-Q passive controls
- any future indicator LED or relay-drive features that would justify populating `U601`
