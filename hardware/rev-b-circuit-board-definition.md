# GAS Rev B Circuit Board: Schematic-Ready Definition (2026-09-13)

**Illicit Apothecary, The Great American Spring.** This board replaces the Rev A `filter-clipper` board. It is the hardware translation of the plugin's CIRCUIT block as it stands on 2026-09-12: Drive, fixed-Q pre-HPF, a seven-position Mode circuit (Clean, Tube, Tape, Tube Screamer, Opto Comp, FET Comp, VCA Limiter), fixed-Q post-LPF. The circuit sits on the wet path only (after the tanks and Ext Mix, before the feedback block), exactly where the plugin has it.

KiCad files: `hardware/kicad/circuit-board.kicad_pro / .kicad_sch`, project symbol lib `GAS_Parts.kicad_sym`, footprint `GAS_Parts.pretty/Vactrol_VTL5C3_Axial.kicad_mod`. The schematic is generated from `hardware/kicad/revb-gen/design.py` (netlist-by-label capture: every pin has a stub wire and a local label; connectivity is the label names). ERC: 0 errors, 0 warnings (KiCad 10.0.5, 2026-09-13).

## 1. What changed versus Rev A and why

| Plugin change (Sept 2026) | Hardware consequence |
| --- | --- |
| Mode list is now Clean / Tube / Tape / Tube Screamer / Opto / FET / VCA (7) | Si/LED/Ge diode ladders and the 2-bit clip decode are gone. Seven relay-selected stereo circuits, one energised at a time from a 7-position rotary switch. |
| HPF Q and LPF Q knobs removed, both fixed at 0.707 | Q pot landings removed. Filters are 2nd-order Sallen-Key Butterworth with fixed damping. Cutoff needs two tracking resistors per channel, so each filter uses a **4-gang** pot (see section 5). |
| Circuit Position selector removed, circuit is wet-path only | No change to the harness topology: this board still sits between JXF (feedback/wet board send) and JFILT-WET (return). |
| Crossfade removed from the plugin | Not on this board. On the Rev A crossfade/feedback/wet board, delete the crossfade pot and bridge P307 pins 1-2 (XFD_L_HI to XFD_L_WIPER) and pins 4-5 (XFD_R_HI to XFD_R_WIPER) in the harness. No PCB respin needed there. |
| Series inter-tank gain +12 dB to +6 dB | Bench target for the ext-tank-routing board's R241 series-mode trim. Not on this board. |
| Drive is +/-24 dB, unity at centre, ahead of the HPF | Drive moved ahead of the HPF (Rev A had it after). Symmetric-in-dB inverting gain pot, 0 dB at centre with a linear dual pot. |

## 2. Level reference

Everything on the board is designed around one scale so the plugin's dBFS numbers map to volts:

- **0 dBFS = 4.36 Vpk at the board input and output** (= +12 dBu rms sine). Nominal program (+4 dBu) is then -8 dBFS; the plugin's +12 dBFS sanitize ceiling lands at 17 Vpk, i.e. the +/-15 V rails are the sanitize clamp.
- The HPF has a gain of 1.59 (needed for Q = 0.707 with equal parts), so on the **mode bus 0 dBFS = 6.93 Vpk**. The output buffer divides by 1.59 again.
- The three pedal-level modes (Tube, Tape, Tube Screamer) run on a local +9 V rail biased at 4.5 V, exactly as the plugin models them, and see **0.1 Vpk per full scale** through a -36.8 dB pad. Their outputs are scaled back to bus level with the same normalisation the plugin uses (unity below the knee).
- The three dynamics modes run at bus level on +/-15 V. Their fixed threshold, -18 dBFS, is **0.87 Vpk (0.62 Vrms)** on the bus.

## 3. Signal path (per channel, L shown, R is 3xx/5xx/7xx/9xx)

