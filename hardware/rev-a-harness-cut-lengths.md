# GAS Rev A Harness Cut Lengths

This file adds first-pass physical cut lengths to the logical harness map.

These values are intended for:

- prototype cable planning
- quote sanity-checks
- deciding whether a grouped control backplane is cleaner than many direct runs

They are based on the draft axial station map in [rev-a-board-outline-assumptions.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.md:1).

## Length Policy

All lengths below are **prototype cut lengths**, not exact finished installed lengths.

Include in every internal harness:

- at least `25 mm` service slack at each end for JST-terminated links
- at least `40 mm` service slack at the panel side for hand-installed panel parts

If the final board positions move more than `40 mm`, recalculate before ordering finished harnesses.

## Board-To-Board Harness Lengths

| Harness | From | To | Draft route length | Prototype cut length |
|---|---|---|---:|---:|
| `H1` | power/backplane | I/O board | `90 mm` | `150 mm` |
| `H2` | I/O board | ext-routing | `180 mm` | `240 mm` |
| `H3` | I/O board | dry-distribution reserve | `120 mm` | `180 mm` |
| `H4` | crossfade/wet | I/O board | `300 mm` | `360 mm` |
| `H5` | ext-routing | tank driver/recovery | `420 mm` | `500 mm` |
| `H6` | ext-routing | tank driver/recovery | `420 mm` | `500 mm` |
| `H7` | ext-routing | crossfade/wet | `110 mm` | `170 mm` |
| `H8` | crossfade/wet | filter/clipper | `105 mm` | `165 mm` |
| `H9` | filter/clipper | crossfade/wet | `105 mm` | `165 mm` |
| `H10` | crossfade/wet | ext-routing | `135 mm` | `195 mm` |
| `H11` | power/backplane | tank driver/recovery | `520 mm` | `600 mm` |
| `H12` | power/backplane | crossfade/wet | `250 mm` | `320 mm` |
| `H13` | power/backplane | filter/clipper | `320 mm` | `390 mm` |
| `H14` | power/backplane | ext-routing | `170 mm` | `230 mm` |

## Tank Harness Lengths

Because the exact tank mounting positions depend on the user-supplied tube, keep the first set deliberately generous.

| Harness | Tank | Draft route length | Prototype cut length | Notes |
|---|---|---:|---:|---|
| `T1` | primary left `4AB1C1B` | `320 mm` | `450 mm` | shielded send/return pair |
| `T2` | primary right `4AB1C1B` | `320 mm` | `450 mm` | mirror of `T1` |
| `T3` | secondary left `9EB2C1B` | `430 mm` | `560 mm` | longer because secondaries can live deeper in the tube |
| `T4` | secondary right `9EB3C1B` | `430 mm` | `560 mm` | mirror of `T3` |

## Panel And Control Harness Lengths

These are the lengths most affected by whether the control-backplane strategy is used.

### If Using The Control Backplane

| Harness | Panel item group | To board | Prototype cut length |
|---|---|---|---:|
| `PC1` | combo jack field to I/O board | I/O board | `120 mm` |
| `PC2` | DC jack to power/backplane | power/backplane | `120 mm` |
| `PC3` | upper switch/rotary group to control backplane | control backplane | `150 mm` |
| `PC4` | lower pot group left | control backplane | `170 mm` |
| `PC5` | lower pot group center | control backplane | `170 mm` |
| `PC6` | lower pot group right | control backplane | `170 mm` |

### If Not Using The Control Backplane

Do not prebuild full custom harnesses yet.

Instead:

- build temporary point-to-point control links at `200-260 mm`
- verify final routing and strain relief in the tube
- only then freeze grouped control harnesses

## Cable-Type Recommendations

- `H1`, `H11-H14`: `24 AWG` stranded for power
- `H2-H10`: `26 AWG` stranded twisted triplets or equivalent quiet audio wiring
- `T1-T4`: shielded spring-tank cable, keep send and return separated from power bundles
- `PC1-PC6`: `26 AWG` stranded, panel-rated insulation preferred

## Practical Build Advice

- cut one prototype harness kit first, not a batch
- label both ends before terminating
- keep the tank harnesses physically on the quiet side of the tube
- keep the DC-entry and relay-power runs on the opposite side where practical

This file should be updated as soon as the first real mockup of the boards inside the user-supplied tube exists.
