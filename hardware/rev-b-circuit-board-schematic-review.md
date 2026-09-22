# GAS Rev B Circuit Board: Schematic Review (2026-09-13)

Board: `hardware/kicad/circuit-board.kicad_sch` (single sheet, 311 placed parts, 195 nets). Reviewer: Claude (Cowork), with an independent adversarial pass by a second review agent on the netlist. Method follows the kicad-schematic-review contract: extracted netlist (generated from `design.py`, so the pin-to-net facts are exact), datasheet checks for the non-trivial ICs, checklist items, and a raw spot-check of the KiCad file after each fix.

## Verification basis

- ERC (KiCad 10.0.5, on Jason's machine with the full libraries): **0 errors, 0 warnings**, run after every change.
- Netlist report `netlist-report.txt`: no single-pin nets, no unintended merges (every AGND/VBIAS/+9VC/+15VA/-15VA member was listed and read).
- Datasheets read: THAT 2180 series (600029 Rev 02), THAT 2252 (600032 Rev 03, then dropped as discontinued), THAT 4305 (checked for a replacement, EOL), Xvive VTL5C3/5C4, TL072/TL072H supply range (TI), L78L09 SOT-89 pinout (via KiCad MC78L05_SOT89 symbol, cross-checked to ST: 1 OUT, 2 GND, 3 IN).
- Not checked against a datasheet: OPA1679 (same part and footprint as Rev A, already reviewed), passives, JST connectors (Rev A parts).
- No PCB-level conclusions in this document (trace width, thermal, clearance are in the PCB DRC section of the PCBWay package).

## Blockers found and fixed

| # | Finding | Evidence | Fix |
| --- | --- | --- | --- |
| 1 | THAT2180 pin 5 (V-/ISET) was wired straight to -15VA. The datasheet (p.8) requires a current-setting resistor to VEE, typically 5.1k for 2.4 mA; a direct rail connection over-biases and can destroy the part. | 2180 datasheet, netlist `VCA_VN_L/R` | R1306 / R1326 5.1k added between pin 5 and -15VA. |
| 2 | Tube, Tape and Tube Screamer make-up stages were computed as if 1 V/FS reached the pedal stage, but the -36.9 dB pad is in the path: all three modes would have been 20 dB quiet at the bus. | arithmetic in section 4 of the definition doc | R408 4.32k -> 43.2k (Tube). Tape and TS make-ups changed from dividers to non-inverting gain stages (x2 and x6.9). Verified: pad 0.01426 x stage gain x make-up = 1.00 (Tube), 1.00 (Tape incl. 0.835 loading), 1.185 (TS, the plugin's +1.4 dB). |
| 3 | THAT2252 RMS detector is discontinued (Mouser: obsolete, 0 stock; THAT product page: "No longer available"); THAT 4301/4305 Analog Engines also EOL with 0 stock. | Mouser lookups 2026-09-13, thatcorp.com | Detector rebuilt from a precision full-wave rectifier, 10 ms average and MMBT3906 transdiode log converter (U1305 quad). Ratio math re-done for the 3.0 mV/dB log slope (gain 18.2). |

## Should-fix items, all applied

| # | Finding | Fix |
| --- | --- | --- |
| 4 | THAT2180 Ec- driven from a 10k node (diode clamp + pull-down). Datasheet wants a low-impedance control source; high impedance adds 2nd harmonic. | U1302D follower between the clamp node and VCA_EC. |
| 5 | 2252 IBIAS at spec max and bypassed to ground (moot after item 3). | Removed with the 2252. |
| 6 | FET Q-bias trim could only reach -3.75 V at the gate; 2N5457 Vgs(off) spreads to -6 V. | R1205 / R1225 100k -> 47k (gate reaches -5.1 V). BOM note: screen FETs for |Vgs(off)| < 5 V. |
| 7 | J201 drain trimmer (10k) only covered Id > 0.28 mA; J201 Idss spreads 0.2 to 1 mA. | RV401 / RV501 -> 50k. |
| 8 | Difference-amp reference leg was 10k, so the 10k trimmer wiper (up to 2.5k) unbalanced it by up to 25 %. | Reference legs raised 10x (100k / 1.82M). |
| 9 | HPF_OUT loading: seven parallel loads plus the SK feedback path could pull ~24 mA from one OPA1679 unit at +12 dBFS. | Pad 10k/147R -> 47k/680R, opto shunt R 10k -> 22k, FET pad 10k/1k -> 22k/2.2k. Load now about 5.5k plus the SK path (< 8 mA). |
| 10 | THAT2180A is factory trimmed; an external symmetry trim can only make it worse. | RV1301/1321 and R1305/1325 set DNP (footprints kept for a 2181). |
| 11 | Op-amp offset into the 2180 log core causes control-voltage thumps. | C1301 / C1321 1u film added in series with the VCA input resistor (datasheet recommendation). |
| 12 | BAT42W (SOD-123 Schottky) is obsolete at Vishay. | D1243 -> 1N5819HW-7-F (SOD-123, active, 479k stock). |
| 13 | TL072C is only characterised from +/-5 V; this board runs it on 9 V total. | Value TL072H, MPN TL072HIDR (rated 4.5 V to 40 V). |
| 14 | A shorting (make-before-break) rotary would tie two mode outputs together through the relay contacts. | Panel switch specified non-shorting in the definition doc. |

## Per-IC checks (pass unless noted)

- **U201 / U301 OPA1679 (main path)**: V+ pin 4 = +15VA, V- pin 11 = -15VA, 100n on each rail. A: inverting drive stage, feedback closed via pot path and R203 1M, + at AGND. B: SK HPF, + biased through R208 1M and the R2 rheostat, feedback R206/R207. C: SK LPF unity follower. D: inverting output buffer. No floating inputs. Output isolator R214/R314 100R.
- **U202 / U302 OPA1679 (make-ups)**: A inverting (Tube), B and C non-inverting gain stages with bias returns R616/R804 100k to AGND, D follower on the vactrol node. All inputs biased.
- **U102, U401, U501, U402 TL072H (+9VC / AGND)**: V+ pin 8 = +9VC, V- pin 4 = AGND, 100n each. Every input sits at VBIAS (4.5 V) through 100k or the gain network, well inside the single-supply common-mode range. Spare U102B: + VBIAS, - tied to out.
- **U1101 OPA1679 (opto sidechain + FET follower)**: A follower (FET_SC), B inverting summer, C precision rectifier (+ at AGND), D non-inverting LED driver. LED chain VT1101 -> VT1121 -> AGND; the driver output is 0 V or positive only, LEDs never reverse biased.
- **U1201 OPA1679 (FET)**: A/B non-inverting x11 make-ups with + on the FET node (DC 0 V via R1202 2.2k), C summer, D rectifier.
- **U1301 OPA1679 (VCA audio)**: A/C unity inverters, B/D current-to-voltage converters on the 2180 outputs with 20k feedback and 22p.
- **U1303 / U1304 THAT2180A**: pin 1 IN via 20k from an op-amp through 1u; pin 2 EC+ AGND; pin 3 EC- VCA_EC (buffered); pin 4 SYM open (DNP network); pin 5 via 5.1k to -15VA; pin 6 GND; pin 7 +15VA; pin 8 OUT to virtual ground. Decoupling 100n per rail per device. Signal current at +12 dBFS 1.9 mA, within the 2.05 mA cell budget.
- **U1305 OPA1679 (detector)**: A summer, B rectifier, C full-wave summer, D log amp with MMBT3906 transdiode (C at inverting input, E at output, B at AGND) and 100p stability cap. Input current 5.5 uA at threshold, log region.
- **U1302 OPA1679 (threshold)**: A difference amp, B clamp with D1341 inside the loop, C spare tied off, D follower.
- **U101 L78L09**: IN +15VA (6 V headroom, 25 mA, 0.15 W), GND AGND, OUT +9VC with 10u + 100n. C103 100n at the input.
- **Q401 / Q501 J201**: gate 1M to AGND, source 470R with 10u bypass, drain load 4.7k + 50k trim to +9VC. Q601/Q602, Q701/Q702 MMBT3904 differential pair: bases 2.87 V, tail 0.9 mA, collectors ~6.9 V. Q1201/Q1221 2N5457: drain on the divider node, source AGND, gate through 1M from the CV mix with 1M drain-to-gate.
- **K1..K7 TQ2-5V**: coil A1 = MODEn (positive), A2 = AGND, flyback D1..D7 cathode on MODEn. Contacts 11/21 = BUS_L/R, 14/24 = mode output, 12/22 no-connect. Bus pulled down by 100k. Coil current 28 mA from the panel's +5VAUX line.
- **Connectors**: P1/P2 audio 3-pin, P3 power VH 3-pin (+15VA / AGND / -15VA, same as every Rev A board), P4/P5 16-pin control (see the definition doc for the pinout).

## Checklist items

- Power: every IC has 100n per rail; bulk 10u on both rails at P3; +9VC has 10u + 100n; VBIAS 47u + op-amp buffer. PWR_FLAGs on +15VA, -15VA, AGND. Pass.
- Current paths: highest current is the relay coil (28 mA on a JST XH contact rated 3 A) and the +15VA feed (about 120 mA total on a VH contact rated 10 A). Pass.
- Unused pins: relay NC contacts no-connect; spare op-amp units tied; 2180 SYM open per datasheet. Pass.
- Polarity: electrolytics C101 (+15VA), C102 (+ on AGND, - on -15VA), C104/C106/C403/C503/C604/C704 (+ on the positive node). Pass.
- Audio-path capacitor policy: all series signal caps are PPS or MKS film; electrolytics only on bypass/bias nodes. Pass.

## Manual-review questions left for the bench

1. TQ2 pin 4 = NO on the physical relay (Rev A footprint note still applies).
2. VTL5C3 LED current vs resistance curve sets the Opto depth; RV1101 range 2.2k to 12.2k should cover it, verify at +12 dB over threshold.
3. J201 gm x Rd spread means Tube mode unity level will vary a few dB between devices; RV401 sets bias, not gain.
4. Log detector: check DET_OUT sits near +0.5 V at -18 dBFS and that RV1342 has margin either side.

## Parser / method limitations

Connectivity is by labels on stub wires, so the sheet is a netlist drawing rather than a readable schematic. Anyone reading it should use the definition document alongside it. The netlist itself is exact (generated), so there is no extraction uncertainty.
