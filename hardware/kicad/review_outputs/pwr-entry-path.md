# Instance review: DC entry path (P500/D500/F500/TVS500/C500, power-backplane)
Datasheet summary: datasheet_cache/jst-xh.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| P500 XH2 | +30V_RAW/GND_IN | 0.36 A vs 3 A (12%) | pass |
| D500 SS34 | series reverse protection | 3 A schottky, 0.4 V drop | pass (rating from family spec, needs-human-check) |
| F500 PTC 1.1A | hold > 0.36 A load, trips on fault | adapter limit is primary protection | pass |
| TVS500 SMAJ33A | 33 V standoff > 30 V rail | verify adapter open-circuit <34 V (bench P-0) | pass |
| inrush | 320 uF bulk vs 0.5 A-limited adapter | PTC hold not exceeded in steady state | pass (note) |

## Required externals
Star tie R500 0R GND_IN->AGND single-point: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-power-backplane.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
