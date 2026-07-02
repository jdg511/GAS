# GAS Rev A Board Outline Assumptions

This file gives the first concrete board-size and placement assumptions for the cylindrical rev-A build.

These are **prototype-planning numbers**, not final fab outlines. Their purpose is to:

- keep the six-board split physically plausible inside the tube
- support rail spacing and harness-length planning
- give KiCad layout work a target envelope before the mechanical package is fully frozen

## Mechanical Reference Frame

- enclosure shell: user-supplied tube
- preferred outer diameter: `9.0 in` (`228.6 mm`)
- acceptable fallback outer diameter: `8.0 in` (`203.2 mm`)
- design target length: `48 in` (`1219 mm`)

For the draft board envelopes below, assume:

- usable internal width between rails and curvature keepout: about `160 mm`
- usable straight-line board length near the service end: `80-170 mm` depending on board
- minimum side clearance from board corners to curved shell: `10 mm`
- minimum board-to-board axial service gap: `18 mm`

## Preferred Internal Rail Geometry

- two longitudinal rails or angle brackets
- nominal rail separation: `140 mm` center-to-center
- board mounting plane offset from shell wall: `18-25 mm`
- keep the deepest components on the inward-facing side where possible

## Draft Board Envelopes

### 1. Input / Output Board

- target outline: `160 mm x 75 mm`
- orientation: wide edge parallel to the service endcap
- location: immediately behind the combo-jack field

Reason:

- the board mainly needs room for balanced I/O stages, harness headers, and optional short panel harnesses
- combo jacks themselves should remain panel parts, not board-edge mechanical anchors, in the preferred rev-A interpretation

### 2. Power / Control Backplane

- target outline: `150 mm x 95 mm`
- orientation: broad side parallel to the service endcap
- location: behind or slightly below the I/O board, close to DC entry and chassis bond

Reason:

- this board wants room for the DC-DC module, rail filtering, power headers, and grouped control landings

### 3. Ext Tank Routing Board

- target outline: `120 mm x 80 mm`
- location: first mid-tube audio board after the service-end boards

Reason:

- relay routing is more important than density
- keep one long edge available for the harness field

### 4. Crossfade / Feedback / Wet Board

- target outline: `100 mm x 70 mm`
- location: adjacent to the routing board

Reason:

- this is electrically compact and should be one of the smaller boards

### 5. Filter / Clipper Board

- target outline: `140 mm x 90 mm`
- location: adjacent to the crossfade board

Reason:

- this board is likely to grow because of film-capacitor footprints and control-header density

### 6. Tank Driver / Recovery Board

- target outline: `170 mm x 110 mm`
- location: deeper into the tube, near the tank zone

Reason:

- this board carries the most analog risk
- it needs room for TO-126 devices, recovery spacing, RCA or equivalent tank landings, and thermal/mechanical breathing room

## Draft Axial Station Map

Measured from the inside face of the service endcap:

| Station | Start | End | Notes |
|---|---:|---:|---|
| I/O board zone | `25 mm` | `100 mm` | close to combo-jack harnesses |
| Power/control zone | `105 mm` | `200 mm` | close to DC entry and chassis bond |
| Ext-routing zone | `225 mm` | `305 mm` | first mid-path audio board |
| Crossfade zone | `325 mm` | `395 mm` | short audio links to routing and filter |
| Filter/clipper zone | `415 mm` | `505 mm` | keep controls reachable by one grouped harness |
| Tank driver/recovery zone | `575 mm` | `685 mm` | quiet zone near tank harness landings |
| Tank mounting zone | `720 mm` | `1120 mm` | user-supplied tanks and isolation hardware |

This intentionally leaves:

- one service gap between the filter/clipper and tank-driver board
- a quiet transition zone before the tank area

## Curvature And Height Keepouts

Do not assume a rectangular box interior.

For boards wider than `140 mm`:

- keep tall parts inside an inner rectangle about `140 mm x board length`
- reserve corner triangles as no-go zones for tall electrolytics, relays, or stacked connectors

Practical rule:

- if a component is taller than `14 mm`, keep it at least `12 mm` inboard from the board outline on the shell-facing side

## Preferred Mounting-Hole Pattern

Use a simple 4-hole pattern on each board where practical:

- hole size: `3.2 mm` for `M3` or `4-40`
- edge setback: `5-7 mm`
- slotted holes acceptable only on the tank-driver board if thermal or harness alignment needs them

## What This File Does And Does Not Freeze

This file freezes:

- a plausible physical envelope for each board
- a believable axial layout for harness planning
- a preferred rail-mounted construction style

This file does not freeze:

- exact final PCB outline
- final mounting-hole coordinates
- exact component keepouts from the eventual KiCad 3D models
