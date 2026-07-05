# GAS Rev A Bench Test Procedures

Concrete bench procedures for each board, run in the order given in [rev-a-bringup-sequence.md](rev-a-bringup-sequence.md). The validation checklist in [rev-a-validation-checklist.md](rev-a-validation-checklist.md) covers what to confirm; this file covers how to confirm it, with specific signals, equipment, and pass/fail numbers tied to [rev-a-numeric-targets.md](rev-a-numeric-targets.md).

## Required bench equipment

- Bench DMM with 10 mV resolution and a 100 mA range
- Dual-channel oscilloscope, 50 MHz bandwidth or better, with two 10x probes
- Audio signal generator capable of balanced output, or a USB audio interface with a balanced line out
- Audio analyzer or USB interface plus FFT software (REW, ARTA, or equivalent) for THD+N and frequency response
- Dummy load: two `600 ohm 1 W` non-inductive resistors plus two `10 kohm 1/4 W` resistors
- Bench power supply rated at least `+/-20 V` at 250 mA for pre-installation rail injection
- Two pairs of audio cables: balanced XLR/TRS, plus internal harness adapters per [rev-a-interconnect-pin-map.md](rev-a-interconnect-pin-map.md)
- Bench DMM probe or breakout for the external `+24 VDC` wall adapter plug

## Reference signal definitions

- `REF-DBU-0`: balanced sine, `1 kHz`, `0 dBu` (`0.775 Vrms` differential)
- `REF-DBU+4`: balanced sine, `1 kHz`, `+4 dBu` (`1.228 Vrms` differential)
- `REF-DBU+18`: balanced sine, `1 kHz`, `+18 dBu` (`6.16 Vrms` differential, headroom check)
- `REF-SWEEP`: balanced log sweep `20 Hz` to `20 kHz`, `+4 dBu`
- `REF-IMPULSE`: balanced single-cycle `1 kHz` burst for tank excitation

## P-0  Power Backplane (before any audio board is connected)

Equipment: DMM, scope.

1. Verify the wall adapter is the intended `Triad WSU240-0750` `+24 VDC` model (open-circuit `+22.8 V` to `+25.2 V`, reject above `+27 V`) and that the barrel polarity matches the service-endcap jack before any board is connected.
2. Apply the wall adapter with all downstream board connectors unmated.
2. Measure each rail at the backplane test points:
   - `+15VA` to `AGND`: `+14.85 V` to `+15.30 V`, ripple under `5 mVpp` at 100 kHz scope bandwidth
   - `-15VA` to `AGND`: `-14.85 V` to `-15.30 V`, ripple under `5 mVpp`
   - `+5VAUX` to `DGND`: `+4.90 V` to `+5.20 V`, ripple under `20 mVpp`
3. Scope `AGND` to chassis at the star-ground point. Low-frequency component under `2 mVpp`.
4. Load each rail to its rev-A budgeted draw from [rev-a-power-budget.md](rev-a-power-budget.md) using bench resistors. Rails must hold within the limits above and the DC-DC plus `+5V` regulator stack must not enter thermal foldback within 5 minutes.

Pass condition: all three rails within tolerance under loaded and unloaded conditions, no oscillation on the scope, no thermal warning from the conversion modules.

## P-1  Input / Output Board

Equipment: balanced generator, DMM, scope, audio analyzer, 600 ohm load.

Setup: connect the board through its own power harness from P-0. Leave all downstream audio connectors floating. Connect a balanced load (`600 ohm` in parallel with a `10 kohm` voltmeter tap) to each output jack.

1. Quiescent check
   - Measure DC at each balanced receiver output pin. Target within `+/-5 mV` of `AGND`.
   - Measure DC at each balanced driver output pin. Target within `+/-15 mV` of `AGND`.
2. Balanced receiver gain
   - Apply `REF-DBU+4` to the left input. Measure the post-receiver test point.
   - Expected internal level matches the rev-A internal nominal in [rev-a-numeric-targets.md](rev-a-numeric-targets.md) within `+/-0.3 dB`.
3. Mono-to-stereo switch
   - Apply `REF-DBU+4` to the left input only, right input shorted.
   - Toggle `STEREO/MONO`. In `MONO`, the right internal channel must match the left within `0.3 dB` and remain phase-coherent on the scope.
4. Headroom
   - Apply `REF-DBU+18`. THD+N at the post-receiver test point under `0.05 percent` measured at `20 Hz - 20 kHz`.
5. Wet / dry control behavior
   - Sweep the `WET/DRY` pot through its full travel with `REF-DBU+4` applied. Output at the balanced driver must transition monotonically with no zipper noise audible on a powered monitor through the analyzer return.