`XFADE_OUT_L (P1)` -> Drive `U201A` -> HPF `U201B` -> **HPF_OUT_L** -> [seven mode circuits in parallel] -> relay contacts -> **BUS_L** -> LPF `U201C` -> output buffer `U201D` -> R214 100R -> `FILTCLIP_OUT_L (P2)`.

Polarity: Drive inverts, output buffer inverts back. Every mode circuit is non-inverting from HPF_OUT to its output (the Tube JFET stage inverts and its make-up stage inverts again), so switching modes never flips polarity into the feedback loop.

### 3.1 Drive (U201A)
Inverting stage with the pot as both input and feedback resistor. Gain = -(R202 + Rpot_lower) / (R201 + Rpot_upper) with R201 = R202 = 680R and a 10k linear dual pot (`DRV_L_HI / DRV_L_W / DRV_L_LO` on P4): -23.9 dB fully down, 0 dB at centre, +23.9 dB fully up, symmetric in dB. C201 22p for stability, R203 1M keeps the loop closed if the pot is unplugged. Minimum input impedance 680R at full drive; the upstream buffer (100R isolator) drives it fine.

### 3.2 HPF (U201B), Sallen-Key, Q = 0.707 fixed
C202 = C203 = 68 nF PPS film, R = 1k + rheostat gang (two gangs per channel: R204 -> `HPF_L1_W`, its HI end is HPF_OUT_L; R205 -> `HPF_L2_W`, its HI end is AGND). Gain K = 1 + R206/R207 = 1 + 5.9k/10k = 1.59, so Q = 1/(3 - K) = 0.71. With a 100k gang: fc = 1/(2*pi*R*68n) = **23 Hz (fully up) to 2.3 kHz (fully down)**; plugin range is 1 Hz to 4 kHz, defaults 100 Hz (GAS) / 250 Hz (GBS). R208 1M keeps the + input biased if the pot is unplugged.

### 3.3 Pad to pedal circuits
R215 47k / R216 680R: 0.01426 = -36.9 dB, so 6.93 Vpk (0 dBFS on the bus) becomes 0.1 Vpk (47k keeps the HPF op-amp load light). Feeds Tube, Tape and Tube Screamer through 1 uF film caps into 100k bias resistors to VBIAS (fc 1.6 Hz).

### 3.4 LPF (U201C), Sallen-Key unity gain, Q = 0.74 fixed
R209 = R210 = 1k + rheostat gang (`LPF_L1_W` with HI end `LPF_N1_L`, `LPF_L2_W` with HI end `LPF_P_L`). C204 15 nF (feedback) and C205 6.8 nF (to ground): Q = 0.5*sqrt(15/6.8) = 0.74, fc = 1/(2*pi*R*sqrt(C1*C2)) = **156 Hz (fully up) to 15.8 kHz (fully down)**; plugin 500 Hz to 20 kHz, defaults 12 kHz / 8 kHz. R211 100k bus pull-down so the bus never floats between relay positions.

### 3.5 Output buffer (U201D)
Inverting, gain -R213/R212 = -10k/15.8k = -0.633 = 1/1.59, C206 22p. Restores the input scale and the polarity. R214 100R output isolator.

## 4. Mode circuits

All values are the ones the plugin solves its transfer curves from (see `circuit-modes-tube-tape-2026-09-12.md` and `clipper-dynamics-circuits-2026-09-06.md`). Make-up gains are computed so each mode is unity at the bus below its knee, which is exactly the plugin's normalisation.

### Mode 1: Clean
Relay K1 routes HPF_OUT straight to the bus.

### Mode 2: Tube (J201 "Fetzer" stage), +9 V. Refs 4xx (L), 5xx (R), TL072 U401A / U501A
- C401 1u -> U401A non-inverting x11 (R402 100k / R403 10k to VBIAS), R401 100k bias. Output clamps at the 9 V rails (about +/-3.3 V), which the plugin models.
- C402 47n into the gate, R404 1M gate to AGND, Q401 J201 (TO-92), R405 470R source, C403 10u source bypass, drain load R406 4.7k + RV401 50k trimmer to +9VC (**set drain to 4.9 V**; plugin uses 8.2k; 50k covers the J201 Idss spread down to 0.13 mA).
- Output: C404 1u -> R407 100k -> U202A inverting, R408 43.2k: gain 0.432 = 69.3 / (11 x 14.5) (the pad took 1/69.3 out, the stage gain puts 159.5 back, so the mode is unity below the knee). Inversion restores polarity (the plugin flips polarity in code).

