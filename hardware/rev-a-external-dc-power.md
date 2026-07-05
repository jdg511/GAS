# GAS Rev A External DC Power

Rev A now sources low-voltage DC from an **external wall adapter** instead of an internal `Mean Well RT-50C` triple-output AC/DC module. This eliminates the mains-hazard zone, IEC inlet, fuse holder, and Class I safety burden inside the enclosure.

This file is the authority for the new power topology. The earlier internal-PSU references in [rev-a-power-budget.md](rev-a-power-budget.md), [rev-a-system-architecture.md](rev-a-system-architecture.md), [boards/system-remaining.md](boards/system-remaining.md), and the power-backplane BOM are superseded by this document.

## Wall Adapter Choice

- **Triad Magnetics WSU240-0750 (selected `2026-07-04`)**
  - single output `+24 VDC`, regulated SMPS
  - `750 mA` / `18 W`
  - regulation (line and load combined): `+/-5%`; output ripple `150 mVpp` max
  - UL 62368-1 Class II double-insulated (UL file `E345519`), DOE Level VI, 5-year warranty
  - `5.5 mm OD / 2.1 mm ID` center-positive barrel plug
  - source: [DigiKey WSU240-0750](https://www.digikey.com/en/products/detail/triad-magnetics/WSU240-0750/3094933), `USD 12.43` at qty 1, `>1000` in stock on `2026-07-04`
  - datasheet: [Triad WSU240-0750 PDF](https://catalog.triadmagnetics.com/Asset/WSU240-0750.pdf)

This supersedes the earlier Jameco `DDU300050E9340` `+30 VDC` candidate, whose live product page described an **unregulated linear** adapter. Moving to a confirmed-regulated `+24 VDC` SMPS closes that open item and puts the input at the DC-DC module's nominal design-center voltage. The P-0 open-circuit measurement is retained as a receiving check.

Approved alternates for sourcing resilience (same `+24 VDC` nominal, regulated SMPS, equal or higher current rating):

- Tri-Mag `L6R20-240` (`24 V / 0.83 A / 20 W`, UL 62368-1, [DigiKey listing](https://www.digikey.com/en/products/detail/tri-mag-llc/L6R20-240/13538149))
- Triad `WSU240-1000` (`24 V / 1 A / 24 W`) if extra headroom is ever wanted, no design change needed
- Any UL/CE-listed regulated `+24 VDC` SMPS wall adapter with `>= 750 mA` capability and a `5.5 x 2.1 mm` center-positive plug

## Rail Generation Strategy

The audio design still requires three rails:

- `+15VA` and `-15VA` for the analog signal path
- `+5VAUX` for the routing relays and any control overhead

These are generated **on-board** from the external `+24 VDC` input by a small "power entry and conversion" section that replaces the old `RT-50C` block on the power-backplane PCB.

### Stage 1: Input protection and fusing

- DC barrel jack on the **service endcap**: Same Sky `PJ-005A` (`5.5 mm OD / 2.1 mm ID`, center positive, 5 A, same mounting hole and hardware as the previously specified `PJ-005B`); confirm polarity matches the Triad adapter
- **Series Schottky** for reverse-polarity protection (`SS34` or equivalent, 40 V / 3 A SMD). Voltage drop is roughly `0.4 V` at the rev-A max current, which is acceptable
- **Polyfuse** at the input as belt-and-suspenders against board shorts (Bourns `MF-R100`, 1 A hold). The adapter's own current limit is the primary protection
- Bulk input cap, 220-470 uF electrolytic, low-ESR
- TVS for surge protection (SMAJ33A or similar, 33 V standoff)

### Stage 2: +24 V to ±15 V isolated DC-DC

- **Recommended:** Mornsun `URA2415YMD-10WR3` (9-36 V in, 24 V nominal, +/-15 V dual out, 10 W) — the URA dual-output variant is what the captured schematic and priced BOM carry; the URB suffix in earlier revisions of this file was the single-output variant and was corrected per [kicad/datasheet_cache/ura2415ymd.summary.md](kicad/datasheet_cache/ura2415ymd.summary.md)
- **Alternate:** RECOM `REC10-2415DZ/H1/A/M` (18-36 V in, +/-15 V out, 10 W) at higher cost / better stock
- **Alternate:** XP Power `JTD1024S15` (18-36 V in, +/-15 V out, 10 W)

All three are isolated dual-output modules whose input range brackets `+24 V` — for the Mornsun, `+24 V` is the nominal design-center input — and rated output power is above the rev-A `7.5 W` worst-case analog load. The Mornsun is the lowest-cost current pick; RECOM is the highest-stock alternate per [rev-a-supply-watch.md](bom/rev-a-supply-watch.md).

### Stage 3: Post-DC-DC ripple filter on each analog rail

Switching DC-DC modules add `30-150 mVpp` of high-frequency ripple. This must not reach the audio op-amp rails.

Per rail (`+15VA` and `-15VA`), at the output of the DC-DC and before any audio board's local decoupling:

- ferrite bead, `BLM18PG471SN1` class, `>= 470 ohm` at 100 MHz, `1 A` rated, in series
- `100 uF / 25 V` low-ESR electrolytic to AGND
- `10 uF` film or X7R MLCC to AGND
- `100 nF` film to AGND

This is a passive LC + bead network, no linear post-regulator. Target rail ripple at the power-backplane output to the audio harness: under `5 mVpp` at any frequency, matching the previous internal-PSU spec in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md).

If bench measurement at the P-0 step in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) shows the LC filter alone cannot meet `5 mVpp`, fall back to linear post-regulation with `LM7815CT` / `LM7915CT` and a `+24 V` to `+/-18 V` DC-DC module instead. This is documented as a contingency, not the rev-A default.

### Stage 4: +5VAUX generation

- **Recommended:** RECOM `R-78E5.0-0.5` switching regulator (7-28 V in, 5 V at 500 mA out, 7805 pinout, no heatsink required)
- Fed from the `+15VA` rail, not directly from the `+24 V` input, to keep the input voltage inside the regulator's max range and to share the DC-DC's filtering
- Add `47 uF` electrolytic plus `100 nF` X7R at the output
- Local decoupling on the ext-routing board where relay coils land remains unchanged

## Updated Rail Block Diagram

```
[Triad WSU240-0750 wall adapter]
   |
   |  +24 VDC, 750 mA max
   v
[PJ-005A DC barrel jack on service endcap, 5.5 x 2.1 mm center positive]
   |
   v
[SS34 reverse-polarity Schottky] -> [MF-R100 polyfuse] -> [220 uF bulk + SMAJ33A TVS]
   |
   v
[Mornsun URA2415YMD-10WR3 isolated DC-DC]
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
| Adapter capacity |  | 18 W |
| Headroom |  | **~43 percent** |

The 18 W adapter is adequate. Input current at the worst-case `10.3 W` wall-side load is about `0.43 A` against the adapter's `0.75 A` rating. The `WSU240-1000` (`24 W / 1 A`) variant of the same Triad family adds further headroom if desired later, with no design change.

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

1. **Adapter receiving check.** Measure open-circuit voltage at the barrel plug with no load. The regulated `WSU240-0750` should read `+22.8 V` to `+25.2 V` (`24 V +/-5%`). If it reads above `+27 V`, the unit is not the intended regulated adapter (wrong SKU or counterfeit) and must not be connected to the power backplane
2. Polarity sanity check at the jack vs adapter; reverse-polarity Schottky must reverse-bias safely on opposite polarity (verify by measuring `0 V` downstream when the plug is flipped)
3. Bulk cap inrush: scope the input rail during plug-in; should settle to `+24 V` within 100 ms with no overshoot above `+30 V`
4. DC-DC output ripple per rail at full load: under `5 mVpp` at any frequency at the harness output (after the LC filter), measured per the existing P-0 procedure

## Open Items For This Topology

- **KiCad net names still say `+30V_RAW` / `+30V_F`.** The captured power-backplane schematic predates the `2026-07-04` adapter change; those nets now carry `+24 V` nominal. Rename to `+VIN_RAW` / `+VIN_F` (or `+24V_RAW` / `+24V_F`) at the next schematic capture pass before layout freeze
- `PJ-005A` footprint pin map needs the same datasheet-to-footprint sanity pass previously flagged for `PJ-005B` (same mechanical family, but confirm before layout freeze)
- Final ferrite bead part number freezes after the first DC-DC module sample is bench-measured for its actual ripple spectrum
- If a future revision wants `+/-18 V` rails for extra headroom, the `+24 V` source supports that with a different DC-DC module choice and no chassis-side change
