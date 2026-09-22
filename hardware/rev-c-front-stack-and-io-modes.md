# GAS Rev C: Front Stack (control deck + jack deck), I/O Modes, Footswitch, V2181 (2026-09-17, revised 2026-09-21b)

Illicit Apothecary, The Great American Spring. This adds to `rev-c-hardware-definition.md` and replaces its jack, panel wiring and THAT2180 sections. Decisions from Jason: **option A** (two stacked 6 in boards behind the cap) and **trails** bypass (2026-09-17);
**option 3 for the pull switches** (2026-09-21): no dual-gang linear push-pull pot is stocked anywhere, so Vol, Gain
and Output are now plain dual pots with their own mini toggle. The switch row went from 4 to 7 toggles, and all six
dual pots are PCBWay-mounted on the control deck.

**2026-09-21b, edge pass and 3.5 mm footswitch jack.** Jason's review of the control-deck render found parts
overhanging the board edge and asked for a small 1/8 in footswitch jack that PCBWay fits, not a hand-wired 1/4 in
one. Both are done: nothing on either deck now comes within 2 mm of the 76.2 mm edge, and the footswitch jack is a
PCB-mounted 3.5 mm TRS (XKB PJ-301C). The DC lead's solder pads became a JST VH-2 header at the same time, so the
only hand wiring left on the whole unit is the two 4-gang filter pots.

**2026-09-21c, filter-pot risers.** Jason then asked for the riser boards, so the last 16 crimped wires are gone
too. Each PTD904 now rides on a **filter-pot riser**, a 46 x 15 mm carrier board that PCBWay assembles complete;
the assembly passes through the control deck's window and nut-mounts to the cap exactly as a bare pot would, and
one JST XH-8 goes to the circuit board. **Nothing in the unit is hand wired or hand soldered by Jason any more.**

## 1. What changed

| Area | Before (2026-09-15) | Now |
| --- | --- | --- |
| Jacks | 4 x NCJ6FI-H on the front edge of the io-board | 4 x **NCJ6FI-V** on the new **jack-board** (jack deck), a 6 in round board behind the cap |
| Panel parts | all hand-wired to io / circuit / tank headers | everything is PCBWay assembled: 7 toggles, DC jack, footswitch jack and **all six dual pots** on the **control-deck**, and the two 4-gang filter pots on their own **filter-pot risers** |
| Pull switches | push-pull on the Vol / Gain / Output knobs | separate **Tube / Dirt / Tape** mini toggles in the switch row (no stocked dual-gang linear push-pull pot exists) |
| Inputs | unity balanced receiver, 10k per leg | 1 M ohm per leg (JFET followers), XLR = line, 1/4 in TS = instrument, 1/4 in TRS = line (auto) |
| Outputs | OPA1656 hot/cold, TS plug shorts the cold driver | **DRV135** cross-coupled drivers (TS safe), -12 dB instrument level when the input is an instrument |
| Bypass | none | optional TS or TRS latching footswitch: **trails** bypass; unplugged = always ON; true bypass at power off / first 3 s |
| Limiter VCA | THAT2180AL08-U (end of life, $14.83) | **Coolaudio V2181** + symmetry trim (fitted RV1301 / RV1321, 150k) |
| HPF / LPF pots | PTD904 100k lin (out of stock everywhere) | **PTD904-2015K-B503 50k lin** (in stock); circuit board 1k -> 499R and each filter cap doubled, so the sweep and law are unchanged |
| DC jack | Switchcraft L712A hand-wired | Same Sky PJ-064B on the control deck |
| Footswitch jack | 1/4 in Switchcraft 112BX, nut mounted, hand wired (about $3.50) | **XKB PJ-301C 3.5 mm TRS**, vertical PCB mount on the control deck, LCSC C692433, $0.26 at 1 / $0.208 at 50. Panel hole 9.6 -> **6.4 mm** |
| DC lead to the power board | W1, two solder pads on the control deck | **JST VH-2 header P9**, so nothing on the deck is hand soldered |
| HPF / LPF pots | nut mounted in the cap, 8 crimped wires each to circuit P5 / P6 | **filter-pot riser**, 46 x 15 mm, one PTD904 + one JST XH-8 per board, PCBWay assembled. Two identical boards |
| Panel geometry | toggle row 18.5 mm pitch, outer pot arc r 66, rectangular filter-pot windows | toggle row **17.0 mm** pitch, outer pot arc **r 63**, radial capsule windows. Worst courtyard radius 80.4 -> **74.2 mm** against a 76.2 mm edge |

