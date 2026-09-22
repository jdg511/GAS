# GAS Rev B Circuit Board: PCBWay Fabrication + Assembly Order
**Customer:** Illicit Apothecary (Jason G, jdg511@gmail.com)
**Date:** 2026-09-13 · **Board:** `circuit-board` Rev B, qty 5, PCB fabrication + turnkey assembly
**Design tool:** KiCad 10.0.5 (Gerber X2 + Excellon drill + drill map)

This board **replaces the Rev A `filter-clipper` board** in the 2026-08 order. The other five Rev A boards (power-backplane, crossfade-feedback-wet, ext-tank-routing, io-board, tank-driver-recovery) are unchanged; do not re-order them unless you want spares. Harness changes are listed at the end.

## PCB specification (same rules as the Rev A boards)
| Parameter | Value |
|---|---|
| Size | 190 x 170 mm, rectangular, 4x M3 holes 4 mm from the corners |
| Layers | 2 (F.Cu / B.Cu), AGND pour both sides |
| Material / thickness | FR-4 TG150, 1.6 mm |
| Copper | 1 oz outer |
| Finish | HASL lead-free |
| Soldermask / silkscreen | Green / white, both sides |
| Min trace / space | 0.20 / 0.20 mm |
| Min via | 0.60 mm pad / 0.30 mm drill |
| Impedance control | Not required |
| E-test | 100 % flying probe |

## Assembly
- Turnkey, mixed SMD + THT, **top side only**, 5 boards assembled.
- Stencil: yes, frameless.
- Files: `circuit-board-gerbers-RevB.zip`, `circuit-board-BOM-RevB.csv` (grouped, MPN + Manufacturer + Alt_MPN, DNP flagged), `circuit-board-centroid-RevB.csv` (KiCad pos, mm, top, DNP excluded).
- Centroid origin: KiCad page origin (board top-left corner is at 0,0). Rotation per KiCad convention.

### DNP (do not populate)
RV1301, RV1321, R1305, R1325 (THAT2180 symmetry network; the A-grade part is factory trimmed). Flagged DNP in the BOM and excluded from the centroid. Leave the pads empty.

### Parts that need attention
| Refs | Part | MPN | Note |
|---|---|---|---|
| U1303, U1304 | THAT 2180A VCA, SIP-8 THT | 2180AL08-U | **End of life.** Mouser had 1226 pcs on 2026-09-13. If PCBWay cannot source, the customer will consign (buy from Mouser 887-2180AL08-U). Alt: 2180CL08-U (lower grade, same pinout). |
| VT1101, VT1121 | Vactrol VTL5C3, axial 4-lead THT | VTL5C3 (Xvive) | Not at DigiKey/Mouser; sold by pedal-parts distributors (Stompbox Parts, Small Bear, Synthrotek, Tayda). **Customer consigns if not sourceable.** Mount flat, LED end toward the silkscreen "K" mark. |
| Q401, Q501, Q1201, Q1221 | J201 / 2N5457 JFET, TO-92 | J201, 2N5457 (InterFET) | InterFET is the only active TO-92 source (Mouser 106-J201). Mount upright. For Q1201/Q1221 the customer prefers |Vgs(off)| under 5 V; any 2N5457 is acceptable, the board has a trim. |
| K1..K7 | DPDT signal relay 5 V | Panasonic TQ2-5V | **No substitutes** (footprint is TQ2 specific). Pin 1 marked on silkscreen. |
| U101 | 9 V regulator SOT-89 | L78L09ACUTR | |
| U102, U401, U402, U501 | TL072H SOIC-8 | TL072HIDR | The H grade (4.5 V rated) is required, not TL072C. |
| U201, U202, U301, U302, U1101, U1201, U1301, U1302, U1305 | OPA1679 SOIC-14 | OPA1679IDR | No substitutes. |
| C401, C404, C601, C603, C606, C701, C703, C706, C801, C804, C901, C904, C1141, C1301, C1321, C1341, C1342, C1344 | 1 uF 63 V film, box, 5 mm pitch | WIMA MKS2C041001F00KSSD | Alt Kemet R82EC4100AA50K. Any 1 uF metallised polyester/PP box cap on 5 mm pitch, 7.2 x 4.5 mm max body, is fine. |
| C202, C203, C302, C303 (1210); C204, C304, C402, C502 (1206); C205, C305, C602, C702, C605, C705 (0805) | PPS film SMD | Panasonic ECH-U1C series per BOM | Film, not ceramic. Do not substitute MLCC. |
| RV401, RV501, RV1101, RV1201, RV1221, RV1342 | 4 mm SMD trimmers | Bourns 3314J-1-503E / -103E | Set to mid travel at assembly. |
| P4, P5 | JST XH 16-pin | B16B-XH-A(LF)(SN) | JST-compatible OK. |

Generic passives (0603 1 % resistors, C0G/X7R 0603 caps, SMD electrolytics, 1N4148W, MMBT3904/3906): PCBWay standard stock is fine, keep the values and packages.

## Assembly notes
1. Relay orientation: TQ2 coil is polarised, follow silkscreen pin 1 and centroid rotation.
2. Electrolytic polarity per silkscreen.
3. TO-92 JFETs upright, flat side per silkscreen.
4. Vactrols lie flat along the axis marked on the silkscreen; LED leads at the "LED / K" end.
5. SIP-8 THAT2180 upright, pin 1 at the marked end.

## Harness / system changes that go with this board (for the customer's own build notes)
- JXF-FILT / JFILT-WET 3-pin audio cables are unchanged (now labelled JXF-CIR / JCIR-WET on this board).
- Control cables are new: two 16-pin JST XH harnesses (P4, P5) replace the Rev A 12-pin JFILT-CTL-A/B. Pinout in `rev-b-circuit-board-definition.md` section 6.
- Panel: Drive dual 10k linear pot, HPF and LPF 4-gang 100k pots wired as rheostats, 1P7T non-shorting rotary for Mode (common to +5VAUX). The Rev A clip-mode 2-bit lines and the HPF-Q / LPF-Q pots are gone.
- Crossfade/feedback/wet board: delete the crossfade pot; bridge P307 pins 1-2 and 4-5 in the harness.
