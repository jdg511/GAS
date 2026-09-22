# GAS Rev C Hardware Definition (2026-09-15)

**Illicit Apothecary, The Great American Spring, Rev C.** This is the hardware translation of the plugin as it stands on 2026-09-15: the Rev C signal flow (Vol, tanks, HPF > Gain/Dirt > Comp/Off/Limit > LPF, feedback with MEGAVERB, Wet/Dry, Output) with the TUBE revision folded in: **real 6GY8 triodes** at the Vol and Output positions, a **2N5457 FET compressor** as Comp and the **THAT2180 VCA limiter** as Limit. The In / Wet / Out L+R meters stay plugin only.

Two boards go to PCBWay for Rev C. Everything else in the Rev A board set is reused **electrically**; see section 1.3 for the mechanical catch.

| Board | Status | Size (max) | What it does |
| --- | --- | --- | --- |
| `circuit-board` Rev C | respin of the Rev B circuit board | 125 x 170 mm | HPF, Gain pot stage, Dirt (TS808) relay, FET compressor, VCA limiter, LPF, MEGAVERB feedback swap relay |
| `tube-io-board` Rev C | **new** | 125 x 170 mm | Vol pot stage + 6GY8 input triodes, Output pot stage + 6GY8 output triodes, Tape stage, their bypass relays, 250 V B+ supply, 6.3 V heater supply |

Reference documents: `rev-b-circuit-board-definition.md` (level plan, filters, TS808, FET, VCA, connectors, Rev B layout), `rev-c-plugin-2026-09-15.md` (signal flow, Rev C hardware notes), the TUBE experiment `README.md` / `ARCHITECTURE.md` (6GY8 stage design and the FET compressor as modelled), GE 6GY8 datasheet ET-T1607.

## 1. What changed and why

### 1.1 Plugin to hardware map

| Plugin (Rev C + TUBE, 2026-09-15) | Hardware |
| --- | --- |
| Vol -18..+18 dB, pull = Tube (6GY8 section 1 after Vol, section 2 after Output) | Vol push-pull pot. The switch half drives relays K1 (tube in) and K2 (tube out) together. Two 6GY8 tubes, one per channel, two sections used per tube |
| Gain -18..+18 dB, pull = Dirt (TS808) | Gain push-pull pot, switch drives K3 (Dirt) on the circuit board |
| Output -18..+18 dB, pull = Tape (2N3904 pair), runs after the output triode | Output push-pull pot, switch drives K4 (Tape) on the tube-io board |
| FB Dyn: Comp (2N5457 FET) / Off / Limit (THAT2180) | ON-OFF-ON toggle driving K5 (Comp) or K6 (Limit) on the circuit board |
| Source: Stereo / Mono > Stereo / MEGAVERB | ON-OFF-ON toggle: one side = the existing mono-sum relay line, centre = Stereo, other side = K7 (MEGAVERB) which swaps the L and R feedback returns |
| HPF before Gain/Dirt, LPF after Comp/Off/Limit, fixed Q | unchanged from Rev B (4-gang 100k pots) |
| Ext Tanks Off / Series / Parallel, Ext Mix, Feedback, FB Phase, Wet/Dry | unchanged (Rev A ext-routing and crossfade/feedback/wet boards) |
| Pre Input, Post Output, predelay, In/Wet/Out meters | plugin only, nothing on the PCB |
| 7-position Mode rotary, Clean/Tube/Tape/Opto modes, crossfade pot | **gone** (Tube and Tape moved to the tube-io board as real stages, Opto dropped) |

### 1.2 Where the new stages sit in the existing harness

The Rev A harness already has the right cut points, so no Rev A board is re-spun for the signal path:

- **H2 `JIO-WETSEND`** (I/O board P2 to ext-routing P201) is the wet path right after the dry/wet split and before the feedback return is summed in. The tube-io board is inserted here: P2 -> tube-io `P1 IN-WETSEND` -> [Vol pot stage -> K1: clean or 6GY8 section A] -> tube-io `P2 OUT-WETSEND` -> ext-routing P201. This is exactly the plugin's `Vol -> tube -> [IN meter] -> + feedback return`.
- **H4 `JIO-WETRET`** (crossfade P304 to I/O board P3) is the wet signal after the Wet/Dry mix point on the I/O board side. The tube-io board is inserted here too: P304 -> tube-io `P3 IN-WETRET` -> [Output pot stage -> K2: clean or 6GY8 section B -> K4: clean or Tape] -> tube-io `P4 OUT-WETRET` -> I/O P3.
- **H10 `JFB-INJ`** (crossfade P305 to ext-routing P205) carries the feedback returns FB_RET_L/R. The Rev C circuit board gets a pass-through pair `P6 FB-IN` / `P7 FB-OUT` with relay K7 in between: de-energised straight through, energised L and R swapped. That is the plugin's MEGAVERB (L path out feeds R path in and vice versa) and it leaves the direct wet return untouched, which is what the plugin does.
- **H8 / H9** (crossfade P302 -> circuit board P1, circuit board P2 -> crossfade P303) are unchanged.

Note on the plugin: in the plugin the Output knob and its tube/tape run after the Wet/Dry mix, i.e. on the mixed signal. In the hardware the Wet/Dry mix lives on the I/O board, so the Output stage is on the wet return just before the mix. The dry path therefore does not pass through the output triode. If you want the plugin's behaviour exactly (dry also through the tube and tape), the Output section has to move onto a re-spun I/O board; for Rev C it stays on the wet return.

### 1.3 The 6 inch pipe changes the board sizes (read this before ordering)

The Rev A boards were laid out for an 8 to 9 in tube: I/O 160 x 75, power backplane 150 x 95, ext-routing 120 x 80, crossfade 100 x 70, tank driver 170 x 110, and the Rev B circuit board is 190 x 170 mm. A 6 in Sch 40 / DWV pipe has a 154 mm bore (6.065 in). **A 160, 170 or 190 mm board cannot go into a 154 mm bore in any orientation.** The two Rev C boards below are limited to **125 mm wide** (a 125 mm chord sits 45 mm off the bore centre line; on the centre line there is 14 mm of wall clearance each side and 20 mm tall parts near the edge still clear). If the enclosure really is 6 in, the I/O board, the power backplane and the tank driver board need a narrower respin as well (same schematics, new outlines: 125 x 100, 125 x 115, 125 x 150). Ext-routing (120 wide) and crossfade (100 wide) fit as they are. This is the one thing that stops "Rev C is going to PCBWay now" from being just two boards.

## 2. Level plan (unchanged, with the tube additions)

