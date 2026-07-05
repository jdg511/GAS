# GAS Rev A Endcap Panel Layout

This file translates the cylindrical-enclosure decision into a practical service-endcap layout.

## Panel Intent

The service endcap carries:

- left and right balanced inputs
- left and right balanced outputs
- DC power entry from the external wall adapter
- the rev-A user controls

All of that lands on one circular face.

## Preferred Endcap Diameter

- preferred: **`10 in` nominal** (standard pipe/cap size; measured face will be larger than `10.00 in` on most cap styles)
- the frozen layout also passes all rules on a `9.0 in` face; below that becomes risky once the combo-jack cutouts and nine control bushings are included

## Recommended Zones

### Upper Arc

Use for low-count switches and mode selectors:

- mono-input / stereo selector
- ext-tank mode
- clip mode
- feedback phase

These parts are visually important but do not need as much finger clearance as the combo jacks.

### Mid-Band

Reserve the widest chord across the circle for the connector field:

- `J1` left input combo jack
- `J2` right input combo jack
- `J3` left output combo jack
- `J4` right output combo jack

The reference image's "jack bar" concept is the right model here: mount these on a rectangular subpanel or shared reinforcement plate fastened to the circular endcap.

### Lower Arc

Use for the continuous controls:

- wet/dry
- ext amount
- crossfade
- feedback
- drive
- HPF cutoff
- HPF Q
- LPF cutoff
- LPF Q

The rev-A control count is high enough that the lower half should be treated as a two-row arc, not one straight row.

### Power Zone

Put the DC jack near the edge of the connector field, not at the center of the knob cluster:

- preferred location: lower-right or lower-left edge of the jack subpanel
- keep enough clearance for the wall-adapter barrel plug body and cable bend radius

## Spacing Rules To Preserve

- combo-jack center spacing: target `>= 31 mm`
- pot bushing center spacing: target `>= 24 mm`
- keep at least `12 mm` from any control hole edge to the circular endcap perimeter
- do not place the DC barrel plug where it blocks XLR latches or TRS cable insertion

## Recommended Mono Switch Interpretation

The minimum requirement is a dedicated mono-input-to-stereo function.

Because the unit has two inputs and the Great British Spring reference uses explicit source selection, the preferred rev-A user experience is:

- `Stereo`
- `Mono L -> L/R`
- `Mono R -> L/R`

If the final panel density makes that impractical, fall back to:

- `Stereo`
- `Mono L -> L/R`

and document the simplification on the panel art.

## PCB Consequence

The endcap layout strongly favors:

- combo jacks and the DC jack as panel parts
- short harnesses from those panel parts to the I/O board and power backplane
- a dedicated control-backplane landing board rather than forcing all controls onto one audio PCB

That is now the preferred rev-A interpretation.