## 2. Your impedance question (checked)

- **Outputs:** yes, line and instrument outputs are both low impedance (tens of ohms), so one driver serves both. The level is what differs: instrument about -20 dBu to 0 dBu, +4 dBu line is about 12 to 20 dB hotter.
- **Inputs: not the same.** A passive guitar pickup needs about **1 M ohm** or it loses its top end and level. Line inputs are normally 10k to 20k, which would dull a guitar. So every GAS input is now 1 M ohm on each leg, all the time. Line sources are happy driving 1 M ohm, so nothing has to switch for impedance. The sense only switches level: +12 dB of input gain for an instrument, and the matching -12 dB at the output, so guitar in to amp out is unity (Vol knob still has +/-18 dB on top).

## 3. Input and mode sensing (jack-board)

Per input combo jack: XLR 2 and tip = HOT, XLR 3 = COLD, 1/4 in ring joins COLD through 10 uF. HOT and COLD each go 1k -> clamp diodes -> 1 uF C0G (no microphonics) -> 1 M ohm -> OPA1642 follower, then a short harness to the io-board receiver.

The ring gets 0.5 V through 10k (bootstrapped from the cold follower so it does not load the cold leg at audio), filtered 1 s, into an LMV393 with hysteresis (instrument below 0.089 V, line above 0.116 V).

| What is plugged in | Ring DC | Mode |
| --- | --- | --- |
| nothing | 0.5 V | LINE |
| XLR (any source) | 0.5 V (the 1/4 in ring is untouched) | LINE |
| 1/4 in TS (guitar, keys, pedal) | 0 V: the TS sleeve shorts ring to sleeve | **INST** |
| 1/4 in TRS from a transformer or capacitor coupled balanced output | 0.16 to 0.5 V | LINE |
| 1/4 in TRS from a DC-coupled electronically balanced output | about 0 V | reads INST (known limit: use the XLR input or a TRS to XLR cable for that source) |

Mono > Stereo: the R input follows the L input's mode (io-board K1 second pole), so a mono guitar into L gives instrument level on both outputs.

## 4. Outputs, footswitch and bypass

- io-board: after the receiver, INST relay K5 (L) / K6 (R) switches x4 (+12.06 dB) in the input and x0.124 (-12.07 dB) before the DRV135. DRV135 gain 2, so LINE: balanced in to balanced out is unity, as before.
- Footswitch jack (**3.5 mm TRS, XKB PJ-301C, soldered to the control deck**, tip and sleeve out on control-deck P8 to jack-board P4): tip to sleeve closed = bypass. Ring is tied to sleeve on the board, so a TS latching switch and a TRS cable wired tip-sleeve both work. Unplugged = effect ON (10k pull-up R51 on the jack board). Momentary switches are not supported. You will need a 3.5 mm cable or a 1/4 in to 3.5 mm adapter at the stompbox end.
- **Trails bypass (default):** io-board K7 mutes WET_SEND into the tanks. The tails and the feedback loop ring out and the dry level does not jump.
- **True bypass:** jack-board K1 / K2 wire the input jack straight to the output jack whenever they are not energised: power off, and the first ~3.4 s after power on (this also hides the JFET servo settle thump). Close solder jumper **JP1** on the jack-board if you want the footswitch to do true bypass instead of trails (cuts tails).

## 5. Front stack mechanics

z is measured inward from the **outer** face of the cap. Cap face T = 7 to 9 mm (measure yours).

| Item | z (mm) |
| --- | --- |
| Control deck PCB, component side (faces the cap) | 15.0 |
| Combo jack flange contact (inside of the cap, pocketed to 7 mm if thicker) | 7 |
| Jack deck PCB, component side (faces the cap) | 31.0 |
| Jack deck headers, back side, plugs reach | about 50 |

