# Rev C: edge pass, 3.5 mm footswitch jack, filter-pot risers (2026-09-21)

Supersedes the front-stack geometry in `rev-c-front-stack-and-io-modes.md` sections 5 and 10 (that file is
updated to match). Build notes for the 2026-09-21 pass. Everything below is built, verified and exported here.

**Headline: nothing in the unit is hand wired or hand soldered by Jason any more.**

## 1. Why

Jason's review of the control-deck render found four things, and then approved a fifth change:

1. Parts hanging off the board edge (the S1 / S4 end toggles and the HPF / LPF windows).
2. The footswitch jack was a 1/4 in part; it should be a small 1/8 in (3.5 mm) jack.
3. The 3.5 mm jack must be PCB mounted and supplied by PCBWay, not hand wired.
4. A list of everything still hand wired by him or supplied by him.
5. Then: "yes please do the two small riser PCBs" for the 4-gang filter pots.

## 2. Edge pass

Worst radius reached by any footprint courtyard or pad, measured from the disc centre (edge = 76.2 mm):

| Feature | Before | After |
| --- | --- | --- |
| S1 / S4 end toggles | 77.57 (1.37 mm outside) | 74.21 |
| HPF / LPF windows | 80.42 (4.22 mm outside) | 72.00 |
| Worst feature, control deck | 80.42 | **74.21** |
| Worst feature, jack deck | 74.02 | **74.02** |

Changes in `kicad/revc/gen/boards/panel_geom.py`:

- Toggle row pitch 18.5 to 17.0 mm: the seven bushings now sit at 0, +/-17, +/-34, +/-51 at Y 43.
- Outer pot arc r 66 to r 63: Vol (-59.20, -21.55), HPF (-36.14, -51.60), Gain (0, -63),
  LPF (36.14, -51.60), Output (59.20, -21.55).
- Feedback VR7 from (0, -40) to (0, -37); Ext Mix and Wet/Dry from Y -25.5 to Y -23.5.
- The 16 x 24 mm rectangular filter-pot windows became radial capsules: two 9.0 mm circles per pot, one on the
  shaft axis and one 8.0 mm inboard, 18 mm of clear width. The capsule follows the radius, so it stays inside
  the edge where the rectangle did not.
- Bottom pot headers P3 / P4 from X +/-19 to +/-18.
- Five silkscreen labels that ran off the edge were shortened or moved inboard.

New verification tool: `kicad/revc/gen/tools/edge_check.py`. It reads the finished `.kicad_pcb`, measures every
footprint courtyard and pad against the disc centre, and fails anything within 1.0 mm of the edge:

    python tools\edge_check.py control-deck jack-board

Result: at least 1.99 mm of board material beyond the outermost part everywhere on both decks.

## 3. Footswitch jack: 1/4 in hand wired to 3.5 mm PCB mounted

**Part: XKB Connection PJ-301C, LCSC C692433.** Vertical 3.5 mm TRS, M6 bushing, through hole, body
8.5 x 10.2 mm, 14.1 mm tall. Stock 9,114. $0.2623 at 1, $0.2082 at 50, $0.1849 at 150. It replaces a Switchcraft
112BX at about $3.50 that was hand wired.

Selection notes: it is the only "Straight" (axis perpendicular to the board) 3.5 mm jack in the LCSC catalogue;
everything else stocked is right-angle or SMD. The PJ-392-AU (C49274302) is the only other panel-mount candidate
and is more than twice the price.

**Footprint: `GAS_Parts:Jack_3.5mm_PJ-301C_Vertical`.** Land pattern taken from the official LCSC / EasyEDA
drawing `AUDIO-TH_PJ-301C`, origin at the bushing axis. Slots widened from the library's 0.70 mm to 0.90 mm for
PCBWay's plated-slot minimum. Pads S (4.40, -0.74), R (0, -3.30), T (0, +4.50); names match the
`Connector_Audio:AudioJack3` symbol pins, so no pinmap is needed. Pin functions confirmed from the LCSC schematic
symbol: pin 1 wired to the barrel body = sleeve, pin 2 the middle spring contact = ring, pin 3 the deep contact
= tip.

**Wiring.** Tip to `FS_TIP`, ring and sleeve both to `AGND`, so a TS or a TRS footswitch cable both work. The
existing 10k pull-up (R51 on the jack board) still means open or unplugged = effect ON. Trails / true bypass via
JP1 unchanged. A 3.5 mm cable or a 1/4 in to 3.5 mm adapter is needed at the stompbox end.

**Position.** Control deck J6 at panel (0, -14), moved down from (0, -20) so its 16 mm inside counterbore clears
the Feedback knob (the endcap fit checker flagged a 2.9 mm gap at -20).

**Endcap.** Hole 9.6 to **6.4 mm**, with a 16 mm counterbore from the inside leaving a **5.0 mm skin**. With the
control deck 15.0 mm behind the outer face and the jack 14.1 mm tall, the bushing nose is a slip fit in the
6.4 mm hole and the jack mouth sits essentially flush with the face, so no nut is needed and the plug reaches the
tip contact normally.

**Open item:** the PJ-301C thread length is not published by XKB. If the first sample measures 5.5 mm or more,
thin the skin at J6 to 3 mm and fit the supplied M6 nut.

**Connection.** New control-deck header **P8** (JST XH-2, FS_TIP + AGND) to jack-board P4. `FS_TIP` is the one net
that crosses the jack bar, through the 5 mm bridge between the two centre jack windows; Freerouting takes it in
one pass. The 21 mm footswitch window is deleted from **both** decks.

## 4. Filter-pot risers (new board)

