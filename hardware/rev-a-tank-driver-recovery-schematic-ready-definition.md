# GAS Rev A Tank Driver / Recovery Schematic-Ready Definition

This file is the direct electrical definition for the rev-A tank driver / recovery board.

It is more specific than [boards/system-remaining.md](C:/Users/Jason/GAS-build/repo/hardware/boards/system-remaining.md:1), [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1), and [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1), but it still stops short of pretending the tank-drive and recovery values are already bench-final.

Use this file when:

- promoting the current KiCad `tank-driver-recovery.kicad_sch` page from single-unit placeholders to a true multi-unit schematic
- assigning the first-pass driver, bias, recovery, and shield-bond parts without inventing new node names
- checking that the real spring-tank substitution for the software-only predelay/convolution surrogate is still captured honestly

## 1. Assumed First-Pass Circuit Strategy

This definition freezes the first-pass tank board topology as:

- direct-coupled split-rail primary send stages for the two `4AB1C1B` tanks
- complementary emitter-follower output stages for the two primary sends using `BD139-16` and `BD140-16`
- lower-current op-amp secondary send stages for the `9EB2C1B` left and `9EB3C1B` right tanks
- one low-noise recovery stage per tank return
- explicit local tank-shield handling on this board, not hidden inside harness prose

Important note:

- the current fixed rev-A board package remains solid-state
- spring tanks are separately procured and user-installed
- any vacuum tubes used in a later build remain outside this fixed PCB BOM unless a separate tube daughterboard is explicitly added

## 2. Required KiCad Multi-Unit Promotion

The checked-in `tank-driver-recovery.kicad_sch` still has only one symbol unit placed for each multi-unit package. The real capture pass should promote the sheet to this exact unit set:

### Active Devices

| Ref | Unit | Job |
| --- | --- | --- |
| `U101` | `1` | `U101A` primary left predriver |
| `U101` | `2` | `U101B` primary right predriver |
| `U101` | `3` | power pins |
| `U102` | `1` | `U102A` secondary left send |
| `U102` | `2` | `U102B` secondary right send |
| `U102` | `3` | power pins |
| `U103` | `1` | `U103A` primary left recovery |
| `U103` | `2` | `U103B` primary right recovery |
| `U103` | `3` | power pins |
| `U104` | `1` | `U104A` secondary left recovery |
| `U104` | `2` | `U104B` secondary right recovery |
| `U104` | `3` | power pins |
| `Q101` | `1` | primary left NPN emitter follower |
| `Q102` | `1` | primary left PNP emitter follower |
| `Q103` | `1` | primary right NPN emitter follower |
| `Q104` | `1` | primary right PNP emitter follower |

### Tank Cable Landings

| Ref | Unit | Role |
| --- | --- | --- |
| `J101` | `1` | primary left send landing |
| `J102` | `1` | primary left return landing |
| `J103` | `1` | primary right send landing |
| `J104` | `1` | primary right return landing |
| `J105` | `1` | secondary left send landing |
| `J106` | `1` | secondary left return landing |
| `J107` | `1` | secondary right send landing |
| `J108` | `1` | secondary right return landing |

## 3. Header And Tank-Landing Pin Ownership

### P101 `JTR-PRI`

| Pin | Net |
| --- | --- |
| `1` | `PRI_SEND_L` |
| `2` | `PRI_RET_L` |
| `3` | `AGND` |
| `4` | `PRI_SEND_R` |
| `5` | `PRI_RET_R` |
| `6` | `AGND` |

### P102 `JTR-SEC`

| Pin | Net |
| --- | --- |
| `1` | `SEC_SEND_L` |
| `2` | `SEC_RET_L` |
| `3` | `AGND` |
| `4` | `SEC_SEND_R` |
| `5` | `SEC_RET_R` |
| `6` | `AGND` |

### P103 `JTR-PWR`

| Pin | Net |
| --- | --- |
| `1` | `+15VA` |
| `2` | `AGND` |
| `3` | `-15VA` |

### Tank Landings

Treat each tank connector as a two-conductor boundary:

| Ref | Signal Pin | Shield / Return Handling |
| --- | --- | --- |
| `J101` | `PRI_TANK_L_IN` | local send-side shield landing |
| `J102` | `PRI_TANK_L_OUT` | local return-side shield landing |
| `J103` | `PRI_TANK_R_IN` | local send-side shield landing |
| `J104` | `PRI_TANK_R_OUT` | local return-side shield landing |
| `J105` | `SEC_TANK_L_IN` | local send-side shield landing |
| `J106` | `SEC_TANK_L_OUT` | local return-side shield landing |
| `J107` | `SEC_TANK_R_IN` | local send-side shield landing |
| `J108` | `SEC_TANK_R_OUT` | local return-side shield landing |

The exact connector family can stay provisional until the isolated RCA or shielded-wire landing choice is frozen, but the send/return ownership above should not drift.

## 4. Internal Audio And Shield Nodes

Use these node names when drawing the final KiCad page:

