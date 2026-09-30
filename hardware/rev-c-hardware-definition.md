# GAS Rev C Hardware Definition (2026-09-15, PCBWay release)

> ## Status: this is the LIVE hardware spec
>
> Build, order and review from this file. `claude/rev-c-pcb-release-2026-09-16.md` in the project is a **historical record of the 2026-09-16 release only** and is out of date by design; where the two disagree, this file wins.
>
> The one standing exception is below: for jacks, panel wiring, the V2181 and the DNP list (sections 1, 4.1, 5, 6, 7), `rev-c-front-stack-and-io-modes.md` still wins over this file.
>
> **Board set is now seven:** `circuit-board`, `control-deck`, `filter-pot-riser`, `io-board`, `jack-board`, `power-board`, `tank-board`, each with its own package under `kicad\revc\fab\`.
>
> **2026-09-30 update:** the `circuit-board` main path was re-netted so the **HPF sits ahead of the Gain stage** (section 4.3), matching the plugin. Regenerated and re-verified: ERC 0 violations, Freerouting rc 0, 0 unrouted nets, DRC 0 unconnected pads and 0 schematic parity issues; fab package re-exported. Section 4.3 also now names the limiter part (U1303 / U1304 Coolaudio V2181) explicitly rather than saying THAT2180A. Pre-swap backup: `backups\revc-hpf-gain-swap-2026-09-30-064655\`.

> **2026-09-21 update:** the three push-pull pots became plain dual pots plus their own Tube / Dirt / Tape mini toggles (7 toggles in the row); all six dual pots are on the control deck; io P5 split into P5 (Wet/Dry) + P8 (switch lines) and circuit P5 into P5 (HPF) + P9 (Gain).
>
> **2026-09-17 update:** jacks moved to the new jack-board, panel parts to the new control-deck, auto line / instrument inputs, DRV135 outputs, footswitch trails bypass, THAT2180 -> Coolaudio V2181, HPF / LPF pots 100k -> 50k. See `rev-c-front-stack-and-io-modes.md`; where it disagrees with this file (sections 1, 4.1, 5, 6, 7 on jacks, panel wiring, THAT2180 and DNP), that file wins. Six boards now: io, circuit, tank, power, control-deck, jack-board.

**Illicit Apothecary, The Great American Spring, Rev C.** Hardware translation of the Rev C plugin as it stands today (the TUBE build that became Rev C): Vol pull = 6GY8 triode section after Vol and after Output, Gain pull = TS808 Dirt, FB Dyn = FET Comp / Off / VCA Limit, Output pull = Tape, Source = Mono > Stereo / Stereo / MEGAVERB, feedback injected before the tanks, In / Wet / Out meters plugin only.

**No vacuum tubes and no high voltage anywhere.** The two 6GY8 sections per channel are emulated with SMD parts (section 3). This replaces the earlier 2026-09-15 draft that used real 6GY8s on a 250 V supply (kept as `rev-c-hardware-definition-REAL-TUBES-superseded.md` for reference only).

Everything is sized for a **6 in PVC DWV pipe, 154 mm bore**, and generated from code so it can be regenerated after any change:

- Generator: `hardware/kicad/revc/gen/` (`core.py`, `gen_sch.py`, `pcb.py`, `route.py`, `build.py`, `boards/*.py`). Run `runb.ps1 -m <module>` (stages sch, pcb, route, pour, drc). **The `-m` argument is the python module name, so it takes underscores, not the board name's hyphens: `runb.ps1 -m circuit_board`, not `-m circuit-board`.** The hyphenated form fails with `ModuleNotFoundError`. Logs land in `gen\logs\<module>.log` and `.err`, named after the module too. Fab re-export is separate: `& 'C:\Program Files\KiCad\10.0\bin\python.exe' -u export_fab.py circuit-board` from the `gen` folder, and that one does take the **hyphenated** board name.
- KiCad projects: `hardware/kicad/revc/<board>/`. Fab packages: `hardware/kicad/revc/fab/<board>/`.
- Mechanical: `hardware/rev-c-tube-layout.*` (side view, sections, DXF) and `rev-c-endcap-fit-check.md` (cap face, unchanged).
- Tube emulation fit: `hardware/kicad/revc/sim/` (plugin TriodeStage port, ngspice fit and spread check).

## 1. Board set (Rev A / Rev B boards are all retired)

| Board | Size (mm) | Replaces | Job |
| --- | --- | --- | --- |
| `io-board` | 136 x 180 | Rev A io-board | 4 x Neutrik NCJ6FI-H through the cap, balanced receive, Mono > Stereo relay, dry tap, Vol + tube 1, Wet/Dry, Output + tube 2 + Tape, balanced out |
| `circuit-board` | 120 x 175 | Rev B circuit-board + Rev A crossfade/feedback/wet | Ext Mix, HPF + Gain, Dirt relay (TS808), FET Comp, VCA Limit, LPF, Feedback amount, FB phase, MEGAVERB swap |
| `tank-board` | 120 x 150 | Rev A tank-driver-recovery + ext-tank-routing | wet + feedback sum, 4 drivers, 4 recovery amps, 8 RCA, Off / Series (+6 dB) / Parallel |
| `power-board` | 120 x 62 | Rev A power-backplane | DC entry, TRACO TEL 12-2423 isolated +/-15 V, RECOM R-78HB +5VAUX, 4 VH-4 outputs |

Why four instead of six: Crossfade is gone from the plugin, the Ext routing logic lives next to the tank drivers it switches, and the feedback path belongs right after the LPF where the plugin taps it. It cuts the audio harnesses from 10 to 4.

### 1.1 Rev A problems fixed on the way (found while porting)

1. **Feedback was injected after the main tanks** (ext-routing U201A summed FB_RET with PRI_RET). The plugin adds the feedback to the wet input *before* the tanks. Rev C sums WET_SEND + FB_RET on the tank board and drives both the main tank and, in Parallel, the 2nd tank from that sum.
2. **Feedback amount pot was not actually in circuit** (crossfade board: the wiper summed into a node that also got the full signal; no amount control on the non-inverted path). Rev C: pot HI = wet output, LO = AGND, wiper buffered, then phase relay and MEGAVERB relay.
3. **Series inter-tank +6 dB was never implemented** (R241-243 left as DNP reservations). Rev C: x2 non-inverting stage on the main tank return, selected by the Series/Parallel relay.
4. **Rev A wet/dry buffer loaded the pot wiper with a 20k virtual earth**, bending the blend law. Rev C buffers the wiper with a follower (linear crossfade exactly like the plugin).
5. **Mono switch on a 3-position toggle would float the right input in the centre position** (Rev A P6 was a bare switch landing). Rev C uses relay K1 with a pull-down.
6. **Input bulk capacitor was 25 V on a 30 V rail** (power backplane C500). Rev C: 100 uF 50 V.
7. **Mornsun URA/URB2415 pinout was never verified.** Rev C uses TRACO TEL 12-2423 with the KiCad library footprint (pins 1 -Vin, 16 +Vin, 9 +Vout, 8 Com, 10 -Vout).
8. **Balanced output was 6 dB hotter than the input** (follower + unity inverter on a unity receiver). Rev C drives each leg at x0.5, so balanced in to balanced out is unity at 0 dB.
9. Obsolete / out of stock parts replaced: 2N5457 TO-92 (obsolete) -> **MMBF5457** SOT-23; TQ2-5V THT relay (0 stock) -> **Omron G6K-2F-Y DC5** SMD (21 mA coil, KiCad footprint); BD139/BD140 TO-126 -> **BCP56-16 / BCP53-16** SOT-223.

## 2. Level plan

- Between boards: **0 dBFS = 4.36 Vpk** (+12 dBu). Rails +/-15 V clip at about +9.8 dBFS.
- Circuit board bus after the HPF: 0 dBFS = 6.93 Vpk (HPF gain 1.59), divided back by 1.59 before WET out.
- Pedal-level stages (TS808, Tape): 0.1 Vpk per full scale, 9 V rail biased at 4.5 V (L78L09 + TL072H buffer), as Rev B.
- Tube emulation grid: 0 dBFS = 0.137 Vpk.
- Dynamics threshold -18 dBFS = 0.87 Vpk on the circuit-board bus, as Rev B.
- Every level knob is the same +/-18 dB inverting pot stage: 1.43k + 10k linear gang + 1.43k gives -18.0 / 0 / +18.0 dB, symmetric in dB (plugin range exactly).

## 3. 6GY8 section emulation (io-board, 4 stages: tube 1 L/R after Vol, tube 2 L/R after Output)

What the plugin does: one 6GY8 section as a common-cathode stage (B+ 250 V, Rp 47k, Rk 470R bypassed, 68k grid stopper, 22 nF coupling cap, 1M grid leak, grid diode that charges the coupling cap = blocking distortion, tau 22 ms). The pot ahead of it sets how hard the grid is driven; at 0 dB a 0 dBFS peak just reaches grid conduction; output normalised to unity clean.

The hardware stage, per section:

```
pot stage out (inverted, 4.36 Vpk/FS)
  -> 30.9k / 1.00k pad (0.137 Vpk/FS)
  -> 22 nF C0G (Cc) -> 68k (grid stopper) -> GATE ----+---- 1M ----.
                                                     +-|>|- BAT54 -+-- BIAS (servo output)
                                                     +-- 10 pF to AGND
  MMBF5457: drain 47k to +15VA, source 2.2k to AGND (unbypassed)
  servo: OPA1679 integrator, 470k from source, 1 uF to BIAS, + input = TUBE_REF 123 mV (100k / 825R from +15VA)
         -> holds Id = 56 uA whatever the JFET's Vp and Idss are
  drain -> 1 uF film -> 1M -> OPA1679 non-inverting make-up 1 + (18k + 20k trim) / 10k  (x2.8 .. x4.8, nominal x3.6)
  -> unity clean, non-inverted, to the tube relay
```

Why this topology:

- **Square law instead of a diode curve.** A JFET's drain current is a square law of its gate voltage, which is the even-harmonic curvature a triode has. The unbypassed 2.2k source resistor plays the part of the triode's internal plate feedback (it flattens the small-signal curve).
- **Grid conduction and blocking are copied, not faked.** The BAT54 conducts when the gate rises above its bias, the current flows through the 68k stopper and charges the 22 nF cap, and it bleeds off through the 1M: the same parts and the same 22 ms as the plugin.
- **No per-part bias trim.** JFET Vp spreads -0.5 to -6 V. The servo fixes the drain current, so the operating point depends only on the JFET's beta. ngspice check with the same circuit: Vp -0.7, -2 and -4.5 V give identical results; beta 0.45 to 1.2 mA/V2 moves the level +/-1.2 dB (the one trim) and the curve 1 to 2 dB.
- The clamp is referenced to the servo output, so it follows the bias for every JFET.

Measured in ngspice (1 kHz sine, steady state) against a sample-accurate Python port of the plugin's `TriodeStage` (plugin in brackets):

| Input | Level out | H2 | H3 |
| --- | --- | --- | --- |
| -18 dBFS | -18.0 (-18.0) | -67 (-80) | -69 (-70) |
| -12 | -12.0 (-12.0) | -61 (-62) | -57 (-55) |
| -6 | -6.1 (-6.2) | -55 (-42) | -45 (-41) |
| 0 | -0.4 (-0.7) | -44 (-43) | -35 (-32) |
| +6 | +4.6 (+3.9) | -27 (-29) | -26 (-24) |
| +12 | +6.3 (+5.8) | -11 (-13) | -20 (-19) |
| +18 | +6.4 (+5.7) | -6 (-7) | -30 (-44) |

Largest difference: about 12 dB less 2nd harmonic right at -6 dBFS, where the plugin's grid diode just switches on. Above 0 dBFS (where you hear the tube) level is within 0.7 dB and H2/H3 within 2 to 4 dB.

Bench: with Vol pulled and at 0 dB, send 1 kHz at -12 dBFS (1.1 Vpk) and set RV4001 / RV4101 (tube 1) and RV7001 / RV7101 (tube 2) so the level matches Vol pushed in. Check 123 mV at each JFET source (TP by R4005 etc.).

## 4. Signal flow per board

### 4.1 io-board

1. Jacks J1/J2 -> 100R + 220 pF (DNP) -> OPA1644 unity differential receiver (10k 0.1 %).
2. K1 (Source toggle, Mono throw): right program = left input. Followers give L_PROG / R_PROG = **dry tap**.
3. Vol pot stage -> clean inverter (20k/20k) and tube 1 -> K2 (Vol pull) -> 100R -> WET_SEND (to tank board).
4. WET (from circuit board) and dry -> Wet/Dry pot (HI dry, LO wet) -> follower = linear crossfade.
5. Output pot stage -> clean inverter and tube 2 -> K3 (Vol pull) -> Tape (pad 47k/1.1k, Rev B record EQ, MMBT3904 pair, repro EQ, make-up x1.255) -> K4 (Output pull) -> balanced driver (OPA1656: 10k/10k pad + follower on hot, x-0.5 inverter on cold, 49.9R) -> J3/J4. Unity from balanced in to balanced out.

Polarity: every path into a relay is non-inverted, so pulling a knob never flips phase.

### 4.2 tank-board

- U5A/C: SUM = -(WET_SEND + FB_RET), unity.
- Main tanks (4AB1C1B, 8 R input): Rev A driver (OPA1656 + BCP56/BCP53 follower inside the loop, 2 x 1N4148W bias, 10R 1 W emitters, 47R 1206 to the RCA). Recovery x48, 2.2k across the coil, 220 pF, 10 uF out + 100k.
- U5B/D: SER = 2 x main return (+6 dB, Series only).
- K1 (Ext B = Parallel): 2nd tank source = SUM (Parallel) or SER (Series).
- K2 (Ext A = engage): 2nd tank drivers get the source or AGND. K3 (Ext A): 2nd tank returns to the circuit board or AGND (Off = silent).
- 2nd tanks (9EB2C1B L, 9EB3C1B R): same driver / recovery.

### 4.3 circuit-board

- Ext Mix: TANK_MIX = -(PRI_RET + wiper), 100k / 100k / 100k (wiper loading under 2.5 %); pot HI = 2nd tank return, LO = AGND: primary always full, 2nd tank 0 to 100 % added (plugin law, Series and Parallel).
- HPF (Sallen-Key, K 1.59, Q 0.71, 4-gang 100k) -> Gain pot stage (+/-18 dB). **Order corrected 2026-09-30: the HPF sits AHEAD of the Gain stage, as in the plugin (`RevCStages.h`: pre-HPF -> Gain -> [Tube Screamer] -> [Comp | Off | Limit] -> post-LPF).** This doc previously had Gain first. Both stages are linear so the order changes neither the response nor the level, but it matters for what follows: with the HPF first, subsonic energy is removed before the Gain stage rather than being amplified into the TS808 clipper, which is also what a real Tube Screamer does with its own input high-pass. Springs throw off a lot of low-frequency junk, so this is not academic.

  > **Board swapped to match, 2026-09-30.** Up to this date the generated netlist really was Gain then HPF, and the schematic annotation saying so was correct; it was the generator's own module docstring and board title that had been claiming HPF first. `gen/boards/circuit_board.py` has now been re-netted so the board matches the plugin:
  >
  > | Net | Now carries |
  > | --- | --- |
  > | `TANK_MIX_{ch}` | Ext Mix sum output into the HPF input caps C{n}02 / C{n}12 |
  > | `HPF_OUT_{ch}` | HPF output into the Gain pot stage input R{n}01, and the pot HI end at P5 (unchanged) |
  > | `GAIN_OUT_{ch}` | Gain stage output into the 47k TS808 pad R{n}15 and the K1 Dirt relay |
  >
  > The OPA1679 units were reordered with it so they follow the signal (1 Ext Mix, 2 HPF, 3 Gain, 4 LPF) instead of doubling back across the quad. Net **names** keep their old meaning, so the filter-pot riser and P5 are untouched. Inversion count is unchanged (the HPF is non-inverting, the pot stage inverting, either order), so loop polarity and the FB Phase convention still hold.
  >
  > Verified after regenerating: **ERC 0 violations, Freerouting rc 0, 0 unrouted nets, DRC 0 unconnected pads and 0 schematic parity issues.** The 14 remaining DRC entries are the pre-existing silkscreen-overlap warnings. Fab package re-exported to `kicad/revc/fab/circuit-board/`. Backup of the pre-swap generator, project and fab package: `backups/revc-hpf-gain-swap-2026-09-30-064655/`.
- K1 Dirt (Gain pull): DYN_IN = **GAIN_OUT** or TS808 (pad 47k/680R off GAIN_OUT, TL072H Rf 51k / Rg 4.7k, 1N4148W pair, make-up x6.9). Was HPF_OUT before the 2026-09-30 stage swap.
- Comp: MMBF5457 FET compressor (screen for |Vgs(off)| under 5 V: the trim reaches -5.1 V) fed from DYN_IN, sidechain summer **x4** (20k inputs, 40.2k feedback, the Rev C plugin change), BAT/1N5819HW peak detector 150 us / 220 ms, RV1201 / RV1221 threshold trims.
- Limit: **U1303 / U1304 Coolaudio V2181** (SIP-8, THAT 2181 pinout: 1 IN, 2 EC+, 3 EC-, 4 SYM, 5 V-, 6 GND, 7 V+, 8 OUT; alternates THAT 2181BL08-U, Alfa AS2181) + discrete log-average detector, 10:1, RV1342 threshold, fed from DYN_IN. Same 6.1 mV/dB control law as the Rev B THAT2180A, so no maths changes, but RV1301 / RV1321 50k symmetry trims are **fitted** for the 2181 (they were DNP with the factory-trimmed 2180A). Corrected 2026-09-30: this line previously said THAT2180A.
- K2 (Comp) and K3 (Limit) select BUS = DYN_IN / FET_OUT / VCA_OUT; toggle centre = Off.
- LPF (Sallen-Key unity, Q 0.74) -> inverting x-1/1.59 (15.8k / 10k) -> 100R -> WET (to io-board). This inversion makes the loop an even number of inversions, so WET is in phase with the dry signal and FB Phase normal adds, as in the plugin (assuming the tanks themselves are non-inverting: check with a pulse on the bench and flip FB Phase if not).
- Feedback: pot HI = wet out, wiper follower (amount 0..1 linear) -> K4 FB Phase (normal / inverted) -> K5 MEGAVERB (L and R crossed) -> 100R -> FB_RET (to tank board).

### 4.4 power-board

P1 (VH-2) from the panel DC jack -> MF-SM100/33 polyfuse -> SS34 series diode -> SMAJ33A + 100 uF 50 V + 4.7 uF -> TEL 12-2423 (18-36 V in, +/-15 V 400 mA) -> 10 uF + BLM21PG221 ferrite + 220 uF + 100 nF per rail -> +15VA / -15VA. R-78HB5.0-0.5 (9-72 V in) makes +5VAUX straight from the protected adapter input, so the relay coils do not load the 400 mA +/-15 V converter. R1 0R links input ground to AGND at one point. P2..P5 VH-4 (1 +15VA, 2 AGND, 3 -15VA, 4 +5VAUX) to io, circuit, tank, spare.

**Adapter:** regulated 24 V to 30 V, 1 A (24 W class), centre positive, 5.5 x 2.5 mm. Estimated draw: +/-15 V at about 0.3 A and 0.2 A peak (tank drive), +5VAUX up to 0.2 A with every relay on: about 11 W at the wall. The old 30 V / 0.5 A (15 W) adapter works if it is regulated; unregulated wall warts can exceed the TEL 12's 36 V limit at light load. With +5VAUX on its own converter the +/-15 V rails carry about 0.2 A plus tank drive, inside the TEL 12's 400 mA.

## 5. Connectors and harnesses

| Harness | From | To | Type | Pins |
| --- | --- | --- | --- | --- |
| H1 | panel DC jack J5 (Switchcraft L712A) | power P1 | VH-2, 20 AWG | 1 centre (+), 2 sleeve |
| H2 / H3 / H4 | power P2 / P3 / P4 | io P1 / circuit P4 / tank P4 | VH-4, 22 AWG | +15VA, AGND, -15VA, +5VAUX |
| H5 | io P2 WET-SEND | tank P1 | XH-3, twisted | L, AGND, R |
| H6 | circuit P2 WET | io P3 | XH-3, twisted | L, AGND, R |
| H7 | tank P3 TANK-RET | circuit P1 | XH-6, twisted pairs | PRI L, AGND, PRI R, SEC L, AGND, SEC R |
| H8 | circuit P3 FB-RET | tank P2 | XH-3, twisted | L, AGND, R |
| T1..T8 | tank J1..J8 (RCA) | tanks | shielded RCA | main L send/return, main R, 2nd L, 2nd R |

Panel:

| Control | Part | Wires to |
| --- | --- | --- |
| Vol, pull = Tube | Alpha 16 mm dual 10k lin push-pull DPDT | gangs io P4 1-6; switch: common io P5-10 (+5VAUX), NO io P5-8 (CTL_TUBE) |
| Output, pull = Tape | same | gangs io P4 7-12; switch NO io P5-9 (CTL_TAPE) |
| Gain, pull = Dirt | same | gangs circuit P5 1-6; switch: common circuit P6-14, NO circuit P6-9 (CTL_DIRT) |
| HPF | Bourns PTD904-2015K-B104 4-gang 100k lin | circuit P5 7-14 (rheostats: HI + wiper, LO tied to wiper) |
| LPF | same | circuit P6 1-8 |
| Wet/Dry | 16 mm dual 10k lin | io P5 1-6 (HI dry / wiper / LO wet) |
| Ext Mix | 16 mm dual 10k lin | circuit P7 1-6 (HI / wiper / AGND) |
| Feedback | 16 mm dual 10k lin | circuit P7 7-12 |
| S1 Source | NKK M2022 SPDT ON-OFF-ON | common +5VAUX; up = Mono > Stereo -> io P5-7; centre = Stereo; down = MEGAVERB -> circuit P6-12 |
| S2 Ext tanks | NKK M2023 DPDT ON-OFF-ON | pole 1: common +5VAUX, both throws -> tank P5-1 (A); pole 2: common +5VAUX, down throw -> tank P5-2 (B). Up = Series, centre = Off, down = Parallel. +5VAUX from tank P5-3 |
| S3 FB Dyn | NKK M2022 | up = Comp -> circuit P6-10, down = Limit -> circuit P6-11 |
| S4 FB Phase | NKK M2012 SPDT ON-ON | one throw -> circuit P6-13 (inverted), other throw unused |

Every relay control line has a 10k pull-down on its board, so an unplugged or centred switch is a defined Off. G6K coil 21 mA; worst case all relays on (11) is about 230 mA on +5VAUX (R-78HB is 500 mA).

## 6. PCBWay specification (all four boards)

| Parameter | Value |
| --- | --- |
| Layers / material | 2 layers, FR-4 TG150, 1.6 mm, 1 oz |
| Finish / colours | HASL lead-free, green mask, white silk |
| Min track / space / via | 0.20 / 0.20 mm, 0.6 / 0.3 mm via |
| Assembly | turnkey, top side only, mixed SMD + THT |
| THT parts | NCJ6FI-H x4 (io), WIMA MKS2 1 uF film caps, RCJ-041 RCA x8 (tank), TEL 12-2423 and R-78HB (power), Coolaudio V2181 SIP-8 (circuit), JST XH / VH headers |
| DNP | io C1-C4 (RF caps), circuit RV1301 / RV1321 / R1305 / R1325 (2180A symmetry) |
| Watch list | **V2181 is the chosen limiter VCA** (U1303 / U1304) and is not at Mouser, DigiKey or LCSC: hobby distributors or consign to PCBWay. The THAT2180AL08-U it replaced is end of life. OPA1679IDR stock is low at Mouser (115 on 2026-09-15), allow alternate distributors; G6K-2F-Y DC5 no substitutes (footprint); MMBF5457 for the FET compressor: prefer |Vgs(off)| under 5 V |

## 7. Bench trims (all SMD Bourns 3314J)

| Board | Trim | Set |
| --- | --- | --- |
| io | RV4001, RV4101, RV7001, RV7101 (20k) | tube level = clean level at -12 dBFS, Vol at 0 dB, per tube |
| circuit | RV1201, RV1221 (10k) | FET comp threshold: gain just starts to drop at -18 dBFS |
| circuit | RV1342 (10k) | VCA threshold: VCA_EC starts rising at -18 dBFS |
| circuit | RV1301, RV1321 (50k) | V2181 symmetry: minimum THD at 1 kHz, 0 dB VCA gain (2026-09-17) |

Known behaviour: the JFET servos take about 2 s to settle after power-on. If Vol is already pulled at power-up you get a low thump through the tube path during that time; power up with Vol pushed in (or let it settle before playing).

## 8. Independent netlist review (2026-09-15)

A second reviewer built every board from the generator and checked pin maps, bias paths, loop signs, relays and levels. Fixed before layout: tank driver bias diodes were reversed (would have shorted the output transistors rail to rail at power-on); balanced out +6 dB; odd number of inversions in the wet loop; Ext Mix wiper loading; +5VAUX moved off +15VA; TVS symbol. Confirmed correct: tube stage servo sign and clamp orientation, all relay NC/NO and coil/flyback wiring, pot stage +/-18.06 dB, HPF K 1.59 / Q 0.709, LPF Q 0.743, TS808 and tape unity make-ups, FET x11, series x2, VCA limiter detector and clamp, MEGAVERB cross, power protection order and converter pinouts.
