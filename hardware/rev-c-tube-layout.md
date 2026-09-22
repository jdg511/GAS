# GAS Rev C: Boards and 4 Tanks inside a 6 in PVC Pipe (2026-09-15, front stack updated 2026-09-17)

**2026-09-17 update:** the jacks are no longer on the io-board. A 6 in control deck and a 6 in jack deck now sit right behind the cap (see `rev-c-front-stack-and-io-modes.md`). The io-board moves back onto the sled plate. The zone table and 4.1 below are updated; `revc_mech.py` was re-run on 2026-09-21, so the drawings in `mech-rev-c/` now show the front stack (new detail panel), the io-board at Z 45 to 225 and the circuit board at Z 230 to 405.

Drawings: `mech-rev-c/rev-c-tube-layout.pdf` / `.png` (side view + front stack detail + 4 cross sections), `rev-c-tube-layout.dxf` (layers PIPE, BOARDS, PLATE, TANKS, CAGE, TEXT, plus the bulkhead disc), `revc_mech.py` (re-run after any size change; it prints the clearance report below).

Frame: Z runs down the pipe from the inside of the service cap face (Z = 0). X right, Y up, seen from outside the service cap. The instrument lies **horizontal** (all four tanks are mounting code B: horizontal, open side down). Do not stand it on end.

## 1. The one thing that decides everything: 154 mm, not 168 mm

A DWV cap's socket is 168.3 mm, but the pipe slides into it and bottoms against the face. So once assembled, **everything behind the cap face lives in the pipe's 154 mm bore**. Consequences for the endcap parts (layout from `rev-c-endcap-fit-check.md`, unchanged):

- Turn each outer-arc push-pull pot (Vol, Gain, Output) so a **flat side of its 18 mm square body faces the pipe wall**: corner-out they reach r = 78.7 mm and hit the wall; flat-out they reach r = 75 mm.
- S1 and S4 (outer toggles) reach r = 74.9 mm: 2 mm to the wall, fine, but mount them with the body's long side tangential.
- Everything else behind the face clears by 5 mm or more.

## 2. Tank sizes (Accutronics)

| Tank | L x W x H mm | Where |
| --- | --- | --- |
| 4AB1C1B (Type 4) x2 | 425.5 x 120.3 x 33.4 | cage 1, main L upper, main R lower |
| 9EB2C1B / 9EB3C1B (Type 9) | 425.5 x 111.1 x 33.4 | cage 2, 2nd L upper, 2nd R lower |

Two tanks side by side are 231 mm wide, so they cannot sit next to each other. Stacked face to face with a 14 mm gap they are 81 mm tall; the Type 4 corners land at r = 72.5 mm (4.5 mm from the wall), the Type 9 corners at 68.7 mm. Four stacked would need 150 mm of height: no. So the tanks go in **two stacked pairs, one behind the other**.

## 3. Layout

| Zone (Z mm) | Contents |
| --- | --- |
| -8 to 0 | service cap face (drilled per the endcap template) |
| 0 to 35 | pot and toggle bodies behind the face |
| 7 (T = 8) | **control deck** PCB (6 in round, parts toward the cap) |
| 23 (T = 8) | **jack deck** PCB (6 in round below Y = 49, jacks toward the cap), harness plugs behind it to about Z 42 |
| 45 to 225 | **io-board** on the plate top, 6 mm standoffs |
| 45 to 430 | **sled plate**: 3 mm aluminium (5052 or 6061), 140 x 385 mm, at Y = -10.6 (top) |
| 230 to 405 | **circuit-board** on the plate top, 6 mm standoffs |
| 60 to 122 | **power-board** under the plate, 5 mm standoffs, parts facing down |
| 270 to 420 | **tank-board** under the plate, parts facing down, RCA jacks on the rear edge pointing at the tanks |
| 460 to 942 | **cage 1** (main tanks) |
| 957 to 1438 | **cage 2** (2nd tanks) |
| 1453 | far cap face: **pipe length 1453 mm (57.2 in)** |

Clearance report (corner radius of every envelope against the 77 mm bore radius):