Hole layout (X right, Y up, from the cap centre, seen from outside). Changes from `rev-c-endcap-fit-check.md`:
jack bar up 5 mm to Y = 15, **switch row now 7 toggles at Y = 43 on a 17.0 mm pitch** (Source, Tube, Dirt, Tape,
Ext tanks, FB Dyn, FB Phase, left to right), the five outer pots moved onto an **r 63** arc, Feedback to (0, -37),
the footswitch jack to (0, -14), and Vol / Gain / Output are ordinary 16 mm knobs.

The 2026-09-21b edge pass shrank the toggle pitch from 18.5 to 17.0 and the outer arc from r 66 to r 63 because
the S1 / S4 toggle courtyards reached 77.57 mm and the filter-pot windows 80.42 mm, against a 76.2 mm board edge.
`gen/tools/edge_check.py` (new) measures every footprint courtyard and pad on the finished board against the disc
centre and fails anything within 1.0 mm of the edge. It now reports **74.21 mm worst on the control deck and
74.02 mm on the jack deck**, so there is at least 1.99 mm of board beyond the outermost part everywhere.

`endcap-rev-c/revc_endcap.py` re-run: **FIT OK**, tightest face gap 5.5 mm between adjacent toggles. The hole
table CSV, DXF and 1:1 template PDF are regenerated, and the counterbore column now carries a per-part
remaining-skin figure instead of one generic note.

| Ref | Part | X, Y | Drill | Skin left after the inside counterbore | Counterbore |
| --- | --- | --- | --- | --- | --- |
| J1..J4 | NCJ6FI-V combo | -49.5 / -16.5 / 16.5 / 49.5, 15 | 24 + 2 x 3.2 (+/-10, +/-11.5) | 7 max | one pocket 134 x 32 mm (Y -1 to 31) to 7 mm, only if the face is thicker than 7 |
| S1, S5, S6, S7, S2, S3, S4 | mini toggle 1/4-40 | -51 / -34 / -17 / 0 / 17 / 34 / 51, 43 | 6.5 | 4.0 | 14 mm dia, depth T - 4.0 |
| J5 | DC PJ-064B 5/16-32 | 0, 66 | 8.2 | 3.7 (nut only, no washer) | 14 mm, depth T - 3.7 |
| VR1, VR3, VR5 | RK09L M9 (Vol, Gain, Output) | -59.2,-21.55 / 0,-63 / 59.2,-21.55 | 9.5 | 1.5 | 14 mm, depth T - 1.5 |
| VR6, VR7, VR8 | RK09L M9 (Ext Mix, Feedback, Wet/Dry) | -25.5,-23.5 / 0,-37 / 25.5,-23.5 | 9.5 | 1.5 | 14 mm, depth T - 1.5 |
| VR2, VR4 | PTD904 M7 on a filter-pot riser (HPF, LPF) | -36.14,-51.6 / 36.14,-51.6 | 7.5 | 3.0 | 18 mm, depth T - 3.0 |
| J6 | **PJ-301C 3.5 mm TRS, M6, PCB mounted** | 0, -14 | **6.4** | **5.0** | 16 mm, depth T - 5.0 |

The footswitch jack is the one hole that is not a nut mount. The control deck holds the jack at 15.0 mm behind the
outer face and the jack is 14.1 mm tall, so with a 5.0 mm skin its shoulder lands on the counterbore floor, the M6
bushing is a slip fit in the 6.4 mm hole, and the jack mouth finishes essentially flush with the face. The plug
reaches the tip contact normally and the jack is held by its three soldered pins plus the bushing in the hole.
**Check on the first sample:** the PJ-301C thread length is not published. If it turns out to be 5.5 mm or more,
thin the skin at J6 to 3 mm and fit the supplied M6 nut for belt and braces.

Heights of the RK09L, the toggles and the PJ-064B come from datasheets, so the skin numbers above are the plan.
You do not need calipers or any parts on hand to use them. Order of work when the assembled deck arrives:

