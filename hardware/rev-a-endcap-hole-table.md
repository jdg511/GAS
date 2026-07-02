# GAS Rev A Endcap Hole Table

This is the first drilling and cutout draft for the circular service endcap.

It is intentionally a **prototype handoff table**, not a final CNC drawing. The goals are:

- prove the control and connector count fits the preferred `9 in` face
- provide a metal shop with an organized cutout schedule
- expose where the `8 in` fallback diameter becomes tight

## Reference System

- preferred endcap outer diameter: `9.0 in` (`228.6 mm`)
- coordinate origin: center of the circular endcap
- `+X` to the right when facing the unit
- `+Y` upward when facing the unit
- all dimensions in `mm`

## Important Draft Assumptions

- all combo jacks mount to a reinforced "jack bar" region
- all pot and toggle diameters are **panel-hole targets**, not full body diameters
- exact Neutrik cutout details must be taken from the chosen combo-jack datasheet before metalwork release
- exact rotary anti-rotation tab treatment depends on whether the builder wants tab slots or tab clipping

## Service-End Hardware Table

| Ref | Item | Qty | X | Y | Hole / Cutout | Notes |
|---|---|---:|---:|---:|---|---|
| `J1` | left input combo jack | 1 | `-78` | `18` | combo-jack rectangular cutout per Neutrik | jack-bar mounted |
| `J2` | right input combo jack | 1 | `-26` | `18` | combo-jack rectangular cutout per Neutrik | jack-bar mounted |
| `J3` | left output combo jack | 1 | `26` | `18` | combo-jack rectangular cutout per Neutrik | jack-bar mounted |
| `J4` | right output combo jack | 1 | `78` | `18` | combo-jack rectangular cutout per Neutrik | jack-bar mounted |
| `J5` | DC jack | 1 | `88` | `-48` | `8.0 mm` round pilot, enlarge to selected jack bushing | keep cable bend clearance |
| `SW701` | mono selector | 1 | `-70` | `74` | `6.5 mm` round | upper-left switch zone |
| `J701` | ext mode rotary | 1 | `-25` | `78` | `9.5 mm` round | upper-center left |
| `J702` | clip mode rotary | 1 | `25` | `78` | `9.5 mm` round | upper-center right |
| `SW702` | feedback phase | 1 | `70` | `74` | `6.5 mm` round | upper-right switch zone |
| `VR701` | wet/dry | 1 | `-78` | `-52` | `7.5 mm` round | lower outer row |
| `VR702` | ext amount | 1 | `-47` | `-70` | `7.5 mm` round | lower outer row |
| `VR703` | crossfade | 1 | `-15` | `-82` | `7.5 mm` round | lower outer row |
| `VR704` | feedback | 1 | `18` | `-82` | `7.5 mm` round | lower outer row |
| `VR705` | drive | 1 | `50` | `-70` | `7.5 mm` round | lower outer row |
| `VR706` | HPF cutoff | 1 | `80` | `-52` | `7.5 mm` round | lower outer row |
| `VR707` | HPF Q | 1 | `-48` | `-26` | `7.5 mm` round | lower inner row |
| `VR708` | LPF cutoff | 1 | `0` | `-36` | `7.5 mm` round | lower inner row |
| `VR709` | LPF Q | 1 | `48` | `-26` | `7.5 mm` round | lower inner row |

## Jack-Bar Recommendation

Instead of cutting four independent combo-jack plates, use:

- one circular endcap
- one internal rectangular reinforcement plate behind `J1-J4`

Recommended first-pass jack-bar envelope:

- width: `198 mm`
- height: `42 mm`
- centered at `X = 0`, `Y = 18`

Benefits:

- reduces endcap flex
- keeps the combo-jack field aligned
- makes service easier if the combo-jack fasteners share one reinforcement part

## Edge-Clearance Audit

For the `9 in` draft:

- the farthest round-control centers stay comfortably inside the edge
- the lower control cluster remains plausible with medium knobs
- the DC plug clears the lower-right pot zone better than a center-bottom power jack would

For an `8 in` fallback:

- the connector field may still fit
- the lower control cluster becomes the main risk area
- expect smaller knobs or tighter spacing if `8 in` is forced

## Metal-Shop Deliverable Recommendation

When this moves from draft to fab:

1. turn this table into a true `DXF`
2. pull exact combo-jack geometry from the selected Neutrik datasheet
3. confirm the exact bushing diameters for the selected rotaries, toggles, and pots
4. decide whether anti-rotation tabs get their own holes/slots or are removed at assembly

Until then, this file is the rev-A drilling intent record.
