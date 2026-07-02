# GAS Rev A Ext-Routing Schematic-Ready Definition

This file is the direct electrical definition for the rev-A ext-tank routing board.

It is more specific than [boards/ext-tank-routing-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/ext-tank-routing-board.md:1), [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1), and [rev-a-mode-truth-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-mode-truth-tables.md:1), but it does not pretend the final tank-level gain trim has already been bench-tuned.

Use this file when:

- promoting the current KiCad `ext-tank-routing.kicad_sch` page from symbol-only placeholders to a real first-pass electrical page
- freezing the actual relay role split for `Off / Series / Parallel`
- keeping the control-harness definition on `P206` aligned with the routing logic instead of treating it as an abstract mode placeholder

## 1. Assumed First-Pass Circuit Strategy

This definition freezes the first-pass topology as:

- the primary tank path is always driven from `WET_SEND_L/R`
- the secondary tank path is globally bypassed or engaged with one shared control line
- when the secondary path is engaged, a second shared control line selects whether the secondary send source is:
  - the primary recovery path (`Series`)
  - or the original wet send (`Parallel`)
- primary return, scaled secondary return, and feedback reinjection are actively summed per channel on this board before handoff to the crossfade board
- the secondary amount control is a passive stereo attenuator landing on `P206`, where the high end of each pot track is fed from the corresponding secondary return and the low end returns to `AGND`

This preserves the user-visible meaning from the mode truth table:

- `Off` = primary returns only
- `Series` = primary plus a cascaded secondary contribution
- `Parallel` = primary plus a parallel secondary contribution

## 2. Control Decode Freeze

The ext-routing board has two raw mode-control lines on `P206`:

- `CTL_EXT_MODE_A`
- `CTL_EXT_MODE_B`

For the first real capture pass, freeze their meaning as:

| `CTL_EXT_MODE_A` | `CTL_EXT_MODE_B` | Result |
| --- | --- | --- |
| `0` | `0` | `Off` |
| `1` | `0` | `Series` |
| `1` | `1` | `Parallel` |
| `0` | `1` | reserved / off-equivalent service state |

Interpretation:

- `CTL_EXT_MODE_A` is the **secondary engage** line
- `CTL_EXT_MODE_B` is the **series-versus-parallel source-select** line
- if `CTL_EXT_MODE_A` is low, the secondary path remains bypassed regardless of `CTL_EXT_MODE_B`
- under the current direct-drive rev-A assumption, these two lines may be carried as switched `+5VAUX` control rails rather than logic-only low-current indicators
- that keeps the package analog-only while avoiding any requirement for a separate MCU or dedicated relay-driver bus

This is intentionally easy to implement with a 3-position analog switch or relay-decoder strategy without needing firmware.

## 3. Required KiCad Multi-Unit Promotion

The checked-in `ext-tank-routing.kicad_sch` still needs its active and relay ownership translated into a real electrical page. The functional unit ownership should be:

| Ref | Unit / Pole Ownership | Job |
| --- | --- | --- |
| `U201A` | signal channel A | left final routing / wet-output summing |
| `U201B` | signal channel B | right final routing / wet-output summing |
| `U201C` | signal channel C | left secondary-send buffer |
| `U201D` | signal channel D | right secondary-send buffer |
| `K201` | left source-select relay | chooses left secondary source between `PRI_RET_L` and `WET_SEND_L` |
| `K202` | right source-select relay | chooses right secondary source between `PRI_RET_R` and `WET_SEND_R` |
| `K203` | left engage/bypass relay | enables or bypasses left secondary send/return path |
| `K204` | right engage/bypass relay | enables or bypasses right secondary send/return path |

Coil ownership freeze:

- `K203` and `K204` coils are driven by `CTL_EXT_MODE_A`
- `K201` and `K202` coils are driven by `CTL_EXT_MODE_B`

## 4. Connector Pin Ownership

### P201 Wet Input

| Pin | Net |
| --- | --- |
| `1` | `WET_SEND_L` |
| `2` | `AGND` |
| `3` | `WET_SEND_R` |

### P202 Primary Tank Bundle

| Pin | Net |
| --- | --- |
| `1` | `PRI_SEND_L` |
| `2` | `PRI_RET_L` |
| `3` | `AGND` |
| `4` | `PRI_SEND_R` |
| `5` | `PRI_RET_R` |
| `6` | `AGND` |

