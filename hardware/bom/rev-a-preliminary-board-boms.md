# Rev A Preliminary Board BOMs

These per-board BOM files are not the same thing as the priced sourcing BOM package.

Their purpose is to make schematic capture easier by assigning:

- reference designator groups
- core IC population per board
- connector population per board
- which passive sets remain to be tuned

## Files

- `rev-a-input-output-preliminary-bom.csv`
- `rev-a-tank-driver-recovery-preliminary-bom.csv`
- `rev-a-ext-routing-preliminary-bom.csv`
- `rev-a-crossfade-feedback-preliminary-bom.csv`
- `rev-a-filter-clipper-preliminary-bom.csv`
- `rev-a-power-backplane-preliminary-bom.csv`

Related priced fixed-parts companions:

- [rev-a-board-priced-summary.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-board-priced-summary.md:1)

## How To Use Them

During KiCad capture:

1. instantiate the fixed active and connector parts first
2. assign the refdes groups from these files and from [../rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1)
3. fill in passive designators as each circuit is captured
4. replace the generic `R*` and `C*` set notes with actual values once the sheet is real
