# GAS Rev A Open Issues

This file keeps the remaining unresolved items visible so they do not get mistaken for completed design decisions.

## 0. io-board: Vias in SMD Pads (rev-B layout item)

Recorded `2026-07-04` from the NextPCB HQDFM report on the io-board fab package.

Open issue:

- four `AGND` vias sit inside SMD pads: `C92.2`, `C94.2` (100n decoupler pads, 0.4 mm drill) and `U2.5`, `U4.5` (OPA1656 pads, 0.3 mm drill)
- during reflow, solder can wick down the via barrel and starve the joint (tombstoning / weak fillet risk)
- automated relocation was attempted and rejected: with the rev-A 0.2 mm design rules there is no compliant off-pad landing within 3.2 mm of any of the four pads (nearest candidate: 0.21 mm margin to a `-15VA` rail at `U2`) — a proper fix needs interactive re-routing

Status:

- rev A: accepted for the 5-board prototype run; order with bottom-side solder-mask plugged vias if offered, and bench-inspect these four joints on arrival (all reworkable by hand, all `AGND`)
- rev B: relocate the four vias off-pad during the next layout pass, when re-routing is on the table anyway
- HQDFM false alarms noted for the record: "Missing THT holes x9 / pad count mismatch x9" is the tool matching `J1-J4` to the 9-terminal Neutrik panel jack instead of the board-mounted JST `B3B-XH-A`; all 37 through-hole pads verified present in the drill file on `2026-07-04`. "Open/Shorts (IPC): Fail" reflects the absent IPC-D-356 netlist, not a detected fault.

All-board HQDFM triage (`2026-07-04`, reports on the other five boards):

- drill files verified complete on **all six boards**: every through-hole pad and via in each `.kicad_pcb` has a matching hit in its `.drl`; every "missing THT hole / pad count mismatch" flag traces to the same JST-vs-library matching artifact (flagged refs: `P301`, `P201`, `P501` area, `J101`, `P402`)
- **filter-clipper had 9 duplicated AGND vias** (8 stacked at identical coordinates, one pair 8 um apart). Fixed in the fab output on `2026-07-04`: duplicate drill hits removed from `filter-clipper.drl` (loose and in-zip; 118 -> 109 hits), verified zero duplicates and full pad/via coverage after the edit; original zip preserved in the session backup. The duplicate via objects still exist in `filter-clipper.kicad_pcb` — deduplicate there during the rev-B pass
- further via-in-pad instances to relocate in rev B (accepted for rev A): ext-tank-routing `C297` area (x2), power-backplane `C505` (via only 11.75% on pad — barely touching), tank-driver-recovery `R153` area (x2)
- power-backplane "NPTH attribute PTH" flag: no drill hit exists at the flagged location (nearest holes are the `P502`/`P503`/`P504` 1.7 mm PTH pads >=1.4 mm away); with KiCad merged drill files fabs plate all holes by default, so no unplated-signal-hole risk exists. Noise
- minor footprint-quality notes for rev B, no rev-A action: "heel distance F_Flat_Lead" x1 on four boards (same footprint signature), "oversized chip pads" x2 on filter-clipper (tombstone-risk warning), "side distance C_C_Bend" x1 on power-backplane, no fiducials on any board (fab adds panel fiducials for assembly; consider 3 local fiducials per board in rev B)

## 1. Combo Jack Output Convention

The project requirement is combo `XLR / TRS` jacks for both input and output.

Open issue:

- standard combo-jack families are most conventional on inputs
- using them on balanced outputs may force a less-common female-XLR output convention

Status:

- requirement preserved
- needs final mechanical sanity-check before enclosure metalwork is frozen

## 2. Primary Tank Driver Final Topology

Current rev-A starting point:

- split-rail `OPA1656IDR` predriver plus `BD139-16` / `BD140-16` emitter-follower output stage

Open issue:

- this is more aligned with the audio-path capacitor preference
- but it is more complex and needs bias/stability tuning
- the old LM386 path remains as a fallback if bench results force a simpler first build

Status:

- preferred direction is now the direct-coupled split-rail stage
- final bias/stability details still need schematic and bench work

## 3. Exact Stereo Pot Families

Open issue:

- final panel hardware families for the multi-control stereo sections are not fully frozen

Status:

- architecture is stable
- exact panel hardware can be finalized after enclosure spacing is more concrete

## 4. Endcap Density And Preferred Diameter

