# GAS Rev A Quote Request Packet

This file tells the builder exactly which files to send each vendor, in what form, and what to ask for in the email. It is the practical companion to [rev-a-manufacturing.md](rev-a-manufacturing.md). The roll-up cost expectation lives in [rev-a-total-cost-rollup.md](rev-a-total-cost-rollup.md).

Important current status: this packet is ready as a vendor-prep checklist, but the checked-in KiCad project is still at an intermediate schematic-capture stage and should not be treated as a final fab-release bundle until the remaining audio/control-sheet wiring and PCB layout work are complete. The latest `2026-06-29` top-level ERC baseline is `650` known intermediate violations after the first I/O-board center-short cleanup pass.

## Vendor recommendation order

For each board, request quotes in this order. The intent is to land on one vendor for SMT and one for through-hole / hand work, not to switch per board.

1. **JLCPCB** for fast SMT prototype spins on the six-board electrical set with through-hole and panel hardware marked `DNP`. Cheapest at single-unit quantity and explicit KiCad-compatible BOM/CPL paths.
2. **PCBWay** when a board mixes SMT plus enough through-hole population that you want the house to install it rather than hand-install it.
3. **MacroFab** when the user wants one US-based turnkey vendor for everything, accepts a higher per-unit cost, and wants a single point of contact for re-spins.
4. **Front Panel Express / SendCutSend / Protocase** for the circular service-endcap metalwork and internal brackets, not the PCBs.

The package below assumes the JLCPCB-and-PCBWay split. Adapt to a single-vendor MacroFab path by bundling all six boards into one project file, and treat the endcap metalwork as a separate package.

## Files to attach per board

For each of the six boards, attach the bundle below. File names follow the [rev-a-manufacturing.md](rev-a-manufacturing.md) naming.

| Bundle file | Source | Notes |
|---|---|---|
| `<board>-gerbers.zip` | KiCad PCB plot output | All copper, mask, silkscreen, paste, drill, edge-cut layers |
| `<board>-drill.zip` | KiCad drill output | Plated and non-plated holes |
| `<board>-bom.csv` | Per-board preliminary BOM under [bom/](bom/) | Add the columns the vendor requires (see vendor section) |
| `<board>-priced-bom.csv` | Per-board priced hard-part BOM under [bom/](bom/) where available | Use as the sourcing cross-check, not as a claim that tuned passives are fully frozen |
| `<board>-cpl.csv` | KiCad position file | Use mm, top side |
| `<board>-readme.md` | Excerpt from [rev-a-schematic-packets.md](rev-a-schematic-packets.md) for that board | Reference designator legend and any DNP marks |
| `<board>-fabnotes.txt` | Excerpt from [rev-a-pcb-fabrication-assumptions.md](rev-a-pcb-fabrication-assumptions.md) | Stackup, copper weight, finish, panelization preference |

Bundle the six per-board sets plus a single project-level `system-readme.md` (excerpted from [README.md](README.md), [rev-a-system-architecture.md](rev-a-system-architecture.md), and [rev-a-interconnects.md](rev-a-interconnects.md)) into one ZIP per vendor request.

Also include these current project-level references in every electrical quote bundle:

- [bom/rev-a-procurement-snapshot.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-procurement-snapshot.md:1)
- [rev-a-board-package-freeze.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-package-freeze.md:1)
- [rev-a-board-connector-schedule.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-connector-schedule.csv:1)
- [rev-a-control-backplane-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-schematic-ready-definition.md:1)

For the mechanical vendor, create a separate bundle that includes:

- [rev-a-pipe-enclosure-concept.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-pipe-enclosure-concept.md:1)
- [rev-a-endcap-panel-layout.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-panel-layout.md:1)
- [rev-a-endcap-hole-table.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-hole-table.md:1)
- [rev-a-endcap-hole-table.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-hole-table.csv:1)
- [rev-a-board-outline-assumptions.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.md:1)
- [rev-a-board-outline-assumptions.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.csv:1)
- [rev-a-harness-cut-lengths.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-harness-cut-lengths.md:1)
- [rev-a-harness-cut-lengths.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-harness-cut-lengths.csv:1)

## JLCPCB request

Reference: [JLCPCB BOM and CPL guide from KiCad](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad).

Columns required in `<board>-bom.csv` for JLCPCB:

- `Comment`, `Designator`, `Footprint`, `LCSC Part #` (use `C` prefix for the JLCPCB-stocked part)

For parts not in the JLCPCB Basic library, either:

- accept the SMT extended-part fee per unique non-basic SKU, or
- mark the part as "Customer Supplied" and ship the reel/tube before assembly

Mark all through-hole or panel hardware (combo jacks, DC jack, toggles, rotaries, dual pots, TO-126 transistors if desired) as `DNP / NOT INSTALLED` on the JLCPCB BOM unless you have confirmed JLCPCB will accept them at quote time.

Template request body:

```
Quote request: GAS Rev A audio hardware, six-board low-voltage analog set.

Boards attached, single unit each:
- input-output         (rev A, 2 layer, 1.6 mm, HASL, ENIG acceptable)
- ext-tank-routing
- filter-clipper
- crossfade-feedback-wet
- tank-driver-recovery
- power-backplane

For each board:
- assembled top side, paste mask included
- through-hole and panel hardware are not in scope unless explicitly quoted, and are marked DNP in attached BOM
- SMT extended-part fee on non-basic parts is acceptable; please flag the unique part count in the quote

Please quote PCB fab and SMT assembly as separate line items.
Quote should include LCSC sourcing for parts marked with `C` codes in the BOM column.
Shipping to: <fill in>
Timeline: standard, no rush.

Files attached:
- gas-rev-a-jlcpcb.zip (gerbers, drill, BOM CSV, priced-BOM CSV, CPL CSV, fab notes per board, system readme)
```

## PCBWay request

