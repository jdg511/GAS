# GAS Rev C plugin (2026-09-15)

> ## STALE COPY. The live version of this doc is the project one.
>
> This file is the 2026-09-15 snapshot and has not tracked the plugin since. The live
> version is the GAS project doc **`claude/rev-c-plugin-2026-09-15.md`**, which carries
> the corrected compressor, the supplies table, the per-lane predelays and the current
> measurements. Read that one.
>
> The specific things this file got wrong, corrected inline below so nobody is misled
> by a stale line: the FB Dyn compressor is the **MMBF5457 FET compressor**, not a
> VTL5C3 vactrol; the limiter part is a **Coolaudio V2181**, not a THAT2180; and the
> Comp measurements below were taken from the vactrol model and do not describe the
> circuit that is on the board or in the plugin.

**Illicit Apothecary, The Great American Spring reverb Rev C.** Built and installed 2026-09-15: Standalone `The Great American Spring reverb Rev C.exe` and VST3 `The Great American Spring reverb Rev C.vst3` (in `C:\Program Files\Common Files\VST3\`). Only the name changed ("Rev C" appended); the plugin code `Gas1` and bundle ID are the same as before, so a DAW that already has the old build will see two entries with the same ID. Version 3.0.0.

Restore point for the Rev B plugin: `C:\Users\Jason\GAS-build\backups\pre-revc-2026-09-15\` (Source, CMakeLists.txt, prebuilt Standalone + VST3). The retired Rev B mode-circuit block is parked in `Source\DSP\_retired\`.

## Signal flow

```
host / playback
  -> Pre Input  (plugin only, -18..+18 dB)
  -> dry tap ----------------------------------------------------------------.
  -> Vol (Solid State / Tube), -18..+18 dB, PULL = J201 tube stage            |
  -> [IN meter]                                                                |
  -> + feedback return                                                          |
  -> predelay -> main tanks -> Ext tanks (Off / Series / Parallel), Ext Mix     |
  -> HPF -> Gain, -18..+18 dB, PULL = Dirt (TS808 stage) -> Comp / Off / Limit -> LPF
  -> [WET meter]                                                                |
  -> feedback block (Stereo: own channel; MEGAVERB: L out -> R in, R out -> L in)
  -> Wet/Dry mix <---------------------------------------------------------------'
  -> Output, -18..+18 dB, PULL = Tape (2N3904 pair). Tube runs first if Vol is pulled.
  -> Post Output (plugin only, -18..+18 dB)
  -> [OUT meter]
```

- **Pull knobs**: click a pull knob (press and release without dragging) to pull it out or push it in. Pulled knobs get a copper halo and the label changes ("Vol: TUBE (pulled)"). Drag still turns the knob. The pulls are real parameters (`inputTube`, `dirt`, `outputTape`) so presets and host automation move them.
- **Source switch** (was the "Mono Source To Stereo" toggle): Stereo / Mono > Stereo / MEGAVERB. The first two behave as before. MEGAVERB leaves both channel paths as they are and crosses the feedback: what leaves the Left path (after the circuit) is fed to the start of the Right path with the Feedback knob amount, and the Right path's output goes back to the start of the Left path, so a sound ping-pongs L > R > L > R through both tank chains. Switching Source flushes the feedback loop.
- **FB Dyn switch**: Comp (**MMBF5457 FET compressor**, 1176 territory, linked feedback sidechain) / Off / Limit (**Coolaudio V2181** VCA limiter, 10:1). Both are stereo linked and share the Gain knob with the Dirt circuit. Three positions. CORRECTED 2026-09-30: this line used to say a VTL5C3 vactrol and that the FET comp was gone. The opposite is true.
- **Meters** (plugin only, none on the PCB): In after the Vol/Tube knob, Wet after the Gain/Dirt/Comp-Limit circuit just before the feedback path, Out as the very last thing.
- Ext Tanks routing, Ext Mix, Feedback, FB Phase, Wet/Dry, HPF/LPF (fixed Q 0.707) are unchanged. Every level knob is now the same -18..+18 dB pot stage (the old -96 dB mute bottom is gone).
- Presets: "GBS default" is all solid state, dynamics Off, Stereo. "GAS default" has Vol pulled (tube in and out), Gain pulled (Dirt), Output pulled (Tape), Series ext tanks. Old saved states are migrated: Mode Tube -> Vol pulled, Tape -> Output pulled, Tube Screamer -> Gain pulled, Opto/FET -> Comp, VCA -> Limit; Drive -> Gain (clamped to +/-18); the mono toggle -> Source.

## Circuit models (component level, Rev B / Rev C part values)

All nonlinear stages run 4x oversampled. Pedal-level stages see 0 dBFS = 100 mV (the board's -36.8 dB pad); the dynamics run at bus level, 0 dBFS = 6.93 Vpk, threshold -18 dBFS = 0.87 Vpk.

| Stage | Model | Parts |
|---|---|---|
| Tube (Vol pull, and Output when pulled) | J201 common-source, Shichman-Hodges load line solved into a table; gate-source diode charges Cin and sags the bias (tau 47 ms) | TL072 x11 boost (100k/10k), Cin 47n, Rg 1M, Rs 470R, Rd = 4.7k + 50k trim **solved for Vd = 4.9 V** (lands on 8.2k for a typical J201) |
| Tape (Output pull) | record EQ -> 2N3904 long-tailed pair (tanh, solved) -> passive repro EQ | Rf 82k, 10k \|\| (4.7k + 6.8n); Re 470R, Rt 2.2k, Rc 4.7k; 15k / 10k / 3.3n |
| Dirt (Gain pull) | TS808 feedback clipper solved from the Shockley equation | TL072, Rf 51k, 2x 1N4148W, Rg 4.7k, 9 V rail |
| Comp (SUPERSEDED, see the project doc) | VTL5C3 shunt divider; linked sidechain -> half-wave -> 10 ms average -> LED driver; cell law 1.5k at 1 mA, ~I^-0.7, 2.5 ms on, 35 ms + 1.5 s dual-slope off | R1101 22k, sum 100k/100k/47k, 10k + 1u average, **driver x3 with 2.62 V offset, LED resistor 78k (Rev C change, see below)** |
| Limit (part is now Coolaudio V2181, same 6.1 mV/dB law) | THAT2180 (6.1 mV/dB) under a discrete log-average detector on the output (feedback) | 20k/20k/10k summer, full-wave, 10k + 1u, 100k into an MMBT3906 transdiode (3.0 mV/dB), difference amp x18.2, positive clamp |

Measured in a local harness (176.4 kHz, L = R sine):

- Limit: unity to -18 dBFS, then 0 -> -16.2, +6 -> -15.6 dBFS: ratio 10:1, hard knee, exactly the Rev B design intent.
- Comp (VACTROL FIGURES, NOT THE SHIPPING CIRCUIT): 0.6 dB at -18, 4.2 dB at -12, **7.3 dB at -6 dBFS (+12 over, the design target)**, 10.5 dB at 0, 13.3 dB at +6. Release from 10 dB: 5.6 dB left after 50 ms, 3.3 after 100 ms, 1.5 after 1 s (the vactrol dual slope).
- Tube: unity to about -18 dBFS, ceiling around -11 dBFS out. Tape: unity to -12, ceiling -4.4 dBFS out.

## Rev C hardware notes (for the next schematic pass)

1. ~~**Opto sidechain driver (U1101D) needs redesign.**~~ SUPERSEDED: there is no vactrol in Rev C. Solving the VTL5C3 law against the Rev B target (7 dB GR at +12 dB over threshold) shows R1150 2.2k + RV1101 10k would run the LEDs at nearly 1 mA and pull the divider down 20+ dB, and a x13 driver hits its 14 V rail at only +12 dB over threshold, so compression would stop there. Rev C model: driver gain 3 (20k / 10k) plus a 2.62 V DC offset into the non-inverting input (so the LEDs still light at the 0.26 V / -18 dBFS average), LED resistor 78k. Rails at about +23 dB over threshold. RV1101 can become a trim around 78k.
2. **Controls move.** The 7-position Mode rotary and its seven relays are replaced by: Vol push-pull pot (Tube relay pair, engages BOTH the input tube stage and an output tube stage), Gain push-pull pot (TS relay), Output push-pull pot (Tape relay), and a 3-position Comp / Off / Limit switch. The FET compressor circuit (12xx) is dropped. Two extra pedal-level stages (tube after Vol, tube + tape after the Wet/Dry mix on the feedback/wet board) with their pads and make-up stages are new.
3. **Vol / Gain / Output are all the same +/-18 dB inverting pot stage** (680R ends around a 10k lin dual, like the Rev B Drive stage but with the range trimmed to 18 dB). Vol sits right after the dry/wet split on the wet path, Output after the mix. Pre Input and Post Output exist only in the plugin.
4. **MEGAVERB** is a routing change on the feedback/wet board: a 3-position Source switch whose third position swaps the L and R feedback returns (L path output -> R path input and vice versa). Mono > Stereo is the existing mono sum switch.
5. Meters are plugin only; nothing to add to the PCB.

## Files

- `Source/DSP/RevCStages.h` (TubeTapeStage, DirtDynamicsBlock), `DynamicsModels.h` (Comp, Limit), `SaturationModels.h` (tube drain trim), `FeedbackBlock.h` (cross coupling), `ModularFxChain.h`; `PluginProcessor.*`, `PluginEditor.*` (PullKnobSlider, 3-way switches, meters).
- Build: `scripts\Build-RevC.ps1` (configure + Release build of Standalone and VST3, log in `revc-build.log`), `scripts\Install-RevC-VST3.ps1`, `scripts\Launch-RevC.ps1`.
- The draw.io signal-flow map has not been updated for Rev C yet.
