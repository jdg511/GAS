# Rev A Procurement Snapshot

This file is the clean purchasing view for the rev-A hardware package.

Snapshot date: `2026-06-29`

Use it for three things:

1. identifying the exact fixed parts already standardized enough to source
2. separating SMD-house scope from panel/mechanical scope
3. keeping user-supplied items out of the assembly quote

The authoritative machine-readable companion is:

- [rev-a-procurement-snapshot.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-procurement-snapshot.csv:1)

## Scope Notes

- Prices are single-unit or nearest-visible live product-page snapshot values in `USD`.
- The fixed-part rows in this file were rechecked against current vendor product listings or live vendor search results on `2026-06-29`.
- Where a live page no longer shows a clean one-piece quote, the practical sourcing note now calls that out directly.
- These are procurement references, not a guarantee that any given assembler will source at the same unit price.
- Spring tanks stay outside the SMD assembly quote.
- Any vacuum tubes used in a given build are user-supplied consigned parts; the current rev-A fixed PCB BOM does not include tube SKUs.
- The cylindrical enclosure tube is user-supplied and stays outside all vendor sourcing.
- The separate panel-control reference BOM is still useful, but it was not fully repriced in this refresh pass.

## Build-Scope Split

### SMD House Scope

These are the parts most suitable for JLCPCB, PCBWay, or MacroFab sourcing and placement:

| Item | MPN | Qty | Snapshot Price | Vendor |
|---|---|---:|---:|---|
| JFET input op amp | `OPA1644AIDR` | 1 | `4.65` | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/OPA1644AIDR/2353575) |
| Dual audio op amp | `OPA1656IDR` | 7 | `2.99` each | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/OPA1656IDR/10715414) |
| Quad audio op amp | `OPA1679IDR` | 4 | `1.52` each | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/OPA1679IDR/7034963) |
| Signal relay | `G6K-2F-Y-DC5` | 4 | `4.89` each | [Mouser](https://www.mouser.com/ProductDetail/Omron-Electronics/G6K-2F-Y-DC5?qs=SXIVkn%252Bm38kNKs%252BIzeJTSg%3D%3D) |
| Primary send NPN | `BD139-16` | 2 | `1.44` each | [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/BD139-16/2529325) |
| Primary send PNP | `BD140-16` | 2 | `1.57` each | [DigiKey](https://www.digikey.com/en/products/detail/stmicroelectronics/BD140-16/3945995) |
| Isolated DC-DC | `URA2415YMD-10WR3` | 1 | `9.27` | [DigiKey](https://www.digikey.com/en/products/detail/mornsun-america-llc/URA2415YMD-10WR3/13160913) |
| +5V regulator | `R-78E5.0-0.5` | 1 | `3.37` | [DigiKey](https://www.digikey.com/en/products/detail/recom-power/R-78E5-0-0-5/2834904) |
| Optional relay driver | `ULN2003ADR` | 1 | `0.91` | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/ULN2003ADR/277011) |

Practical note:

- the current DigiKey page for `OPA1644AIDR` still shows the device as not normally stocked; the `4.65` snapshot above reflects the current visible product-page unit price, and for an immediate-order rev-A build `2x OPA1642AIDR` remains the best mainstream alternate
- the current DigiKey page for `OPA1679IDR` is backorderable rather than cleanly in stock, so `OPA1664AIDR` remains the preferred live alternate if assembler sourcing gets tight
- `ULN2003ADR` is now treated as a reserve-only part under the current control harness and should not be assumed populated in the fixed rev-A build

### Panel / Hand-Install Scope

These are the preferred parts for panel assembly or manual install after SMT:

| Item | MPN | Qty | Snapshot Price | Vendor |
|---|---|---:|---:|---|
| Combo XLR/TRS jack | `NCJ6FI-S` | 4 | `4.71` each | [Mouser](https://www.mouser.com/ProductDetail/Neutrik/NCJ6FI-S?qs=2AuUxvzm3x9XIIQSbwRdvA%3D%3D) |
| Panel DC jack | `PJ-005A` | 1 | `3.07` | [DigiKey](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/PJ-005A/165838) |
| External wall adapter | `WSU240-0750` | 1 | `12.43` | [DigiKey](https://www.digikey.com/en/products/detail/triad-magnetics/WSU240-0750/3094933) |

The panel controls remain tracked in:

- [rev-a-panel-controls-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-controls-priced-bom.csv:1)

The mechanical references remain tracked in:

- [rev-a-panel-and-mechanical-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-and-mechanical-reference-bom.csv:1)

## User-Supplied Or Separately Procured Items

Keep these outside the SMT assembly quote:

| Item | Source Direction | Notes |
|---|---|---|
| Primary tanks `4AB1C1B` x2 | separate purchase | not installed by the SMT house |
| Secondary tanks `9EB2C1B` and `9EB3C1B` | separate purchase | not installed by the SMT house |
| Vacuum tubes, if used in the build | user-supplied | keep outside the assembler quote; current rev-A fixed BOM has no tube SKUs |
| Cylindrical enclosure tube | user-supplied | user-provided mechanical shell; not in vendor BOM |
| Circular endcaps and rail metalwork | mechanical vendor | quote separately from PCB assembly |
| Tank RCA cabling and final harness consumables | hand-build or consigned | depends on final tank mounting geometry |

## Approved Alternates

Use the current supply-risk and alternate guidance in:

- [rev-a-supply-watch.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-supply-watch.md:1)

Most important alternates:

- `OPA1644AIDR` -> `2x OPA1642AIDR` as the practical immediate-order path when the quad is not stocked cleanly
- `OPA1679IDR` -> `OPA1664AIDR` if availability moves again
- `URA2415YMD-10WR3` -> `REC10-2415DZ/H1/A/M` or `JTD1024S15`
- the wall adapter is now the regulated `Triad WSU240-0750` (`+24VDC` SMPS, UL 62368-1, selected `2026-07-04`); the earlier unregulated-Jameco concern is retired, keep only the P-0 open-circuit receiving check

## Recommended Buying Pattern

For the first rev-A build:

1. let the board house quote and place the common SMD parts
2. keep combo jacks, the DC jack, panel controls, tanks, and tube outside that quote
3. send the mechanical package separately for endcaps, brackets, and drilling
4. do not freeze tuned passives until the first tank-drive and recovery bench session is complete
