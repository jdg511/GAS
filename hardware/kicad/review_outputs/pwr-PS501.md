# Instance review: PS501 (R-78E5.0-0.5, power-backplane)
Datasheet summary: datasheet_cache/r78e.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| 1 Vin | +15VRAW (review fix F1) | 7-28 V range | pass |
| 2 GND | AGND |  | pass |
| 3 Vout | +5VAUX | 0.5 A vs ~0.21 A worst | pass |

## Required externals
C512 10u input (added), C507 47u + C508 100n output: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-power-backplane.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
