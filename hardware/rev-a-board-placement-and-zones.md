# GAS Rev A Board Placement And Zones

This file turns the abstract board split into layout-facing placement guidance.

It is intentionally more concrete than the general layout rules, but less fake-precise than claiming a final enclosure before the mechanics are frozen.

## Global Placement Rules

- Keep the power-entry and DC-DC conversion zone as far as practical from tank recovery circuitry.
- Keep every board's power entry on a predictable edge or corner so the harnessing stays legible.
- Keep low-level recovery, feedback, and balanced-input nodes away from relay coils, PSU ripple loops, and tank-send current paths.
- Prefer one consistent "quiet edge" and one consistent "connector edge" on each board instead of scattering interfaces on every side.
- Treat the cylindrical tube axis as the main mechanical reference direction.

## 1. Input / Output Board

### Role

- service-endcap-adjacent signal entry/exit board
- balanced receive and balanced drive boundary

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| panel edge | `J1-J4` combo jacks and any immediately adjacent RF boundary parts |
| quiet input corner | balanced receiver ratios and `U1` |
| internal signal edge | `P2`, `P3`, `P4` harness connectors |
| output edge near panel | `U3`, `U4`, and output build-out resistors |
| utility/control edge | `P5`, `P6` if controls are off-board |

### Routing Intent

- keep the input receivers and output drivers physically separated
- do not let output leg return currents share the same copper region as the input ratio network
- keep combo-jack pin-1 or sleeve-to-chassis strategy physically close to the connector boundary

## 2. Tank Driver / Recovery Board

### Role

- quietest analog board in the system except for the local send transistor hot zones

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| hot/send edge | `Q101-Q104`, emitter resistors, zobels, any small heatsink allowance |
| tank connector edge | `J101-J108` or their chosen equivalents |
| quiet recovery corner | `U103`, `U104`, recovery bias/gain parts |
| internal harness edge | `P101`, `P102`, `P103` |
| service/test strip | primary bias/current test pads and return-node test pads |

### Routing Intent

- keep send current loops short and local to the output devices
- keep recovery traces physically separated from send traces, even when they terminate at the same tank interface area
- if the board must sit near the tanks, orient the recovery side away from the PSU and relay boards

## 3. Ext Tank Routing Board

### Role

- mode-switching and secondary contribution management board

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| relay/power side | `K201-K204`, coil-drive or suppression parts, `P207` |
| wet audio side | `U201`, active summing parts |
| signal harness edge | `P201-P205` |
| control edge | `P206` or the local mode/amount hardware |

### Routing Intent

- draw the relay contact flow in a way that is visually traceable on the PCB
- keep coil supply and flyback current loops out of the high-impedance summing area
- prefer one edge for all inter-board signal harnesses so routing mode debug is simpler

## 4. Crossfade / Feedback / Wet Board

### Role

- loop-management and final wet handoff board

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| input edge | `P301` routed-tank input and `P303` filter return |
| loop core | `U301`, feedback summing parts, phase switch interface |
| output edge | `P302`, `P304`, `P305` |
| power/control edge | `P306`, `P307` |

### Routing Intent

- keep the feedback loop physically compact and obvious
- put the feedback reinjection output near the edge that faces the routing board
- avoid long wandering traces between the filter-return point and the wet-output point

## 5. Filter / Clipper Board

### Role

- dense tone-shaping and nonlinear board

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| input edge | `P401` and the first HPF stage |
| center mirror line | left/right matched filter sections |
| clip core | diode networks and drive-stage feedback loops |
| output edge | `P402` and output buffers |
| control edge | `P403` or board-mounted control hardware |
| power corner | `P404` and local decoupling |

### Routing Intent

- mirror left and right channels as much as practical
- keep each clip network close to its drive op amp
- do not place long control traces through the most sensitive summing nodes if the controls land off-board

## 6. Power / Backplane Board

### Role

- low-voltage source, star-ground, and distribution board

### Preferred Zones

| Zone | Preferred Contents |
| --- | --- |
| service-endcap side | `J500` harness landing from panel DC jack, `D500`, `F500`, `TVS500`, `C500` |
| conversion side | `PS500`, `PS501`, ferrites, rail bulk caps |
| low-voltage distribution side | `P501-P506`, rail bulk capacitors, test pads |
| bond zone | controlled `AGND` to `CHASSIS` connection |
| optional control landing side | grouped panel-control headers if this board becomes the control backplane |

### Routing Intent

- keep dirty input-conversion loops local to the DC-DC area
- place the star ground and chassis bond close to the low-voltage distribution center, not in the middle of the quiet audio harness field
- point the `P506` auxiliary-power output toward the ext-routing board if the enclosure allows it

## Board-To-Board Physical Relationship

The preferred physical ordering inside the cylindrical enclosure is:

1. service-endcap plane: combo jacks, DC jack, switches, pots
2. just behind endcap: input/output board plus power/control backplane
3. middle analog area: ext-routing, crossfade/feedback, and filter boards on rails
4. quiet deep-tube area: tank driver/recovery board near the tank harness landings
5. along tube wall or subframe: spring tanks

This ordering helps the harness set follow the signal flow while keeping the power-entry and relay energy away from the quietest tank-return circuitry.

## What This File Does Not Pretend To Freeze

- exact board outline dimensions
- exact mounting-hole pattern
- exact front-panel spacing
- exact circular endcap hole pattern
- whether every control is board-mounted or backplane-landed

Those still depend on the final enclosure and metalwork package.
