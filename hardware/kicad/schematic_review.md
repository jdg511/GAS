# GAS Rev A — Pass 2 Schematic Review (kicad-schematic-review methodology)

Date: 2026-07-31 · Reviewer: Claude (Illicit Apothecary / GAS project) · Scope: all 6 board schematics

## Method (Verification Basis)

Pass 2 used an **independent extraction path** — a purpose-built s-expression parser
(`extract_sch.py`) that reads the raw `.kicad_sch` files directly, computes every pin
position from `lib_symbols` + instance transforms (calibrated against known-good pin
locations), and rebuilds connectivity from wires, labels, junctions, pin-on-wire and
label-on-wire geometry. Its "multi-name net" report lists every net carrying more than
one name; each was classified against the spec docs as an intended alias or a defect.
KiCad's own ERC was re-run after every fix as a second opinion. Datasheets verified this
session: Mornsun URA_YMD-10WR3 (official PDF, pinout read from the p.5 drawing),
OPA1656/OPA1679 pin maps via the KiCad library symbols cross-checked against placed
instances. No project checklist files exist; the skill's baseline contract was applied.

## High-severity defects found and FIXED in pass 2

All were silent shorts that KiCad ERC did not flag as errors (connected pins are not an
ERC violation). Evidence: extractor multi-name-net groups + raw-file geometry; all fixes
re-verified by re-extraction (all six boards now report zero unexpected merges) and ERC.

### io-board.kicad_sch
1. **All three power rails were one net.** Stray `+15VA`/`-15VA` global labels sat on the
   AGND pins of every op-amp decoupling cap (C91–C98 area, 8 labels), and vertical wires
   were drawn **across** the four −15 VA decoupling caps, shorting them. The previously
   "benign" ERC error "Power output and Power output are connected" was in fact this
   short web. Fixed: 8 labels + 4 cap-crossing wires removed. ERC error gone.
2. **Input filter caps C1–C4 were shorted by wires drawn across them**, which also tied
   `IN_BAL_L_P/N` and `IN_BAL_R_P/N` to AGND (both balanced input lines grounded).
   Fixed: 4 wires removed.
3. **Crossed ±15 VA globals at power header P1** (`-15VA` on the +15 V pin row and vice
   versa) — +15 V shorted to −15 V at the power inlet. Fixed: both removed (net labels
   on the pins are correct).
4. **Blend/output-driver section: 20 crossed or row-shifted global labels** merging
   `WD_L/R_WIPER`, `U2A/U2B` input nodes, `L/R_BLEND`, `U3B/U4B` nodes, and the
   hot/cold drive nets into two giant left/right shorts. Fixed per the io definition doc
   (R31/R35/R43/R44/R49/R50 tables): all crossed globals deleted; net labels on pins
   already carried correct names.
5. **R21/R23 and R22/R24 pin overlap** — the right-channel dry/wet isolator resistors
   were placed one row too high, so their input pins landed on the left channel's output
   pins (`DRY_L`=`R_PROG`, `WET_SEND_L`=`R_PROG`). Fixed: R23/R24 moved down 2.54 mm,
   labels re-seated on pins.
6. **Combo-jack (NCJ6FI) TRS rows shifted one row** on both input jacks (Sleeve carried
   `IN_BAL_x_N`, Ring carried `IN_BAL_x_P`, Tip floated). Fixed to Sleeve=AGND,
   Ring=`IN_BAL_x_N`, Tip=`IN_BAL_x_P`. Output jacks had stray `OUT_BAL_x_P/N` globals on
   ground/wrong rows (output hot tied to XLR pin 1 ground) — removed; TRS net labels on
   the output jacks were already correct.
7. **`U1A_P`/`U1B_P` aliases** were on the AGND end of R14/R18 instead of the op-amp +
   input node — relocated to the `L_RX_P`/`R_RX_P` rows per spec.
8. Removed 8 crossed floating `±15VA` decorations + stub wires near U1–U4 power pins
   (no current short, but adjacent to V+/V− pins — layout landmines).

