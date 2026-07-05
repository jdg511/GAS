# GAS Rev A — Schematic Review Report

## FINAL PRE-ORDER REVIEW — 2026-07-04

Scope: delta review on top of the 2026-07-02 baseline (kept in full below).
Focus: (1) everything that changed since 2026-07-02 — the ext-tank-routing
re-spin (new U202 send summers) and the same-day PCB fixes; (2) the
2026-07-04 power-source change from the +30 V Jameco candidate to the
regulated **Triad WSU240-0750 (+24 VDC / 750 mA / 18 W)**; (3) a ratings
re-check of the power entry path at the new voltage.

### Verdict

**Gerbers: OK to upload — W5 via cleanup done and both boards re-gated +
re-exported 2026-07-04 15:30 (0 errors / 0 unconnected / 0 hole warnings).**
**Parts order: OK — the input-capacitor and PTC purchasing corrections (F3)
are reflected in the docs BOMs.**

### New findings

#### F3 — input electrolytics were spec'd at 25 V on the DC input (fail → fixed in BOM)
The purchasing BOM listed `EEU-FR1E221` (220 µF **25 V**) for C500, and no
50 V part existed anywhere in the docs BOMs for the PS500 Cin position
(schematic C509, 100 µF — URA datasheet Fig.2 requires a **50 V** Cin).
Worst-case input is 25.2 V with the new 24 V adapter — at/over the 25 V
rating — and this was **also wrong for the old +30 V design**; the
2026-07-02 entry-path review checked pin-nets and current, not cap voltage
ratings. **Fix (done):** `EEU-FR1H221` (220 µF / 50 V, D10/P5 — drop-in on
both footprints, buy 2) spec'd in `bom/rev-a-power-backplane-preliminary-bom.csv`.
Rail-side electrolytics stay 25 V (fine on ±15 V / +5 V). No PCB change.
Evidence: `review_outputs/pwr-entry-path-24v.md`, fab BOM footprints,
`datasheet_cache/ura2415ymd.summary.md`. Confidence: high.

#### W5 — overlapping/duplicate drill hits (fix before gerber upload)
The 2026-07-04 pm DRC gates are 0 errors / 0 unconnected on all six boards,
but four *warning*-severity drill items remain, all same-net AGND:
- io-board: stitching via at (106.64, 97.44) overlaps P4 pad 2 drill (0.00 mm
  hole-to-hole), reported twice.
- io-board: two exactly co-located duplicate via pairs at (164.475, 59.905)
  and (137.675, 59.905).
- ext-tank-routing: stitching via at (116.00, 70.00) overlaps K202 pad 16
  drill (0.00 mm hole-to-hole).
Electrically benign (same net), but overlapping drill hits commonly trigger a
fab DFM hold/email and can cause drill breakout at the pad barrel.
**RESOLVED 2026-07-04 15:30:** the two pad-overlapping vias deleted, one via
of each co-located pair deleted (one stitching via retained at each spot);
DRC re-run on both boards via kicad-cli 10.0.3 — 0 errors, 0 unconnected,
0 hole_to_hole / holes_co_located warnings; gerbers + drill re-exported and
re-zipped (`fab/io-board/`, `fab/ext-tank-routing/`, 15:31). **Discard any
gerber zips downloaded before 2026-07-04 15:31 for these two boards.**
Evidence: `rebuild/io-drc.json`, `rebuild/ext-drc.json` (2026-07-04T15:30).
Confidence: high.

#### W6 — feedback loop sign changed by the ext-routing re-spin (bench)
U202's send summers are inverting and feedback now reinjects **before** the
springs, so net loop phase differs from the pre-re-spin topology. The
crossfade board's `Feedback Phase Invert` covers either sense; at bench,
confirm which switch position gives regenerative build-up and correct the
panel labeling if swapped. Evidence: `review_outputs/ext-U202-send-summers.md`,
`rebuild/ext-sim.cir`. Confidence: high (that the sign flipped), bench (label).

### New instance reviews (2026-07-04)

- **U202 (OPA1656, ext-routing send summers — new part, previously
  unreviewed):** all 8 pins pass against the verified OPA1656 summary;
  decoupling, loading, and stability pass. See
  `review_outputs/ext-U202-send-summers.md`.
- **DC entry path at +24 V:** P500 at 14% of XH rating (0.43 A vs 3 A),
  MSMF110 PTC and SS34 pass, SMAJ33A margin improved (25.2 V worst case vs
  33 V standoff), inrush pass with the current-limited adapter. Supersedes
  the +30 V review. See `review_outputs/pwr-entry-path-24v.md`.

### Adapter-change consistency (2026-07-04, docs side)

- `rev-a-external-dc-power.md` is the authority for the new topology; P-0
  receiving check is now open-circuit +22.8 to +25.2 V, reject >+27 V.
- Jack changes PJ-005B → **PJ-005A** (5.5×2.1 mm; same mounting hole). The
  jack is panel-mounted and hand-wired — **no PCB impact**.
- PS500 schematic value already reads URA2415YMD-10WR3 (correct); docs
  URB references were cleaned up.
- Docs BOM F500 corrected to the SMD `MF-MSMF110` actually on the board.
- KiCad net names `+30V_RAW`/`+30V_F` are historical (now +24 V nominal);
  rename at next capture pass. Cosmetic; does not affect fab outputs.
