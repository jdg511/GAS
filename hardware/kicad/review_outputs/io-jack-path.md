# Instance review: J1-J4 landings + panel jacks (XH3 landings -> NCJ6FI-S, io-board)
Datasheet summary: datasheet_cache/jst-xh.summary.md

| Pin/Group | Net | Check | Result |
| --- | --- | --- | --- |
| J1-J4 XH3 | P/N/AGND per jack | line-level: mA | pass |
| panel wiring | XLR2/T->P, XLR3/R->N, XLR1/S/G->AGND | off-board harness step | manual_review (assembly) |

## Required externals
Combo jacks are hand-installed panel parts (Panel-DNP scope).

## Findings
None.

Evidence: extracted JSON (rebuild/review-extract-io-board.json), raw .kicad_sch
spot-check, datasheet summary above, verified ngspice run. Confidence: high
unless noted.