### ext-tank-routing.kicad_sch
9. **Ghost stub-wire column (x≈96.5–101.6)**: 8 leftover wires from a global-label
   landing column crossed the U201A summing-resistor pins mid-span, tying `SEC_RET_R`
   and `FB_RET_L` directly into the left summing node (bypassing R203/R204). Fixed:
   8 wires + 8 redundant globals removed.
10. **R223/R224 pin overlap (right summing network)** — `FB_RET_R` was tied directly to
    `U201B_M`, bypassing R224. Fixed: R224 moved down 2.54 mm, labels re-seated.

### Earlier in this same session (pass 1 + parked questions — summarized for the record)
- ext-tank: right-edge header alias columns fully mirrored (incl. +15 VA↔−15 VA);
  U201 quad op-amp placed as five copies of unit A (units reassigned A–D + power,
  including the `(instances)` records); relay-area ghost wiring shorted both
  `CTL_EXT_MODE` lines to AGND — all fixed.
- io-board: `WET_SEND`/`WET_SUM` crossed strays; wet/dry pot header block realigned;
  `MONO_B` moved off `R_RX_M`.
- filter-clipper: `DRV_*` nets renamed to spec (`DRV_HI/WIPER` shared pot per spec).
- tank-driver-recovery: U101–U104 power units were entirely unplaced — added on the
  waiting ±15 VA labels; P101/P102 pin 6 grounded per spec; PWR_FLAGs added.
- power-backplane: three leftover mis-aimed fix stubs removed; **PS500 pinout confirmed
  from the official Mornsun datasheet** (1=GND, 2=Vin, 3=+Vo, 4=0V, 5=−Vo, 6=Ctrl/open)
  — the previous guess was wrong on 4 of 5 pins and was corrected. Note on PS500.
- Decisions: relay coils stay direct-driven from switched +5VAUX (5 V-coil relays
  REQUIRED — noted on K201–K204); R241–R243 deleted per Jason.

## Intended aliases (verified, do not "fix")
`L_PROG=WD_L_HI`, `R_PROG=WD_R_HI`, `WET_SUM_L=WD_L_LO`, `WET_SUM_R=WD_R_LO`,
`L_RX=MONO_A`, `R_RX=MONO_B`, `L_RX_P=U1A_P`, `R_RX_P=U1B_P`,
`U3A_OUT=L_HOT_DRV`, `U4A_OUT=R_HOT_DRV`, `U3B_OUT=L_COLD_DRV`, `U4B_OUT=R_COLD_DRV`
(io-board); `EXTMIX_L_LO=EXTMIX_R_LO=AGND` (ext-tank).