1. Drill the through holes only (sizes in the table, printed next to every hole on the bare board).
2. Lay the assembled deck against the inside of the cap. Every bushing will be short of the outside by a few mm.
3. Counterbore from the inside in small steps with a Forstner bit, testing the deck each time, until each nut
   catches about three threads. That is the same answer as the table without measuring anything.
4. The 4 combo jacks are the datum: they hold the jack deck at 24 mm and set the whole stack.

Using the bare control deck as a drill template: lay it component side up on the outside of the cap. Every hole
centre is marked with a silkscreen cross and its drill size, and the toggle centre pin, the DC jack centre and the
cut-outs line up with the holes themselves.

Cartridge: the io-board no longer carries jacks. It moves onto the sled plate top at Z 45 to 225 (Z from the inside of the cap), circuit board to Z 230 to 405. The plate ends at Z 430 as before, so the pipe length (1453 mm) does not change. An aluminium angle on the front of the plate bolts to jack-board holes H1 / H2 (M3 at X +/-68, Y +5, nylon washers).
`mech-rev-c/revc_mech.py` was re-run on 2026-09-21: the side view now has a **front stack** detail panel, and the
clearance report covers both decks (7.0 mm to the cap socket wall).

Jack deck outline: the 6 in circle between Y = -40 and Y = +49 (the control deck's switch headers sit above that
line, its filter-pot headers below), with two 34 x 10 mm windows at (+/-26, -16) for the control deck's pot-harness
plugs. The 21 mm footswitch hole is gone, since that jack is now on the control deck. Tallest part on it is a
5.2 mm relay, so it clears the control deck's pins by about 5 mm.

Control deck cut-outs: the four combo jack bodies (28 x 32 mm each) and the two filter-pot risers. Each filter-pot
window is now a **radial capsule** rather than a 16 x 24 mm rectangle: two 9.0 mm circles, one on the shaft axis
and one 8.0 mm inboard, giving 18 mm of clear width. That passes the whole riser assembly, the PTD904 body plus
the 15 mm wide carrier board below it, and the capsule follows the radius so it stays inside the board edge where
the rectangle did not. Ext Mix and Wet/Dry moved from Y -25.5 to Y -23.5 and the two bottom pot headers from
X +/-19 to +/-18 to clear the bigger windows; every other control stayed put.

Assembly order at the filter pots: fit the control deck to the cap first, then feed each riser through its window
from behind until the M7 bushing enters the 7.5 mm hole, and nut it from outside. The XH-8 end of the riser stays
behind the deck and never passes through the window.

## 6. Harnesses (all 1:1, JST XH / VH)

| From | To | Pins |
| --- | --- | --- |
| jack-board P2 | io-board P6 | XH-12: IN L hot/cold, AGND, IN R hot/cold, AGND, OUT L hot/cold, AGND, OUT R hot/cold, AGND |
| jack-board P3 | io-board P7 | XH-4: CTL_INST_L, CTL_INST_R, CTL_BYP, AGND |
| power-board P5 (spare) | jack-board P1 | VH-4 |
| control-deck P1 | io-board P4 | XH-12 (Vol and Output pots) |
| control-deck P2 | circuit-board P7 | XH-12 (Ext Mix and Feedback pots) |
| control-deck P3 | io-board P5 | XH-6 (Wet/Dry pot) |
| control-deck P4 | circuit-board P9 (new) | XH-6 (Gain pot) |
| control-deck P5 | io-board P8 (new) | XH-5 (Source, Tube, Tape switch lines) |
| control-deck P6 | circuit-board P8 | XH-7 (Dirt, FB Dyn, MEGAVERB, FB Phase) |
| control-deck P7 | tank-board P5 | XH-4 (Ext tanks) |
| control-deck P9 (new) | power-board P1 | VH-2, 20 AWG, both ends housed |
| control-deck P8 (new) | jack-board P4 | XH-2 (footswitch tip, sleeve) |
| HPF filter-pot riser P1 | circuit-board P5 (now 8 pins) | XH-8 |
| LPF filter-pot riser P1 | circuit-board P6 (now 8 pins) | XH-8 |

Pot headers sit in the bottom half of the control deck and switch headers in the top half, so no harness net has to
squeeze past the jack bar. Everything is a straight 1:1 cable. The single exception on copper is FS_TIP, which runs
from the jack at (0, -14) up through the 5 mm bridge between the two centre jack windows to P8; Freerouting takes
it in one pass.

