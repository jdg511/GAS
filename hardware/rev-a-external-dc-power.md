# GAS Rev A External DC Power

Rev A now sources low-voltage DC from an **external wall adapter** instead of an internal `Mean Well RT-50C` triple-output AC/DC module. This eliminates the mains-hazard zone, IEC inlet, fuse holder, and Class I safety burden inside the enclosure.

This file is the authority for the new power topology. The earlier internal-PSU references in [rev-a-power-budget.md](rev-a-power-budget.md), [rev-a-system-architecture.md](rev-a-system-architecture.md), [boards/system-remaining.md](boards/system-remaining.md), and the power-backplane BOM are superseded by this document.

## Wall Adapter Choice

- **Jameco ReliaPro DDU300050E9340 candidate**
  - single output `+30 VDC`
  - `500 mA`
  - `15 W` total
  - `5.5 mm OD / 2.5 mm ID` barrel plug, center positive per the Jameco listing snapshot from `2026-06-29`
  - current live Jameco page text describes the SKU as an `unregulated linear wall adapter`
  - source: [Jameco DDU300050E9340 product page](https://www.jameco.com/z/DDU300050E9340-Jameco-ReliaPro-AC-to-DC-Wall-Adapter-Transformer-Single-Output-30-Volt-500mA-15-Watt_199523.html)

Approved alternates for sourcing resilience (same `+30 VDC` nominal output, equal or higher current rating):

- Jameco DDU300100xxx series at `1 A` if available
- Any UL/CE-listed `+30 VDC` regulated SMPS wall adapter with `>= 500 mA` capability and matching barrel polarity

## Rail Generation Strategy

The audio design still requires three rails:

- `+15VA` and `-15VA` for the analog signal path
- `+5VAUX` for the routing relays and any control overhead

These are generated **on-board** from the external `+30 VDC` input by a small "power entry and conversion" section that replaces the old `RT-50C` block on the power-backplane PCB.

### Stage 1: Input protection and fusing

- DC barrel jack on the **service endcap**; use a `5.5 mm OD / 2.5 mm ID` compatible jack and confirm polarity matches the Jameco adapter
- **Series Schottky** for reverse-polarity protection (`SS34` or equivalent, 40 V / 3 A SMD). Voltage drop is roughly `0.4 V` at the rev-A max current, which is acceptable
- **Polyfuse** at the input as belt-and-suspenders against board shorts (Bourns `MF-R100`, 1 A hold). The adapter's own current limit is the primary protection
- Bulk input cap, 220-470 uF electrolytic, low-ESR
- TVS for surge protection (SMAJ33A or similar, 33 V standoff)

### Stage 2: +30 V to ±15 V isolated DC-DC

- **Recommended:** Mornsun `URB2415YMD-10WR3` (18-36 V in, +/-15 V out, 10 W)
- **Alternate:** RECOM `REC10-2415DZ/H1/A/M` (18-36 V in, +/-15 V out, 10 W) at higher cost / better stock
- **Alternate:** XP Power `JTD1024S15` (18-36 V in, +/-15 V out, 10 W)

All three are isolated dual-output modules with input range that comfortably brackets `+30 V` and rated output power above the rev-A `7.5 W` worst-case analog load. The Mornsun is the lowest-cost current pick; RECOM is the highest-stock alternate per [rev-a-supply-watch.md](bom/rev-a-supply-watch.md).

### Stage 3: Post-DC-DC ripple filter on each analog rail

Switching DC-DC modules add `30-150 mVpp` of high-frequency ripple. This must not reach the audio op-amp rails.

Per rail (`+15VA` and `-15VA`), at the output of the DC-DC and before any audio board's local decoupling:

- ferrite bead, `BLM18PG471SN1` class, `>= 470 ohm` at 100 MHz, `1 A` rated, in series
- `100 uF / 25 V` low-ESR electrolytic to AGND
- `10 uF` film or X7R MLCC to AGND
- `100 nF` film to AGND

This is a passive LC + bead network, no linear post-regulator. Target rail ripple at the power-backplane output to the audio harness: under `5 mVpp` at any frequency, matching the previous internal-PSU spec in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md).

If bench measurement at the P-0 step in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) shows the LC filter alone cannot meet `5 mVpp`, fall back to linear post-regulation with `LM7815CT` / `LM7915CT` and a `+30 V` to `+/-18 V` DC-DC module instead. This is documented as a contingency, not the rev-A default.

### Stage 4: +5VAUX generation

- **Recommended:** RECOM `R-78E5.0-0.5` switching regulator (7-28 V in, 5 V at 500 mA out, 7805 pinout, no heatsink required)
- Fed from the `+15VA` rail, not directly from the `+30 V` input, to keep the input voltage inside the regulator's max range and to share the DC-DC's filtering
- Add `47 uF` electrolytic plus `100 nF` X7R at the output
- Local decoupling on the ext-routing board where relay coils land remains unchanged