## Known-benign ERC noise (confirmed again)
- "Hierarchical label … non-existent parent sheet" pairs on every board (child sheets
  ERC'd in isolation).
- Cosmetic dangling wire stubs on io-board from the placeholder capture (no longer any
  that cross pins or carry conflicting labels — the dangerous ones were removed).
- Unused relay pole-2 pins on K201/K202 (pins 21/22/24) — genuinely unused.
- PS500 pin 6 (Ctrl) intentionally open = module always on, per datasheet.

## Current-path notes (schematic-stage)
- +5VAUX budget: PS501 (R-78E5.0-0.5, 0.5 A) vs ≤5 relay coils ≈ 0.15 A worst case +
  logic — ample margin. PWR path connectors are JST XH class (≈3 A/contact) carrying
  audio/low-power rails — no derating concerns at these currents.
- Trace width / copper / thermal items remain `manual_review` until PCB layout exists.

## Manual-review items — ALL RESOLVED same day (2026-07-31)
1. **Relay parts:** all five relays (K201–K204, K301) standardized on Panasonic
   **TQ2-5V** (alt: Hongfa HFD4/5, LCSC C23510, pin-compatible). MPN/Alt_MPN/Value set
   on every symbol; polarized-coil notes added. Also found & fixed: **K301 had no
   flyback diode** — D301 (1N4148) added, matching the D261–D264 convention.
   Coil budget: 8 coils worst-case ≈ 224 mA of the 500 mA +5VAUX regulator.
2. **PS500 ground tie:** input-side grounds split onto their own net **PGND_IN**
   (DC jack J500, TVS500, C500, PS500 pin 1 — verified island) and joined to AGND
   only through **R502 (0R link)**. Populate for single-ground operation; remove to
   restore the module's isolation if hum appears at bring-up.
3. **Clip-mode decoder DESIGNED & CAPTURED** on filter-clipper: a 3-relay mechanical
   decode tree (K401 coil=MODE_B routes CLIP_NODE→W0/W1; K402 coil=MODE_A on W0:
   NC=open/Clean, NO=LED; K403 coil=MODE_A on W1: NC=Si, NO=Ge), reproducing the spec
   truth table 00=Clean 01=Si 10=LED 11=Ge with no ICs or transistors. Flybacks
   D421/D422; NC flags on the Clean dead-ends; all TQ2-5V. Clean mode is now
   mechanically guaranteed (no contact closed). Verified pin-by-pin by the independent
   extractor: zero unexpected merges.
4. **io-board stub cleanup:** 13 pure-floating wire fragments (no pin or label in
   their connected group) removed by scripted pass; remaining dangling-end stubs each
   carry a live pin/label attachment and were kept (prettifying them is a KiCad-UI
   redraw job, purely visual).

## Schematic → PCB sync (2026-07-31, same session)
All six PCBs updated from their schematics after DRC showed the placement scaffolds
were out of sync. Work done:
- **~203 footprint assignments** written into the schematics by class, matching board
  conventions (0603 R/C, CP_Elec_5x5.8 for 10 µF, SOD-123 for the 1N4148 family,
  SOIC-8/14 for OPA1656/OPA1679, TO-126 for BD139/140, 1206 for the 10R emitter
  resistors, BarrelJack for J500).
- **Custom project footprint library created** (`GAS_Parts.pretty` + `fp-lib-table`):
  `Relay_DPDT_Panasonic_TQ2` — geometry verified against the Panasonic TQ catalog
  (10 holes, 2.54 mm pitch, 7.62 mm row spacing; contact sets 2-3-4 / 7-8-9, coil 1/10);
  pad numbers mapped to the KiCad Relay_DPDT symbol convention. NC/NO and coil-polarity
  detail from SamacSys — **bench-verify with one physical relay (continuity check)
  before assembling all 8**. Discovered en route: the stock KiCad EC2 footprint is NOT
  TQ2-compatible (8 pins, 5.08 rows) and HFD4 is a smaller package — Alt-part notes
  corrected accordingly.
- K201–K204's stale Omron G6K SMD footprints replaced with the TQ2 footprint.
- All new footprints placed (no courtyard overlaps on any board): io-board +4,
  crossfade +24, filter-clipper +31 (incl. the clip-decoder relay bank),
  ext-tank +30, power-backplane +2, tank-driver-recovery +88 (channel-grouped grid).
- Post-sync DRC: clean on all six boards (mounting-hole edge overhangs only).
- Unmatched pads are all accounted for: mounting holes, relay mechanical pins,
  K402's intentional Clean dead-ends, K201/K202 unused second poles.

## Still open on the PCB side
1. ~~PS500 footprint~~ **DONE**: custom `GAS_Parts:Converter_DCDC_Mornsun_URA_YMD_THT`
   built from the Mornsun datasheet drawings (both views cross-checked: 2.54 grid,
   rows 20.32 apart, pin1 5.08 from pin2 / 7.62 from pin6, 1.5 mm holes). PS500 synced
   and placed; only pin 6 (Ctrl, intentionally open) unconnected. **Approved alternates
   stamped on PS500** — same industry 1×1 in package: Traco TEN 10-2423WIN,
   CUI PDQ10-D24-D15-D, Mean Well DKMW10F-15, plus LCSC-stocked URA2415YMD clones
   (YLPTEC C5369748 preferred; its pinout matched the Mornsun original).
2. ~~J101–J108 tank landings~~ **FROZEN by Jason 2026-07-31: board-mount RCA jacks.**
   Part: Same Sky (CUI) **RCJ-041** right-angle metal PCB RCA (MPN stamped on all 8
   symbols; colors -042/-043/-044 share the footprint if he wants send/return color
   coding). Custom footprint `GAS_Parts:Jack_RCA_SameSky_RCJ-041_Horizontal` from the
   SamacSys model of the RCJ-04 datasheet (pad 1 = center/signal, pad 2 = shield,
   2 NPTH mounting posts). All 8 synced and placed along the tank board's bottom edge
   (barrels facing off-board), signal+shield pads all netted. Board DRC: 0 errors.
3. TQ2 NC/NO + coil polarity bench check (see above) before full assembly.
4. Placement is a functional scaffold — refine locations during real layout/routing.
5. Cosmetic: 8 "lib footprint mismatch" DRC *warnings* on the jacks (board copies were
   embedded by the sync before minor silkscreen simplifications in the library file) —
   harmless; refresh via Tools→Update Footprints in the UI if desired.

## Pass 3 — visual (by-eye) inspection of all 6 sheets (2026-07-31)
Method: every sheet exported to SVG, rasterized, and inspected as an image — the first
pass in the project where the schematics were literally *looked at*.

Found & FIXED:
1. **Page overflow** — filter-clipper's drive/LPF/buffer stages, ext-tank's right-channel
   summing + U201C/D, and tank-driver's SR sections all rendered *below the A4 frame*
   (invisible in any print/PDF). Paper resized: filter-clipper → **A2 portrait**,
   ext-tank-routing → **A3**, tank-driver-recovery → **A3**. Re-render confirmed all
   content now inside the frame; K403 no longer collides with the title block.
2. **Stale sheet notes memorializing false or outdated conclusions** — every sheet still
   carried "first-pass … still need the next capture pass" text, filter-clipper still
   declared the clip decoder "an open TODO", and io-board's note claimed the PWR_FLAG
   ERC items were "reviewed and judged benign" (disproven in pass 2). All notes and
   title-block comments rewritten to dated, accurate statements pointing here.
3. **Sprawling Notes properties** (P206, PS500, and two others) rendered as giant text
   across the drawings — set to hidden (content preserved in the file + this report).

Checked & cleared:
- The alarming "X" on the power sheet is TVS500's bidirectional-TVS bow-tie glyph —
  correct symbol, correct nets (verified earlier in the PGND_IN island audit).
- K301+D301, the K401–K403 decoder, PS500's corrected pin labels, and R502's ground
  link all render as intended.

Accepted cosmetics (hand-nudge in the KiCad UI at leisure; no electrical content):
- Label text overlapping symbol bodies throughout (label-on-pin capture style).
- io-board / crossfade top decoupling rows straddle the top frame line by ~2 mm.
- TVS500 drawn overlapping P501's zone on the power sheet.

All six boards re-verified after the text/paper edits: parser clean, only the 13
intended aliases, component counts unchanged. Three review passes now complete:
(1) ERC + raw label sweep, (2) independent geometry extraction, (3) visual.

---

## PCB routing — 2026-07-31 (all six boards, 2-layer)

Per Jason's go-ahead ("start routing nonstop", 2-layer, components movable, edge
connectors stay on their edges). Pipeline per board: design rules (0.2 clearance /
0.25 track / 0.8-0.4 via, Power netclass 0.6 track already in each .kicad_pro) →
AGND copper pours on **both** F.Cu and B.Cu (0.3 clearance, inset 0.5 mm) →
Freerouting 2.2.4 → KiCad DRC → **independent connectivity check** (`pcb_check.py`,
a from-scratch parser that unions every pad/track/via per net and confirms no net
is left in disconnected islands — the PCB equivalent of the pass-2 schematic parser).