### Mode 3: Tape (record EQ, 2N3904 differential limiter, repro EQ), +9 V. Refs 6xx / 7xx, U401B / U501B
- Record EQ: C601 1u, R601 100k bias, U401B non-inverting with R604 82k feedback; gain leg R602 10k to VBIAS in parallel with R603 4.7k + C602 6.8n (x9.2 LF rising to x26.6 above ~3 kHz).
- Limiter: C603 1u into Q601 base; both bases biased ~2.9 V by 47k/22k (R605-R608), C604 10u quiets the Q602 base; R609/R610 470R emitter resistors into shared tail R611 2.2k; R612/R613 4.7k collector loads to +9VC. Output from Q602 collector (non-inverting).
- Repro EQ: R614 15k series (the 4.7k collector resistor adds to it), R615 10k + C605 3.3n to AGND.
- Output: C606 1u -> R616 100k bias return (loads the 19.7k repro source by 0.835) -> U202B non-inverting x2 (R617 / R618 100k): 0.835 x 2 = 1.67 = 69.3 / (9.2 x 4.53), unity below the knee.

### Mode 4: Tube Screamer feedback clipper, +9 V. Refs 8xx / 9xx, TL072 U402A / U402B
C801 1u, R801 100k bias, R802 4.7k gain leg to VBIAS, R803 51k feedback with D801/D802 1N4148W anti-parallel and C803 51p. Output C804 1u -> R804 100k bias return -> U202C non-inverting x6.9 (R805 59k / R806 10k) = 69.3 x 1.185 / 11.85, which keeps the plugin's +1.4 dB clean gain. No 47n in the gain leg because the plugin's stage is flat.

### Mode 5: Opto compressor (LA-2A / CL 1B territory), +/-15 V. Refs 11xx
- Audio: R1101 22k into the VT1101 photocell to AGND (shunt divider), buffered by U202D. Dark the cell is >10 M, so the mode is unity at rest. Same for R with R1121 / VT1121 / U302D.
- Sidechain (feed-forward, linked): U1101B sums HPF_OUT_L and _R (100k / 100k / 47k, -0.47 each), U1101C precision half-wave rectifier (R1144, R1145 10k, D1141, D1142) with positive output, R1146 10k + C1141 1u = 10 ms average. U1101D non-inverting driver, gain 13 (R1148 120k / R1149 10k), drives the two vactrol LEDs in series through R1150 2.2k + RV1101 10k. Two LEDs (3.4 V) light when the averaged sidechain reaches 0.26 V, which is the -18 dBFS threshold. **RV1101 sets depth: target 7 dB of gain reduction at +12 dB over threshold.** The vactrol's own 35 ms turn-off plus photocell memory supplies the dual-slope release.

### Mode 6: FET compressor (1176 territory), +/-15 V. Refs 12xx
- Audio: R1201 22k / R1202 2.2k pad (-20.8 dB, keeps the FET below ~0.3 Vpk), Q1201 2N5457 drain on the pad node, source AGND, gate through R1203 1M from the control mix with R1204 1M drain-to-gate for even-harmonic cancellation. U1201A non-inverting x11 (R1207 100k / R1208 10k) restores unity.
- Control: FET_CV_L mixes FET_BIAS_L (R1205 47k) and FET_SC (R1206 100k); with R1203 / R1204 the gate sits at about FET_BIAS/3.4, so RV1201 (10k, -15VA to AGND) reaches -5.1 V at the gate. RV1201 is the **Q-bias trim: set the gate at Vgs(off) so the FET just starts to conduct at threshold** (2N5457 Vgs(off) spreads -0.5 to -6 V, so each channel has its own trim; screen for |Vgs(off)| under 5 V).
- Sidechain (feedback, linked): U1201C sums FET_OUT_L/R, U1201D precision half-wave (R1244, R1245, D1241, D1242), D1243 BAT42W peak detector with R1246 1.5k / C1241 100n (150 us attack) and R1247 2.2M (220 ms release), follower U1101A -> FET_SC.

