# GAS Rev A Endcap Hole Table

This is the first drilling and cutout draft for the circular service endcap.

It is intentionally a **prototype handoff table**, not a final CNC drawing. The goals are:

- prove the control and connector count fits the preferred `10 in` face
- provide a metal shop with an organized cutout schedule
- record that the layout also passes all spacing rules on a `9 in` face (no longer preferred only because `9 in` pipe caps are rarely stocked)

## Reference System

- preferred endcap outer diameter: `10.0 in` nominal (`254 mm`)
- note: "10 in" nominal pipe/cap hardware is not 10.00 in actual (e.g. 10 in steel pipe is `10.75 in` OD; PVC socket vs spigot caps differ) — final DXF must use the measured face of the purchased cap
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
| `J5` | DC jack | 1 | `95` | `-18.35` | `8.0 mm` round pilot, enlarge to selected jack bushing | keep cable bend clearance; use compact-bushing jack |
| `SW701` | mono selector | 1 | `-63.65` | `61.3` | `6.5 mm` round | upper-left switch zone |
| `J701` | ext mode rotary | 1 | `-25` | `78` | `9.5 mm` round | upper-center left |
| `J702` | clip mode rotary | 1 | `25` | `78` | `9.5 mm` round | upper-center right |
| `SW702` | feedback phase | 1 | `63.65` | `61.3` | `6.5 mm` round | upper-right switch zone |
| `VR701` | wet/dry | 1 | `-78` | `-45.65` | `7.5 mm` round | lower outer row |
| `VR702` | ext amount | 1 | `-47` | `-70` | `7.5 mm` round | lower outer row |
| `VR703` | crossfade | 1 | `-15` | `-82` | `7.5 mm` round | lower outer row |
| `VR704` | feedback | 1 | `18` | `-82` | `7.5 mm` round | lower outer row |
| `VR705` | drive | 1 | `50` | `-70` | `7.5 mm` round | lower outer row |
| `VR706` | HPF cutoff | 1 | `80` | `-45.65` | `7.5 mm` round | lower outer row |
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

For the `10 in` (`254 mm`) preferred face, every item passes all spacing rules with margin. Tightest gaps at the final positions:

- `J5` DC to `VR706` HPF cutoff: `31.2 mm` center-to-center (rule `>= 24 mm`)
- `J5` DC to `J4` out-R combo: `40.1 mm` (rule `>= 31 mm`)
- `J5` DC hole edge to rim: `~26 mm` on the `10 in` face (rule `>= 12 mm`)
- `SW701`/`SW702` toggle hole edge to rim: `~35 mm`
- closest pot pair (`VR703`-`VR704` crossfade/feedback): `33 mm` (rule `>= 24 mm`)

On a `9 in` face the same layout still passes everywhere; the slimmest number becomes the DC jack edge margin at `~13.5 mm` against the `12 mm` rule. `9 in` was dropped as the preferred target for sourcing reasons only: standard pipe and cap sizes jump from `8 in` to `10 in`.

### Position-Change History (draft corrections)

- `J5` DC jack: `(88, -48)` clashed with `VR706` at `~9 mm` center-to-center → `(88, -12)` → final `(95, -18.35)` for knob-size headroom around `VR706` and hand clearance under `J4`
- `SW701`/`SW702` toggles: `(±70, 74)` violated the `12 mm` edge rule on the `9 in` draft (`~9 mm` actual) → final `(±63.65, 61.3)`
- `VR701`/`VR706`: raised `1/4 in` from `Y = -52` to `Y = -45.65` for rim clearance and a softer outer arc

## Metal-Shop Deliverable Recommendation

When this moves from draft to fab:

1. turn this table into a true `DXF`
2. pull exact combo-jack geometry from the selected Neutrik datasheet
3. confirm the exact bushing diameters for the selected rotaries, toggles, and pots
4. decide whether anti-rotation tabs get their own holes/slots or are removed at assembly

Until then, this file is the rev-A drilling intent record.
