# GAS Rev A Total Cost Roll-Up

A single-unit build cost estimate that combines every priced layer in the package. This rolls up [rev-a-cost-summary.md](bom/rev-a-cost-summary.md) and adds the remaining categories that summary explicitly excludes.

All figures are USD per unit, single-prototype quantity. Currency conversions use `EUR 1 = USD 1.07`.

## Bill of materials totals

| Layer | Source | Low | Mid | High |
|---|---|---|---|---|
| Core active / SMD parts | [rev-a-core-priced-bom.csv](bom/rev-a-core-priced-bom.csv) | 84 | 87 | 100 |
| Per-board preliminary passives and small actives, all six boards | per-board BOMs under [bom/](bom/) | 60 | 90 | 130 |
| Common passives reference (audio + decoupling) | [rev-a-common-passives-reference-bom.csv](bom/rev-a-common-passives-reference-bom.csv) | 40 | 50 | 65 |
| Connectors / internal harness | [rev-a-connectors-and-harness-reference-bom.csv](bom/rev-a-connectors-and-harness-reference-bom.csv) | 10 | 12 | 16 |
| Panel controls (pots, rotaries, toggles) | [rev-a-panel-controls-priced-bom.csv](bom/rev-a-panel-controls-priced-bom.csv) | 56 | 60 | 72 |
| Panel + mechanical references (jacks, DC jack, endcap stock, hardware) | [rev-a-panel-and-mechanical-reference-bom.csv](bom/rev-a-panel-and-mechanical-reference-bom.csv) | 46 | 50 | 65 |
| Control backplane parts (if used) | [rev-a-control-backplane-preliminary-bom.csv](bom/rev-a-control-backplane-preliminary-bom.csv) | 8 | 12 | 18 |
| **Subtotal: priced electronics + controls + mechanical references** |  | **307** | **365** | **470** |

The "low" column assumes high availability and worst-case substitutes against the approved alternates in [rev-a-supply-watch.md](bom/rev-a-supply-watch.md); the "high" column adds 15 percent contingency on each line.

## Items the BOM does not cover

These are required to actually ship a unit and are deliberately outside the BOM CSVs.

| Item | Notes | Low | Mid | High |
|---|---|---|---|---|
| Primary tanks (`4AB1C1B` x2) | User-procured separately; not part of the SMD quote. | 70 | 80 | 95 |
| Secondary tanks (`9EB2C1B`, `9EB3C1B`) | User-procured separately; not part of the SMD quote. | 70 | 80 | 100 |
| Tank interconnect cables (4x shielded RCA, right-angle) | Pre-made or fabricated per [rev-a-harness-map.md](rev-a-harness-map.md). | 20 | 30 | 45 |
| PCB fabrication, all 6 boards, 2-layer, 1 oz Cu, 1.6 mm, HASL, JLCPCB-class | Single-prototype run. Fab quote varies with panel utilization. | 40 | 65 | 110 |
| SMT assembly, JLCPCB-class, single side, no exotic parts | Excludes through-hole panel hardware. | 90 | 140 | 220 |
| Through-hole and panel hand assembly labor (3-4 hours) | Builder time, not vendor. | 60 | 120 | 180 |
| Circular endcaps, internal rails, and bracket metalwork | User-supplied tube not included. | 70 | 130 | 240 |
| Endcap print or engraving | Front Panel Express / equivalent | 50 | 90 | 150 |
| External wall adapter (already counted in core BOM line above; this line is the assembled cordage) | barrel-jack cable retention if added | 0 | 2 | 5 |
| Bench calibration time (2-3 hours) | Builder time during P-0 through S-1 in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md). | 40 | 80 | 120 |
| Shipping, taxes, freight | Distributor + fab. Region-dependent. | 30 | 60 | 100 |
| **Subtotal: items outside BOM CSVs** |  | **540** | **867** | **1365** |

## Combined per-unit estimate

| Range | Total |
|---|---|
| Low (best availability, hobbyist labor cost, minimal contingency) | **USD 847** |
| Mid (typical) | **USD 1232** |
| High (worst-case sourcing, paid labor, contingency) | **USD 1835** |

## What dominates the cost

The pattern observed in [rev-a-cost-summary.md](bom/rev-a-cost-summary.md) holds at full system scope: the electronics are not the dominant line. In the mid column, the breakdown is roughly:

- electronics + panel parts: ~28 percent
- user-supplied tube materially reduces the mechanical cash outlay versus buying a complete custom shell
- fabrication + SMT assembly: ~16 percent
- mechanical (endcaps + panel art + brackets, not the tube): ~18 percent
- tanks + tank cables: ~15 percent
- labor (hand assembly + bench): ~16 percent
- shipping / freight / contingency: ~7 percent

Builder labor is roughly the same order as the electronics cost, which is worth understanding before committing to a quantity larger than one or two.

## How the volume cost would change

Rough scaling notes for thinking about a second build or a small batch:

- 5x build quantity drops the per-unit fab cost roughly 40 percent because the panel utilization improves
- SMT setup amortization drops the per-unit SMT cost roughly 30 percent at 5x
- Distributor break points kick in for the OPA1656 / OPA1679 lines at 10x and 25x
- Tank cost is essentially flat versus quantity at this scale
- Enclosure cost drops the most with quantity if you commit to a single supplier and a fixed front-panel art

## What this estimate is not

- not a vendor quote
- not a contract price
- not a NRE (non-recurring engineering) estimate; assumes the rev-A design ships as documented
- not a service / warranty cost
- not currency-hedged

Treat this file as the single number to walk into a kitchen-table budgeting conversation with. The authoritative per-vendor numbers come from the actual quotes returned against the package described in [rev-a-quote-request-packet.md](rev-a-quote-request-packet.md) and [rev-a-manufacturing.md](rev-a-manufacturing.md).
