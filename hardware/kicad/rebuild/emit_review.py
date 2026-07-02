#!/usr/bin/env python3
"""Emit the kicad-schematic-review skill's output files: datasheet summaries
(datasheet_cache/*.summary.md) and per-instance reviews (review_outputs/*.md).
Content authored from verified datasheet evidence + schematic facts."""
import os

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DS = os.path.join(ROOT, "datasheet_cache")
RO = os.path.join(ROOT, "review_outputs")
os.makedirs(DS, exist_ok=True)
os.makedirs(RO, exist_ok=True)

SUMMARIES = {
"opa1656.summary.md": """# OPA1656 (SOIC-8 dual audio op amp) — datasheet summary
Status: verified (pin table, ROC, cached PDF datasheet_cache/opa1656_eb3ddbf012.pdf)
## Key limits (datasheet text evidence)
- Supply: +/-2.25 V to +/-18 V (4.5-36 V). Design uses +/-15 V: PASS.
- Output current: 100 mA; short-circuit +/-100 mA.
- Iq ~3.9 mA/ch (~7.8 mA/package).
## Pin-level requirements (SOIC-8 dual)
1 OUT_A | 2 IN_A- | 3 IN_A+ | 4 V- | 5 IN_B+ | 6 IN_B- | 7 OUT_B | 8 V+
- V+/V- require local decoupling (100 nF class) per rail.
- CMOS inputs: pA bias; high-value bias resistors (2.2M) acceptable.
""",
"opa1679.summary.md": """# OPA1679 (SOIC-14 quad audio op amp) — datasheet summary
Status: verified (supply range from cached PDF datasheet_cache/opa1679_e09979f1c7.pdf)
- Supply: +/-2.25 V to +/-18 V (4.5-36 V), ~2 mA/ch. +/-15 V used: PASS.
- Output-drive spec not text-extracted: loads in this design are >=10k or
  behind 100-220R isolators (<5 mA) — needs-human-check only for margins.
## Pins (standard quad): 1 OUT_A, 2 IN_A-, 3 IN_A+, 4 V+, 5 IN_B+, 6 IN_B-,
7 OUT_B, 8 OUT_C, 9 IN_C-, 10 IN_C+, 11 V-, 12 IN_D+, 13 IN_D-, 14 OUT_D.
""",
"opa1644.summary.md": """# OPA1644 (SOIC-14 quad JFET audio op amp) — datasheet summary
Status: verified for supply range (cached PDF datasheet_cache/opa1644_652e77ac8c.pdf)
- Supply: +/-2.25 V to +/-18 V. +/-15 V used: PASS. JFET input, pA bias.
- KiCad symbol used: TL074 (identical industry quad pinout as above).
""",
"ura2415ymd.summary.md": """# Mornsun URA2415YMD-10WR3 — datasheet summary
Status: verified (pinout/dimensions read visually from the PDF drawing,
datasheet_cache/ura-ymd-10wr3.pdf p.5; specs from text p.1-4)
- 10 W isolated DC-DC, in 9-36 V (24 V nominal); out +/-15 V, +/-333 mA.
- IMPORTANT: URB variant = single output. URA = dual (BOM corrected).
## Pins (DIP 25.4x25.4, dual-output table): 1 GND(in-), 2 Vin, 3 +Vo,
4 0V(common), 5 -Vo, 6 Ctrl (open = ON; schematic: no_connect) — matches
schematic nets GND_IN/+30V_F/+15VRAW/AGND/-15VRAW/NC: PASS.
- Required externals per datasheet Fig.2 (24 V series, +/-15 V out):
  Cin 100 uF/50 V -> C509 PASS; Cout 10 uF/25 V per rail -> C510/C511 PASS.
- Max capacitive load 330 uF/rail; fitted ~120-130 uF per rail: PASS.
- Ripple 40-80 mVp-p at 350 kHz -> bead+LC filter, sim shows -50 dB: PASS.
""",
"r78e.summary.md": """# RECOM R-78E5.0-0.5 — datasheet summary
Status: verified (text, datasheet_cache/R-78E-0.5_4908d77dcc.pdf)
- Input 7-28 VDC, output 5 V 0.5 A, 7805 pinout (1 Vin, 2 GND, 3 Vout).
- Fed from +15VRAW (review fix F1): inside range, PASS. Load worst-case
  ~210 mA (relay coils): 42% of rating, PASS.
- Externals: input cap C512 10u (added), output C507 47u + C508 100n: PASS.
""",
"g5v2.summary.md": """# Omron G5V-2 (DPDT signal relay) — datasheet summary
Status: partially verified (contact ratings from text; coil table is a
graphic — needs-human-check at order time)
- Contacts: rated 0.5 A/125 VAC, 2 A/30 VDC; carry 2 A. Audio/logic signals
  here are mA-level: PASS with large margin.
- Coils used: DC5 (K201-K204, K401-K403; ~30-40 mA each assumed) and DC12
  (K301, fed from +15VA through R351 240R sized for a ~960R coil).
  ACTION AT ORDER: confirm coil resistance of the exact DC5/DC12 variants;
  if DC12 coil is 720R, R351 -> 150R.
- Pinout used: 1/16 coil; 4 COM1, 6 NC1, 8 NO1; 13 COM2, 11 NC2, 9 NO2
  (KiCad library symbol geometry). NC/NO polarity affects which panel
  position means 'inverted'/mode — bench-verify once, swap wires if flipped.
""",
"jst-xh.summary.md": """# JST XH connector family — datasheet summary
Status: verified (rating block read visually, datasheet_cache/eXH_98b6fe789a.pdf p.1)
- 3 A AC/DC (AWG#22), 250 V, contact R 10 mOhm initial, wire 30-22 AWG.
- Worst path on XH here: +30 V DC input landing P500 ~0.36 A = 12%: PASS.
  Tank sends ~65 mA pk, audio signals lower: PASS.
""",
"jst-vh.summary.md": """# JST VH connector family — datasheet summary
Status: verified (rating block read visually, datasheet_cache/eVH_35d0fc229b.pdf p.1)
- 10 A (AWG#16) / 7 A (AWG#18), 250 V. Rails carry <=0.25 A/pin: <4%: PASS.
""",
"bd139-bd140.summary.md": """# BD139-16 / BD140-16 (TO-126 complementary pair)
Status: manual_review — ST datasheet fetch timed out twice; ratings below are
industry-standard values, NOT verified against a cached datasheet.
- Typical family ratings: 80 V, 1.5 A, 12.5 W (heatsink-dependent).
- Circuit stress (from verified simulation): ~65 mA pk into 8R tank,
  dissipation <0.7 W/device on +/-15 V rails: consistent, wide margin.
- ACTION: cache the ST datasheet and confirm SOA + hFE bin before the
  production spin.
""",
}

