# GAS Rev A — PCBWay Fabrication + Assembly Order
**Customer:** Illicit Apothecary (Jason G — jdg511@gmail.com)
**Date:** 2026-08-01 · **Order:** 6 distinct boards, **qty 5 each**, PCB fabrication + turnkey assembly
**Design tool:** KiCad 10.0.5 (Gerber X2 + Excellon drill + drill map included per board)

## Global PCB specifications (all 6 boards)
| Parameter | Value |
|---|---|
| Layers | 2 (F.Cu / B.Cu) |
| Material | FR-4, TG150 standard |
| Thickness | 1.6 mm |
| Copper weight | 1 oz outer |
| Surface finish | HASL lead-free |
| Soldermask | Green, both sides |
| Silkscreen | White, both sides |
| Min trace / space | 0.20 mm / 0.20 mm (signals 0.25 mm, power nets 0.60 mm) |
| Min via | 0.60 mm pad / 0.30 mm drill (most vias 0.8/0.4) |
| Smallest drill | 0.30 mm |
| Edge connector / castellation | None |
| Impedance control | Not required |
| Panelization | Single boards; PCBWay may panelize at their discretion |
| E-test | 100% flying probe |
| UL marking / date code | Acceptable anywhere on B.Cu silkscreen |

## Boards in this order
| Board | Size (mm) | Assembly parts | Sides | Notes |
|---|---|---|---|---|
| power-backplane | 150 × 95 | ~15 | Top only | DC-DC module PS500 is THT; barrel jack THT |
| crossfade-feedback-wet | 100 × 70 | ~50 | Top only | 1× TQ2-5V relay (THT) |
| ext-tank-routing | 120 × 80 | ~60 | Top only | 4× TQ2-5V relays (THT) |
| filter-clipper | 140 × 90 | ~55 | Top only | 3× TQ2-5V relays; **6 diodes DNP — see below** |
| io-board | 160 × 75 | ~65 | Top only | Combo XLR/TRS jacks THT on both edges |
| tank-driver-recovery | 170 × 110 | ~130 | Top only | 8× RCA jacks THT; TO-126 transistors |

## Assembly specifications
- **Type:** Turnkey preferred (PCBWay sources parts). Mixed SMD + through-hole, top side only, 5 boards assembled per design (no spares required, but quote +2 spares if marginal cost is low).
- **Stencil:** Yes, framework-less is fine.
- **Files per board folder:** `<board>-gerbers-RevA.zip` (Gerber X2 + Excellon + map), `<board>-BOM.csv` (grouped, DNP flagged), `<board>-centroid.csv` (KiCad pos, mm, top side, DNP excluded).
- **Centroid origin:** KiCad page origin; rotation per KiCad convention. Please confirm against gerbers during DFM.

### DNP — filter-clipper board ONLY (critical)
D401, D403, D405, D407, D409, D411 are **DO NOT POPULATE** (deliberate asymmetric-clipping design choice). They are excluded from the centroid file and flagged "DNP" in the BOM. **Leave the pads empty — do not source or place.** All other boards: populate everything.

### Key / non-generic parts (exact MPN required, no substitutes unless noted)
| Refs (board) | Part | MPN | Package | Note |
|---|---|---|---|---|
| K301, K201–K204, K401–K403 | DPDT signal relay, 5 V coil | **Panasonic TQ2-5V** | 10-pin THT, 2.54 mm pitch, 7.62 mm row | NO substitutes — HFD4/HFD3 are NOT footprint-compatible |
| PS500 (power-backplane) | ±15 V DC-DC module | **Mornsun URA2415YMD-10WR3** | 1"×1" THT | Acceptable drop-ins: Traco TEN 10-2423WIN, CUI PDQ10-D24-D15-D, Mean Well DKMW10F-15 |
| J101–J108 (tank-driver-recovery) | RCA jack, right-angle PCB | **Same Sky (CUI) RCJ-041** | THT, 2 mounting posts | RCJ-042/-043/-044 same footprint (color variants) OK |
| U-refs, opamps | OPA1679IDR / OPA1656 / OPA1644 per BOM | TI | SOIC | Substitutes: no |
| Audio jacks (io-board) | Combo XLR/TRS per BOM | per BOM MPN | THT | — |
| D409–D412 refs on BOM (Ge) | Germanium diodes | — | DO-35 | **All DNP or customer-installed — do NOT source** |
| P4xx/P2xx/P1xx connectors | JST XH / VH per BOM | JST | THT | Substitutes: JST-compatible OK |

Generic passives (0603 R/C, electrolytics, 1N4148WS, LEDs): PCBWay's standard stock brands are fine; ±1% resistors, X7R caps preferred.

### Assembly notes
1. Relay orientation: TQ2 coil is polarized; pin 1 marked on silkscreen — follow silk + centroid rotation.
2. Electrolytic capacitor polarity per silkscreen.
3. TO-126 transistors (BD139/BD140, tank board) mounted upright, no heatsink.
4. RCA jacks and XLR/TRS combos must sit flush to the board edge — they are panel-facing.
5. No conformal coating, no special cleaning. Standard no-clean flux OK.
6. Custom footprints (TQ2, DC-DC module, RCA) have no 3D models in files — pads/drills are authoritative.

## DFM / questions policy
For any DFM issue: minor silk trims and non-electrical edits are pre-approved; **any copper, drill, or footprint change requires customer confirmation first** (email above). Silk-over-copper warnings on some boards are known and accepted.

## Shipping
Ship all 6 sub-jobs together in one shipment when complete. Address, shipping method, and payment to be entered by the customer at checkout.