### P203 Secondary Tank Bundle

| Pin | Net |
| --- | --- |
| `1` | `SEC_SEND_L` |
| `2` | `SEC_RET_L` |
| `3` | `AGND` |
| `4` | `SEC_SEND_R` |
| `5` | `SEC_RET_R` |
| `6` | `AGND` |

### P204 Routed Output

| Pin | Net |
| --- | --- |
| `1` | `TANK_MIX_L` |
| `2` | `AGND` |
| `3` | `TANK_MIX_R` |

### P205 Feedback Reinjection

| Pin | Net |
| --- | --- |
| `1` | `FB_RET_L` |
| `2` | `AGND` |
| `3` | `FB_RET_R` |

### P206 Mode And Amount Controls

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `EXTMIX_L_HI` | left secondary-return high end |
| `2` | `EXTMIX_L_WIPER` | left amount-control wiper |
| `3` | `EXTMIX_L_LO` | left amount-control low end |
| `4` | `EXTMIX_R_HI` | right secondary-return high end |
| `5` | `EXTMIX_R_WIPER` | right amount-control wiper |
| `6` | `EXTMIX_R_LO` | right amount-control low end |
| `7` | `+5VAUX` | relay/control support rail |
| `8` | `AGND` | control return |
| `9` | `CTL_EXT_MODE_A` | secondary engage logic line |
| `10` | `CTL_EXT_MODE_B` | series/parallel source-select logic line |

### P207 Power

| Pin | Net |
| --- | --- |
| `1` | `+15VA` |
| `2` | `AGND` |
| `3` | `-15VA` |
| `4` | `+5VAUX` |

## 5. Internal Functional Nodes

Use these names as local labels or stage notes during capture:

| Node | Meaning |
| --- | --- |
| `PRI_SRC_L` | left primary send source from `WET_SEND_L` |
| `PRI_SRC_R` | right primary send source from `WET_SEND_R` |
| `SEC_SEL_L` | left secondary source selected by `K201` |
| `SEC_SEL_R` | right secondary source selected by `K202` |
| `SEC_DRV_L` | left engaged secondary-send drive node into `U201C` |
| `SEC_DRV_R` | right engaged secondary-send drive node into `U201D` |
| `SEC_AMT_L` | left scaled secondary-return contribution from `EXTMIX_L_WIPER` |
| `SEC_AMT_R` | right scaled secondary-return contribution from `EXTMIX_R_WIPER` |

## 6. Relay Functional Ownership

### K201 Left Source-Select Relay

Functional job:

- selects the left secondary send source before the left secondary-send buffer

First-pass contact meaning:

- de-energized: `PRI_RET_L` -> `SEC_SEL_L`
- energized: `WET_SEND_L` -> `SEC_SEL_L`

### K202 Right Source-Select Relay

Functional job:

- selects the right secondary send source before the right secondary-send buffer

First-pass contact meaning:

- de-energized: `PRI_RET_R` -> `SEC_SEL_R`
- energized: `WET_SEND_R` -> `SEC_SEL_R`

### K203 Left Engage / Bypass Relay

Use the two poles as:

- pole A:
  - bypass state: disconnect or park the left secondary-send buffer input so no left secondary send is driven
  - engaged state: `SEC_SEL_L` -> `SEC_DRV_L`
- pole B:
  - bypass state: disconnect `SEC_RET_L` from the amount-control high node
  - engaged state: `SEC_RET_L` -> `EXTMIX_L_HI`

### K204 Right Engage / Bypass Relay

Use the two poles as:

- pole A:
  - bypass state: disconnect or park the right secondary-send buffer input so no right secondary send is driven
  - engaged state: `SEC_SEL_R` -> `SEC_DRV_R`
- pole B:
  - bypass state: disconnect `SEC_RET_R` from the amount-control high node
  - engaged state: `SEC_RET_R` -> `EXTMIX_R_HI`

## 7. Exact First-Pass Active Wiring Intent

### U201A Left Final Sum

- inverting active summer
- `U201A+` to `AGND`
- `PRI_RET_L` enters through a `20k` input resistor
- `EXTMIX_L_WIPER` enters through a `20k` input resistor
- `FB_RET_L` enters through a `20k` input resistor
- `U201A out` returns through a `20k` feedback resistor
- output drives `TANK_MIX_L` through a small isolator resistor

### U201B Right Final Sum