def inst(name, part, board, summary, rows, externals, findings="None."):
    tbl = "\n".join("| %s | %s | %s | %s |" % r for r in rows)
    return """# Instance review: %s (%s, %s)
Datasheet summary: datasheet_cache/%s

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
%s

## Required externals
%s

## Findings
%s

Evidence: extracted JSON (rebuild/review-extract-%s.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
""" % (name, part, board, summary, tbl, externals, findings, board)

INSTANCES = {
# --- tank-driver-recovery
"tdr-U101.md": inst("U101", "OPA1656", "tank-driver-recovery", "opa1656.summary.md",
    [("1/2/3 (A)", "PRI_DRV_L / N_PRI_L_M / N_PRI_L_P", "left primary predriver, fb post-follower", "pass"),
     ("5/6/7 (B)", "N_PRI_R_P / N_PRI_R_M / PRI_DRV_R", "right primary predriver", "pass"),
     ("8 / 4", "+15VA / -15VA", "within +/-18 V abs max", "pass")],
    "C291/C295 100n at rails: pass. Base drive ~0.7 mA vs 100 mA capability: pass."),
"tdr-U102-U104.md": inst("U102-U104", "OPA1656 x3", "tank-driver-recovery", "opa1656.summary.md",
    [("U102 A/B", "SEC sends, gain 2.2 into 800R tanks", "sim: 1.04 Vpk out", "pass"),
     ("U103/U104 A/B", "recovery, gain 34, 2.2M bias to AGND", "CMOS pA bias: OK", "pass"),
     ("power units", "+15VA/-15VA + 100n each", "decoupling present", "pass")],
    "Recovery offset x34 -> ~17 mV DC downstream (bench note, see final report)."),
"tdr-Q101-Q104.md": inst("Q101-Q104", "BD139-16/BD140-16", "tank-driver-recovery", "bd139-bd140.summary.md",
    [("B/C/E", "base stoppers 68R; C to rails; 0.33R emitters to PRI_OUT", "class-B in-loop", "pass (sim)"),
     ("bias reserve", "D101/D102/D121/D122 DNP", "spec-frozen reserve", "pass")],
    "Datasheet not cached: dissipation margin is schematic+sim consistency only.",
    "manual_review: verify SOA/hFE bin from ST datasheet before production."),
"tdr-power-path.md": inst("tank cable + harness paths", "JST XH/VH", "tank-driver-recovery", "jst-xh.summary.md",
    [("J101-J108 (XH2)", "tank sends/returns", "~65 mA pk vs 3 A", "pass"),
     ("P101/P102 (XH6)", "audio harness", "mA-level vs 3 A", "pass"),
     ("P103 (VH3)", "+/-15 V feed", "~0.15 A vs 10 A", "pass")],
    "Shield bond network R205/C191/R206 present on returns: pass."),
# --- power backplane
"pwr-PS500.md": inst("PS500", "URA2415YMD-10WR3", "power-backplane", "ura2415ymd.summary.md",
    [("1 GND", "GND_IN", "input return", "pass"),
     ("2 Vin", "+30V_F (post Schottky+PTC+TVS+bulk)", "9-36 V range", "pass"),
     ("3/4/5", "+15VRAW / AGND / -15VRAW", "dual-output mapping", "pass"),
     ("6 Ctrl", "no_connect", "open = ON per datasheet", "pass")],
    "Cin 100u (C509): pass. Cout 10u/rail (C510/C511): pass. Cap load 130u < 330u max: pass.",
    "URB->URA part correction captured in BOM and readiness report."),
"pwr-PS501.md": inst("PS501", "R-78E5.0-0.5", "power-backplane", "r78e.summary.md",
    [("1 Vin", "+15VRAW (review fix F1)", "7-28 V range", "pass"),
     ("2 GND", "AGND", "", "pass"),
     ("3 Vout", "+5VAUX", "0.5 A vs ~0.21 A worst", "pass")],
    "C512 10u input (added), C507 47u + C508 100n output: pass."),
"pwr-entry-path.md": inst("DC entry path", "P500/D500/F500/TVS500/C500", "power-backplane", "jst-xh.summary.md",
    [("P500 XH2", "+30V_RAW/GND_IN", "0.36 A vs 3 A (12%)", "pass"),
     ("D500 SS34", "series reverse protection", "3 A schottky, 0.4 V drop", "pass (rating from family spec, needs-human-check)"),
     ("F500 PTC 1.1A", "hold > 0.36 A load, trips on fault", "adapter limit is primary protection", "pass"),
     ("TVS500 SMAJ33A", "33 V standoff > 30 V rail", "verify adapter open-circuit <34 V (bench P-0)", "pass"),
     ("inrush", "320 uF bulk vs 0.5 A-limited adapter", "PTC hold not exceeded in steady state", "pass (note)")],
    "Star tie R500 0R GND_IN->AGND single-point: pass."),
# --- crossfade
"xfade-U301.md": inst("U301", "OPA1679", "crossfade-feedback-wet", "opa1679.summary.md",
    [("A/B", "crossfade summers, unity inverting", "sim exact", "pass"),
     ("C/D", "feedback drivers, gain 0.5 per input", "loop floor 10k", "pass"),
     ("4/11", "+15VA/-15VA + C391/C392", "", "pass")],
    "C321/C322 47p DNP stability slots present: pass."),
"xfade-K301.md": inst("K301", "G5V-2 DC12", "crossfade-feedback-wet", "g5v2.summary.md",
    [("coil 1/16", "+15VA via R351 240R -> CTL_FB_INV (panel switch to GND)", "~12.5 mA switch current", "pass"),
     ("pole1/2", "NC=FILTCLIP (normal), NO=FB_INV (inverted)", "de-energized = normal", "pass"),
     ("D301", "flyback across coil", "cathode to +15 side", "pass")],
    "Contact load is line-level audio: pass.",
    "needs-human-check: confirm DC12 coil resistance at order (R351 sizing)."),
# --- filter
"filt-U401-U402.md": inst("U401/U402", "OPA1679 x2", "filter-clipper", "opa1679.summary.md",
    [("U401 A/B", "HPF buffers (47n + pot rheostat)", "fc 33 Hz-3.4 kHz", "pass (sim)"),
     ("U401 C/D", "drive 4.9x fixed", "sim exact", "pass"),
     ("U402 A/B", "LPF buffers (pot series + 10n)", "fc 157 Hz-16 kHz", "pass (sim)"),
     ("U402 C/D", "output buffers + 100R isolators", "", "pass"),
     ("power units", "+/-15 V + 100n x4 + 22u x2", "", "pass")],
    "Audio-path caps are film-footprint (1210 ECHU class): policy pass."),
"filt-clip-decode.md": inst("K401-K403 + diodes", "G5V-2 DC5, 1N4148W/LED/1N5819HW", "filter-clipper", "g5v2.summary.md",
    [("truth 00/01/10/11", "clean/Si/LED/Schottky via contact tree", "traced pin-by-pin", "pass"),
     ("coils", "CTL_CLIP_MODE_A (1 coil), _B (2 coils ~60-80 mA)", "switched +5VAUX lines", "pass"),
     ("flybacks D421/D422", "one per mode line", "shared-line clamping OK", "pass"),
     ("clip floor", "diode returns -> DRV_HI pot landing", "shared pot: L/R clip-current interaction", "warning (bench)")],
    "LED clip current ~2.6 mA max: pass.",
    "warning: when both channels clip hard, small L/R interaction through the shared clip-floor pot; inherent to the frozen 3-wire drive landing."),
# --- ext routing
"ext-U201-relays.md": inst("U201 + K201-K204", "OPA1679 + G5V-2 DC5", "ext-tank-routing", "g5v2.summary.md",
    [("U201 A/B", "final summers (pri + scaled sec + feedback)", "sim exact", "pass"),
     ("U201 C/D", "secondary send followers + DNP gain slots", "park 100k in bypass", "pass"),
     ("mode truth", "Off/Series/Parallel per freeze", "traced pin-by-pin + sim (Series/Off)", "pass"),
     ("coils", "A line 2 coils, B line 2 coils (~60-80 mA each line)", "rotary-switched +5VAUX", "pass")],
    "Flybacks D261/D262 per mode line: pass."),
# --- io board
"io-U1-U4.md": inst("U1-U4", "OPA1644 (TL074 sym) + OPA1656 x3", "io-board", "opa1644.summary.md",
    [("U1 A/B", "unity diff receivers, 4x10k 0.1%", "CMRR by matching", "pass"),
     ("U1 C/D", "program buffers; U1D+ from MONO_C + R25 1M bleed (fix F2)", "no float with center-off switch", "pass"),
     ("U2 A/B", "inverting blend buffers 20k/20k", "sim exact", "pass"),
     ("U3/U4", "hot follower + cold inverter, 49.9R build-outs", "23 mA pk into 600R vs 100 mA", "pass"),
     ("power units", "+/-15 V, 100n x8, 22u x2", "", "pass")],
    "RF clamp C1-C4 220p DNP per spec deferral: pass.",
    "Note: absolute polarity inverted end-to-end (inverting blend per spec); swap hot/cold at drivers later if desired."),
"io-jack-path.md": inst("J1-J4 landings + panel jacks", "XH3 landings -> NCJ6FI-S", "io-board", "jst-xh.summary.md",
    [("J1-J4 XH3", "P/N/AGND per jack", "line-level: mA", "pass"),
     ("panel wiring", "XLR2/T->P, XLR3/R->N, XLR1/S/G->AGND", "off-board harness step", "manual_review (assembly)")],
    "Combo jacks are hand-installed panel parts (Panel-DNP scope)."),
}

for name, text in SUMMARIES.items():
    with open(os.path.join(DS, name), "w", encoding="utf-8") as f:
        f.write(text)
for name, text in INSTANCES.items():
    with open(os.path.join(RO, name), "w", encoding="utf-8") as f:
        f.write(text)
print("wrote", len(SUMMARIES), "summaries,", len(INSTANCES), "instance reviews")
