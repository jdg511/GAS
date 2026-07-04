# Review: io-board AGND orphan island (2026-07-04)

Instance: io-board.kicad_pcb F.Cu AGND zone | Severity: medium | Confidence: high
Evidence: rebuild/io-drc.json (05:06:52, 1 unconnected error, zone uuid
79aa02c5, pos ~31/31 header — island located by audit at x≈117.1 y≈96.5);
file mtimes (board saved 05:07:17, after DRC; gerbers 05:10); independent
copper connectivity audit of the saved board; flash present in
fab/io-board/gerbers/io-board-F_Cu.gtl at X117.10/Y-96.48.

## Finding

- The F.Cu AGND zone fills as two islands. The minority island (one via +
  two small zone slivers near x=117.1, y=96.5) carries no pads.
- The board was re-saved after the last DRC, and gerbers were exported from
  the newer save, so "DRC 0 unconnected" was never demonstrated for the
  shipped file; my audit shows the island is still present in it.
- Electrical impact: low (floating sliver, no floating component pads);
  process impact: real DRC error in the gate, wrong row in
  rev-a-order-readiness.md.

## Recommendation

Set min-island removal (or stitch the sliver) on the F.Cu AGND zone, refill,
re-run DRC to 0/0, re-export io-board gerbers, update the readiness table.
All other five boards: my connectivity audit confirms zero split nets in the
saved copper — their gerber packets stand.
