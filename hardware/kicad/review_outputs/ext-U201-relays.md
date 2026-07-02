# Instance review: U201 + K201-K204 (OPA1679 + G5V-2 DC5, ext-tank-routing)
Datasheet summary: datasheet_cache/g5v2.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| U201 A/B | final summers (pri + scaled sec + feedback) | sim exact | pass |
| U201 C/D | secondary send followers + DNP gain slots | park 100k in bypass | pass |
| mode truth | Off/Series/Parallel per freeze | traced pin-by-pin + sim (Series/Off) | pass |
| coils | A line 2 coils, B line 2 coils (~60-80 mA each line) | rotary-switched +5VAUX | pass |

## Required externals
Flybacks D261/D262 per mode line: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-ext-tank-routing.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
