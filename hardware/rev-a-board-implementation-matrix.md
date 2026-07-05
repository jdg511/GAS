# GAS Rev A Board Implementation Matrix

This file turns the architecture into concrete board ownership so schematic capture does not drift.

## Board Summary

| Board | Main Function | Active Parts | Key Controls | Main Risk |
| --- | --- | --- | --- | --- |
| Input / Output | Balanced receive, mono-to-stereo, wet/dry sum, balanced drive | `1x OPA1644AIDR`, `3x OPA1656IDR` | Wet/Dry, Mono->Stereo | balanced I/O behavior and headroom |
| Tank Driver / Recovery | Tank send drive and tank recovery | `4x OPA1656IDR`, `2x BD139-16`, `2x BD140-16` | none on panel directly | primary send level and recovery noise |
| Ext Tank Routing | Off/Series/Parallel routing and secondary mix | `4x G6K-2F-Y-DC5`, `1x OPA1679IDR` | Ext Mode, Ext Mix | relay routing around sensitive recovery nodes |
| Crossfade / Feedback / Wet Summing | Stereo crossfade, feedback, wet handoff | `1x OPA1679IDR` | Crossfade, Feedback, Feedback Invert | loop stability |
| Filter / Clipping | HPF, drive, clipping, LPF | `2x OPA1679IDR` | Drive, HPF F/Q, LPF F/Q, Clip Mode | stereo tracking and clip switching artifacts |
| Power / Backplane | DC entry, rail conversion, star ground, harnessing | `1x URA2415YMD-10WR3`, `1x R-78E5.0-0.5` | none | ripple control and grounding |

## Input / Output Board Allocation

### U1 `OPA1644AIDR`

- balanced input receiver left
- balanced input receiver right
- mono-to-stereo routing buffer left
- mono-to-stereo routing buffer right or spare unity-gain utility stage

### U2 `OPA1656IDR`

- wet/dry mix left
- wet/dry mix right

### U3 `OPA1656IDR`

- balanced output driver left hot
- balanced output driver left cold

### U4 `OPA1656IDR`

- balanced output driver right hot
- balanced output driver right cold

### I/O Board Connectors

- `J1` left combo `XLR / TRS`
- `J2` right combo `XLR / TRS`
- `J3` left combo `XLR / TRS` output
- `J4` right combo `XLR / TRS` output
- `P1` power
- `P2` wet send
- `P3` wet return
- `P4` dry distribution
- `P5` wet/dry control
- `P6` mono-to-stereo switch

## Tank Driver / Recovery Board Allocation

### U101 `OPA1656IDR`

- primary left send predriver
- primary right send predriver

### Q101 / Q102 / Q103 / Q104 `BD139-16` / `BD140-16`

- complementary output pair for primary left send
- complementary output pair for primary right send

### U102 `OPA1656IDR`

- secondary left tank send
- secondary right tank send

### U103 `OPA1656IDR`

- primary left recovery
- primary right recovery

### U104 `OPA1656IDR`

- secondary left recovery
- secondary right recovery

### Tank Board Connectors

- `P101` primary routing bundle
- `P102` secondary routing bundle
- `P103` power
- `J101-J108` tank send/return landings

## Ext Tank Routing Board Allocation

### K201-K204 `G6K-2F-Y-DC5`

- route primary and secondary path state for Off / Series / Parallel

### U201 `OPA1679IDR`

- left final routing / wet-output sum
- right final routing / wet-output sum
- left secondary-send buffer
- right secondary-send buffer

### Routing Board Connectors

- `P201` wet input from I/O board
- `P202` primary tank bundle
- `P203` secondary tank bundle
- `P204` routed output to crossfade board
- `P205` feedback reinjection input
- `P206` control or panel-backplane header
- `P207` power input including `+5VAUX`

## Crossfade / Feedback / Wet Summing Board Allocation

### U301 `OPA1679IDR`

- `U301A` left inverting crossfade summer
- `U301B` right inverting crossfade summer
- `U301C` left feedback driver / invert stage
- `U301D` right feedback driver / invert stage
- `U301` power unit for local `+15VA / -15VA` decoupling ownership

### Crossfade / Feedback / Wet Connectors

- `P301` routed tank input: `TANK_MIX_L`, `AGND`, `TANK_MIX_R`
- `P302` send to filter / clipper: `XFADE_OUT_L`, `AGND`, `XFADE_OUT_R`
- `P303` filter return: `FILTCLIP_OUT_L`, `AGND`, `FILTCLIP_OUT_R`
- `P304` direct wet return to I/O board: `WET_SUM_L`, `AGND`, `WET_SUM_R`
- `P305` feedback reinjection output: `FB_RET_L`, `AGND`, `FB_RET_R`
- `P306` power input: `+15VA`, `AGND`, `-15VA`
- `P307` grouped control landing for crossfade, feedback amount, and feedback phase invert

### Crossfade / Feedback / Wet Circuit Freeze Notes

- the direct wet return is sourced from the post-filter `FILTCLIP_OUT_L/R` path and is not phase-flipped
- `CTL_FB_INV` only changes the feedback-send source between direct and inverted paths
- the current `P307` header is good enough for rev-A capture, but still slightly compressed for a completely raw off-board passive feedback-pot implementation

## Filter / Clipping Board Allocation

### U401 `OPA1679IDR`

- left pre-HPF
- right pre-HPF
- left drive/clipping buffer
- right drive/clipping buffer

### U402 `OPA1679IDR`

- left post-LPF
- right post-LPF
- left output buffer
- right output buffer

### Filter / Clipping Connectors

- `P401` input from crossfade board
- `P402` output to crossfade/feedback board
- `P403` control group A
- `P404` power input
- `P405` control group B

## One Important Connector Caveat

Standard combo `XLR / TRS` receptacles are typically `XLR female + TRS`.

That is conventional for balanced inputs, but unconventional for XLR outputs.

Rev A therefore has two practical interpretations:

1. honor the combo-jack requirement literally and accept the unusual female-XLR output convention
2. use the combo format where physically possible, but treat the TRS side as the primary balanced output path

The project currently preserves the literal combo-jack requirement, but this should be sanity-checked before enclosure metalwork is frozen.