## Updated Rail Block Diagram

```
[Jameco DDU300050E9340 wall adapter]
   |
   |  +30 VDC, 500 mA max
   v
[DC barrel jack on service endcap]
   |
   v
[SS34 reverse-polarity Schottky] -> [MF-R100 polyfuse] -> [220 uF bulk + SMAJ33A TVS]
   |
   v
[Mornsun URB2415YMD-10WR3 isolated DC-DC]
   |
   +--> +15VA  -> [ferrite + 100 uF + 10 uF + 100 nF] -> harness to audio boards
   +--> -15VA  -> [ferrite + 100 uF + 10 uF + 100 nF] -> harness to audio boards
                                                            |
                                                            v
                                              [R-78E5.0-0.5] -> +5VAUX -> ext-routing relay coils
```

## Power Budget Versus Adapter Capacity

| Rail | Worst-case current | Rail power |
|---|---|---|
| `+15VA` | ~250 mA | 3.75 W |
| `-15VA` | ~250 mA | 3.75 W |
| `+5VAUX` | ~250 mA | 1.25 W |
| **Audio-side subtotal** |  | **~8.75 W** |
| DC-DC + +5V reg losses (~15 percent) |  | ~1.3 W |
| Schottky + polyfuse drop |  | ~0.2 W |
| **Wall-side total** |  | **~10.3 W** |
| Adapter capacity |  | 15 W |
| Headroom |  | **~31 percent** |

The 15 W adapter is adequate. The 1 A variant of the same Jameco family doubles the headroom if desired later, with no design change.

## Grounding

- DC barrel jack outer ring is the chassis-side incoming `0V` reference
- on-board: `0V` from the jack becomes `AGND` at the bulk cap; chassis bond is the existing star-ground point per [rev-a-layout-rules.md](rev-a-layout-rules.md)
- DC-DC module output `0V` ties to the same `AGND` point (the DC-DC's isolation barrier is what allows the module's outputs to define the analog ground reference for the rest of the unit)
- `DGND` for the `+5VAUX` rail remains the relay/control return only; tied to `AGND` at the star point, single connection

## What This Removes From The Rev-A BOM

- `Mean Well RT-50C` AC/DC module
- IEC mains inlet, fuse holder, mains cordage inside the chassis
- mains-side X / Y caps and the high-voltage zone of the power backplane

These are now replaced by the parts in [bom/rev-a-power-backplane-preliminary-bom.csv](bom/rev-a-power-backplane-preliminary-bom.csv) (updated in this same revision).

## What This Changes In Manufacturing

The power backplane is now a low-voltage-only board. Practical effects, called out in [rev-a-manufacturing.md](rev-a-manufacturing.md):

- mains-side creepage / clearance rules no longer apply to any board in the unit
- no Class I AC entry means no chassis-bond safety-test step at final assembly
- the wall-adapter side still benefits from external pre-certified supply handling, but the exact production adapter should not be frozen until regulation behavior is verified on the chosen SKU
- the power backplane can now be SMT-assembled by JLCPCB at the same tier as the audio boards, instead of needing PCBWay's mixed-tech path for the mains module

## Verification Items

These are added to the front of [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) at step P-0:

1. **Regulated vs unregulated adapter check.** Measure open-circuit voltage at the barrel plug with no load. Should read `+29 V` to `+31 V`. If it reads above `+34 V`, the adapter is unregulated and must be replaced with a regulated SMPS variant before powering any DC-DC module
2. Polarity sanity check at the jack vs adapter; reverse-polarity Schottky must reverse-bias safely on opposite polarity (verify by measuring `0 V` downstream when the plug is flipped)
3. Bulk cap inrush: scope the input rail during plug-in; should settle to `+30 V` within 100 ms with no overshoot above `+35 V`
4. DC-DC output ripple per rail at full load: under `5 mVpp` at any frequency at the harness output (after the LC filter), measured per the existing P-0 procedure

## Open Items For This Topology

- **Regulated-vs-unregulated confirmation on the exact Jameco SKU.** Jameco's listing language still uses "wall adapter transformer" wording, so the first physical sample must be checked before any DC-DC module is powered. If verification step 1 above fails, substitute a confirmed regulated `+30 VDC` adapter before continuing
- Final ferrite bead part number freezes after the first DC-DC module sample is bench-measured for its actual ripple spectrum
- If a future revision wants `+/-18 V` rails for extra headroom, the `+30 V` source supports that with a different DC-DC module choice and no chassis-side change
