# BOM Package

The rev-A hardware package now uses multiple BOM layers on purpose.

## Files

- `rev-a-core-priced-bom.csv`
  - common SMD active devices plus the external-DC / on-board-conversion power core
- `rev-a-preliminary-board-boms.md`
  - index for the per-board population/BOM starter files used during schematic capture
- `rev-a-board-priced-summary.md`
  - index and subtotal summary for board-by-board priced hard-part BOM companions
- `rev-a-control-backplane-priced-bom.csv`
  - priced hard-part companion for the optional / deferred control-backplane landing layer
- `rev-a-procurement-snapshot.md`
  - current exact-part sourcing snapshot with assembly-scope split and current vendor links
- `rev-a-common-passives-reference-bom.csv`
  - representative critical passive/device families with current pricing, aligned to the non-ceramic audio-path capacitor preference
- `rev-a-connectors-and-harness-reference-bom.csv`
  - internal board-to-board connector families and harness references
- `rev-a-panel-and-mechanical-reference-bom.csv`
  - combo jacks and panel/mechanical reference parts
- `rev-a-bom-notes.md`
  - explains what is locked and what still needs bench tuning
- `rev-a-common-smd-policy.md`
  - gives the builder-friendly passive substitution policy
- `rev-a-supply-watch.md`
  - approved alternates and the current common-parts sourcing direction
- `../rev-a-capacitor-policy.md`
  - documents the capacitor-avoidance preference and how to treat exceptions

## Why It Is Split

This project has three distinct procurement realities:

1. common SMD parts the board house can place
2. internal harness and connector parts
3. external mechanical parts and spring tanks

Splitting the BOM this way makes quoting cleaner and keeps the first prototype build realistic.

There are also two capture/quote-support layers:

4. board-level preliminary population files
5. board-level priced fixed-parts quote companions
6. current fixed-part procurement snapshot for builder/vendor use

Those files are there to keep the actual schematic capture organized.
