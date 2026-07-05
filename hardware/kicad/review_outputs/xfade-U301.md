# Instance review: U301 (OPA1679, crossfade-feedback-wet)
Datasheet summary: datasheet_cache/opa1679.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| A/B | crossfade summers, unity inverting | sim exact | pass |
| C/D | feedback drivers, gain 0.5 per input | loop floor 10k | pass |
| 4/11 | +15VA/-15VA + C391/C392 |  | pass |

## Required externals
C321/C322 47p DNP stability slots present: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-crossfade-feedback-wet.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