| Board | Tracks | Vias | DRC errors | DRC warnings | Connectivity |
|---|---|---|---|---|---|
| power-backplane | 80 | 3 | 0 | 0 | all nets complete |
| crossfade-feedback-wet | 218 | 19 | 0 | 10 silk-over-copper | all nets complete |
| ext-tank-routing | 297 | 24 | 0 | 40 silk-over-copper | all nets complete |
| filter-clipper | 374 | 41 | 0 | 30 silk-over-copper | all nets complete |
| io-board | 408 | 43 | 0 | 0 | all nets complete |
| tank-driver-recovery | 946 | 128 | 0 | 8 lib-footprint-mismatch | all nets complete |

Warning notes (all cosmetic, zero electrical impact):
- *silk-over-copper*: reference-designator text printed over copper/pads. Fix by
  nudging silk text in the KiCad UI if desired; fabs accept these as-is.
- *lib-footprint-mismatch* (tank board): the 8 RCA jack copies on the board differ
  from the GAS_Parts library file only in text/format normalization introduced by
  the sync — pads, drills and outlines are identical.

Both AGND pours act as ground planes; the AGND net is carried by the planes plus
stitching vias rather than discrete traces. Freerouting's per-pass "N unrouted"
log lines refer to mid-run state; the imported result was verified complete by
KiCad DRC (0 unconnected-items errors) **and** the independent parser on every board.

