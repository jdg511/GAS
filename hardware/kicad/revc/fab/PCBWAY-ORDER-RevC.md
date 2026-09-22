# GAS Rev C: PCBWay Fabrication + Turnkey Assembly Order

**Customer:** Illicit Apothecary (Jason G). **Date:** 2026-09-21c (control-deck carries all six dual pots, 7 toggles and the 3.5 mm footswitch jack; the two 4-gang filter pots ride on a new filter-pot riser; io-board and circuit-board connectors re-pinned). **Qty:** 5 of each board, 10 of the filter-pot riser. KiCad 10.0 (Gerber X2, Excellon, centroid mm).

This order replaces every earlier GAS board (Rev A power-backplane, io-board, ext-tank-routing, crossfade-feedback-wet, tank-driver-recovery, filter-clipper and Rev B circuit-board). Do not build any of those.

| Board | Folder | Size mm | Parts (placed) | THT parts |
| --- | --- | --- | --- | --- |
| io-board | `io-board/` | 136 x 180 | 255 | 10 x WIMA 1 uF film (MKS2), JST headers (no jacks any more) |
| circuit-board | `circuit-board/` | 120 x 175 | 238 | 2 x Coolaudio V2181 (SIP-8), 9 x WIMA 1 uF film, JST headers |
| control-deck | `control-deck/` | 152.4 round, with cut-outs | 24 | 7 x Dailywell 1M toggles, 6 x Alps RK09L pots, Same Sky PJ-064B DC jack, XKB PJ-301C 3.5 mm jack, 8 x JST XH + 1 x JST VH headers **on the bottom side** |
| jack-board | `jack-board/` | 152.4 round band (Y -40 to +49), 2 cut-outs | 103 | 4 x Neutrik NCJ6FI-V, 4 x JST headers **on the bottom side** |
| filter-pot-riser | `filter-pot-riser/` | 46 x 15 | 2 | 1 x Bourns PTD904-2015K-B503 (side adjust, 12 pins), 1 x JST XH-8. **Build 2 per unit**, both identical |
| tank-board | `tank-board/` | 120 x 150 | 154 | 8 x Same Sky RCJ-041 RCA, JST headers |
| power-board | `power-board/` | 120 x 62 | 24 | TRACO TEL 12-2423, RECOM R-78HB5.0-0.5, JST headers |

Each folder: `<board>-RevC-gerbers.zip`, `<board>-RevC-BOM.csv` (Designator, Qty, Value, Package, MPN, Manufacturer, Description, DNP), `<board>-RevC-centroid.csv`, `<board>-RevC-assembly-top.pdf`, `<board>-RevC-schematic.pdf`, DRC and ERC reports, render.

## PCB specification (all boards)

| Parameter | Value |
| --- | --- |
| Layers | 2, FR-4 TG150, 1.6 mm, 1 oz copper |
| Finish | HASL lead-free |
| Mask / silk | green / white |
| Min track / space | 0.20 / 0.20 mm |
| Min via | 0.60 mm pad / 0.30 mm drill |
| Board outline | io / circuit / tank / power: rectangular with 4 x M3 plated holes. control-deck and jack-board: **round 152.4 mm with internal and edge cut-outs** (routed, not V-scored; see Edge.Cuts) |
| E-test | 100 % |

## Assembly

- Turnkey, SMD top side only, mixed SMD + THT, frameless stencil. **Exception:** the JST headers on control-deck (P1..P9) and jack-board (P1..P4) go on the **bottom** side (THT, hand solder); they are in the centroid file with side = bottom. The filter-pot riser is THT only, both parts on the top side.
- Centroid origin: KiCad page origin, units mm, rotation per KiCad convention.
- DNP: none. jack-board JP1 is a solder jumper: leave it **open**.
- Set all Bourns 3314J trimmers to mid travel.

## Parts needing attention

| Part | Boards | Note |
| --- | --- | --- |
| Coolaudio V2181 (SIP-8) | circuit | Not at Mouser / DigiKey / LCSC: hobby distributors (Small Bear, synthCube, musikding) or customer consigns. Alternate: THAT 2181BL08-U (same pinout) |
| TI DRV135UA | io | SO-8 balanced line driver, no substitute (DRV134UA is the SO-16 version and does not fit) |
| TI OPA1642AIDR | jack | JFET input dual; no substitute |
| TDK C3225C0G1H105J250AA | jack | 1 uF C0G 1210; must be C0G |
| Neutrik NCJ6FI-V | jack | vertical combo jacks |
| Alps RK09L1240015 | control-deck | dual 10k linear, centre detent, 6 off |
| Dailywell 1MS3T1B1M2QES-5 (6 off) and 1MD3T1B1M2QES (1 off) | control-deck | PC-pin (M2) versions only, not solder lug (M1) |
| Same Sky PJ-064B | control-deck | low stock (50 at Mouser); PJ-064A is the wrong centre pin (2.0 mm) |
| XKB PJ-301C | control-deck | LCSC C692433, vertical 3.5 mm TRS with M6 bushing. Must be the **vertical / "straight"** type, not a right-angle PJ-320 / PJ-342. Pads are plated slots 0.9 x 2.6 mm |
| Bourns PTD904-2015K-B503 | filter-pot-riser | 4-gang 50k linear, **side adjust** (pins at 90 degrees to the shaft), M7x0.75, 15 mm shaft. 2 per unit. Nut and washer supplied with the pot are needed |
| OPA1679IDR | io, circuit | Low stock at Mouser; any authorized distributor. No substitute |
| OPA1644AIDR, OPA1656IDR | io, tank | No substitute |
| Omron G6K-2F-Y DC5 | all but power | SMD relay, no substitute (footprint). Pin 1 mark per silkscreen |
| onsemi MMBF5457 | io (4), circuit (2) | SOT-23 JFET. For circuit Q1201 / Q1221 the customer prefers parts with |Vgs(off)| under 5 V if selectable |
| Diodes Inc BAT54-7-F | io | single Schottky SOT-23 (not the BAT54S/C/A doubles) |
| TRACO TEL 12-2423 | power | isolated DC/DC. Customer consigns if needed |
| Panasonic ECH-U film caps | circuit | PPS film SMD: do not substitute ceramic |
| C0G 22 nF 1206 (Murata GRM31C5C1H223JA01L) | io | must be C0G / NP0 |
| RCJ-041 | tank | barrels overhang the rear board edge by design |
