# Instance review: tank cable + harness paths (JST XH/VH, tank-driver-recovery)
Datasheet summary: datasheet_cache/jst-xh.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| J101-J108 (XH2) | tank sends/returns | ~65 mA pk vs 3 A | pass |
| P101/P102 (XH6) | audio harness | mA-level vs 3 A | pass |
| P103 (VH3) | +/-15 V feed | ~0.15 A vs 10 A | pass |

## Required externals
Shield bond network R205/C191/R206 present on returns: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-tank-driver-recovery.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
