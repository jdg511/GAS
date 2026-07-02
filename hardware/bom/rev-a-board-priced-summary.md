# Rev A Board-Priced Fixed-Parts Summary

These files complement the preliminary board BOMs by adding current pricing and source links for the **fixed hard parts** that are already well enough defined to quote.

They are intentionally **not** full production BOMs.

What they include well:

- op amps
- relays
- transistors
- defined power modules
- defined JST headers
- panel DNP hardware where it is already fixed enough to cost

What they still do **not** pretend to freeze:

- tuned resistor/capacitor populations
- final control-header implementation where the control-backplane decision still affects pin count
- tank RCA landing hardware where the final mechanical connector method is still open

## Files

- [rev-a-input-output-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-input-output-priced-bom.csv:1)
- [rev-a-ext-routing-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-ext-routing-priced-bom.csv:1)
- [rev-a-crossfade-feedback-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-crossfade-feedback-priced-bom.csv:1)
- [rev-a-filter-clipper-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-filter-clipper-priced-bom.csv:1)
- [rev-a-tank-driver-recovery-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-tank-driver-recovery-priced-bom.csv:1)
- [rev-a-power-backplane-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-power-backplane-priced-bom.csv:1)
- [rev-a-control-backplane-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-control-backplane-priced-bom.csv:1)

## Current Fixed-Parts Subtotals

These are the priced hard-part subtotals from the CSVs above.

| Board | Fixed-parts subtotal | Notes |
|---|---:|---|
| Input / Output | `USD 33.44` | includes combo jacks as panel DNP references |
| Ext Routing | `USD 21.26` | does not price `P206` because control-landing format is not frozen |
| Crossfade / Feedback / Wet | `USD 2.50` | does not price `P307` because control-landing format is not frozen |
| Filter / Clipper | `USD 3.57` | does not price `P403/P405` and does not pretend clip-diode family is fully frozen |
| Tank Driver / Recovery | `USD 18.69` | excludes final tank landing hardware and tuned passive set |
| Power Backplane | `USD 20.66` | excludes unpriced protection/decoupling passives even though topology is defined |
| **Total fixed priced hard parts across 6 boards** | **`USD 100.12`** | before tuned passives, harness consumables, and assembly |

Optional adjunct:

| Board / Layer | Fixed-parts subtotal | Notes |
|---|---:|---|
| Control Backplane landing layer | `USD 1.80` populated baseline, `USD 2.71` with reserve `U601` included | separate from the six-board electrical set; grouped-control headers still carry known placeholder caveats |

## Practical Use

Use these files when:

1. asking a builder for a first-pass per-board quote
2. checking whether one board's hard-part cost is drifting unexpectedly
3. splitting panel DNP parts from house-placed SMD parts

Use the older preliminary board BOMs when:

1. capturing the actual schematic
2. assigning refdes ranges
3. filling in the tuned passive population later
