# Mornsun URA2415YMD-10WR3 — datasheet summary
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