### Mode 7: VCA limiter (dbx 160 territory), +/-15 V. Refs 13xx
- Audio: U1301A unity inverter (R1301 / R1302 20k) -> C1301 1u film (keeps op-amp offset out of the log core) -> R1303 20k -> THAT2180 U1303 pin 1 -> pin 8 -> U1301B current-to-voltage (R1304 20k, C1302 22p). Net non-inverting. Ec+ (pin 2) to AGND, Ec- (pin 3) is the shared control VCA_EC. Pin 5 (V-) goes to -15VA through R1306 5.1k (ISET 2.4 mA, per datasheet; never straight to the rail). Symmetry trim RV1301 / R1305 are DNP because the 2180A grade is factory trimmed (fit them only with a 2181). Same for R with U1304 / U1301C / U1301D / R1326.
- Detector (feedback, linked, log-average): THAT's 2252 RMS detector and the 4301/4305 Analog Engines are all discontinued with no stock (checked Mouser 2026-09-13), so the detector is discrete. VCA_OUT_L and _R through C1341 / C1342 1u and R1341 / R1342 20k into U1305A inverting summer (R1343 10k, SUM = -(L+R)/2). U1305B precision half-wave (R1344 / R1345 10k, D1342 / D1343) and U1305C summer (R1347 20k, R1348 10k, R1349 20k) make a full-wave rectifier, FW = -|L+R|/2. R1346 10k + C1344 1u average it (10 ms, the plugin's RMS constant). R1350 100k feeds the average into U1305D with Q1341 (MMBT3906) as a transdiode in the feedback: DET_OUT = Vt ln(I/Is), about +3.0 mV/dB, rising with level. Both the log converter and the 2180's control law scale with kT/q, so the ratio holds with temperature. Mean-absolute rather than true RMS: for program material the difference is under 1 dB and the dbx-style log-domain behaviour (level-independent ratio, gentle on transients) is preserved.
- Threshold and ratio: U1302A difference amplifier gain 18.2 (R1351 10k / R1352 182k on the detector side, R1353 100k / R1354 1.82M on the reference side so the trimmer wiper impedance does not unbalance it) between DET_OUT and TH_REF. 18.2 x 3.0 mV/dB = 54 mV/dB at Ec-, and the 2180 reduces gain 6.1 mV/dB, so k = 8.9 dB per dB over threshold; in a feedback topology that is a ratio of about 10:1. TH_REF comes from RV1342 10k between R1355 / R1356 100k dividers (+/-0.71 V span, more than the whole useful range of the log output). U1302B is a precision positive clamp (D1341 in the loop, R1357 10k) so the control only ever goes positive (gain reduction) and sits at exactly 0 V below threshold; U1302D buffers it into VCA_EC because the 2180 control port wants a low source impedance. The plugin's 12 dB over-easy knee is not implemented (hard knee). The 2180's own release follows the detector (10 ms) rather than the plugin's separate 120 ms release; a slower release is a bigger C1344.

## 5. Mode relays and control

K1..K7 Panasonic TQ2-5V (same part and footprint as Rev A). One coil per rotary position, driven directly by the panel switch from +5VAUX: `MODEn` -> A1, A2 -> AGND, D1..D7 1N4148W flyback. Contacts: 11/21 = BUS_L / BUS_R, 14/24 = the mode's L / R output, 12/22 unused. Only one relay is on at a time (28 mA from +5VAUX). Between positions the bus is muted by R211 / R311.