Resolved 2026-07-04:

- diameter decided: `10 in` nominal, chosen for off-the-shelf pipe/cap availability (`9 in` fits the layout but is rarely stocked)
- hole-table positions finalized: toggles moved inboard/down, wet/dry and HPF cutoff raised `1/4 in`, DC jack at `(95, -18.35)` after two clash corrections

Status:

- the endcap drilling pattern passes all spacing rules on both `10 in` and `9 in` faces
- remaining before metalwork freeze: measured face diameter of the purchased cap, exact Neutrik cutout geometry, and final bushing diameters

## 5. Final Filter Values

Open issue:

- HPF/LPF values and Q ranges still need listening-based tuning against the real tanks

Status:

- topology is defined
- value freezing waits for prototype evaluation

## 6. Real KiCad Capture

Open issue:

- the package now has a real top-level hierarchical KiCad shell plus full first-pass symbol coverage, but five of the six rev-A child sheets are still largely un-wired electrically

Status:

- hierarchy and PDF export workflow are now real
- manifest net-label coverage is now `82 / 82`
- all six rev-A child sheets now have first-pass real symbols (`88 / 88` required refs across the full manifest)
- overall schematic symbol coverage is now `88 / 88` refs on the latest capture audit
- the power/backplane page now has a first-pass real electrical capture for DC entry, split-rail generation, and harness fanout
- the I/O page now has an explicit schematic-ready electrical definition in [rev-a-io-schematic-ready-definition.md](rev-a-io-schematic-ready-definition.md) that freezes unit allocation, passive naming, and connector ownership before the eventual KiCad multi-unit pass
- the current top-level ERC intentionally remains an intermediate failure (`650` known violations on the latest `2026-06-29` rerun), still dominated by top-level unconnected sheet pins, placeholder wire endpoints, off-grid legacy symbol endpoints, and still-unwired child-sheet labels on the non-power sheets
- the latest contained cleanup pass was on the I/O board, where removal of accidental center-short stubs reduced that child sheet from `404` to `376` local violations and dropped its multiple-net-name collisions from `8` to `2`
- actual pin-level wiring, footprint confirmation, ERC cleanup, and PCB layout are still the next major phase

## 7. External Wall Adapter: Regulated vs Unregulated Confirmation — RESOLVED `2026-07-04`

Resolution:

- the wall adapter is now the **Triad Magnetics `WSU240-0750`**: regulated SMPS, `+24 VDC / 750 mA / 18 W`, UL 62368-1 (file `E345519`), DOE Level VI, purchased from DigiKey
- this retires the unregulated-adapter damage risk: worst case with the Triad's combined `+/-5%` regulation is `+25.2 V`, far inside the `URA2415YMD-10WR3` input range (`9-36 V`, `24 V` nominal)
- barrel plug changes from `5.5 x 2.5 mm` to `5.5 x 2.1 mm`; the service-endcap jack changes from `PJ-005B` to `PJ-005A` (same mounting hole and hardware)
- full topology update in [rev-a-external-dc-power.md](rev-a-external-dc-power.md)

Remaining follow-ups (also tracked in the rev-a-external-dc-power.md open items):

- P-0 receiving check at first power-up: open-circuit `+22.8 V` to `+25.2 V`, reject above `+27 V`
- KiCad net names `+30V_RAW` / `+30V_F` are historical labels that now carry `+24 V` nominal; rename at the next schematic capture pass before layout freeze
- the exact `PJ-005A` footprint pin map and the `PS500` enable-pin treatment still need one final datasheet-to-footprint sanity pass before layout freeze

## 8. Control Backplane Versus Direct Panel Wiring

Open issue:

- the filter and mode sections have enough controls that several small direct-control JST links are not the cleanest final wiring strategy
- the currently checked-in grouped placeholders for `P307`, `P403`, and `P405` are still electrically compressed relative to a fully honest passive off-board control harness
- the current frozen control-backplane contract does not support putting `U601` in charge of ext-routing relay coils without changing the inter-board harness definition
- rev A likely wants either board-mounted controls or a power/control/backplane landing board for the denser control groups

Status:

- the audio harness map is now stable
- the ext-routing control landing is now electrically frozen with the raw stereo amount pot plus encoded two-bit mode control
- the crossfade feedback and filter-Q control groups now have explicit schematic-ready definitions, and the new control-backplane companion makes the compressed-placeholder status expl