Reference: [PCBWay assembly file requirements](https://www.pcbway.com/assembly-file-requirements.html).

Boards most likely to benefit from a PCBWay quote:

- tank-driver-recovery
- power-backplane

Columns required in `<board>-bom.csv` for PCBWay:

- `Designator`, `Manufacturer Part Number`, `Manufacturer`, `Description`, `Quantity`, `Supplier`, `Supplier Part Number`, `Package`

Through-hole population is fine at PCBWay. Mark the spring tanks themselves and the chassis hardware as customer-supplied and out of scope.

Template request body:

```
Quote request: GAS Rev A audio hardware, mixed-tech subset.

Boards attached, single unit each:
- tank-driver-recovery (SMT plus optional TO-126 transistor installation)
- power-backplane      (low-voltage DC input and DC-DC conversion only)

For each board:
- 2 layer, 1.6 mm, 1 oz Cu, HASL or ENIG acceptable
- assembled top side, paste mask included
- TH parts populated where called for in the BOM (BD139/BD140, panel-jack wires if accepted, etc.)
- the actual spring tanks are NOT included and will be installed by the builder

Please source priced parts per the attached `BuyURL` column where possible.

Please quote PCB fab and assembly as separate line items.
Shipping to: <fill in>
Timeline: standard, no rush.

Files attached:
- gas-rev-a-pcbway.zip (gerbers, drill, BOM CSV, priced-BOM CSV, CPL CSV, fab notes per board, system readme)
```

## MacroFab request

Reference: [MacroFab platform / required design files](https://www.macrofab.com/platform/).

If using MacroFab as a single vendor for all six boards, attach the full six-board bundle as one MacroFab project. Use the MacroFab project import flow; the bundle structure above maps cleanly to the MacroFab "project plus per-board manifest" model.

If the build keeps the separate control-backplane landing board rather than folding those functions into the power board, also include:

- [bom/rev-a-control-backplane-preliminary-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-control-backplane-preliminary-bom.csv:1)
- [bom/rev-a-control-backplane-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-control-backplane-priced-bom.csv:1)
- [rev-a-control-backplane-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-schematic-ready-definition.md:1)

Template request body:

```
Quote request: GAS Rev A audio hardware, six-board fully turnkey single-unit build.

Boards attached:
- input-output
- ext-tank-routing
- filter-clipper
- crossfade-feedback-wet
- tank-driver-recovery
- power-backplane

For each board:
- 2 layer, 1.6 mm, 1 oz Cu, HASL or ENIG acceptable
- SMT + TH where called for
- per the supplied BOM, source from DigiKey/Mouser where MPN is specified

Consigned / customer-supplied parts:
- the four spring tanks (4AB1C1B x2, 9EB2C1B, 9EB3C1B)
- any vacuum tubes used in the build
- the enclosure tube
- knobs and circular endcap art

Please quote per-board fab + assembly with one combined project shipping line.
Shipping to: <fill in>
Timeline: standard, no rush.

Files attached:
- gas-rev-a-macrofab.zip (six per-board bundles including priced-BOM companions, system readme)
```

## Distributor purchasing checklist

Buy these directly, not through the assembler, because they are panel/mechanical/consigned items the assemblers will not source for a single unit at competitive cost:

| Group | Source | File |
|---|---|---|
| Spring tanks (`4AB1C1B` x2, `9EB2C1B`, `9EB3C1B`) | user-procured separately | call out in [rev-a-manufacturing.md](rev-a-manufacturing.md) and [bom/rev-a-procurement-snapshot.md](bom/rev-a-procurement-snapshot.md) |
| Vacuum tubes, if used | user-supplied | keep outside assembler sourcing; current fixed PCB BOM has no tube SKUs |
| Combo XLR/TRS jacks (`NCJ6FI-S` x4) | DigiKey or Mouser | [rev-a-panel-and-mechanical-reference-bom.csv](bom/rev-a-panel-and-mechanical-reference-bom.csv) |
| `5.5 x 2.5 mm` panel DC jack | DigiKey | [rev-a-panel-and-mechanical-reference-bom.csv](bom/rev-a-panel-and-mechanical-reference-bom.csv) |
| Panel pots and toggles | DigiKey and Mouser per row | [rev-a-panel-controls-priced-bom.csv](bom/rev-a-panel-controls-priced-bom.csv) |
| Rotary mode switches | Mouser EU per row | [rev-a-panel-controls-priced-bom.csv](bom/rev-a-panel-controls-priced-bom.csv) |
| Knobs (12-14, depending on final panel count) | DigiKey | tracked under panel/mechanical reference |
| Circular endcap, reinforcement plate, and bracket metalwork | Front Panel Express / SendCutSend / Protocase | tracked under panel/mechanical reference |
| Tank interconnect cables, 4x shielded RCA right-angle | Amplified Parts / Tubes And More | external sourcing, not in BOM |
| Main cylindrical enclosure tube | user-supplied | explicitly outside the vendor quote |

## Mechanical-vendor request

Use this as the companion request when the circular endcaps and brackets are ready to quote.

```
Quote request: GAS Rev A cylindrical service-endcap and bracket set.

Scope requested:
- 1x circular service endcap
- 1x plain opposite endcap or simple matching blank
- 1x internal jack-bar / reinforcement plate
- 2x simple internal rail or angle brackets for PCB mounting

Reference files attached:
- rev-a-pipe-enclosure-concept
- rev-a-endcap-panel-layout
- rev-a-endcap-hole-table
- rev-a-board-outline-assumptions
- rev-a-harness-cut-lengths

Notes:
- the main tube itself is user-supplied and is NOT in scope
- the main cylindrical enclosure tube is supplied by the user and should not be sourced by the metal vendor
- this is a prototype analog audio build, so alignment and serviceability matter more than cosmetic perfection
- please flag any hole-spacing or edge-distance concern before manufacture
```

## Quote sanity checks before accepting

Before paying any vendor, check that:

- the supplied BOM and the vendor's quoted BOM agree line by line, including DNP marks
- no `OPA1656IDR` / `OPA1644AIDR` / `OPA1679IDR` line has been silently substituted to a non-approved alternate; the approved alternates are in [rev-a-supply-watch.md](bom/rev-a-supply-watch.md)
- the panel-hardware DNP set on the JLCPCB boards is actually marked DNP (otherwise you will be charged for parts you will not install)
- the per-board fab spec matches [rev-a-pcb-fabrication-assumptions.md](rev-a-pcb-fabrication-assumptions.md): 2-layer, 1.6 mm, 1 oz Cu, HASL or ENIG, no exotic stackup
- shipping incoterms are clear before card capture

## Final pre-launch checklist

- KiCad project opens cleanly on the build machine
- ERC and DRC reports archived per board
- Gerbers reviewed in a free gerber viewer (GerbV or KiCad's own GerberViewer) before sending
- the connector pinout in [rev-a-interconnect-pin-map.md](rev-a-interconnect-pin-map.md) has not drifted from the schematic
- the bring-up sequence in [rev-a-bringup-sequence.md](rev-a-bringup-sequence.md) and the bench test procedures in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) are printed and ready
