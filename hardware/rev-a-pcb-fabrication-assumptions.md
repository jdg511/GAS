# GAS Rev A PCB Fabrication Assumptions

This file records the first-pass PCB fabrication assumptions for the analog hardware package.

## Default Board Style

Rev A should begin with conventional rigid FR-4 boards.

Preferred defaults:

- layer count: `2-layer`
- thickness: `1.6 mm`
- outer copper: `1 oz`
- surface finish: `ENIG`
- solder mask: green unless branding needs something else later
- silkscreen: white

Reason:

- these defaults are easy for prototype fabs
- the analog density does not currently demand more than 2 layers
- ENIG is friendly for mixed SMD / through-hole and repeat rework

## Manufacturer Capability References

The current assumptions are intentionally aligned to easy, standard offerings from the prototype vendors already referenced in the package.

### JLCPCB

Relevant capability references:

- [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities)
- [Copper weight guide](https://jlcpcb.com/help/article/jlcpcb-copper-weight)
- [How to choose board thickness](https://jlcpcb.com/blog/how-to-choose-the-thickness-of-pcb)

Useful current points from those sources:

- 2-layer FR-4 is standard
- 1 oz and 2 oz outer copper are standard options
- 1.6 mm is a normal board thickness choice

### PCBWay

Relevant capability references:

- [PCB capabilities](https://www.pcbway.com/capabilities.html)
- [Manufacturing tolerances](https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_tolerances.html)

Useful current points from those sources:

- minimum manufacturable trace/spacing is `4/4 mil`
- they strongly suggest `6/6 mil` or wider to save cost
- minimum drill sizes go down below what this project should need

## Rev A Design Rules To Target

For quote-friendly prototype boards:

- nominal trace/space target: `6/6 mil`
- minimum drill target: `0.3 mm`
- through-hole parts are acceptable where they materially help:
  - combo jacks
  - JST headers
  - TO-126 transistors
  - film capacitors in the audio path

## Board-Specific Notes

### Input / Output Board

- likely mixed-technology board because of combo jacks and possible film audio capacitors
- keep balanced I/O traces symmetrical near the panel connectors

### Tank Driver / Recovery Board

- likely mixed-technology board
- TO-126 output transistors and film audio-path parts may push board area up
- treat this board as the least likely to stay compact

### Ext Tank Routing Board

- mostly friendly to SMD assembly
- relay keepouts and coil-current routing matter more than density

### Crossfade / Feedback / Wet Board

- should be one of the easiest boards to keep compact and SMD-heavy

### Filter / Clipper Board

- may become mixed-technology if the chosen audio-path capacitor policy drives film-capacitor footprints into the filter sections

## When To Revisit The Layer Count

Stay at 2 layers unless one of these becomes true:

- grounding around the tank recovery stage becomes too compromised
- the filter / clipper board becomes too dense to route cleanly
- relay routing plus analog return paths become messy enough to justify extra planes

If that happens, the best upgrade path is:

- move the problem board only to `4-layer`
- keep the simpler boards at `2-layer`

## Practical Rev A Recommendation

Start all boards assuming:

- `2-layer`
- `1.6 mm`
- `1 oz`
- `ENIG`
- `6/6 mil`
- `0.3 mm` drill or larger

Only promote an individual board to `4-layer` if the actual KiCad routing proves it needs it.