- same structure as `U201A`
- output drives `TANK_MIX_R`

### U201C Left Secondary-Send Buffer

- unity-gain follower or unity-gain non-inverting stage
- input source is `SEC_DRV_L`
- output drives `SEC_SEND_L` through a small isolator resistor

### U201D Right Secondary-Send Buffer

- unity-gain follower or unity-gain non-inverting stage
- input source is `SEC_DRV_R`
- output drives `SEC_SEND_R` through a small isolator resistor

## 8. Exact First-Pass Passive Map

### Left Channel

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R201` | `100R` | `WET_SEND_L` | `PRI_SEND_L` | left primary-send isolator |
| `R202` | `20k` | `PRI_RET_L` | `U201A-` | left primary-return summing resistor |
| `R203` | `20k` | `EXTMIX_L_WIPER` | `U201A-` | left scaled-secondary summing resistor |
| `R204` | `20k` | `FB_RET_L` | `U201A-` | left feedback reinjection resistor |
| `R205` | `100R` | `U201A out` | `TANK_MIX_L` | left routed-output isolator |
| `R206` | `100R` | `U201C out` | `SEC_SEND_L` | left secondary-send isolator |
| `R209` | `20k` | `U201A out` | `U201A-` | left final-sum feedback resistor |
| `R211` | `100k` | `SEC_DRV_L` | `AGND` | left secondary-send park / bias footprint |

### Right Channel

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R221` | `100R` | `WET_SEND_R` | `PRI_SEND_R` | right primary-send isolator |
| `R222` | `20k` | `PRI_RET_R` | `U201B-` | right primary-return summing resistor |
| `R223` | `20k` | `EXTMIX_R_WIPER` | `U201B-` | right scaled-secondary summing resistor |
| `R224` | `20k` | `FB_RET_R` | `U201B-` | right feedback reinjection resistor |
| `R225` | `100R` | `U201B out` | `TANK_MIX_R` | right routed-output isolator |
| `R226` | `100R` | `U201D out` | `SEC_SEND_R` | right secondary-send isolator |
| `R229` | `20k` | `U201B out` | `U201B-` | right final-sum feedback resistor |
| `R231` | `100k` | `SEC_DRV_R` | `AGND` | right secondary-send park / bias footprint |

### Amount-Control Landing

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R241` | `20k` nominal / trim-capable | series-mode gain trim reservation | utility stage or DNP option | reserve only if series mode needs gain recovery |
| `R242` | `20k` | `FB_RET_L` | left routing node | keep as named feedback entry anchor |
| `R243` | `20k` | `FB_RET_R` | right routing node | keep as named feedback entry anchor |

Passive pot landing ownership:

- `EXTMIX_L_HI` from engaged `SEC_RET_L`
- `EXTMIX_L_LO` to `AGND`
- `EXTMIX_R_HI` from engaged `SEC_RET_R`
- `EXTMIX_R_LO` to `AGND`

## 9. Coil Support And Housekeeping

Reserve these parts on the relay/control side:

- `D261-D264`
  - one flyback or suppression position per relay coil
- `R261-R264`
  - optional base/gate/drive-limiting positions if a discrete or backplane driver is later inserted
- `C291-C299`
  - local power decoupling near relay coils and `U201`

## 10. Verification Gate For The Later KiCad Pass

When this definition is translated into the actual KiCad page, verify all of the following:

1. `P202` and `P203` keep the frozen `send / return / AGND / send / return / AGND` order.
2. `P206` remains the full 10-wire landing with separate left/right amount-pot ends and both raw mode lines.
3. `CTL_EXT_MODE_A` alone can bypass the secondary path regardless of the source-select state.
4. `CTL_EXT_MODE_B` changes the secondary send source only when the secondary path is engaged.
5. `TANK_MIX_L/R` always include the primary return path in all three user modes.
6. `SEC_RET_L/R` are disconnected from the output sum in `Off`.
7. `SEC_SEND_L/R` are not actively driven in `Off`.

## 11. Explicitly Deferred Items

These are intentionally left for later bench or layout passes:

- exact final gain of the secondary-send buffers
- whether `R241` remains DNP or becomes a real series-mode makeup trim
- any extra crosstalk-bleed or relay-contact damping parts that prove necessary with real tanks
- the exact transistor or backplane-driver stage, if the relay coils are not driven directly from the switched `CTL_EXT_MODE_A/B` control rails
