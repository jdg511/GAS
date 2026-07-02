# GAS Rev A I/O Schematic-Ready Definition

This file is the direct electrical definition for the rev-A input/output board.

It is more specific than [boards/input-output-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/input-output-board.md:1) and [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1), but it still stops short of claiming the board is already fully bench-tuned.

Use this file when:

- promoting the current KiCad `io-board.kicad_sch` page from single-unit placeholders to a true multi-unit schematic
- assigning passive references and starting values without inventing new naming
- checking that the balanced `+4 dBu`, 600-ohm-capable line-I/O requirement is still reflected in the actual board capture

## 1. Assumed First-Pass Circuit Strategy

This definition freezes the first-pass topology as:

- classic unity-gain differential receiver per input channel using `U1A` and `U1B`
- mono duplication after the balanced receive boundary using the off-board `P6` switch landing
- dry and wet-send fanout from buffered single-ended left/right program sources
- passive off-board wet/dry blend at `P5`, with the pot wiper buffered by `U2A` and `U2B`
- fully active balanced output per channel using one follower leg and one unity-gain inverting leg

Important note:

- this keeps `P5` as the user-required raw 6-wire stereo control landing
- it is intentionally easy to retune later into a more active or equal-power law without changing the external harness convention

## 2. Required KiCad Multi-Unit Promotion

The checked-in `io-board.kicad_sch` still has only one symbol unit placed for each multi-unit package. The real capture pass should promote the sheet to this exact unit set:

### Combo Jacks

| Ref | Unit | Role |
| --- | --- | --- |
| `J1` | `1` | left XLR input face |
| `J1` | `2` | left TRS input face |
| `J2` | `1` | right XLR input face |
| `J2` | `2` | right TRS input face |
| `J3` | `1` | left XLR output face |
| `J3` | `2` | left TRS output face |
| `J4` | `1` | right XLR output face |
| `J4` | `2` | right TRS output face |

### Active Devices

| Ref | Unit | Job |
| --- | --- | --- |
| `U1` | `1` | `U1A` left balanced receiver |
| `U1` | `2` | `U1B` right balanced receiver |
| `U1` | `3` | `U1C` left post-mono buffer |
| `U1` | `4` | `U1D` right post-mono buffer |
| `U1` | `5` | power pins |
| `U2` | `1` | `U2A` left wet/dry buffer |
| `U2` | `2` | `U2B` right wet/dry buffer |
| `U2` | `3` | power pins |
| `U3` | `1` | `U3A` left hot driver |
| `U3` | `2` | `U3B` left cold driver |
| `U3` | `3` | power pins |
| `U4` | `1` | `U4A` right hot driver |
| `U4` | `2` | `U4B` right cold driver |
| `U4` | `3` | power pins |

## 3. External Connector Pin Ownership

All jack grounds on this board return to `AGND`. The only controlled `AGND` to `CHASSIS` bond remains on the power/backplane page.

### J1 Left Input

| Jack Pin | Net |
| --- | --- |
| `XLR 1` | `AGND` |
| `XLR 2` | `IN_BAL_L_P` |
| `XLR 3` | `IN_BAL_L_N` |
| `TRS T` | `IN_BAL_L_P` |
| `TRS R` | `IN_BAL_L_N` |
| `TRS S` | `AGND` |
| `G` | `AGND` |

### J2 Right Input

| Jack Pin | Net |
| --- | --- |
| `XLR 1` | `AGND` |
| `XLR 2` | `IN_BAL_R_P` |
| `XLR 3` | `IN_BAL_R_N` |
| `TRS T` | `IN_BAL_R_P` |
| `TRS R` | `IN_BAL_R_N` |
| `TRS S` | `AGND` |
| `G` | `AGND` |

### J3 Left Output

| Jack Pin | Net |
| --- | --- |
| `XLR 1` | `AGND` |
| `XLR 2` | `OUT_BAL_L_P` |
| `XLR 3` | `OUT_BAL_L_N` |
| `TRS T` | `OUT_BAL_L_P` |
| `TRS R` | `OUT_BAL_L_N` |
| `TRS S` | `AGND` |
| `G` | `AGND` |

### J4 Right Output

| Jack Pin | Net |
| --- | --- |
| `XLR 1` | `AGND` |
| `XLR 2` | `OUT_BAL_R_P` |
| `XLR 3` | `OUT_BAL_R_N` |
| `TRS T` | `OUT_BAL_R_P` |
| `TRS R` | `OUT_BAL_R_N` |
| `TRS S` | `AGND` |
| `G` | `AGND` |