6. Balanced driver into load
   - Drive `REF-DBU+4` through with `WET/DRY` at fully dry. Output across `600 ohm` must be `+4 dBu +/- 0.5 dB`.
   - Drive `REF-DBU+18` through. Output must remain undistorted (THD+N under `0.1 percent`) and the rails must not sag more than `100 mV`.
7. Frequency response
   - Run `REF-SWEEP`. Response must be flat within `+/- 0.5 dB` from `20 Hz` to `20 kHz` on the dry path.

Pass condition: all six checks within bounds with no audible artifacts on the monitor.

## P-2  Tank Driver / Recovery Board

Equipment: scope, balanced generator, current-limited bench supply for safety.

Setup: connect the board to P-0. Connect the recovery side to a temporary 10 kohm load while the primary tanks are not yet wired in.

1. Quiescent driver bias
   - Measure DC at each `BD139` / `BD140` emitter junction. Should sit within `+/-30 mV` of `AGND`.
   - Measure each transistor's emitter-resistor voltage. Idle current should match the rev-A bias point in [rev-a-circuit-starting-points.md](rev-a-circuit-starting-points.md) within `+/-20 percent`.
2. Send drive level
   - Apply `REF-DBU+4` at the wet send. Verify the driver output across a `10 ohm` dummy tank-input resistor matches the rev-A send-drive target in [rev-a-numeric-targets.md](rev-a-numeric-targets.md) within `+/-1 dB`.
3. Recovery gain
   - Inject a `5 mVrms` `1 kHz` sine into the recovery input through a `10 kohm` series resistor to simulate tank source impedance. Verify recovery output level matches the rev-A recovery gain within `+/-0.5 dB`.
4. Real tank substitution
   - With the bench rails off, install the primary `4AB1C1B` tanks per [rev-a-harness-map.md](rev-a-harness-map.md). Re-energize.
   - Apply `REF-IMPULSE`. The recovery output must show a decaying spring response longer than `1.5 s` on the scope before the next burst.
5. Secondary tank check
   - Repeat step 4 with `9EB2C1B` (left) and `9EB3C1B` (right). Decay should be audibly distinct from the primaries when monitored through P-1.

Pass condition: bias stable, send and recovery levels in range, tanks audibly excited and decaying without oscillation or hum higher than `-70 dBu` at the recovery output.

## P-3  Ext Tank Routing Board

Equipment: signal generator, audio analyzer, scope.

0. Relay receiving check (at parts arrival, review W2 / pre-order double-check item 7)
   - Before installing any relay, measure each `G5V-2` coil resistance with the DMM and record it.
   - DC5 coils (`K201-K204` here): confirm which coil-current variant arrived (30 vs 40 mA class) and that the `+5VAUX` relay allowance in [rev-a-power-budget.md](rev-a-power-budget.md) still holds for 7 coils worst-case.
   - DC12 coil (`K301`, crossfade board): if the coil measures as the `720R` variant, change `R351` from `240R` to `150R` before assembly, per the pre-order double-check.
   - Also bench-confirm NC/NO orientation on one relay before final panel labeling (symbol-orientation risk noted in review W2).

1. Quiescent off state
   - Set the `MODE` rotary to `Off`. Apply `REF-DBU+4` at the wet input. Measure the secondary send output: should be at the analyzer noise floor (under `-80 dBu`).
2. Series mode
   - Set to `Series`. The wet path must pass through the secondary tanks. Verify with `REF-IMPULSE` that the recovery output shows both primary and secondary decay characteristics summed.
3. Parallel mode
   - Set to `Parallel`. The secondary send must be present at the analyzer noise floor while the wet path is also present at the bypass. Confirm the `EXT AMOUNT` pot scales the secondary-tank contribution monotonically from `-inf` to the rev-A maximum in [rev-a-control-ranges-and-laws.md](rev-a-control-ranges-and-laws.md).
4. Relay switching transient
   - With `REF-DBU+4` applied, switch `MODE` between all three positions repeatedly. Scope the wet bypass output. Switching transients must stay below `30 mVpp` at the post-routing output.
5. Crosstalk
   - Apply signal to left only with `MODE` in `Parallel`. Right channel post-routing must show crosstalk under `-70 dB` at `1 kHz`.

Pass condition: all three modes behave per truth table in [rev-a-mode-truth-tables.md](rev-a-mode-truth-tables.md), switching transients within bounds, crosstalk under spec.

## P-4  Filter / Clipper Board

Equipment: signal generator, audio analyzer, scope.