## 7. V2181 (limiter VCA)

- Price: THAT 2180AL08-U $14.83 each at Mouser (end of life). V2181: $2.95 (Small Bear / synthCube, often backordered), $5.75 (PedalPCB), EUR 7.90 (musikding). Per unit with two VCAs plus two 3314J trimmers ($1.57): about **$10 to $20 cheaper**.
- Same SIP-8 pinout as THAT 2181 (1 IN, 2 EC+, 3 EC-, 4 SYM, 5 V-, 6 GND, 7 V+, 8 OUT). 5.1k ISET kept (2.4 mA).
- Sourcing: not stocked at Mouser, DigiKey or LCSC. Tell PCBWay it is a Coolaudio part (hobby distributors), or consign it. THAT 2181BL08-U drops in with the same trim if needed.
- Trim once: 1 kHz, 0 dBu into the limiter, Limit selected but under threshold (0 dB VCA gain). Adjust RV1301 (L) and RV1321 (R) for minimum distortion on a THD meter or an FFT in your DAW (lowest 2nd harmonic).

## 8. Power budget update

Relays on +5VAUX: io 7 (K1..K7), circuit 5, tank 3, jack-board 2 (K1 / K2 always on when powered) = 17 x 21 mA = 357 mA worst case, inside the R-78HB5.0-0.5's 500 mA.

## 9. Parts added (approximate, qty 1, 2026-09-17)

| Part | Where | Qty | Each | Source |
| --- | --- | --- | --- | --- |
| Neutrik NCJ6FI-V | jack-board | 4 | $3.82 | Mouser |
| OPA1642AIDR | jack-board | 2 | $1.26 to $2.14 | LCSC / Mouser |
| LMV393IDR, 74LVC2G04GW, AO3401A x4, 2N7002 | jack-board | 1 set | about $1.50 | LCSC |
| Omron G6K-2F-Y DC5 | jack-board 2, io-board +3 | 5 | $1.63 to $4.92 | LCSC / Mouser |
| DRV135UA | io-board | 2 | $7.29 | Mouser |
| OPA1644AIDR (gain / pad stages) | io-board | 1 | about $3 | Mouser |
| Dailywell 1MS3T1B1M2QES-5 (S1, S3, S4, S5, S6, S7) | control deck | 6 | $1.41 | LCSC C908270 |
| Dailywell 1MD3T1B1M2QES (S2, Ext tanks) | control deck | 1 | $5.28 | Mouser |
| Alps RK09L1240015 dual 10k lin (centre detent) | control deck | 6 | $3.74 | Mouser |
| Same Sky PJ-064B | control deck | 1 | $3.57 | Mouser (50 in stock) |
| Bourns PTD904-2015K-B503 | filter-pot riser | 2 | $3.17 | Mouser / DigiKey |
| Coolaudio V2181 | circuit-board | 2 | $2.95 to $7.90 | Small Bear / musikding |
| JST XH / VH headers, housings, crimps | all | set | about $10 | Mouser / LCSC |
| XKB PJ-301C 3.5 mm TRS jack, vertical | control deck | 1 | $0.26 (1), $0.208 (50), $0.185 (150) | LCSC C692433 |
| Filter-pot riser PCB, 46 x 15 mm, 2 layer | new board, 2 up | 2 | pennies in the panel | PCBWay |
| Knobs, 6 mm bore | panel | 8 | about $1.30 | Tayda |

## 10. The filter-pot risers (and why nothing is hand wired any more)

**The problem.** The PTD904's PC pins leave the body at 90 degrees to the shaft ("side adjust"), and the Bourns
PTD90 recommended PCB layout draws the mounting surface perpendicular to the board. The four gang columns sit
**5.0, 7.5, 12.5 and 15.0 mm behind the mounting shoulder**. With the shoulder on the endcap counterbore floor at
3.0 mm, that puts the gangs at 8.0, 10.5, 15.5 and 18.0 mm behind the cap's outer face, and the control deck is at
15.0 to 16.6 mm. So the pin field **straddles the deck**: two gangs in front of it, two behind. No board in the
deck's plane can reach them, and no card standing on the deck can either. No 4-gang linear pot with pins parallel
to the shaft is stocked at Mouser, DigiKey, LCSC, Tayda, Small Bear or Amplified Parts, in any value.