**The problem.** The PTD904's PC pins leave the body at 90 degrees to the shaft ("side adjust"), and the Bourns
PTD90 recommended PCB layout draws the mounting surface perpendicular to the board. The four gang columns sit
**5.0, 7.5, 12.5 and 15.0 mm behind the mounting shoulder**. With the shoulder on the counterbore floor at 3.0 mm,
the gangs land at 8.0, 10.5, 15.5 and 18.0 mm behind the cap's outer face, and the control deck is at 15.0 to
16.6 mm. The pin field **straddles the deck**: two gangs in front, two behind. No board in the deck's plane can
reach them, and neither can a card standing on the deck. That is why this is a pot carrier, not a daughtercard.

**The board.** `kicad/revc/gen/boards/filter_pot_riser.py`, 46 x 15 mm, two layer, two parts: one PTD904 at the
panel end and one JST XH-8 at the other. It stands perpendicular to the deck and passes through the deck's capsule
window; the pot's own M7 bushing nut holds the assembly to the cap, exactly as the bare pot did. It hangs clear of
the jack deck (which stops at Y -40, above the filter pots at Y -51.6) and of the sled plate (which starts 45 mm
in).

**One design, built twice.** HPF (circuit P5) and LPF (circuit P6) take the same eight lines in the same order,
(HI, wiper) per gang, so the riser carries generic G1..G4 nets and the cable decides which filter it is.

**Wiring per gang:** pad g1 (CCW end) = HI, pads g2 (wiper) and g3 (CW end) tied together = W. Each gang is a
rheostat whose resistance rises as the knob turns clockwise, so **clockwise lowers both corner frequencies**:
CW = less bass cut on the HPF, CW = darker on the LPF. Jason picked this direction on 2026-09-21 after the first
cut (g3 = HI, the opposite sweep) felt backwards. Because one board design serves both filters, the direction
flips for both together. Those ties used to be made by hand at the pot lugs; now they are copper.

**New library parts:** `GAS_Parts:PTD904` symbol (12 pins, gang g pin p = pad "gp") and
`GAS_Parts:Pot_Bourns_PTD904_SideAdjust` footprint (12 pads, 1.1 mm drill, columns 5.0 / 7.5 / 12.5 / 15.0, rows
on 5.0 mm, origin = shaft axis at the mounting shoulder).

**Assembly order at the filter pots:** fit the control deck to the cap first, then feed each riser through its
window from behind until the M7 bushing enters the 7.5 mm hole, and nut it from outside. The XH-8 end stays
behind the deck and never passes through the window.

**Open item:** the PTD904's pin length below the body is not dimensioned in the datasheet, so the riser sits where
the pins land rather than at a computed height. That is self-jigging and does not affect the panel, but check the
first assembly sits square before nutting it to the cap.

## 5. Other hand wiring removed

`W1`, the solder pads carrying the DC cable from the control-deck jack J5 to power-board P1, is replaced by a
**JST VH-2 header P9** at panel (28, 56).

## 6. Hand-wired and user-supplied list

**Hand wired by Jason: none.** Before this pass it was the footswitch jack lead (2 wires), the W1 DC lead (2
solder pads) and the two PTD904 filter pots (8 crimps each, 16 wires). All three are gone.

**Supplied by Jason rather than PCBWay:**

1. 6 in PVC DWV pipe, 1453 mm, and its two caps
2. DC adapter, Jameco DDU300050E9340
3. Four Accutronics tanks and their RCA leads
4. Knobs, 6 mm bore, 8 off
5. Sled hardware: plate, HDPE, threaded rod, brackets, grommets, felt, standoffs, M3 fasteners
6. The inter-board JST XH / VH harness cables (confirmed against `kicad/revc/fab/PCBWAY-ORDER-RevC.md`: they are
   not on the PCBWay order, which covers bare boards and placed components only)
7. Drilling the cap, using the bare control deck as the 1:1 template

## 7. Verification state

| Check | Control deck | Jack deck | Filter-pot riser |
| --- | --- | --- | --- |
| ERC | 0 violations | 0 violations | 0 violations |
| Unrouted nets | 0 | 0 | 0 |
| DRC unconnected | 0 | 0 | 0 |
| Edge check | 74.21 mm worst, OK | 74.02 mm worst, OK | n/a (rectangular) |

Remaining DRC entries are the pre-existing benign ones: five `net_conflict` warnings for the deliberately unused
toggle throws on the control deck, one `footprint_symbol_mismatch` for JP1's BOM attribute on the jack board, and
silkscreen overlap warnings.

Endcap fit checker (`endcap-rev-c/revc_endcap.py`): **FIT OK**, tightest face gap 5.5 mm between adjacent
toggles. Hole table, DXF and 1:1 PDF template regenerated; the counterbore column now carries a per-part
remaining-skin figure (toggles 4.0, DC 3.7, dual pots 1.5, filter pots 3.0, footswitch jack 5.0 mm).

`mech-rev-c/revc_mech.py` re-run: the front-stack detail now draws the 3.5 mm jack and the filter-pot riser with
its XH-8. Pipe length unchanged at **1453 mm**.

Fab packages re-exported for control-deck, jack-board and the new filter-pot-riser (gerbers, drill, centroid, BOM,
schematic PDF, assembly PDF, render).

## 8. PCBWay order changes

`kicad/revc/fab/PCBWAY-ORDER-RevC.md` updated: new `filter-pot-riser` line (46 x 15 mm, 2 parts, build 2 per unit,
10 off), control-deck now 24 parts with the PJ-301C and 9 headers, jack-board down to 2 cut-outs, **DNP list is
now empty** (W1 is gone), and two new "parts needing attention" rows for the PJ-301C (must be the vertical type,
plated slots) and the PTD904 (side adjust, nut and washer needed).
