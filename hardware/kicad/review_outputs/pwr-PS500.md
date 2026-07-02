# Instance review: PS500 (URA2415YMD-10WR3, power-backplane)
Datasheet summary: datasheet_cache/ura2415ymd.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| 1 GND | GND_IN | input return | pass |
| 2 Vin | +30V_F (post Schottky+PTC+TVS+bulk) | 9-36 V range | pass |
| 3/4/5 | +15VRAW / AGND / -15VRAW | dual-output mapping | pass |
| 6 Ctrl | no_connect | open = ON per datasheet | pass |

## Required externals
Cin 100u (C509): pass. Cout 10u/rail (C510/C511): pass. Cap load 130u < 330u max: pass.

## Findings
URB->URA part correction captured in BOM and readiness report.

Evidence: extracted JSON (rebuild/review-extract-power-backplane.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
