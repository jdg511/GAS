# Instance review: K301 (G5V-2 DC12, crossfade-feedback-wet)
Datasheet summary: datasheet_cache/g5v2.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| coil 1/16 | +15VA via R351 240R -> CTL_FB_INV (panel switch to GND) | ~12.5 mA switch current | pass |
| pole1/2 | NC=FILTCLIP (normal), NO=FB_INV (inverted) | de-energized = normal | pass |
| D301 | flyback across coil | cathode to +15 side | pass |

## Required externals
Contact load is line-level audio: pass.

## Findings
needs-human-check: confirm DC12 coil resistance at order (R351 sizing).

Evidence: extracted JSON (rebuild/review-extract-crossfade-feedback-wet.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