1. Drive stage linearity
   - With `DRIVE` at minimum, apply `REF-DBU+4`. THD+N at the post-drive test point under `0.05 percent`.
   - With `DRIVE` at maximum, expect intentional harmonic content; verify the scope shows the selected `CLIP MODE` waveform shape.
2. HPF sweep
   - Set `CLIP MODE` to clean. Sweep `HPF CUTOFF` across full travel with `REF-SWEEP`. The `-3 dB` point must traverse the rev-A HPF range in [rev-a-numeric-targets.md](rev-a-numeric-targets.md) within `+/- 10 percent`.
   - Sweep `HPF Q` and verify peak amplitude tracks per rev-A control law without self-oscillation at maximum Q.
3. LPF sweep
   - Repeat step 2 with `LPF CUTOFF` and `LPF Q`.
4. Clip mode encoding
   - Step `CLIP MODE` through all four positions with `DRIVE` at maximum and `REF-DBU+4` applied. Each position must produce a visibly distinct scope waveform consistent with the curated mode set in [rev-a-mode-truth-tables.md](rev-a-mode-truth-tables.md).
5. Output level
   - With `DRIVE` minimum, `CLIP MODE` clean, both filters wide open, output level at the filter board send must match input level within `+/- 0.5 dB`.

Pass condition: filter ranges within `+/- 10 percent`, clip modes audibly distinct, drive stage clean at minimum.

## P-5  Crossfade / Feedback / Mixer Board

Equipment: signal generator, audio analyzer, scope.

1. Crossfade law
   - Inject distinct signals into the left and right wet inputs (`1 kHz` left, `1.1 kHz` right). Sweep `CROSSFADE` from full-left to full-right. Each endpoint must show greater than `40 dB` of opposite-channel rejection at the mixer output.
   - Center position must show both channels within `+/-1 dB` of each other.
2. Feedback phase invert
   - Apply `REF-DBU+4` to wet input with `FEEDBACK` near zero. Toggle `FB PHASE`. The mixer output at `1 kHz` must invert polarity cleanly with no level change greater than `0.3 dB`.
3. Feedback stability
   - Slowly raise `FEEDBACK` with `MODE` in `Off` and the filter passing signal. Verify the rev-A feedback maximum stays below self-oscillation when `FILTER` is set to its rev-A nominal narrow band. Document the position where oscillation onsets with the real tanks installed.
4. Feedback loop-sense labeling check (added `2026-07-04`, review finding W6)
   - The `2026-07-04` ext-routing re-spin moved feedback reinjection pre-tank through inverting send summers (`U202`), which changes the net loop sign versus the earlier topology. With the real tanks installed, raise `FEEDBACK` moderately in each `FB PHASE` position and identify which position gives regenerative build-up (blooming decay) versus damping. If the behavior is swapped relative to the panel legend, swap the panel labeling (function is unaffected; the selector covers both senses).
5. Mixer summing
   - Apply matched `REF-DBU+4` to all summing inputs in turn. Total mixer output must scale per rev-A gain plan in [rev-a-capture-value-tables.md](rev-a-capture-value-tables.md).

Pass condition: crossfade endpoints clean, phase invert exact, feedback stable below rev-A documented threshold, and the `FB PHASE` legend matched to observed loop behavior per step 4.

## S-1  Full System Audio Validation

Run only after P-0 through P-5 each pass standalone, with all boards mated through the harness defined in [rev-a-harness-map.md](rev-a-harness-map.md) and all four tanks installed.

1. Repeat the input/output P-1 checks with the full signal chain populated and `WET/DRY` at fully dry. Output must still meet `+4 dBu +/- 0.5 dB` into `600 ohm`.
2. With `WET/DRY` at center and `MODE` cycled through `Off / Series / Parallel`, verify the curated `applyDefaultGasSettings` startup behavior in [rev-a-control-ranges-and-laws.md](rev-a-control-ranges-and-laws.md).
3. THD+N at `+4 dBu` output, `WET/DRY` fully dry, all controls at curated defaults: under `0.05 percent` from `20 Hz` to `20 kHz`.
4. Background noise at the balanced output with inputs terminated in `600 ohm` and `WET/DRY` fully dry: under `-90 dBu A-weighted`.
5. Listen test through the curated defaults. Tank decay, ext-tank routing, filter, clipper, crossfade, and feedback must each be audibly identifiable as distinct controls.

Pass condition: all measurements within bounds and the curated default startup state is reproducible from a cold boot.

## Failure handling

Record any failure in [rev-a-open-issues.md](rev-a-open-issues.md) with the test step number, observed value, and the board harness state. Do not advance to the next P step until the prior one passes; the bring-up sequence depends on each upstream board being correct in isolation.