Panel: 1-pole 7-position **non-shorting (break-before-make)** rotary (Lorlin CK1050 or Grayhill 56 series set to 7 stops), common to +5VAUX, positions 1..7 to MODE1..7. A shorting switch would briefly tie two mode outputs together through the relay contacts.

## 6. Connectors (harness changes from Rev A are marked)

| Ref | Name | Footprint | Pins |
| --- | --- | --- | --- |
| P1 | JXF-CIR (was JXF-FILT) | JST XH 3 | 1 XFADE_OUT_L, 2 AGND, 3 XFADE_OUT_R |
| P2 | JCIR-WET (was JFILT-WET) | JST XH 3 | 1 FILTCLIP_OUT_L, 2 AGND, 3 FILTCLIP_OUT_R |
| P3 | JCIR-PWR | JST VH 3 | 1 +15VA, 2 AGND, 3 -15VA |
| P4 | JCIR-CTL-A **(changed, now 16-pin)** | JST XH 16 | 1-3 DRV_L HI/W/LO, 4-6 DRV_R HI/W/LO, 7 HPF gang L1 HI (= HPF_OUT_L), 8 HPF_L1_W, 9 gang L2 HI (= AGND), 10 HPF_L2_W, 11 gang R1 HI (= HPF_OUT_R), 12 HPF_R1_W, 13 gang R2 HI (= AGND), 14 HPF_R2_W, 15-16 AGND |
| P5 | JCIR-CTL-B **(changed, now 16-pin)** | JST XH 16 | 1 gang L1 HI (= LPF_N1_L), 2 LPF_L1_W, 3 gang L2 HI (= LPF_P_L), 4 LPF_L2_W, 5 gang R1 HI (= LPF_N1_R), 6 LPF_R1_W, 7 gang R2 HI (= LPF_P_R), 8 LPF_R2_W, 9-15 MODE1..MODE7, 16 AGND |

Panel pots (enclosure-level BOM, not on the PCBWay BOM):
- Drive: 10k **linear** dual, e.g. Alps RK097 / Bourns PDB182 dual 10kB.
- HPF and LPF cutoff: 100k **4-gang** pots wired as rheostats (HI to W, leave LO open or tie to W). Linear 4-gang: Bourns PTD904-2015K-B104 (verify at order time). A log/audio taper quad (Alps RK27114A 100kA) spreads the sweep more like the plugin's skewed control; with a linear gang the top decade sits in the first part of the travel. Both fit the same header.
- Mode: 1P7T rotary as above. The Rev A `CTL_CLIP_MODE_A/B` lines and their +5VAUX pin are gone.
- The Rev A `HPF_Q_*` and `LPF_Q_*` landings are gone.

## 7. Power

P3 brings +/-15VA. C101 / C102 10u bulk, 100n at every IC. U101 L78L09 (SOT-89) makes +9VC for the four TL072 pedal-mode op-amps, the J201s and the 2N3904 pair (about 25 mA, 0.15 W in the regulator). VBIAS = 4.5 V from R101 / R102 10k, C106 47u, buffered by U102A. PWR_FLAGs on +15VA, -15VA, AGND.

## 8. Bench trims (Bourns 3314J top-adjust SMD; 6 fitted, 2 DNP)

| Trim | Sets | Procedure |
| --- | --- | --- |
| RV401 / RV501 (50k) | J201 drain voltage | 4.9 V DC at Q401 / Q501 drain, no signal |
| RV1101 | Opto depth | 1 kHz at -6 dBFS (2.2 Vpk at P1): 7 dB gain reduction in Opto mode |
| RV1201 / RV1221 | FET Q bias | -18 dBFS in: turn from full negative until gain just starts to drop, then back off slightly. Match L and R |
| RV1301 / RV1321 | THAT2180 symmetry | DNP with 2180A. If fitted (2181): 1 kHz 0 dBFS, minimise 2nd harmonic |
| RV1342 | VCA threshold | 1 kHz at -18 dBFS in (0.55 Vpk at P1): turn until VCA_EC just starts rising from 0 V |