## 4. Power And Header Pin Ownership

### P1 `JIO-PWR`

| Pin | Net |
| --- | --- |
| `1` | `+15VA` |
| `2` | `AGND` |
| `3` | `-15VA` |

### P2 `JIO-WETSEND`

| Pin | Net |
| --- | --- |
| `1` | `WET_SEND_L` |
| `2` | `AGND` |
| `3` | `WET_SEND_R` |

### P3 `JIO-WETRET`

| Pin | Net |
| --- | --- |
| `1` | `WET_SUM_L` |
| `2` | `AGND` |
| `3` | `WET_SUM_R` |

### P4 `JIO-DRY`

| Pin | Net |
| --- | --- |
| `1` | `DRY_L` |
| `2` | `AGND` |
| `3` | `DRY_R` |

### P5 Wet / Dry Control

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `WD_L_HI` | left dry end of the pot track |
| `2` | `WD_L_WIPER` | left blend wiper |
| `3` | `WD_L_LO` | left wet end of the pot track |
| `4` | `WD_R_HI` | right dry end of the pot track |
| `5` | `WD_R_WIPER` | right blend wiper |
| `6` | `WD_R_LO` | right wet end of the pot track |

### P6 Mono Switch

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `MONO_A` | left-source throw |
| `2` | `MONO_C` | switched common to right-channel source node |
| `3` | `MONO_B` | right-source throw |

## 5. Internal Audio Nodes

Use these node names when drawing the final KiCad page, even if they remain as local notes instead of explicit local labels:

| Node | Meaning |
| --- | --- |
| `L_RX` | left post-receiver single-ended source from `U1A` |
| `R_RX` | right post-receiver single-ended source from `U1B` |
| `L_PROG` | left post-mono buffered internal source from `U1C` |
| `R_PROG` | right post-mono buffered internal source from `U1D` |
| `L_BLEND` | left wet/dry buffered output from `U2A` |
| `R_BLEND` | right wet/dry buffered output from `U2B` |

## 6. Exact First-Pass Passive Map

### Input Boundary And Differential Receive

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R1` | `100R` | `IN_BAL_L_P` | `J1` hot boundary | connector-facing series part |
| `R2` | `100R` | `IN_BAL_L_N` | `J1` cold boundary | connector-facing series part |
| `R3` | `100R` | `IN_BAL_R_P` | `J2` hot boundary | connector-facing series part |
| `R4` | `100R` | `IN_BAL_R_N` | `J2` cold boundary | connector-facing series part |
| `C1` | `220 pF`, DNP | `IN_BAL_L_P` | `AGND` | RF placeholder near `J1` |
| `C2` | `220 pF`, DNP | `IN_BAL_L_N` | `AGND` | RF placeholder near `J1` |
| `C3` | `220 pF`, DNP | `IN_BAL_R_P` | `AGND` | RF placeholder near `J2` |
| `C4` | `220 pF`, DNP | `IN_BAL_R_N` | `AGND` | RF placeholder near `J2` |
| `R11` | `10k`, `0.1%` | post-`R2` left cold leg | `U1A-` | left inverting input resistor |
| `R12` | `10k`, `0.1%` | `U1A out` | `U1A-` | left feedback resistor |
| `R13` | `10k`, `0.1%` | post-`R1` left hot leg | `U1A+` | left non-inverting source resistor |
| `R14` | `10k`, `0.1%` | `U1A+` | `AGND` | left non-inverting reference resistor |
| `R15` | `10k`, `0.1%` | post-`R4` right cold leg | `U1B-` | right inverting input resistor |
| `R16` | `10k`, `0.1%` | `U1B out` | `U1B-` | right feedback resistor |
| `R17` | `10k`, `0.1%` | post-`R3` right hot leg | `U1B+` | right non-inverting source resistor |
| `R18` | `10k`, `0.1%` | `U1B+` | `AGND` | right non-inverting reference resistor |

### Mono Routing And Dry / Wet Send Split

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R21` | `100R` | `U1C out` | `P4 pin 1` | left dry output isolator |
| `R22` | `100R` | `U1C out` | `P2 pin 1` | left wet-send isolator |
| `R23` | `100R` | `U1D out` | `P4 pin 3` | right dry output isolator |
| `R24` | `100R` | `U1D out` | `P2 pin 3` | right wet-send isolator |