- Power budget updated for U202 (+7.8 mA/rail): worst-case analog rails now
  121.6–161.6 mA against the 250 mA budget; the +15VA stack check from the
  pre-order double-check (item 9) still clears the URA's 333 mA/rail limit,
  with the same bring-up current measurement retained.

### Carried items

- **W1 — RETIRED 2026-07-04:** ST BD139/140 datasheet fetched and cached
  (`bd139-bd140.datasheet.txt`); summary status now verified. All numeric
  ratings confirm the sim margins (80 V / 1.5 A / 12.5 W vs 30 V / 65 mA /
  0.7 W). Remaining bench items only: SOA-curve read-off (graphic), pinout
  continuity check on first part, case-temperature check at P-2 (free-air
  Rth j-amb 100 C/W → consider a clip-on heatsink; noted in the summary).
- W2 G5V-2 coil variant / R351 value — now a written receiving step in
  `rev-a-bench-test-procedures.md` P-3 step 0.
- W3 shared clip-floor pot interaction (bench).
- W6 feedback-loop labeling — now a written bench step in
  `rev-a-bench-test-procedures.md` P-5 step 4.
- Panel-jack harness map at assembly.

### Verification basis (2026-07-04 pass)

- The skill's bundled extraction scripts are not present in this install;
  extraction was done with equivalent project-local tooling: regex
  ref/value extraction from all six raw `.kicad_sch`, the post-re-spin SPICE
  export (`rebuild/ext-sim.cir`) for U202 connectivity, fab BOM footprint
  cross-checks, and KiCad 10.0.3 ERC/DRC JSON gates (all six boards,
  2026-07-04T13:31–13:32, 0 errors / 0 unconnected).
- Datasheet evidence: cached verified summaries (OPA1656, URA2415YMD,
  R-78E, G5V-2, JST XH/VH, OPA1644/1679) + Triad WSU240-0750 datasheet PDF
  (fetched 2026-07-04, docs BOM link).
- Raw-schematic spot-checks: power-backplane values (C500/C509/F500/TVS500/
  PS500), ext-routing U201/U202/relay/flyback part set.
- Checklist basis: baseline + connector_power + dcdc + power_entry_inrush
  equivalents re-applied to the changed areas; motor/MCU checklists remain
  not-applicable (analog-only design).
- Not re-checked this pass (unchanged since 2026-07-02, gates still green):
  io/tank-driver/crossfade/filter instance-level pin maps.

---

# Baseline review — 2026-07-02 (retained)

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
  **[2026-07-04: RESOLVED — orphan via removed, zones set to island-removal
  = always, refilled, DRC re-run 0/0, gerbers re-exported; see
  rev-a-order-readiness.md item 1.]**

## Checklist status

Applied (`applies: true` from build_review_context):
- **baseline (checklist_example)** — decoupling per package, DNP marking,
  power flags, connector pin orders vs harness map: pass.
- **connector_power** — all paths ≤12% of verified connector ratings
  (XH 3A visual p.1; VH 10A visual p.1): pass. [2026-07-04: worst path now
  14% at 24 V — still pass.]
- **dcdc** — URA2415 externals per datasheet Fig.2 (Cin 100µ, Cout 10µ/rail,
  cap-load 130µ < 330µ max), ripple filter −50dB @350kHz (sim): pass.
  [2026-07-04: Cin voltage class corrected to 50 V at purchase, F3.]
- **dcdc_bringup_test** — maps to rev-a-bench-test-procedures step P-0
  (adapter open-circuit voltage, polarity, inrush, ripple): manual_review
  (bench). [2026-07-04: thresholds updated for the 24 V adapter.]
- **power_entry_inrush** — 0.5A-limited adapter + 1.1A-hold PTC + SMAJ33A +
  320µF bulk: pass. [2026-07-04: now 0.75 A adapter + ~440 µF with the 50 V
  Cin change; still pass, bench-verify at P-0.]
- **signal_power_integrity** — 2-layer, solid pours both sides + grid
  stitching, balanced I/O with 0.1% receiver networks: pass.

Not applicable (keyword false-positives, documented): motor_driver,
half_bridge_gate_drive, mcu_adc, current_sensing, motor_control_foc — the
design is analog-audio-only by project constraint (no MCU/ADC, no PWM
bridges, no motors).

## Per-instance summary

14 instance reviews in `review_outputs/` covering all 10 op-amp packages,
both power modules, all 8 relays, the transistor output stage, and 4
current-path reviews [2026-07-04: +2 — ext-U202-send-summers.md,
pwr-entry-path-24v.md; total 16 covering 11 op-amp packages]. All pass
except items listed above. 9 datasheet summaries in `datasheet_cache/`
(7 verified from cached PDFs, JST ratings read visually from the PDFs'
rating blocks, BD139 manual_review).

## Manual-review questions for the bench/order stage

1. ~~Adapter open-circuit voltage <34V (unregulated-sample risk, P-0).~~
   [2026-07-04: superseded — regulated WSU240-0750 chosen; receiving check
   is now +22.8 to +25.2 V, reject >+27 V.]
2. G5V-2 coil variants + R351 value (W2).
3. BD139/140 datasheet verification (W1).
4. Panel-jack harness map (XLR2/T→P, XLR3/R→N, XLR1/S/G→AGND) at assembly.
5. ~~io-board pour fragment via (W4).~~ [2026-07-04: resolved.]
6. Feedback phase-invert panel labeling after the pre-tank reinjection
   re-spin (W6, new).

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
