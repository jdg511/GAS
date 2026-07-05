# GAS Rev A Controls And Panel

This document captures the user-facing controls and service-endcap assumptions for the analog hardware.

## Enclosure Context

- cylindrical tube enclosure
- about `48 in` long
- target diameter `10 in` nominal
- all user connections and DC power entry on one circular endcap

Because the control count is high and the I/O format is fixed, the endcap is now the primary user interface rather than a conventional flat rack front panel.

## External Audio Connectors

Rev A uses combo `XLR / TRS` connectors for balanced line I/O.

### Proposed Panel I/O Count

- `J1` left input combo jack
- `J2` right input combo jack
- `J3` left output combo jack
- `J4` right output combo jack
- `J5` DC power jack for the external `+24 VDC` wall adapter

### Electrical Intent

- nominal balanced line level `+4 dBu`
- 600-ohm capable interfacing
- wall power stays outside the enclosure; only low-voltage DC enters the service endcap

## Core Controls

### Input / Output Section

- `Wet / Dry`
  - continuous control
- `Mono -> Stereo`
  - dedicated switch
  - duplicates the selected mono input into both internal channels after the balanced receiver

### Ext Tank Section

- `Ext Reverb Tanks`
  - `Off`
  - `Series`
  - `Parallel`
- `Ext Reverb Tanks Amount`
  - continuous control

### Crossfade / Feedback Section

- `Crossfade Amount`
  - continuous control
- `Feedback`
  - continuous control
- `Feedback Phase`
  - switch
  - normal / invert

### Filter / Clipping Section

- `Drive`
  - continuous control
- `HPF Cutoff`
  - continuous control
- `HPF Q`
  - continuous control
- `LPF Cutoff`
  - continuous control
- `LPF Q`
  - continuous control
- `Clip Mode`
  - `Clean`
  - `Silicon`
  - `LED`
  - `Germanium`

## Recommended Rev A Control Hardware Split

### Rotaries / Toggles

- ext tank mode rotary
- clip mode rotary
- mono-to-stereo switch
- feedback phase switch

### Pots

- wet/dry
- ext tank amount
- crossfade
- feedback
- drive
- HPF cutoff
- HPF Q
- LPF cutoff
- LPF Q

## Panel-Layout Consequences

- The unit has a relatively control-dense **circular endcap**
- The combo-jack requirement takes the widest chord across the face
- `10 in` nominal diameter is the preferred rev-A target: it fits four combo jacks plus the full control set with margin, and unlike `9 in` it is a standard off-the-shelf pipe/cap size
- Keep the mono-to-stereo switch near the input section so the behavior reads clearly
- Keep ext-tank mode and amount adjacent so Off / Series / Parallel behavior is easier to understand
- Keep feedback amount and feedback phase together
- Keep filter and clip controls grouped as one section
- Keep the DC jack away from the center knob field so a plugged-in barrel cable does not block hand access

## Builder Note

The panel hardware is not the same thing as the SMD core BOM.

Treat the panel layer as:

- combo jacks
- DC jack
- switches
- pots
- knobs
- circular endcap drilling/cutouts

That lets the analog PCBs stay modular while the enclosure is refined separately.

## Preferred Rev A Control Wiring

Two control-wiring strategies are acceptable in rev A:

1. board-mounted controls where the PCB can sit directly behind the panel
2. a separate power/control/backplane board that lands panel pots and switches, then fans them out to the audio boards

The second option is preferred for the denser sections:

- ext tank mode and amount
- crossfade and feedback
- filter and clipping controls

The simple local exceptions are:

- `Wet / Dry`
- `Mono -> Stereo`

Further endcap zoning detail lives in [rev-a-endcap-panel-layout.md](C:/U