### Wet / Dry Control And Buffer

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R31` | `20k` | `WD_L_WIPER` | `U2A-` | left blend entry resistor |
| `R32` | `20k` | `WD_R_WIPER` | `U2B-` | right blend entry resistor |
| `R35` | `20k` | `U2A out` | `U2A-` | left unity-gain feedback |
| `R36` | `20k` | `U2B out` | `U2B-` | right unity-gain feedback |

The passive blend landing itself should be wired as:

- `WD_L_HI` driven from `L_PROG`
- `WD_L_LO` driven from `WET_SUM_L`
- `WD_R_HI` driven from `R_PROG`
- `WD_R_LO` driven from `WET_SUM_R`
- `U2A+` and `U2B+` tied to `AGND`

### Balanced Output

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R43` | `10k` | `L_BLEND` | `U3B-` | left cold-leg input resistor |
| `R44` | `10k` | `U3B out` | `U3B-` | left cold-leg feedback resistor |
| `R49` | `49.9R` | `U3A out` | `OUT_BAL_L_P` | left hot build-out resistor |
| `R50` | `49.9R` | `U3B out` | `OUT_BAL_L_N` | left cold build-out resistor |
| `R53` | `10k` | `R_BLEND` | `U4B-` | right cold-leg input resistor |
| `R54` | `10k` | `U4B out` | `U4B-` | right cold-leg feedback resistor |
| `R59` | `49.9R` | `U4A out` | `OUT_BAL_R_P` | right hot build-out resistor |
| `R60` | `49.9R` | `U4B out` | `OUT_BAL_R_N` | right cold build-out resistor |

The hot-leg buffer wiring should be:

- `U3A+` from `L_BLEND`
- `U3A-` tied directly to `U3A out`
- `U4A+` from `R_BLEND`
- `U4A-` tied directly to `U4A out`

The cold-leg inverter wiring should be:

- `U3B+` to `AGND`
- `U4B+` to `AGND`

## 7. Functional Wiring Summary By Stage

### U1A Left Differential Receiver

- source from `IN_BAL_L_P` and `IN_BAL_L_N`
- output node is `L_RX`

### U1B Right Differential Receiver

- source from `IN_BAL_R_P` and `IN_BAL_R_N`
- output node is `R_RX`

### U1C Left Post-Mono Buffer

- `U1C+` from `L_RX`
- `U1C-` tied to `U1C out`
- output node is `L_PROG`

### U1D Right Post-Mono Buffer

- `U1D+` from `MONO_C`
- `U1D-` tied to `U1D out`
- output node is `R_PROG`

### Mono Switch Truth

- `MONO_A` driven from `L_RX`
- `MONO_B` driven from `R_RX`
- `MONO_C` returned to `U1D+`
- switch state `Stereo`: connect `MONO_B` to `MONO_C`
- switch state `Mono -> Stereo`: connect `MONO_A` to `MONO_C`

### Wet / Dry Pot Landing

- `L_PROG` drives `WD_L_HI`
- `WET_SUM_L` drives `WD_L_LO`
- `L_BLEND` is the buffered result of `WD_L_WIPER`
- `R_PROG` drives `WD_R_HI`
- `WET_SUM_R` drives `WD_R_LO`
- `R_BLEND` is the buffered result of `WD_R_WIPER`

## 8. Local Decoupling Intent

Reserve `C91-C99` for local rail decoupling.

First-pass intent:

- at least one `100 nF` from `+15VA` to `AGND` per op-amp package
- at least one `100 nF` from `-15VA` to `AGND` per op-amp package
- one local `10 uF` to `22 uF` bulk rail footprint per board side is acceptable because these are power-path parts, not audio-path coupling parts

## 9. Verification Gate For The Later KiCad Pass

When this definition is translated into the final multi-unit KiCad page, verify all of the following:

1. `J1-J4` each have both symbol units present and electrically tied to the same hot/cold/ground nets.
2. `U1` has all four signal units plus its power unit instantiated.
3. `U2-U4` each have both signal units plus their power unit instantiated.
4. `P5` remains a raw 6-wire stereo control landing.
5. `P6` remains a raw 3-wire mono switch landing.
6. `OUT_BAL_L_P/N` and `OUT_BAL_R_P/N` are driven as opposite-polarity active legs, not the same-polarity duplicate outputs.
7. `P2`, `P3`, and `P4` keep the frozen `signal / AGND / signal` pin order from the harness map.

## 10. Explicitly Deferred Items

These are not left ambiguous; they are intentionally deferred:

- exact EMC clamp network population around `J1/J2`
- final wet/dry taper choice and whether the passive blend law needs a more level-consistent later revision
- any cross-coupled balanced-output refinement beyond the follower-plus-inverter first-pass topology
- final local decoupling values at each package
