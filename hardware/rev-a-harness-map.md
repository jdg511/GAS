# GAS Rev A Harness Map

This file defines the intended board-to-board harnesses for rev A.

## Harness Philosophy

- Keep harnesses modular and replaceable
- Use common JST families for internal board links
- Use shielded cable for spring-tank runs
- Keep relay coil and power wiring physically separate from low-level recovery wiring

## Internal Board Harnesses

### H1 I/O Board Power

- from: power/backplane
- to: input/output board `P1`
- connector family: `JST VH`
- conductors:
  - `+15VA`
  - `AGND`
  - `-15VA`

### H2 I/O Wet Send

- from: input/output board `P2`
- to: ext tank routing board `P201`
- connector family: `JST XH`
- conductors:
  - `WET_SEND_L`
  - `AGND`
  - `WET_SEND_R`

### H3 I/O Dry Distribution

- from: input/output board `P4`
- to: any board that needs the dry reference
- connector family: `JST XH`
- conductors:
  - `DRY_L`
  - `AGND`
  - `DRY_R`

### H4 Wet Return To I/O

- from: crossfade / feedback / wet board `P304`
- to: input/output board `P3`
- connector family: `JST XH`
- conductors:
  - `WET_SUM_L`
  - `AGND`
  - `WET_SUM_R`

### H5 Primary Tank Bundle

- from: ext tank routing board `P202`
- to: tank driver / recovery board `P101`
- connector family: `JST XH` 6-position
- conductors:
  - `PRI_SEND_L`
  - `PRI_RET_L`
  - `AGND`
  - `PRI_SEND_R`
  - `PRI_RET_R`
  - `AGND`

### H6 Secondary Tank Bundle

- from: ext tank routing board `P203`
- to: tank driver / recovery board `P102`
- connector family: `JST XH` 6-position
- conductors:
  - `SEC_SEND_L`
  - `SEC_RET_L`
  - `AGND`
  - `SEC_SEND_R`
  - `SEC_RET_R`
  - `AGND`

### H7 Routed Tank Output

- from: ext tank routing board `P204`
- to: crossfade / feedback / wet board `P301`
- connector family: `JST XH`
- conductors:
  - `TANK_MIX_L`
  - `AGND`
  - `TANK_MIX_R`

### H8 Crossfade To Filter

- from: crossfade / feedback / wet board `P302`
- to: filter / clipper board `P401`
- connector family: `JST XH`
- conductors:
  - `XFADE_OUT_L`
  - `AGND`
  - `XFADE_OUT_R`

### H9 Filter Return

- from: filter / clipper board `P402`
- to: crossfade / feedback / wet board `P303`
- connector family: `JST XH`
- conductors:
  - `FILTCLIP_OUT_L`
  - `AGND`
  - `FILTCLIP_OUT_R`

### H10 Feedback Reinjection

- from: crossfade / feedback / wet board `P305`
- to: ext tank routing board `P205`
- connector family: `JST XH`
- conductors:
  - `FB_RET_L`
  - `AGND`
  - `FB_RET_R`

### H11 Tank Driver / Recovery Board Power

- from: power/backplane `P502`
- to: tank driver / recovery board `P103`
- connector family: `JST VH` 3-position
- conductors:
  - `+15VA`
  - `AGND`
  - `-15VA`

### H12 Crossfade / Feedback / Wet Board Power

- from: power/backplane `P503`
- to: crossfade / feedback / wet board `P306`
- connector family: `JST VH`
- conductors:
  - `+15VA`
  - `AGND`
  - `-15VA`

### H13 Filter / Clipper Board Power

- from: power/backplane `P504`
- to: filter / clipper board `P404`
- connector family: `JST VH`
- conductors:
  - `+15VA`
  - `AGND`
  - `-15VA`

### H14 Ext Tank Routing Board Power

- from: power/backplane `P506`
- to: ext tank routing board `P207`
- connector family: `JST VH` 4-position
- conductors:
  - `+15VA`
  - `AGND`
  - `-15VA`
  - `+5VAUX`

## Tank Harnesses

These are not JST inter-board harnesses.

They should use shielded cable suitable for spring-tank runs.

### T1 Primary Left Tank

- send from tank driver / recovery board to primary left `4AB1C1B`
- return from tank back to recovery input

### T2 Primary Right Tank

- send from tank driver / recovery board to primary right `4AB1C1B`
- return from tank back to recovery input

### T3 Secondary Left Tank

- send from tank driver / recovery board to secondary left `9EB2C1B`
- return from tank back to recovery input

### T4 Secondary Right Tank

- send from tank driver / recovery board to secondary right `9EB3C1B`
- return from tank back to recovery input

## Harness Build Notes

- Keep all low-level recovery conductors short
- Keep tank harnesses away from the DC-entry and conversion wiring
- Twist power conductors where practical
- Label every harness with its `H#` or `T#` identifier during prototype build
- Use [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1) as the pin-number authority during harness build
