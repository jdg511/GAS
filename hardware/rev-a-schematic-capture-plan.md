# GAS Rev A Schematic Capture Plan

This file is the bridge from the current hardware package into real KiCad schematic sheets.

## Planned KiCad Sheet Set

Top level project:

- `GAS-Hardware.kicad_sch`

Planned child sheets:

1. `io-board.kicad_sch`
2. `tank-driver-recovery.kicad_sch`
3. `ext-tank-routing.kicad_sch`
4. `crossfade-feedback-wet.kicad_sch`
5. `filter-clipper.kicad_sch`
6. `power-backplane.kicad_sch`

## Top-Level Sheet Responsibilities

### Top Level

- project title block
- sheet instantiation
- inter-sheet signal naming reference
- revision and note fields

### I/O Board Sheet

- combo `XLR / TRS` connector wiring reference
- balanced receiver
- mono-to-stereo switching
- dry split
- wet/dry summing
- fully active balanced output driver using four output op-amp channels across stereo

### Tank Driver / Recovery Sheet

- primary tank send drivers
- secondary tank send drivers
- primary recovery stages
- secondary recovery stages
- RCA tank connections

### Ext Tank Routing Sheet

- relay routing logic
- Off / Series / Parallel audio path
- ext-tank amount mixing
- routing buffers and optional makeup stage

### Crossfade / Feedback / Wet Sheet

- stereo crossfade block
- feedback amount block
- feedback phase inversion
- wet handoff back to the I/O board

### Filter / Clipper Sheet

- pre-HPF left/right
- drive stage left/right
- clip selection left/right
- post-LPF left/right

### Power / Backplane Sheet

- external `+30 VDC` entry
- isolated DC-DC conversion
- local `+5VAUX` generation
- `+15VA`, `-15VA`, `+5VAUX`, `AGND`, `CHASSIS`
- star-ground point
- board power headers
- relay-coil distribution

## Reference Designator Conventions

### Input / Output Board

- `J1-J4`
  - combo `XLR / TRS` jacks
- `U1`
  - `OPA1644AIDR`
- `U2-U4`
  - `OPA1656IDR`
- `SW1`
  - mono-to-stereo switch if mounted on-board
- `P1-P6`
  - board and control connectors

### Tank Driver / Recovery Board

- `U101-U104`
  - `OPA1656IDR`
- `Q101-Q104`
  - `BD139-16` / `BD140-16`
- `J101-J108`
  - tank RCA connectors or harness connectors
- `P101-P105`
  - board connectors

### Ext Tank Routing Board

- `U201`
  - `OPA1679IDR`
- `K201-K204`
  - `G6K-2F-Y-DC5`
- `P201-P207`
  - board connectors

### Crossfade / Feedback / Wet Board

- `U301`
  - `OPA1679IDR`
- `P301-P307`
  - board connectors

### Filter / Clipper Board

- `U401-U402`
  - `OPA1679IDR`
- `D401-D4xx`
  - silicon / LED / germanium clip devices
- `P401-P404`
  - board connectors

### Power / Backplane Board

- `J500`
  - service-endcap DC input landing
- `PS500`
  - `URB2415YMD-10WR3`
- `PS501`
  - `R-78E5.0-0.5`
- `P501-P5xx`
  - board power outputs
- `F501`
  - low-voltage fuse position

## Suggested Capture Order

1. Power / backplane
2. Input / output
3. Tank driver / recovery
4. Ext tank routing
5. Crossfade / feedback / wet
6. Filter / clipper

Reason:

- it locks rails and connectors first
- then it locks the I/O boundary
- then it locks the highest-risk spring interface

## First ERC Goal

The first KiCad pass does not need to be production-perfect.

It should prove:

- every board has defined power entry
- every inter-board connector is named consistently
- active devices and major controls are instantiated
- the top-level sheet structure is stable

Use these files as the capture inputs:

- [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1)
- [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
- [rev-a-capture-value-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-capture-value-tables.md:1)
- [rev-a-mode-truth-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-mode-truth-tables.md:1)
- [rev-a-control-ranges-and-laws.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-ranges-and-laws.md:1)
