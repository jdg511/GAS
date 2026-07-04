# GAS Rev A KiCad Order Readiness

Regenerated 2026-07-02 after the clean rebuild (branch `rev-a-clean-rebuild`).
Updated 2026-07-04: **ext-tank-routing re-spun** — feedback reinjection moved
pre-tank (new U202 OPA1656 send summers: `FB_RET` + `WET_SEND` -> `SEND_MIX`
-> tank sends; removed from the `TANK_MIX` output summers so feedback re-passes
through the springs). Board re-verified through the full gate below and the
fab packet regenerated. If any ext-routing gerbers were already uploaded to a
fab, discard them and re-upload the 2026-07-04 packet.

Updated 2026-07-04 (pm), after the independent pre-order review
([../rev-a-preorder-double-check.md](../rev-a-preorder-double-check.md)):

1. **io-board AGND island fixed.** An orphan stitching via at
   (117.102, 96.479) plus keep-islands zone fill left floating AGND copper
   in the exported gerbers. Via removed, both AGND zones set to
   island-removal = always, refilled, DRC re-run to 0 errors / 0
   unconnected, gerbers + drill + pos re-exported and re-zipped.
   **If io-board gerbers were uploaded before 2026-07-04 pm, discard and
   re-upload.**
2. **All six BOM CSVs regenerated with the DNP column** (five were missing
   it; assembly would have populated the DNP-reserved parts, including the
   tank-driver bias diodes D101/D102/D121/D122).
3. **Clip-mode +5V wiring decision recorded** (open issue #9): rev A uses a
   panel jumper from the ext-mode rotary 5V bus to the clip rotary common;
   filter `P405.9` is a sourceless spare. H33 + connector schedule updated.
   Rev-B PCB fix recorded (4-pin `P404`/`P504`).
4. **Fresh full gate on all six boards** (ERC + DRC with
   `--severity-all --schematic-parity`, KiCad 10.0.3): 0 ERC violations,
   0 DRC errors, 0 unconnected on every board. Remaining warnings are
   silkscreen/co-located-hole cosmetics plus benign parity nags (symbol
   Tolerance/Sim.* fields not mirrored in footprints; H1-H4 mounting holes
   have no schematic symbols).
5. **Superseded reports archived** to `archive/superseded-reports/`; the
   abandoned hierarchical top level (`GAS-Hardware.*`, 303 known ERC
   errors, superseded by the per-board projects) moved to
   `archive/abandoned-top-level/`.

## Status

**READY TO ORDER.** All six boards pass the full gate (evidence:
`rebuild/<tag>-erc.json` + `rebuild/<tag>-drc.json`, 2026-07-04 pm).

| Board | ERC | Sim verified | DRC errors | Unconnected | Fab exports |
| --- | ---: | :---: | ---: | ---: | :---: |
| tank-driver-recovery | 0 | yes (tran, tank models) | 0 | 0 | yes |
| power-backplane | 0 | yes (AC, -50dB @350kHz) | 0 | 0 | yes |
| crossfade-feedback-wet | 0 | yes (tran) | 0 | 0 | yes |
| filter-clipper | 0 | yes (tran, clip modes) | 0 | 0 | yes |
| ext-tank-routing | 0 | yes (tran, mode states, pre-tank FB verified) | 0 | 0 | yes (2026-07-04) |
| io-board | 0 | yes (tran, balanced I/O) | 0 | 0 | yes (2026-07-04 pm) |

Remaining violations are silkscreen-class warnings only (cosmetic).

## Where everything lives

- Production schematics + boards: `hardware/kicad/*.kicad_sch|_pcb`
- Simulation testbenches (open in KiCad -> Inspect -> Simulator):
  `hardware/kicad/sim/<board>-sim/`
- Fabrication packet: `hardware/kicad/fab/` (see `ORDER-PACKET.md`)
- Generators (single source of truth — edit these, never the .kicad files):
  `hardware/kicad/rebuild/gen_*.py`, router pipeline `route_board.py`

## Part corrections made during the rebuild

1. DC-DC module is **URA**2415YMD-10WR3 (dual +/-15V). The previous BOM's
   URB2415YMD-10WR3 is the single-output 15V part and would not have worked.
2. Feedback-phase selection (crossfade board) and clip-mode decode
   (filter board) had no switching hardware in the old BOM; G5V-2 relays
   were added (K301; K401-K403).
3. Ext-routing relays standardized from G6K-2F-Y to G5V-2 DC5 (KiCad-native
   footprint, one relay type across the whole unit).

## Superseded

The old `test-rev-a-order-readiness.ps1` gate script predates the per-board
project structure and reports against the abandoned hierarchical capture;
this file and the DRC/ERC JSON reports in `hardware/kicad/rebuild/` are the
current gate evidence.
