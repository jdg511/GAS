# Input / Output Board

## Purpose

This board is the entry and exit point for the real device. It should accept balanced line-level audio, create the dry and wet branches, and provide the final balanced line-level output.

## Functions

- Input protection and connector interface
- Balanced input receiver
- JFET / BiFET input buffer stage
- Dedicated mono-input to stereo switch
- Dry-path split
- Wet-path send to the spring-tank system
- Final wet/dry blend
- Balanced output driver

## Software Features Mapped Here

- `Wet/Dry`
- Dry tap behavior
- External source entry point

## Recommended Analog Blocks

1. Input protection
   - Series resistor
   - RF shunt capacitor
   - Clamp diodes or input protection network as needed
2. Balanced line receiver
   - Differential receiver using precision resistor ratios
   - Designed around nominal `+4 dBu` balanced line operation
   - Sized for 600-ohm capable professional line interfacing
   - JFET or BiFET input op amp preferred for the front-end buffer/receiver role
3. Dry split
   - One branch to final mixer
   - One branch to the wet send path
   - Mono mode should be able to copy the selected mono input to both internal channels
4. Wet send driver
   - Low-impedance feed to downstream routing / tank electronics
5. Wet/dry output mixer
   - Dual-ganged pot or control-voltage/VCA approach
   - Keep constant perceived level in mind, even if first prototype is a simple linear blend
6. Balanced output driver
   - Cross-coupled or impedance-balanced line driver
   - Include per-leg series resistors and output protection
   - Must deliver balanced line audio output at nominal `+4 dBu`
   - Designed for 600-ohm capable professional line interfacing

## Proposed Connectors

- `J1` left combo `XLR / TRS` jack
- `J2` right combo `XLR / TRS` jack
- `J3` left combo `XLR / TRS` output jack
- `J4` right combo `XLR / TRS` output jack
- `P1` board power: `+15VA`, `AGND`, `-15VA`
  - preferred family: `JST VH`
- `P2` wet-path output to tank system: `WET_SEND_L`, `AGND`, `WET_SEND_R`
  - preferred family: `JST XH`
- `P3` wet return from downstream mixer: `WET_SUM_L`, `AGND`, `WET_SUM_R`
  - preferred family: `JST XH`
- `P4` dry distribution: `DRY_L`, `AGND`, `DRY_R`
  - preferred family: `JST XH`
- `P5` wet/dry control
  - if the stereo dual-gang pot is off-board, this should be a full 6-wire control connection rather than a compressed 2-wire or 3-wire shortcut
- `P6` mono-to-stereo switch
  - if off-board switch is used, this should be a 3-wire switch connection rather than a 2-wire link

## First-Pass Design Decisions

- Assume stereo balanced input and stereo balanced output.
- Add a dedicated mono-input to stereo switch on rev A.
- Make the input-side buffer/receiver JFET or BiFET based.
- Put the final wet/dry mix on this board so the output stage remains self-contained.
- Keep the input stage clean and high-headroom; clipping belongs on the dedicated filter/clipper board, not here.
- Use combo `XLR / TRS` jacks for the external balanced I/O.
- Keep the combo-jack mechanical choice adjacent to, but not electrically entangled with, the SMD audio core board where possible.
- The output requirement is not optional: rev A must provide balanced line output at nominal `+4 dBu` for 600-ohm capable interfacing.
- Use common, builder-friendly internal connector families for rev A rather than custom harness systems.

## Open Questions To Resolve During Schematic Capture

- Whether the wet/dry control should be passive, active, or VCA-based
- Whether rev A should be fully cross-coupled balanced or impedance-balanced on the outputs

## Rev A Schematic Checklist

- Choose the balanced receiver topology and matched resistor network strategy
- Use a JFET or BiFET input op amp on the input buffer / balanced receiver stage
- Add the dedicated mono-input to stereo routing switch after the balanced receiver stage
- Lock the combo `XLR / TRS` jack footprint and panel cutout strategy
- Define target common-mode rejection and clipping headroom
- Define balanced output topology and minimum load
- Verify the balanced output stage meets the nominal `+4 dBu` 600-ohm-capable requirement
- Freeze connector pinout for dry and wet inter-board links