Leftover `.dsn` / `.ses` files beside each board are the autorouter's
export/import artifacts — safe to delete or keep.

Still open (unchanged): TQ2 relay NC/NO + coil-polarity one-relay bench continuity
check when parts arrive.

---

## Rev A build change — 2026-08-01: asymmetric clipping via DNP

Per Jason, all three clip networks ship **asymmetric** in Rev A: one diode of each
back-to-back pair is marked **DNP** (do-not-populate). Pads stay on the board;
copper untouched (verified: connectivity checker still reports every net complete,
374 segments / 41 vias unchanged).

- **DNP (leave off):** D401, D403 (Si), D405, D407 (LED), D409, D411 (Ge) —
  these are the cathode-to-line diodes that clipped the NEGATIVE half.
- **Populate:** D402, D404, D406, D408, D410, D412 — anode-to-line, clip the
  POSITIVE half. Same polarity both channels, all modes.

Marked in three places so nothing can drift apart:
1. Schematic: `(dnp yes)` on the six symbols (drawn crossed-out) + a dated note
   on the sheet next to the Clip networks section.
2. PCB: `dnp` attribute on the six footprints (so pos/BOM exports with
   `--exclude-dnp` skip them automatically).
3. `filter-clipper-bom-RevA.csv`: grouped by Value+DNP — DNP parts on their own
   rows, clearly flagged.

Also fixed while in there: U401/U402 sub-units carried mixed Values
(OPA1679 vs OPA1679IDR) which produced a phantom third opamp row in the BOM —
all units unified to OPA1679IDR; BOM now shows exactly 2.

Sonic consequence (see clipper_asymmetric_revA.png): even harmonics (2nd, 4th)
now appear alongside the odd ones; a small DC shift arises when clipping hard —
expect a soft thump on mode switches; a series output cap is the Rev B fix if
it matters in practice. Returning any mode to symmetric = solder the DNP pads.

---

## Post-fill DRC sweep — 2026-08-05 (caught by Jason's file-consistency question)

The original routing-day DRC runs happened while the AGND pours were UNFILLED, so
thermal-relief checks could not run. Re-running DRC with fills present exposed
**42 starved_thermal errors** across 5 boards (crossfade 5, ext-tank 13,
filter-clipper 9, io-board 8, tank 7): ground pads reaching the plane through a
single spoke, one via an isolated island. power-backplane was clean.

**Fix:** both AGND pours on the five boards switched from thermal-relief to
**solid pad connection** (`connect_pads yes`), zones refilled headlessly, boards
saved. Post-fix: **0 DRC errors on all six boards**; only known cosmetic warnings
remain (silk-over-copper; 8 text-format lib mismatches on the RCA jacks).
Independent connectivity checker re-verified all five changed boards — every net
complete, segment/via counts unchanged. Gerber zips in fab-RevA/ regenerated for
the five changed boards (power-backplane zip unchanged).

Note for hand-rework: solid plane connections sink more heat than thermal spokes —
use a hotter iron / more dwell when reworking ground-connected THT pads.

File-status ledger (what "final" means per file type):
- .kicad_pcb / .kicad_sch / .kicad_pro / GAS_Parts.pretty / fp-lib-table: SOURCE
  files, all current and committed.
- fab-RevA/ (gerbers, drill, centroid, BOM, spec sheet): DELIVERABLES, regenerated
  from final sources 2026-08-05.
- *_drc_violations.json: reports, refreshed 2026-08-05 (gitignored, local only).
- .dsn / .ses: one-shot autorouter exchange files from routing day. Not design
  sources; never updated afterward by design; safe to delete.