**The riser.** A 46 x 15 mm two-layer carrier, `boards/filter_pot_riser.py`, that stands perpendicular to the deck
and passes through its capsule window. It carries the PTD904 at the panel end and a JST XH-8 at the other end, and
nothing else. PCBWay assembles it complete. Mechanically the assembly behaves exactly like the bare pot it
replaces: the pot's own M7 bushing nut holds it to the cap, and the riser hangs behind, clear of the jack deck
(which stops at Y -40, well above the filter pots at Y -51.6) and clear of the sled plate (which starts 45 mm in).

**One design, built twice.** HPF (circuit P5) and LPF (circuit P6) take the same eight lines in the same order,
(HI, wiper) per gang, so the riser carries generic G1..G4 nets and the cable decides which filter it is.

**Wiring per gang:** pad g1 (CCW end) = HI, pads g2 (wiper) and g3 (CW end) tied together = W. Each gang is a
rheostat whose resistance rises as the knob turns clockwise, so **clockwise lowers both corner frequencies**:
CW = less bass cut on the HPF, CW = darker on the LPF. Jason picked this direction on 2026-09-21 after the first
cut (g3 = HI, the opposite sweep) felt backwards. Because one board design serves both filters, the direction
flips for both together. Those ties used to be made by hand at the pot lugs; now they are copper.

**What it buys:** 16 crimped wires and 8 solder joints per pot disappear, replaced by two standard XH-8 cables
identical to every other harness in the unit.

Everything in the whole unit is now PCBWay-mounted: 7 toggles, 6 dual pots, DC jack, 3.5 mm footswitch jack and
9 headers on the control deck, the two PTD904s on their risers, and all six boards' worth of SMT.

**What Jason supplies rather than PCBWay:** the 6 in PVC DWV pipe (1453 mm) and its two caps; the DC adapter
(Jameco DDU300050E9340); the four Accutronics tanks and their RCA leads; the knobs; the sled hardware (plate,
HDPE, threaded rod, brackets, grommets, felt, standoffs, M3 fasteners); the inter-board JST harness cables; and
drilling the cap using the bare control deck as the template.

## 11. Open items
1. Toggle direction: the C&K 7000 convention (bat toward pin 1 closes 2 to 3) is what the schematic assumes, so up
   = Mono / Tube / Dirt / Tape / Series / Comp, down = MEGAVERB / Limit / Parallel / FB inverted. No meter needed to
   find out: power it up and listen, and if a pair is reversed it is a label change, not a wiring change.
2. Tube, Dirt and Tape use the same ON-OFF-ON toggle as the rest (one throw wired): up = on, centre and down = off.
   The true two-position version of the same switch is $5.75 instead of $1.41 if you want no middle detent.
3. The RK09L has a centre detent. On Vol, Gain and Output that detent marks 0 dB, which is useful; on Ext Mix,
   Feedback and Wet/Dry it is just a click at noon.
4. Jack-board and control-deck harness headers are on the back side (THT, hand soldered by PCBWay).
5. PJ-301C thread length is not published by XKB. The 5.0 mm skin at J6 assumes a slip fit with no nut. Measure the
   thread on the first sample; if it is 5.5 mm or more, take the skin to 3 mm and use the nut.
6. Filter-pot riser: the PTD904's pin length below the body is not dimensioned in the PTD90 datasheet, so the
   riser sits where the pins land rather than at a computed height. That is self-jigging (the pot defines it) and
   does not affect the panel, but check the first assembly sits square before nutting it to the cap.
7. Filter sweep direction is fixed in copper. Rev 1 of the riser had CW = higher corner on both; Jason called that
   backwards on 2026-09-21 and it was respun to **CW = lower corner on both** (CW = less bass cut, CW = darker).
   Confirm it on the bench against the plugin before the production order: changing it again is a riser respin,
   not a rewire, and it moves both filters together.
