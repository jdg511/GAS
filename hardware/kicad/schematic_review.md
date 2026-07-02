# GAS Rev A — Schematic Review Report

Reviewed with the `kicad-schematic-review` skill workflow (staged extraction,
datasheet cross-checks, checklists, current-path ratings). Scope: all six
production schematics + boards in `hardware/kicad/`. Date: 2026-07-02.

## High-severity findings (both FIXED in this pass)

### F1 — +5V switching regulator fed from the filtered analog rail (fail → fixed)
**Board:** power-backplane. PS501 (R-78E5.0-0.5) input was on **+15VA**,
injecting switching-input ripple current into the op-amp supply rail after
its LC/bead filter. **Fix:** input moved to **+15VRAW** (pre-bead, still
7–28V-compliant per cached RECOM datasheet) + C512 10µ input cap added.
Board re-routed; DRC 0 errors / 0 unconnected. Evidence: gen_pwr.py,
datasheet_cache/r78e.summary.md. Confidence: high.

### F2 — right channel floats with a center-off mono switch (fail → fixed)
**Board:** io-board. U1D+ was driven only by MONO_C from the panel switch;
the control spec permits a "3-state" switch, whose center position (or an
unplugged harness) leaves a CMOS op-amp input floating → right channel
noise/latch. **Fix:** R25 1M MONO_C→R_RX added (defaults to stereo; ~100R
source impedances make the switch behavior unchanged). Re-routed; DRC 0
errors. Evidence: review_outputs/io-U1-U4.md. Confidence: high.

## Warnings

- **W1 — BD139/BD140 datasheet unverified** (fetch timed out). Stage stress
  from verified sim (~65mA pk, <0.7W) is consistent with family ratings but
  is a schematic-consistency observation, not datasheet-verified. Cache the
  ST datasheet and check SOA/hFE bin before the production spin.
- **W2 — G5V-2 coil table is a graphic** (contact ratings verified: 2A/30VDC).
  Confirm coil resistance of the exact DC5 and DC12 variants at order time;
  R351 (240R) assumes a ~960R 12V coil. NC/NO orientation from the KiCad
  symbol should be bench-confirmed once (wrong guess only flips a panel
  label, not function).
- **W3 — shared clip-floor pot interaction** (filter board): when both
  channels clip hard, small L/R interaction flows through the shared DRV_HI
  landing — inherent to the frozen 3-wire drive interface; bench-evaluate.
- **W4 — io-board pour bookkeeping:** one DRC "unconnected" item pairing two
  same-net AGND pour fragments remains. Every fragment verifiably contains a
  dual-layer ground via or through-pad by programmatic probe; 0 DRC *errors*.
  Two-minute GUI check: open the board, show ratsnest, drop one via where
  the single white line points. Does not affect any signal/power net.

## Checklist status

Applied (`applies: true` from build_review_context):
- **baseline (checklist_example)** — decoupling per package, DNP marking,
  power flags, connector pin orders vs harness map: pass.
- **connector_power** — all paths ≤12% of verified connector ratings
  (XH 3A visual p.1; VH 10A visual p.1): pass.
- **dcdc** — URA2415 externals per datasheet Fig.2 (Cin 100µ, Cout 10µ/rail,
  cap-load 130µ < 330µ max), ripple filter −50dB @350kHz (sim): pass.
- **dcdc_bringup_test** — maps to rev-a-bench-test-procedures step P-0
  (adapter open-circuit voltage, polarity, inrush, ripple): manual_review
  (bench).
- **power_entry_inrush** — 0.5A-limited adapter + 1.1A-hold PTC + SMAJ33A +
  320µF bulk: pass (bench-verify adapter <34V open-circuit).
- **signal_power_integrity** — 2-layer, solid pours both sides + grid
  stitching, balanced I/O with 0.1% receiver networks: pass.

Not applicable (keyword false-positives, documented): motor_driver,
half_bridge_gate_drive, mcu_adc, current_sensing, motor_control_foc — the
design is analog-audio-only by project constraint (no MCU/ADC, no PWM
bridges, no motors).

## Per-instance summary

14 instance reviews in `review_outputs/` covering all 10 op-amp packages,
both power modules, all 8 relays, the transistor output stage, and 4
current-path reviews. All pass except items listed above. 9 datasheet
summaries in `datasheet_cache/` (7 verified from cached PDFs, JST ratings
read visually from the PDFs' rating blocks, BD139 manual_review).

## Manual-review questions for the bench/order stage

1. Adapter open-circuit voltage <34V (unregulated-sample risk, P-0).
2. G5V-2 coil variants + R351 value (W2).
3. BD139/140 datasheet verification (W1).
4. Panel-jack harness map (XLR2/T→P, XLR3/R→N, XLR1/S/G→AGND) at assembly.
5. io-board pour fragment via (W4).

## Parser limitations (extractor `extraction_notes` preserved)

The skill's lightweight extractor under-merges label-style nets on the
power-backplane (reported 4 nets) and over-counts multi-unit pins; KiCad's
own ERC (0 violations, all six schematics) and exported SPICE netlists
(all six sims run clean in ngspice) were used as the authoritative
connectivity evidence, with raw .kicad_sch spot-checks on PS500 pin nets,
U1A receiver network, K401 decode tree, and Q101 pins.

## Verification basis

- Scripts run: inventory_project.py, extract_kicad_sch.py ×6,
  build_review_context.py, datasheet_tool.py fetch/extract ×8.
- Datasheets cached & summarized: OPA1656, OPA1679, OPA1644, URA_YMD-10WR3,
  R-78E-0.5, G5V-2, JST XH, JST VH (+BD139 attempted, timed out ×2).
- Sims re-run after fixes: io-board transient (values unchanged, exact),
  power AC ripple (−50dB @350kHz).
- Post-fix gates: power-backplane DRC 0/0; io-board DRC 0 errors,
  1 pour-bookkeeping unconnected (W4); ERC 0 on all six schematics.