| Item | Width | Y range | Corner r | Margin |
| --- | --- | --- | --- | --- |
| io-board incl. 14 mm parts | 136 | -4.6 .. +11 | 68.9 | 8.1 |
| circuit-board incl. parts | 120 | -4.6 .. +11 | 61.0 | 16.0 |
| power / tank board incl. 20 mm parts | 120 | -40.2 .. -18.6 | 72.2 | 4.8 |
| sled plate | 140 | -13.6 .. -10.6 | 71.1 | 5.9 |
| Type 4 tanks | 120.3 | +/-7 .. +/-40.4 | 72.5 | 4.5 |
| Type 9 tanks | 111.1 | +/-7 .. +/-40.4 | 68.7 | 8.3 |
| cage rods M6 at (+/-30, +/-60) | | | 68.5 | 8.5 |

## 4. How it is held

### 4.1 Electronics cartridge (comes out with the service cap)

1. Each NCJ6FI-V on the jack deck is held by two M3 screws through the face into its flange (8 screws). The control deck is held by the nuts of its toggles, pots and DC jack. That is the front anchor.
2. An aluminium angle (25 x 25 x 3) on the front of the sled plate bolts to jack deck holes H1 / H2 (M3 at X +/-26, Y -11.5, nylon washers). The io-board sits on the plate top with 4 x M3 x 6 mm standoffs.
3. Circuit board on the plate top (4 x M3 x 6 mm), power and tank boards under the plate (4 x M3 x 5 mm each). Nylon washers under every standoff; the plate is AGND only at one point (power board H1).
4. The plate's rear end rides in a **saddle**: a 6 mm HDPE half-disc (radius 76 mm) screwed to the plate's last 20 mm, with felt tape on its rim. Pulling the cap pulls the whole cartridge out; the tank cages stay in.
5. Harness service loop: leave 150 mm of slack on the 8 tank RCA cables so the cartridge can be pulled 120 mm out before unplugging.

The old jack axis height question is gone: the NCJ6FI-V flange sits 24 mm from the jack deck by Neutrik's drawing, and the cap only needs the jack pocket to 7 mm.

### 4.2 Tank cages (slide in from the far end)

Each cage: two bulkhead discs (151 mm, 6 mm HDPE, felt tape on the rim), 4 x M6 threaded rods at (+/-30, +/-60) with nuts both sides of each disc, cage length 481.5 mm. On each disc, an aluminium L-bracket (25 x 25 x 3, 110 mm long) per tank at the tank's end height. The tank's own end-flange holes bolt to the bracket **through rubber grommets** (Accutronics / Fender style grommet kit, or 3/8 in rubber grommets with shoulder washers): the springs must never see the hard mounting. Drill the brackets to your tanks' flange holes.

- Both tanks in a cage keep the same orientation: open side down, input RCA toward the service end (shorter send cables).
- Cage 1 goes in first from the far end, then a 15 mm spacer ring (PVC coupling stub or HDPE ring), then cage 2, then the far cap. The rims ride on felt, so the cages are snug but not rigid to the pipe; that keeps knob bumps from crashing the springs.
- RCA cables: cage 1 sends/returns about 450 mm, cage 2 about 950 mm (shielded, e.g. Mogami 2319 or any low-capacitance coax). Run sends on the left of the cages and returns on the right, as far apart as the bore allows.

## 5. Parts for the enclosure (approximate prices, Sept 2026, verify locally)

| Part | Qty | Approx |
| --- | --- | --- |
| 6 in PVC DWV pipe, 10 ft (cut to 1453 mm) | 1 | $60 to $110 |
| 6 in DWV socket cap (Charlotte PVC 00116 1400 or equal) | 2 | $15 to $25 each |
| 3 mm aluminium plate 140 x 385 mm | 1 | $15 to $25 (SendCutSend / local) |
| 6 mm HDPE sheet for 4 discs + 1 saddle | 1 x 300 x 600 | $15 to $25 |
| M6 threaded rod, 1 m | 2 | $5 each |
| Aluminium angle 25 x 25 x 3, 1 m | 1 | $10 |
| M3 standoffs / screws / nylon washers kit | 1 | $15 |
| Rubber grommets + shoulder washers | 16 | $10 |
| Felt tape | 1 roll | $6 |

## 6. Heat and noise

About 11 W is dissipated inside (TEL 12 about 1.5 W, R-78E about 0.3 W, the rest op-amps and the tank drivers). Spread over the pipe's 0.7 m2 surface that is only a few degrees C of rise; no vents needed now that the tubes are gone. Keep the power board (DC-DC at 300 to 400 kHz) at the front, the tank-board recovery amps at the rear of the cartridge, and the tank return cables away from the power harness.
