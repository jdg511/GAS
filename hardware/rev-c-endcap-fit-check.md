# GAS Rev C Service Endcap on a 6 in PVC Cap: Fit Check (2026-09-15)

Question: with the Rev C control set (8 pots, 4 toggles, 4 combo jacks, 1 DC jack, 17 items) does everything fit on the face of a 6 in PVC end cap? **Yes**, with the layout below, and with one mechanical rule: the cap face is thicker than the bushings of the pots, toggles and DC jack, so those 13 holes get a counterbore from the inside.

Files: `rev-c-endcap-hole-table.csv` (drill schedule), `rev-c-endcap-layout.dxf` (layers OUTLINE / DRILL / CBORE / KNOB / BODY / TEXT), `rev-c-endcap-template-1to1.pdf` (print at 100 %, check the 100 mm bar), `rev-c-endcap-preview.png`, `revc_endcap.py` (the script that checks the gaps and writes all of these; edit the `ITEMS` table and re-run to move things).

## 1. The cap

Charlotte Pipe 6 in DWV socket cap (PVC 00116 1400, Lowe's item 3132571) or any ASTM D2665 6 in cap. What matters:

| Dimension | Value | Where from |
| --- | --- | --- |
| socket bore (= 6 in pipe OD) | **6.625 in = 168.3 mm** | ASTM D2665 / Charlotte DC-DWV |
| pipe bore inside the tube (Sch 40 wall 0.280 in) | 6.065 in = 154 mm | same |
| socket depth | about 3 in (76 mm) | Charlotte catalogue lists 3 5/8 in overall for part 116; measure yours |
| face thickness | 7 to 9 mm typical for a 6 in DWV cap | **measure yours with calipers**; it sets the counterbore depth |

The usable face is the 168.3 mm circle (inside the socket). The layout keeps every knob, nut and flange at least 5 mm inside that circle (dashed line on the drawing, 3 mm design rule plus the counterbore wall), so the cap's inside corner fillet never interferes. Parts stand behind the face inside the socket, where the diameter is still 168 mm for the first 76 mm of depth, so the 25 mm combo jacks, the 35 mm push-pull pots and the 21 mm DC jack all sit inside the cap itself; only the I/O board behind them is in the 154 mm pipe bore.

If instead you cut a flat disc that sits *inside* the pipe (154 mm bore) the layout does not fit: the outer pot arc would have to move in by 7 mm and the outer jacks by 5 mm, which drops the knob gaps under 5 mm. Stay with the cap face.

## 2. Part sizes used (re-checked from datasheets, old and new parts)

| Item | Part | Panel hole | Face envelope | Behind panel | Bushing / panel limit |
| --- | --- | --- | --- | --- | --- |
| J1-J4 combo XLR/TRS | Neutrik NCJ6FI-H (drawing ST-NCJ6FI-H) | 23.8 mm min round + 2 x 3.2 mm at (-10, +11.5) and (+10, -11.5) from centre | flange 27 x 30 mm | 25.4 mm + 3.5 mm pins | panel max 7 mm (Neutrik spec) |
| J5 DC in | Switchcraft L712A, 5.5 / 2.5 mm | 10.0 mm (3/8-32 bushing; confirm on the L712A drawing, RS lists 9 mm body width and 3.1 mm max panel) | hex nut about 14 mm | 20.8 mm | panel max 3.1 mm -> counterbore |
| VR1, VR3, VR5 push-pull | Alpha 16 mm dual + DPDT, M7 x 0.75 | 7.5 mm (8.0 if you keep the anti-rotation tab: add a 1.5 x 3 mm slot at Y-8) | knob 19 mm | body 18 x 18, about 35 mm deep with the switch, shaft 15 mm | bushing 6.5 mm long -> counterbore to 3 mm |
| VR2, VR4 4-gang | Bourns PTD904-2015K-B104, M7 x 0.75 | 7.5 mm | knob 16 mm | body 9.5 x 11, 17.2 mm deep, 6 mm shaft | bushing 7 mm -> counterbore to 3 mm |
| VR6-VR8 dual | Alpha RD902F / Bourns PDB182, M7 x 0.75 | 7.5 mm | knob 16 mm | 9 to 16 mm body | counterbore to 3 mm |
| S1-S3 | NKK M2023 DPDT ON-OFF-ON, 1/4-40 | 6.5 mm | dress nut 11.5 mm, bat 10.4 mm long | body 12.9 x 7.9, 11.2 mm + terminals | bushing 8.9 mm -> counterbore to 4 mm |
| S4 | NKK M2012 SPDT ON-ON | 6.5 mm | same | same | same |

Old Rev A assumptions corrected: the DC jack is not 8 mm (Rev A guessed from a raster PDF; the L712A is a 3/8-32 bushing, drill 10 mm, and the L722A with the 2.0 mm pin is the wrong part for the 2.5 mm adapter plug); the combo flange is 27 x 30 not 26 x 31; the "9.5 mm rotary" holes are gone because every switch is now a 1/4 in toggle; pot bushings are M7 (7.5 mm hole), not 9.5 mm "full size" (Rev A listed 9.5 mm for 24 mm pots, which we are not using).

## 3. Layout (viewed from outside, X right, Y up, mm from the face centre)

| Ref | Function | X | Y | Drill | Counterbore (inside) | Radius | Margin to bore |
| --- | --- | ---: | ---: | --- | --- | ---: | ---: |
| J1 | In L | -49.5 | 10.0 | 24.0 + 2 x 3.2 | none | 50.5 | 13.5 |
| J2 | In R | -16.5 | 10.0 | 24.0 + 2 x 3.2 | none | 19.3 | 44.7 |
| J3 | Out L | 16.5 | 10.0 | 24.0 + 2 x 3.2 | none | 19.3 | 44.7 |
| J4 | Out R | 49.5 | 10.0 | 24.0 + 2 x 3.2 | none | 50.5 | 13.5 |
| J5 | DC in | 0.0 | 66.0 | 10.0 | 18 mm, leave 3.0 | 66.0 | 8.3 |
| S1 | Source (Mono / Stereo / MEGAVERB) | -51.0 | 44.0 | 6.5 | 16 mm, leave 4.0 | 67.4 | 8.7 |
| S2 | Ext tanks (Series / Off / Parallel) | -17.0 | 44.0 | 6.5 | 16 mm, leave 4.0 | 47.2 | 28.8 |
| S3 | FB Dyn (Comp / Off / Limit) | 17.0 | 44.0 | 6.5 | 16 mm, leave 4.0 | 47.2 | 28.8 |
| S4 | FB Phase | 51.0 | 44.0 | 6.5 | 16 mm, leave 4.0 | 67.4 | 8.7 |
| VR1 | Vol (pull = Tube) | -62.0 | -22.6 | 7.5 | 18 mm, leave 3.0 | 66.0 | 5.4 |
| VR2 | HPF | -37.9 | -54.1 | 7.5 | 18 mm, leave 3.0 | 66.1 | 9.1 |
| VR3 | Gain (pull = Dirt) | 0.0 | -66.0 | 7.5 | 18 mm, leave 3.0 | 66.0 | 5.4 |
| VR4 | LPF | 37.9 | -54.1 | 7.5 | 18 mm, leave 3.0 | 66.1 | 9.1 |
| VR5 | Output (pull = Tape) | 62.0 | -22.6 | 7.5 | 18 mm, leave 3.0 | 66.0 | 5.4 |
| VR6 | Ext Mix | -25.5 | -25.5 | 7.5 | 18 mm, leave 3.0 | 36.1 | 39.1 |
| VR7 | Feedback | 0.0 | -36.0 | 7.5 | 18 mm, leave 3.0 | 36.0 | 39.2 |
| VR8 | Wet/Dry | 25.5 | -25.5 | 7.5 | 18 mm, leave 3.0 | 36.1 | 39.1 |

Zones: jack bar across the middle (33 mm pitch), four toggles on the upper arc reading left to right in signal order (Source near the inputs, then Ext tanks, then the feedback pair), DC jack top centre (away from hands and knobs), pots on two arcs below: outer arc radius 66 mm with the three push-pull pots (19 mm knobs) at the ends and bottom and the two filter quads between them, inner arc radius 36 mm with Ext Mix, Feedback, Wet/Dry. Left to right the outer arc is Vol, HPF, Gain, LPF, Output: the signal order.

## 4. Spacing audit (from the script)

| Check | Result | Rule |
| --- | --- | --- |
| combo flange to combo flange | 6.0 mm | flanges must not touch; XLR plug bodies (19.5 mm) end up 13.5 mm apart, latch clear |
| combo flange to Vol / Output knob | 8.1 mm | >= 5 |
| inner-arc knob to knob (16 mm knobs) | 11.6 mm | >= 5 (Rev A rule was 24 mm centre pitch; here it is 27.6) |
| Feedback knob to Gain knob | 12.5 mm | >= 5 |
| combo flange to inner knobs | 12.5 mm | TRS/XLR plugs go straight out, they do not sweep over the knobs |
| toggle to combo flange | 13.2 mm | bat (10.4 mm) never reaches the flange |
| DC nut to toggles | 22 mm | barrel plug body 10 to 11 mm |
| closest part to the cap bore | 5.4 mm (push-pull knob edge at r = 75.5) | >= 3 plus counterbore wall |

Outer-arc pitch is 39.7 mm, so the 19 mm push-pull knobs have plenty of room to be gripped and pulled. Everything is also inside a 150 mm circle except the three push-pull knobs and the two outer toggles, so a 6 mm bezel ring on the cap rim would still clear.

## 5. Drilling notes

1. Mark the centre and the X/Y axes on the cap, then transfer from the 1:1 PDF or the DXF (a CNC shop or a laser-cut 3 mm drill jig from the DXF is the accurate way; hand drilling with a centre punch and step bits works for 6.5 / 7.5 / 10 mm).
2. Combo jacks: 24 mm hole saw or step bit, then the two 3.2 mm screw holes; use M3 x 16 screws with nuts inside, or put a 1.5 mm aluminium strip behind the four jacks (198 x 42 mm as in Rev A) so the socket walls do not crack when a cable is yanked.
3. Counterbores from the **inside** with a Forstner bit: 18 mm for pots and the DC jack (leave 3.0 mm of face), 16 mm for toggles (leave 4.0 mm). Drill the through hole first, then counterbore with the Forstner centred on it. Check depth with the part: the nut must catch at least 3 threads.
4. Knurled or flatted shafts: the Alpha push-pull pots have solid 6.35 mm shafts (set-screw knobs); the Bourns quads have 6 mm shafts (use 6 mm-bore knobs or 1/4 in set-screw knobs with a shim).
5. Anti-rotation tabs: bend them off or add the 1.5 x 3 mm slot at Y-8 from each pot centre; the tab will not hold in PVC anyway. A drop of thread-locker on the nuts.
6. Print the 1:1 template and lay it on the cap before drilling anything: a DWV cap face is slightly domed, so check that the outer arc (r = 66 mm) is still on flat material on your cap.
