# GAS Rev A KiCad Order Readiness

Regenerated 2026-07-02 after the clean rebuild (branch `rev-a-clean-rebuild`).
Updated 2026-07-04: **ext-tank-routing re-spun** — feedback reinjection moved
pre-tank (new U202 OPA1656 send summers: `FB_RET` + `WET_SEND` -> `SEND_MIX`
-> tank sends; removed from the `TANK_MIX` output summers so feedback re-passes
through the springs). Board re-verified through the full gate below and the
fab packet regenerated. If any ext-routing gerbers were already uploaded to a
fab, discard them and re-upload the 2026-07-04 packet.

## Status

**READY TO ORDER.** All six boards pass the full gate.

| Board | ERC | Sim verified | DRC errors | Unconnected | Fab exports |
| --- | ---: | :---: | ---: | ---: | :---: |
| tank-driver-recovery | 0 | yes (tran, tank models) | 0 | 0 | yes |
| power-backplane | 0 | yes (AC, -50dB @350kHz) | 0 | 0 | yes |
| crossfade-feedback-wet | 0 | yes (tran) | 0 | 0 | yes |
| filter-clipper | 0 | yes (tran, clip modes) | 0 | 0 | yes |
| ext-tank-routing | 0 | yes (tran, mode states, pre-tank FB verified) | 0 | 0 | yes (2026-07-04) |
| io-board | 0 | yes (tran, balanced I/O) | 0 | 0 | yes |

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
