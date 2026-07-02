# Instance review: K401-K403 + diodes (G5V-2 DC5, 1N4148W/LED/1N5819HW, filter-clipper)
Datasheet summary: datasheet_cache/g5v2.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| truth 00/01/10/11 | clean/Si/LED/Schottky via contact tree | traced pin-by-pin | pass |
| coils | CTL_CLIP_MODE_A (1 coil), _B (2 coils ~60-80 mA) | switched +5VAUX lines | pass |
| flybacks D421/D422 | one per mode line | shared-line clamping OK | pass |
| clip floor | diode returns -> DRV_HI pot landing | shared pot: L/R clip-current interaction | warning (bench) |

## Required externals
LED clip current ~2.6 mA max: pass.

## Findings
warning: when both channels clip hard, small L/R interaction through the shared clip-floor pot; inherent to the frozen 3-wire drive landing.

Evidence: extracted JSON (rebuild/review-extract-filter-clipper.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