- 0 dBFS = **4.36 Vpk** at every board input and output (+12 dBu rms sine). Rails +/-15 V clip at about 13.5 Vpk = +9.8 dBFS, which is the hardware version of the plugin's +12 dBFS sanitize clamp.
- Circuit board internals as Rev B: HPF gain 1.59, bus 6.93 Vpk per full scale, pedal-level stages (TS808, Tape) see 0.1 Vpk per full scale through the -36.8 dB pad on a +9 V rail, dynamics threshold -18 dBFS = 0.87 Vpk on the bus.
- **Tube stages**: at Vol = 0 dB, 0 dBFS must swing the grid exactly to the conduction threshold, i.e. a peak equal to the bias, 1.32 V (the plugin's unity-clean reference). So the grid pad is 1.32 / 4.36 = **0.303**. The stage gain is 39.7 and the plate swing at 0 dBFS is 52.4 Vpk; the output divider is **0.0833** (52.4 -> 4.36 Vpk). Both stages are then unity below the knee and clean to 0 dBFS, exactly as the plugin.

## 3. `tube-io-board` Rev C

### 3.1 Signal path

```
P1 WETSEND in (L,R) -> U1A/B Vol pot stage (+/-18 dB, inverting, 1.5k ends, 10k lin dual)
   -> pad 10k / 4.32k (0.302) -> 68k -> 22n -> 6GY8 section A grid (cathode bias 470R || 22u)
   -> plate 47k from B+ -> 100n 400V -> 220k / 20k divider (0.0833) -> U1C/D buffer (inverts back)
   -> K1 (NC = Vol stage output straight, NO = tube output) -> 100R -> P2 WETSEND out

P3 WETRET in (L,R) -> U2A/B Output pot stage (+/-18 dB)
   -> same pad / stopper / cap -> 6GY8 section B grid (fixed bias, see 3.3) -> plate 47k -> 100n -> divider -> U2C/D buffer
   -> K2 (NC = Output stage straight, NO = tube) 
   -> Tape: -36.8 dB pad -> record EQ U3A/B (TL072H, +9V) -> 2N3904 pair -> repro EQ -> U4A/B make-up x1.67 (Rev B refs 6xx/7xx, unchanged)
   -> K4 (NC = straight, NO = tape) -> 100R -> P4 WETRET out
```

Polarity: the pot stages invert (same stage as Rev B Drive). The triode inverts again, so the tube path uses a **non-inverting** buffer after the 220k/20k divider and is net non-inverting; the clean path goes through an **inverting** unity buffer (20k/20k) off the pot stage so it is net non-inverting too (the plugin flips the triode's polarity in code; here the buffer choice does it). Both paths land on the relay at the same polarity and level, so pulling Vol or Output never flips phase into the feedback loop. One OPA1679 per position covers pot stage L/R, tube buffer L/R; a second covers the two clean buffers and the Tape make-ups.

Relays: K1 and K2 are both driven by `CTL_TUBE` (the Vol pull), K4 by `CTL_TAPE` (the Output pull). Panasonic TQ2-5V DPDT, one pole L, one pole R, coils from +5VAUX via the pot switch, 1N4148W flyback, coil return AGND. Only the *output* of each stage is switched (the stage is always driven), same scheme as Rev B, so one DPDT relay covers both channels.

### 3.2 The 6GY8 and which sections to use

GE ET-T1607: high-mu triple triode, **noval E9-1 base, T-6 1/2 glass, 2 3/16 in (55.6 mm) max length, 7/8 in (22.2 mm) max diameter**, heater 6.3 V 0.45 A, 330 V max plate, 2 W per plate, 5 W all plates, 100 V heater-cathode. Sections 2 and 3: mu 63, gm 4.5 mA/V, rp 14k at 125 V / -1 V / 4.5 mA. Basing:

| Pin | Electrode |
| --- | --- |
| 1 | grid, section 3 |
| 2 | plate, section 3 |
| 3 | grid, section 2 |
| 4 | **cathode section 3 + grid section 1 + heater** (internally common) |
| 5 | heater |
| 6 | plate, section 1 |
| 7 | cathode, section 1 |
| 8 | cathode, section 2 |
| 9 | plate, section 2 |

The three sections are **not** independent: pin 4 is one heater end, section 3's cathode and section 1's grid at once. That fixes how the two stages per channel are wired:

- **Section 2** (pins 3, 8, 9) is fully independent. It is the **input (Vol) stage, "section A"**, cathode biased with Rk 470R || 22 uF exactly as modelled (Ip 2.8 mA, Vk 1.32 V, Vp 118 V).
- **Section 3** (grid 1, plate 2, cathode = pin 4) is the **output stage, "section B"**. Its cathode is the heater return, so pin 4 is tied to AGND, the heater runs on **DC** with pin 4 negative, and the stage uses **fixed bias**: the 1M grid leak returns to `VBIAS_B`, a trimmed -1.0 to -2.5 V node (RV1: 10k trimmer, 43k from -15VA, 10 uF to AGND, 100k into the trimmer wiper). Trim for 118 V at the plate (2.8 mA in 47k). Audio-wise a fixed-bias stage with a grounded cathode is the same as the fully bypassed cathode-bias stage in the model; the bias shift under grid current comes from the coupling cap and 1M leak, which are identical.
- **Section 1** is unused: pin 7 (cathode) and pin 6 (plate) both to AGND, so it sits with grid = cathode = plate = 0 V and draws nothing.
- Heater-cathode: section 2's cathode is at +1.3 V against a 0 to 6.3 V heater: fine (100 V rating).

Per section: Rp 47k, 0.37 W at rest (two 1206 thick-film 23.7k / 0.5 W in series, or one 2512 1 W, 200 V rated), plate decoupling 1k + 22 uF 400 V per stage from B+, output coupling 100 nF 400 V film (Panasonic ECQ-E4104KF or WIMA MKP4), grid stopper 68k, input coupling 22 nF 63 V film (WIMA MKS2), grid leak 1M. Dissipation per tube 0.66 W plate + 2.8 W heater.

Sockets: **Belton VT9-PT-2** (PCB-mount noval with centre shield spigot; 9 pins on a 11.9 mm circle, body 22 mm) or Belton VT9-PT (no spigot). Tubes stand 66 mm above the board with the socket. Keep the glass 25 mm from any cable and from the PVC wall, and drill a few vent holes in the pipe near the tube board: with the heaters the whole unit dissipates about 20 W inside a closed pipe.

### 3.3 Power on the tube-io board

- **+30 V raw** arrives on `P5 PWR-RAW` (JST VH 2-pin) straight from the DC jack through a Y in the harness (new harness H15; the power backplane is not modified). Own protection: SS34, MF-R100 polyfuse, SMAJ33A, 100 uF 50 V.
- **B+ 250 V**: LT3757EMSE boost in discontinuous mode. L 220 uH (Bourns SRR1260-221K, Isat 1.5 A), Q STD3NK50Z or IPD50R3K0CE (500 V, DPAK), D ES1J (600 V, SMA), Rsense 0.1 R, fsw 100 kHz (RT 100k), Cout 2 x 10 uF 400 V (Nichicon UCY2G100MPD), feedback 2 x 1M (0805, series) over 12.7k to FBX 1.6 V (253 V), bleeder 470k 1 W, 100 kHz ripple after the 1k / 22 uF per-stage RC is below 0.1 mV. Design numbers: Ipk 0.57 A, ton 4.2 us, demag 0.6 us, well inside DCM at 12 mA load (four sections at 2.8 mA plus bleeder). Input range 20 to 32 V, so the same board also runs from a 24 V adapter.
- **Heater 6.3 V, 0.9 A**: LMR33630ADDAR buck, L 33 uH (Coilcraft XAL6060-333, 2.9 A, handles the cold-heater surge), Cin 2 x 4.7 uF 50 V, Cout 2 x 22 uF 16 V + 100 uF, feedback 100k / 18.7k (6.35 V), then a ferrite bead + 220 uF so the 400 kHz ripple current does not run through pin 4. Heater return is a dedicated trace/pour from pin 4 of both sockets back to the buck ground, joined to the AGND plane only at the sockets.
- **+/-15VA** on `P6 PWR` (JST VH 3-pin) from a spare power-backplane VH position (or a Y from H12). Local L78L09 makes +9VC and VBIAS 4.5 V for the Tape stage, as on Rev B.
- **Adapter**: the Rev A 30 V / 0.5 A wall adapter is no longer enough (analog ~10 W + tubes 8.5 W + converter losses = about 21 W at the wall). Use a regulated **24 V, 2.5 A** desktop supply (Mean Well GST60A24-P1J, 5.5 x 2.5 mm barrel, centre positive) or any regulated 24 to 30 V, 1.5 A or more. The +/-15 V DC-DC on the backplane already accepts 18 to 36 V.

HV safety on the board: 250 V nets stay on the tube-io board only (no HV on any connector), 1.5 mm minimum clearance HV to anything (IPC-2221 external uncoated is 1.25 mm for 250 to 300 V), HV parts grouped in one corner with a silkscreen box and "250 V" text, bleeder fitted, no HV within 5 mm of the board edge or of a mounting hole. The bleeder discharges the 20 uF in about 45 s after power-off; wait before touching.

### 3.4 Connectors

| Ref | Name | Footprint | Pins |
| --- | --- | --- | --- |
| P1 | IN-WETSEND (from I/O P2, H2a) | JST XH 3 | 1 WET_SEND_L, 2 AGND, 3 WET_SEND_R |
| P2 | OUT-WETSEND (to ext-routing P201, H2b) | JST XH 3 | 1 WET_SEND_L', 2 AGND, 3 WET_SEND_R' |
| P3 | IN-WETRET (from crossfade P304, H4a) | JST XH 3 | 1 WET_SUM_L, 2 AGND, 3 WET_SUM_R |
| P4 | OUT-WETRET (to I/O P3, H4b) | JST XH 3 | 1 WET_SUM_L', 2 AGND, 3 WET_SUM_R' |
| P5 | PWR-RAW (H15, from DC jack Y) | JST VH 2 | 1 +30V_RAW, 2 AGND |
| P6 | PWR (+/-15) | JST VH 3 | 1 +15VA, 2 AGND, 3 -15VA |
| P7 | CTL (panel) | JST XH 12 | 1-3 VOL_L HI/W/LO, 4-6 VOL_R HI/W/LO, 7 CTL_TUBE (from Vol switch, +5VAUX when pulled), 8 CTL_TAPE (from Output switch), 9 AGND, 10-12 spare |
| P8 | CTL (panel) | JST XH 8 | 1-3 OUT_L HI/W/LO, 4-6 OUT_R HI/W/LO, 7-8 AGND |

### 3.5 Bench trims

| Trim | Sets | Procedure |
| --- | --- | --- |
| RV1 (L), RV2 (R) 10k | section B grid bias | no signal, B+ up: adjust for 118 V DC at pin 2 (plate) of each tube |
| none for section A | cathode bias | check 1.3 V at pin 8, 118 V at pin 9 |
| RV3 (L), RV4 (R) 5k | tube path unity | Vol pulled, Vol at 0 dB, 1 kHz at -12 dBFS (1.1 Vpk at P1): same level at P2 as with Vol pushed. Trims the 20k leg of the output divider for the real tube's gain |
| HV | B+ | 250 V +/- 5 % at the boost output, no trim (fixed divider) |

## 4. `circuit-board` Rev C

Start from the Rev B KiCad project (`hardware/kicad/circuit-board.*`, generated by `revb-gen/design.py`) and make these changes. Everything not listed stays exactly as `rev-b-circuit-board-definition.md`.

1. **Drive becomes Gain, +/-18 dB.** R201/R202 (and R301/R302) from 680R to **1.5k** with the 10k linear dual pot: gain (1.5k + 10k) / 1.5k = 7.67 = +17.7 dB each way, 0 dB at centre. Net names DRV_* to GAIN_* on P4.
2. **Remove modes 1, 2, 3, 5** and their relays: Clean relay K1 (clean is now the relay NC paths), Tube 4xx/5xx (U401A/U501A, RV401/RV501), Tape 6xx/7xx (moves to the tube-io board), Opto 11xx (U1101, VT1101/VT1121, RV1101). Remove K1..K7 and D1..D7.
3. **Keep** the pad R215/R216 (and R315/R316), Tube Screamer 8xx/9xx with its make-up U202C/U302C, FET compressor 12xx, VCA limiter 13xx, HPF, LPF, output buffer, power (U101 L78L09, U102 VBIAS). TL072H count drops to one (U402 for the TS808 L/R); OPA1679 count drops to six (U201, U301, U202, U302, U1201, U1301, U1302, U1305 = eight, minus nothing on the dynamics side: keep U202/U302 for the TS make-up and the FET/VCA buffers).
4. **New relay chain (three TQ2-5V + flybacks):**
   - K3 `DIRT`: NC = HPF_OUT_L/R, NO = TS_OUT_L/R (from U202C/U302C) -> `DYN_IN_L/R`. Coil from `CTL_DIRT` (Gain pull).
   - K5 `COMP`: NC = DYN_IN, NO = FET_OUT_L/R (U1201A/B outputs) -> `DYN_MID_L/R`. Coil from `CTL_COMP`.
   - K6 `LIMIT`: NC = DYN_MID, NO = VCA_OUT_L/R (U1301B/D) -> `BUS_L/R`. Coil from `CTL_LIMIT`.
   - The FET and VCA inputs are fed from `DYN_IN` (after the Dirt relay), so Dirt feeds the dynamics as in the plugin. R211/R311 100k bus pull-downs stay.
5. **FET compressor sidechain summer gain x4** (the one TUBE-revision change to the 12xx block): U1201C feedback R1243 from 10k to **40.2k** with R1241/R1242 10k. Everything else in 12xx as Rev B (22k/2.2k pad, 2N5457, 1M/1M, x11 make-up, 47k/100k control mix, RV1201/RV1221 Q-bias trims, BAT42W peak detector 1.5k/100n, 2.2M). Screen the 2N5457s for |Vgs(off)| under 5 V as before; InterFET is the TO-92 source.
6. **VCA limiter 13xx unchanged.** THAT2180A (2180AL08-U) is end of life: buy them for every board you intend to build with this order, or fit the Alfa AS2181 / Coolaudio V2181 (same SIP-8 pinout) and populate the symmetry trims RV1301/RV1321 + R1305/R1325 that are DNP for the 2180A.
7. **MEGAVERB relay K7** with pass-through P6/P7 (JST XH 3 each): P6 pins 1/3 -> K7 common L/R; NC -> P7 pins 1/3 straight; NO -> P7 pins 3/1 crossed. Coil from `CTL_MEGA`. 100R isolators are already on the crossfade board outputs, none needed here.
8. **Connectors**: P1, P2, P3, P4 as Rev B (P4 names DRV -> GAIN). P5: pins 1-8 LPF gangs as Rev B, 9 `CTL_DIRT`, 10 `CTL_COMP`, 11 `CTL_LIMIT`, 12 `CTL_MEGA`, 13-16 AGND (MODE1..7 are gone). New P6 `FB-IN`, P7 `FB-OUT`.
9. **Outline 125 x 170 mm** (see 1.3), 4 x M3 4 mm from the corners, all parts top side, 2 layers, AGND pours as Rev B.
10. Bench trims left: RV1201/RV1221 (FET Q bias), RV1342 (VCA threshold), RV1301/RV1321 only with a 2181.

Expected part count drops from 7 relays / 9 OPA1679 / 4 TL072 / 2 vactrols / 4 J201-2N5457 to 4 relays / 8 OPA1679 / 1 TL072 / 2 x 2N5457, which is why the board fits in 125 x 170.

## 5. Panel controls and switches (enclosure BOM, not on the PCBWay BOM)

| Ref | Function | Part | Panel hole | Behind panel | Wiring |
| --- | --- | --- | --- | --- | --- |
| VR1 | Vol, pull = Tube | Alpha 16 mm dual 10k linear with DPDT push-pull switch, M7 x 0.75 bushing, 6.35 mm shaft (Tayda / Amplified Parts "push-pull dual" family; single-gang version is R-VPP-10KL, order the **dual** gang) | 7.5 mm, counterbore | 18 x 18 body, ~35 mm deep | gangs to tube-io P7 1-6; switch pole 1: +5VAUX common, NO to CTL_TUBE |
| VR3 | Gain, pull = Dirt | same | 7.5 mm | same | gangs to circuit P4 1-6; switch NO to CTL_DIRT (P5-9) |
| VR5 | Output, pull = Tape | same | 7.5 mm | same | gangs to tube-io P8 1-6; switch NO to CTL_TAPE (P7-8) |
| VR2 | HPF | Bourns PTD904-2015K-B104, 4-gang 100k linear, M7 x 0.75, 6 mm shaft (Alps RK27114A 100kA quad is the audio-taper alternative but is 27 mm square and needs a 10 mm hole) | 7.5 mm | 9.5 x 11 body, 17.2 deep | circuit P4 7-14 |
| VR4 | LPF | same | 7.5 mm | same | circuit P5 1-8 |
| VR6 | Ext Mix | Alpha RD902F / Bourns PDB182 dual 10k lin (or whatever the Rev A ext-routing board expects), M7 | 7.5 mm | 9 to 16 mm body | ext-routing control header as Rev A |
| VR7 | Feedback | dual 20k lin (crossfade board R323/R324 network), M7 | 7.5 mm | | crossfade P307 7-8 as Rev A |
| VR8 | Wet/Dry | dual 10k lin, M7 | 7.5 mm | | I/O board as Rev A |
| S1 | Source: Mono>Stereo / Stereo / MEGAVERB | NKK M2023 (DPDT ON-OFF-ON), 1/4-40 bushing | 6.5 mm | 12.9 x 7.9 x 11.2 | pole 1 common +5VAUX: up -> existing mono-sum control line, down -> CTL_MEGA (circuit P5-12) |
| S2 | Ext Tanks: Series / Off / Parallel | NKK M2023 (DPDT ON-OFF-ON) | 6.5 mm | | replaces the Rev A ext-mode rotary. Ext-routing decode is A = engage, B = series/parallel (Off 00, Series 10, Parallel 11): pole 1 common +5VAUX with **both** throws tied to `CTL_EXT_MODE_A`; pole 2 common +5VAUX, down throw only to `CTL_EXT_MODE_B`. Centre = Off, up = Series, down = Parallel |
| S3 | FB Dyn: Comp / Off / Limit | NKK M2023 | 6.5 mm | | up -> CTL_COMP (P5-10), down -> CTL_LIMIT (P5-11) |
| S4 | FB Phase | NKK M2012 (SPDT ON-ON) | 6.5 mm | | CTL_FB_INV as Rev A |
| J1-J4 | In L/R, Out L/R | Neutrik NCJ6FI-H (combo XLR-F / TRS, horizontal PCB pins onto the I/O board or flying leads) | 24 mm + 2 x 3.2 mm | 25.4 mm + pins | as Rev A |
| J5 | DC in | Switchcraft L712A (5.5 / 2.5 mm, panel, 3/8-32 bushing, 5 A) | 10 mm, counterbore | 20.8 mm | Y harness to power backplane input and tube-io P5 |
| knobs | | 19 mm (Davies 1900H style, 1/4 in bore) on the three push-pull pots so there is something to grab; 16 mm (Davies 1510 style) on the other five (6 mm bore for the Bourns quads) | | | |

+5VAUX for the switch commons comes from the ext-routing board's control header as in Rev A / Rev B (the relays return to AGND on their own boards). Relay coil budget on +5VAUX: worst case K1 + K2 + K4 + K3 + K5 + K7 + ext-routing relays = about 200 mA at 28 mA each, inside the 250 mA allowance.

Fit of all of this on the 6 in cap face: see `rev-c-endcap-fit-check.md`. Short answer: yes, all 17 items fit with 5 mm or more between anything you touch and 5 mm of margin to the cap wall, but every pot, toggle and the DC jack needs a counterbore from the inside because the cap face is thicker than their bushings.

## 6. PCB specification for PCBWay (both boards)

| Parameter | Value |
| --- | --- |
| Size | circuit-board 125 x 170 mm; tube-io-board 125 x 170 mm; 4 x M3 at 4 mm from the corners |
| Layers | 2, 1 oz, AGND pour both sides |
| Material | FR-4 TG150, 1.6 mm |
| Finish | HASL lead-free, green mask, white silk both sides |
| Min trace / space | 0.20 / 0.20 mm; **tube-io HV nets 1.5 mm clearance, 0.5 mm track** |
| Via | 0.6 / 0.3 mm |
| Assembly | turnkey, mixed SMD + THT, top side only, qty 5, frameless stencil |
| THT on tube-io | 2 x Belton VT9-PT-2 sockets, 4 x 400 V electrolytics, 4 x 400 V film caps, 2 x 47k 2 W resistors (if THT chosen), 3 x TQ2 relays, 2 x 2N3904 TO-92, connectors |
| Consigned or watch-list | THAT2180A (EOL), 2N5457 InterFET, TQ2-5V (no substitute), 6GY8 tubes (NOS only: GE / RCA / Sylvania, about 5 to 12 USD each on eBay; buy four so you have a matched spare pair), Belton sockets |

## 7. Harness changes (Rev A/B to Rev C)

| Harness | Change |
| --- | --- |
| H2 | split: I/O P2 -> tube-io P1; tube-io P2 -> ext-routing P201 |
| H4 | split: crossfade P304 -> tube-io P3; tube-io P4 -> I/O P3 |
| H10 | split: crossfade P305 -> circuit P6; circuit P7 -> ext-routing P205 |
| H13 | circuit board power unchanged (P3) |
| H15 new | DC jack -> Y -> power backplane input and tube-io P5 (2-wire, 18 AWG, keep away from the tank harnesses) |
| H16 new | +/-15VA to tube-io P6 from a spare backplane VH or a Y on H12 |
| control | Rev B P4/P5 16-pin harnesses (Gain, HPF, LPF, CTL lines), new 12-pin and 8-pin to tube-io P7/P8, toggles S1-S4 to the ext-routing / circuit control lines, Mode rotary and clip lines gone |

## 8. Open items before the order

1. Decide the enclosure bore (6 in = 154 mm) or widen it; if 6 in, respin I/O, power and tank driver outlines to 125 mm (section 1.3).
2. (settled) S2 as an ON-OFF-ON toggle matches the ext-routing A/B decode, see section 5.
3. Run the Rev B `design.py` generator with the section 4 edits, then ERC / DRC, then the same adversarial netlist review as Rev B before Gerbers. Add the tube-io board as a second KiCad project in the same GAS_Parts library (new symbols: 6GY8, VT9 socket, LT3757, LMR33630).
4. Buy the 6GY8s first and measure Ip at 250 V / 47k / 470R on the bench: the fit was to 1960 GE curves and NOS tubes drift. RV3/RV4 absorb gain spread; the bias trims absorb Ip spread.
5. Tube heat: 8.5 W of tube inside PVC. Vent holes near the tube board, tubes 25 mm from the wall, and check the wall temperature after an hour on the bench before closing the pipe for good.
6. The 5703 is not used anywhere in Rev C.
