# Instance review: U1-U4 (OPA1644 (TL074 sym) + OPA1656 x3, io-board)
Datasheet summary: datasheet_cache/opa1644.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| U1 A/B | unity diff receivers, 4x10k 0.1% | CMRR by matching | pass |
| U1 C/D | program buffers; U1D+ from MONO_C + R25 1M bleed (fix F2) | no float with center-off switch | pass |
| U2 A/B | inverting blend buffers 20k/20k | sim exact | pass |
| U3/U4 | hot follower + cold inverter, 49.9R build-outs | 23 mA pk into 600R vs 100 mA | pass |
| power units | +/-15 V, 100n x8, 22u x2 |  | pass |

## Required externals
RF clamp C1-C4 220p DNP per spec deferral: pass.

## Findings
Note: absolute polarity inverted end-to-end (inverting blend per spec); swap hot/cold at drivers later if desired.

Evidence: extracted JSON (rebuild/review-extract-io-board.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
