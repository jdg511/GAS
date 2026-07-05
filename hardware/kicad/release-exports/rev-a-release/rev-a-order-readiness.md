# GAS Rev A KiCad Order Readiness

Generated: 2026-07-01 14:37:09 -05:00

This is the manufacturing gate for the current KiCad project. It is intentionally strict: a board should not be ordered until this report has no blockers.

## Status

BLOCKED: this project is not ready to order.

## Blockers

- Top-level ERC is not clean: 650 violations are present.
- Required non-virtual schematic symbols still have empty footprint fields: 10 symbols.
- No KiCad/SPICE simulation model properties are present, so KiCad simulations are not configured yet.

## Board Files

| Board | Footprints | Electrical footprints | DRC violations | Unconnected items | DRC report |
| --- | ---: | ---: | ---: | ---: | --- |
| crossfade-feedback-wet.kicad_pcb | 12 | 8 | 0 | 0 | crossfade-feedback-wet.drc.json |
| ext-tank-routing.kicad_pcb | 16 | 12 | 0 | 0 | ext-tank-routing.drc.json |
| filter-clipper.kicad_pcb | 23 | 19 | 0 | 0 | filter-clipper.drc.json |
| io-board.kicad_pcb | 54 | 50 | 0 | 0 | io-board.drc.json |
| power-backplane.kicad_pcb | 18 | 14 | 0 | 0 | power-backplane.drc.json |
| tank-driver-recovery.kicad_pcb | 15 | 11 | 0 | 0 | tank-driver-recovery.drc.json |

## ERC Summary

- Source: GAS-Hardware.kicad_sch
- Report: GAS-Hardware-erc-current.json
- Violations: 650

| Count | Type |
| ---: | --- |
| 261 | unconnected_wire_endpoint |
| 171 | label_dangling |
| 99 | endpoint_off_grid |
| 60 | isolated_pin_label |
| 43 | pin_not_connected |
| 14 | wire_dangling |
| 2 | multiple_net_names |

| Count | Sheet |
| ---: | --- |
| 648 | / |
| 2 | /input-output/ |

## Empty Required Footprints

| File | Ref | Value | Symbol |
| --- | --- | --- | --- |
| power-backplane.kicad_sch | J500 | PJ-005B | Connector:Barrel_Jack |
| power-backplane.kicad_sch | PS500 | URB2415YMD-10WR3 | Connector_Generic:Conn_01x06 |
| tank-driver-recovery.kicad_sch | J101 | Primary L send | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J102 | Primary L return | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J103 | Primary R send | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J104 | Primary R return | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J105 | Secondary L send | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J106 | Secondary L return | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J107 | Secondary R send | Connector:Conn_Coaxial |
| tank-driver-recovery.kicad_sch | J108 | Secondary R return | Connector:Conn_Coaxial |

## Simulation Readiness

- KiCad/SPICE model property count: 0
- Required next step: add SPICE models or simulator-compatible subcircuits for the active audio stages and power blocks before expecting KiCad simulation to run.