## 9. Known deviations from the plugin (accepted for Rev B)

1. **Filter Q**: the LPF is Q 0.74, not 0.707 (E-series capacitor ratio 15n / 6.8n). Cutoff ranges are narrower than the plugin's (HPF 23 Hz to 2.3 kHz, LPF 156 Hz to 15.8 kHz) and depend on the gangs tracking; the fixed 1k floors set the top of each range.
2. **Opto**: the plugin's electrical dual-slope release is left to the vactrol's physics; the LED law is set by RV1101 rather than solved. GR starts a little above threshold (LED forward voltage) rather than exactly at it.
3. **FET**: ratio is set by the FET law plus the pad, not a fixed 4:1; the 1176's "all buttons" grit comes free. Per-channel Q bias trims replace the plugin's perfectly matched channels.
4. **VCA**: hard knee (no 12 dB over-easy); log-average detector instead of true RMS; single 10 ms detector constant instead of 10 ms RMS / 120 ms release. THAT2180A itself is end-of-life (Mouser stock 1226 on 2026-09-13): order VCAs for every board you ever intend to build with the first batch, or plan a Rev C around a Cool Audio V2181 / Alfa AS2181 clone.
5. **Tube Screamer**: C803 51p (TS808 stock) is present; it is inaudible but not in the plugin model.
6. Source bypass, base-filter and rail caps are electrolytic or X7R (not in the direct audio path). All series audio caps are PPS or MKS film.

## 10. Independent review (2026-09-13)

An adversarial review of the netlist against the THAT datasheets found two blockers (THAT2180 pin 5 hard-wired to -15VA; pedal-mode make-ups 20 dB low because the pad was counted twice) and several should-fixes (Ec- source impedance, 2252 IBIAS at spec max and bypassed to the wrong rail, FET bias trim range, J201 trim range, difference-amp reference impedance, HPF_OUT loading). All are fixed in the netlist above. ERC re-run: 0 / 0.

## 11. Still open before ordering

- Optional: 100R + 1.5n snubber on VCA_EC per THAT app note if control-voltage feedthrough shows up.
- TL072H (TL072HIDR) is specified because it is rated down to 4.5 V total supply; classic TL072C is only characterised at +/-5 V and up.
- Confirm with one relay that TQ2 pin 4 is NO (footprint note from Rev A still applies).
- The four THT parts per channel (J201, film 1u caps, vactrol) are top-side THT; PCBWay assembles mixed SMD/THT as in Rev A.

## Layout (2026-09-13)

- Board: 190 x 170 mm, 2 layers, 4x M3 holes 4 mm from the corners, all parts on the top side. AGND pour on both sides, stitched on an 8 mm grid; the bottom side is kept mostly plane.
- Placement follows the schematic blocks left to right, top to bottom: connectors along the top edge (P3 power, P1 in, P2 out, P4 / P5 control), power (U101 / U102) and the two main-path channels below them, then Tube / Tape L and R, then Tube Screamer + Opto on the right, FET (left) and VCA (right) on the fourth row, and the seven mode relays K1..K7 with their flyback diodes along the bottom edge.
- Routing: Freerouting 1.9 for the signal nets with AGND as a bottom plane, then the last AGND pour island (C205) was cleared by re-routing +15VA and LPF_L1_W on the top side. Track 0.2 mm, clearance 0.2 mm, vias 0.6 / 0.3 mm (0.8 / 0.4 mm on the hand-routed runs).
- DRC (KiCad 10.0.5, all severities, schematic parity on): 0 errors, 0 unconnected items. Remaining warnings are cosmetic only: reference silkscreen touching pads (78) and library-link notices from the batch tool. ERC 0 / 0.
- Fabrication package: `hardware/kicad/fab-RevB/circuit-board/` (Gerber X2 + Excellon drill + drill maps, centroid CSV, BOM CSV, top assembly PDF, schematic PDF, renders, DRC report) and `PCBWAY-ORDER-SPECS-RevB-circuit-board.md`.
