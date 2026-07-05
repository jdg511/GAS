# Instance review: U101 (OPA1656, tank-driver-recovery)
Datasheet summary: datasheet_cache/opa1656.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| 1/2/3 (A) | PRI_DRV_L / N_PRI_L_M / N_PRI_L_P | left primary predriver, fb post-follower | pass |
| 5/6/7 (B) | N_PRI_R_P / N_PRI_R_M / PRI_DRV_R | right primary predriver | pass |
| 8 / 4 | +15VA / -15VA | within +/-18 V abs max | pass |

## Required externals
C291/C295 100n at rails: pass. Base drive ~0.7 mA vs 100 mA capability: pass.

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-tank-driver-recovery.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