| Node | Meaning |
| --- | --- |
| `PRI_DRV_L` | left primary predriver output from `U101A` |
| `PRI_DRV_R` | right primary predriver output from `U101B` |
| `PRI_OUT_L` | left primary high-current tank send node |
| `PRI_OUT_R` | right primary high-current tank send node |
| `SEC_DRV_L` | left secondary send output from `U102A` |
| `SEC_DRV_R` | right secondary send output from `U102B` |
| `PRI_REC_L_IN` | raw primary left return input from `J102` |
| `PRI_REC_R_IN` | raw primary right return input from `J104` |
| `SEC_REC_L_IN` | raw secondary left return input from `J106` |
| `SEC_REC_R_IN` | raw secondary right return input from `J108` |
| `PRI_RET_BUF_L` | amplified primary left recovery output from `U103A` |
| `PRI_RET_BUF_R` | amplified primary right recovery output from `U103B` |
| `SEC_RET_BUF_L` | amplified secondary left recovery output from `U104A` |
| `SEC_RET_BUF_R` | amplified secondary right recovery output from `U104B` |
| `TANK_SHIELD_SEND` | local send-shield collector node |
| `TANK_SHIELD_RET` | local return-shield collector node |

## 5. Exact First-Pass Passive Map

### Primary Left Send

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R101` | `68R` | `U101A out` | `Q101 base` | left NPN base stopper |
| `R102` | `68R` | `U101A out` | `Q102 base` | left PNP base stopper |
| `R103` | `0.33R` | `Q101 emitter` | `PRI_OUT_L` | left NPN emitter resistor |
| `R104` | `0.33R` | `Q102 emitter` | `PRI_OUT_L` | left PNP emitter resistor |
| `R105` | `10R` | `PRI_OUT_L` | `C101 series node` | left zobel resistor |
| `C101` | `47 nF` film preferred | zobel series node | `AGND` | left primary send stabilization |
| `R106` | `1k`, trim or DNP slot | `PRI_SEND_L` | `U101A-` | left drive-trim placeholder |
| `R107` | `10k` | `PRI_SEND_L` | `U101A+` | left primary source resistor |
| `R108` | `10k` | `U101A out` | `U101A-` | left unity-gain feedback start |
| `D101-D102` | bias diode footprints | between transistor-bias nodes |  | left Vbe spreader reserve |

Wire the left primary send stage as:

- `PRI_SEND_L` enters the `U101A` predriver
- `U101A out` drives both complementary transistor bases through `R101/R102`
- `PRI_OUT_L` is the actual send node that goes to `J101` and back to `P101 pin 1`

### Primary Right Send

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R121` | `68R` | `U101B out` | `Q103 base` | right NPN base stopper |
| `R122` | `68R` | `U101B out` | `Q104 base` | right PNP base stopper |
| `R123` | `0.33R` | `Q103 emitter` | `PRI_OUT_R` | right NPN emitter resistor |
| `R124` | `0.33R` | `Q104 emitter` | `PRI_OUT_R` | right PNP emitter resistor |
| `R125` | `10R` | `PRI_OUT_R` | `C121 series node` | right zobel resistor |
| `C121` | `47 nF` film preferred | zobel series node | `AGND` | right primary send stabilization |
| `R126` | `1k`, trim or DNP slot | `PRI_SEND_R` | `U101B-` | right drive-trim placeholder |
| `R127` | `10k` | `PRI_SEND_R` | `U101B+` | right primary source resistor |
| `R128` | `10k` | `U101B out` | `U101B-` | right unity-gain feedback start |
| `D121-D122` | bias diode footprints | between transistor-bias nodes |  | right Vbe spreader reserve |

