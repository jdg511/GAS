# Rev A Cost Summary

This is a quick cost snapshot from the current priced/reference BOM layers.

## Scope

These totals are not a full manufactured product quote.

They are only a snapshot of:

- the core active/SMD layer
- connector/harness references
- passive reference families
- panel/mechanical references where a current price was available

## Core SMD BOM

Source:

- [rev-a-core-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-core-priced-bom.csv:1)

Current extended total:

- about `USD 82.86`

Notes:

- includes the added `OPA1656IDR` now required for a fully active stereo balanced output stage
- includes the preferred direct-coupled primary send transistor pair
- still includes the `LM386MX-1/NOPB` only as a fallback reference
- the fixed-part pricing snapshot was refreshed on `2026-06-29`; the main delta versus the prior snapshot is `OPA1644AIDR` moving to `USD 4.65`
- the internal `Mean Well RT-50C` AC/DC module is gone; replaced by a `+24VDC` external wall-adapter strategy plus the on-board conversion stack: `Triad WSU240-0750` regulated adapter (`+12.43`, DigiKey `2026-07-04`), `Mornsun URA2415YMD-10WR3` DC-DC (`+9.27`), `RECOM R-78E5.0-0.5` +5V regulator (`+3.37`), and `Same Sky PJ-005A` DC jack (`+3.07`). Net `+5.33` versus the `2026-06-29` power-entry snapshot; rollup totals below not yet refreshed for this delta. See [rev-a-external-dc-power.md](../rev-a-external-dc-power.md)

## Connector / Harness Reference BOM

Source:

- [rev-a-connectors-and-harness-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-connectors-and-harness-reference-bom.csv:1)

Current extended total:

- about `USD 11.72`

Notes:

- this is an internal harness reference estimate, not a cut-to-length finished cable quote
- the latest update reflects the split between five 3-pin VH power links and one 4-pin VH power link for the ext-routing board

## Common Passives Reference BOM

Source:

- [rev-a-common-passives-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-common-passives-reference-bom.csv:1)

Current extended total:

- about `USD 50.16`

Notes:

- includes both audio-path film-family references and power-path decoupling references
- these are representative reference parts, not yet the full final passive population

## Panel / Mechanical Reference BOM

Source:

- [rev-a-panel-and-mechanical-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-and-mechanical-reference-bom.csv:1)

Visible priced subtotal:

- about `USD 49.74`

Notes:

- the alternate combo jack entry is not priced and is therefore not counted
- the user-supplied enclosure tube is intentionally outside this subtotal
- this is still not a full enclosure quote

## Panel Controls Priced BOM

Source:

- [rev-a-panel-controls-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-controls-priced-bom.csv:1)

Current extended total:

- about `USD 42.47`
- plus about `EUR 16.46`

Notes:

- with `EUR 1 = USD 1.07`, that is about `USD 60.08`
- this is a good reminder that the endcap control layer is a meaningful share of the build cost

## Control Backplane Hard-Parts Companion

Source:

- [rev-a-control-backplane-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-control-backplane-priced-bom.csv:1)

Current priced subtotal:

- about `USD 1.80` for the currently assumed populated baseline
- about `USD 2.71` if the reserve-only `U601` is included for contingency quoting

Notes:

- this layer remains outside the six-board hard-part subtotal because the current package still treats the control-backplane landing board as optional / deferred relative to the main electrical set
- the grouped-control placeholder caveats still apply to `P612-P614`

## What Is Still Outside These Totals

- the four spring tanks
- final passive population for all boards
- actual PCB fabrication cost
- actual SMT assembly labor
- endcap finishing, bracket fabrication, and any custom rail hardware beyond the reference BOM
- knobs, wiring labor, and final bench calibration

## Practical Interpretation

Even at this stage, the priced documentation shows a consistent pattern:

- the core electronics are not the dominant project cost
- the mechanical build, tanks, assembly, and tuning will likely outweigh the raw semiconductor spend
