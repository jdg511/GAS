# GAS Rev A Pipe Enclosure Concept

This file freezes the first usable mechanical concept for the real enclosure.

## Locked Rev-A Direction

- The shell is a **user-supplied cylindrical tube**
- Target diameter is **`10 in` nominal, preferred** (`8 in` minimum fallback)
- `10 in` chosen over the earlier `9 in` preference because standard pipe, cap, and sonotube sizes jump from `8 in` to `10 in` — `9 in` is effectively a custom part
- nominal is not actual: `10 in` steel pipe is `10.75 in` OD and PVC cap styles differ; final metalwork must use the measured face of the purchased cap
- Target length is about **`48 in`**
- All user-facing I/O and power entry live on **one circular service endcap**
- The opposite endcap is mechanically simple and normally has no external connectors

This matches the Great British Spring style the user pointed to and gives the tanks a long, quiet interior volume.

## What The User Supplies

Treat these as consigned mechanical items, not part of the PCB-house quote:

- cylindrical enclosure tube
- the four spring tanks

The electronics package should therefore focus on:

- PCBs
- internal rails or sled
- circular endcap cut files
- panel hardware
- internal harnesses

## Preferred Mechanical Stack

From the service endcap toward the closed end:

1. service endcap and circular face hardware
2. input/output PCB directly behind the combo-jack field
3. power/control backplane adjacent to the endcap so DC entry and star ground stay short
4. ext-routing, crossfade/feedback, and filter boards on a longitudinal rail pair
5. tank-driver/recovery board farther down the tube, as far from relay and power noise as practical
6. spring tanks mounted along the tube wall or on an internal subframe

## Internal Mounting Strategy

Preferred rev-A mechanical method:

- two longitudinal aluminum rails or angle brackets
- boards mounted perpendicular to the endcap, plugged or harnessed inward along the tube axis
- tanks mounted on separate isolation hardware, not on PCB standoffs

Why:

- it keeps the service end dense and short-wired
- it lets the quiet tank-recovery area live deeper in the tube
- it makes the endcap removable for service without unmounting the tanks

## Diameter Recommendation

If the unit must carry:

- `4x` combo `XLR / TRS` jacks
- `1x` DC jack
- `9x` pots
- `2x` rotary switches
- `2x` toggles

then **`10 in` nominal is the practical rev-A target**.

The frozen hole-table layout also passes all spacing rules on a `9 in` face, so `9 in` remains a functional fallback if one turns up — the preference for `10 in` is sourcing, not fit. `8 in` may still work, but only with tighter spacing, smaller knob selection, or a more aggressive two-ring control layout.

## Endcap Material Direction

Recommended first pass:

- structural endcap: `0.125 in` aluminum or steel plate
- cosmetic overlay or direct print: engraved/anodized aluminum, UV print, or silkscreen

The endcap needs to be rigid enough that:

- combo-jack insertion force does not flex it
- large control pots remain aligned
- the DC jack does not loosen under cable pull

## Tank Placement Direction

- primary `4AB1C1B` tanks should mount closer to the service end than the secondary tanks only if harness lengths demand it
- otherwise, group all tanks toward the quiet half of the tube
- keep recovery cabling away from the power-entry sidewall
- use shielded RCA harnesses and keep send and return bundles physically separated

## Mechanical Deliverables This Concept Implies

Before metalwork freeze, the rev-A package should produce:

- circular endcap drilling drawing
- internal rail spacing drawing
- board-outline and standoff map
- tank mounting map
- harness cut-length table

This repo now covers the first two conceptually, but not yet as fabrication drawings.