### Secondary Sends

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R151` | `12k` | `U102A out` | `U102A-` | left secondary feedback |
| `R152` | `12k` | `U102B out` | `U102B-` | right secondary feedback |
| `R153` | `10k` | `U102A-` | `AGND` | left secondary gain-to-ground |
| `R154` | `10k` | `U102B-` | `AGND` | right secondary gain-to-ground |
| `R155` | `220R` | `U102A out` | `SEC_OUT_L` | left series output isolator |
| `R156` | `220R` | `U102B out` | `SEC_OUT_R` | right series output isolator |
| `R157` | `10k` | `SEC_SEND_L` | `U102A+` | left source resistor |
| `R158` | `10k` | `SEC_SEND_R` | `U102B+` | right source resistor |

Wire the secondary send stage as:

- `SEC_SEND_L` drives `U102A`, then `R155`, then `J105` and `P102 pin 1`
- `SEC_SEND_R` drives `U102B`, then `R156`, then `J107` and `P102 pin 4`

### Recovery Stages

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R171` | `2.2M` | `PRI_REC_L_IN` | `AGND` | primary left input bias |
| `R172` | `2.2M` | `PRI_REC_R_IN` | `AGND` | primary right input bias |
| `R173` | `2.2M` | `SEC_REC_L_IN` | `AGND` | secondary left input bias |
| `R174` | `2.2M` | `SEC_REC_R_IN` | `AGND` | secondary right input bias |
| `R175` | `1k` | `U103A-` | `AGND` | primary left gain-to-ground |
| `R176` | `1k` | `U103B-` | `AGND` | primary right gain-to-ground |
| `R177` | `1k` | `U104A-` | `AGND` | secondary left gain-to-ground |
| `R178` | `1k` | `U104B-` | `AGND` | secondary right gain-to-ground |
| `R179` | `33k` | `U103A out` | `U103A-` | primary left feedback |
| `R180` | `33k` | `U103B out` | `U103B-` | primary right feedback |
| `R181` | `33k` | `U104A out` | `U104A-` | secondary left feedback |
| `R182` | `33k` | `U104B out` | `U104B-` | secondary right feedback |
| `C171` | `68 pF`, DNP-friendly | `U103A out` | `U103A-` | primary left comp |
| `C172` | `68 pF`, DNP-friendly | `U103B out` | `U103B-` | primary right comp |
| `C173` | `68 pF`, DNP-friendly | `U104A out` | `U104A-` | secondary left comp |
| `C174` | `68 pF`, DNP-friendly | `U104B out` | `U104B-` | secondary right comp |
| `C175-C178` | `22 nF` film preferred, DNP default | tank-return input | op-amp input | populate only if direct coupling proves troublesome |

Wire the recovery stage outputs as:

- `U103A out` to `PRI_RET_L` and `P101 pin 2`
- `U103B out` to `PRI_RET_R` and `P101 pin 5`
- `U104A out` to `SEC_RET_L` and `P102 pin 2`
- `U104B out` to `SEC_RET_R` and `P102 pin 5`

### Shield-Bond Reserve

Reserve the first-pass shield-bond footprints below even if some remain DNP:

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R205` | `100R`, DNP-friendly | `TANK_SHIELD_RET` | `AGND` | controlled shield bond option |
| `C191` | `1 nF` ceramic allowed | `TANK_SHIELD_RET` | `AGND` | RF bleed option, not in audio path |
| `R206` | `0R` or jumper | `TANK_SHIELD_SEND` | `TANK_SHIELD_RET` | lets bench work pick one-point or split shield handling |

## 6. Functional Wiring Summary By Stage

### Primary Left

- `PRI_SEND_L` enters `U101A`
- `U101A` drives `Q101/Q102`
- `PRI_OUT_L` leaves at `J101`
- tank return re-enters at `J102` as `PRI_REC_L_IN`
- `U103A` recovers and outputs `PRI_RET_L`

### Primary Right

- `PRI_SEND_R` enters `U101B`
- `U101B` drives `Q103/Q104`
- `PRI_OUT_R` leaves at `J103`
- tank return re-enters at `J104` as `PRI_REC_R_IN`
- `U103B` recovers and outputs `PRI_RET_R`

### Secondary Left

- `SEC_SEND_L` enters `U102A`
- `SEC_DRV_L` leaves at `J105`
- tank return re-enters at `J106` as `SEC_REC_L_IN`
- `U104A` recovers and outputs `SEC_RET_L`

### Secondary Right

- `SEC_SEND_R` enters `U102B`
- `SEC_DRV_R` leaves at `J107`
- tank return re-enters at `J108` as `SEC_REC_R_IN`
- `U104B` recovers and outputs `SEC_RET_R`

## 7. Local Decoupling Intent

Reserve `C291-C299` for local rail decoupling.

First-pass intent:

- one `100 nF` rail-to-ground part per op-amp supply unit
- one `10 uF` to `22 uF` local bulk rail footprint near the send section
- one `10 uF` to `22 uF` local bulk rail footprint near the recovery section

These are power-path parts, not audio-path coupling parts, so ceramics or electrolytics are acceptable here.

## 8. Verification Gate For The Later KiCad Pass

When this definition is translated into the final multi-unit KiCad page, verify all of the following:

1. `U101-U104` each have both signal units plus their power unit instantiated.
2. `PRI_SEND_L/R`, `SEC_SEND_L/R`, `PRI_RET_L/R`, and `SEC_RET_L/R` each appear exactly once at the board boundary and exactly once at the corresponding harness connector pins.
3. `Q101/Q102` and `Q103/Q104` are captured as complementary emitter followers, not floating transistor placeholders.
4. Zobel, base-stopper, emitter-resistor, and bias-reserve footprints remain present on both primary send channels.
5. The return-shield strategy is represented as parts or jumpers on this page, not only in prose.
6. No tank-send node shares copper or schematic ambiguity with the recovery-input nodes.

## 9. Explicitly Deferred Items

These are intentionally deferred:

- final idle-current target and the exact bias-spreader population for the primary send stages
- whether the recovery inputs remain fully direct-coupled or require the small film input capacitors
- final isolated RCA versus shielded-wire hardware choice for `J101-J108`
- any later tube-based coloration stage, which is outside the fixed rev-A solid-state board set unless separately defined
