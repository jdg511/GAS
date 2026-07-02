# KiCad Workspace

KiCad 10 is installed locally on this machine.

This folder is the intended home for the hardware project once schematic capture starts.

## Planned Contents

- `GAS-Hardware.kicad_pro`
- `GAS-Hardware.kicad_sch`
- one schematic file scaffold per board
- board layouts for:
  - input-output
  - tank-driver-recovery
  - ext-tank-routing
  - crossfade-feedback-wet-summing
  - filter-clipper

## Current Status

The KiCad project now has a **real top-level hierarchical shell**, first-pass real symbol capture across every rev-A child sheet, and a first-pass electrically assigned power/backplane page.

What currently exists:

- file naming
- top-level sheet ownership and page ordering
- title blocks
- top-level system notes
- child-sheet interface labels for global rails, I/O boundary nets, inter-board audio nets, and frozen control nets
- first-pass symbol population on every rev-A board sheet
- first-pass DC-entry, rail-generation, and harness-fanout net assignment on `power-backplane.kicad_sch`
- PCB placement scaffold files for all six rev-A boards, generated from the documented board envelope assumptions
- DRC-clean placement scaffolds with four M3 mounting holes plus all currently assigned schematic footprints per board
- capture sequencing
- validated CLI export workflow
- a manifest-driven audit script for measuring schematic population progress

What does **not** yet exist:

- real inter-sheet and intra-sheet pin-level wiring on the five audio/control sheets
- clean ERC after the new symbol-only capture phase
- finished footprint assignment inside every schematic page
- routed copper, zones, final component placement, or Gerber/drill fabrication exports for the PCB files

Capture should now key off:

- [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1)
- [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1)
- [rev-a-io-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-io-schematic-ready-definition.md:1)
- [rev-a-ext-routing-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-ext-routing-schematic-ready-definition.md:1)
- [rev-a-tank-driver-recovery-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-tank-driver-recovery-schematic-ready-definition.md:1)
- [rev-a-crossfade-feedback-wet-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-crossfade-feedback-wet-schematic-ready-definition.md:1)
- [rev-a-filter-clipper-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-filter-clipper-schematic-ready-definition.md:1)
- [rev-a-control-backplane-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-schematic-ready-definition.md:1)
- [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
- [rev-a-bringup-sequence.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-bringup-sequence.md:1)
- [rev-a-sheet-population-plan.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-sheet-population-plan.md:1)
- [rev-a-symbol-manifest.csv](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-symbol-manifest.csv:1)
- [rev-a-net-label-manifest.csv](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-net-label-manifest.csv:1)

## Verification

During this session, the hierarchical top-level shell and all child sheets were accepted by `kicad-cli`, and the release-export script still produced schematic PDFs successfully after the interface-label pass.

Important current nuance:

- symbol population is intentionally ahead of real wire placement
- `kicad-cli sch export pdf` still succeeds
- top-level ERC is no longer clean at this intermediate stage because the hierarchical labels are not yet attached to real wires or symbols
- the current ERC result is therefore a **known intermediate failure**, not a claim that the capture is electrically complete

Current exported folder:

- the historical placeholder export artifact still exists as a file named `hardware/kicad/exports`

Repeatable release/export helper:

- [export-rev-a-release.ps1](C:/Users/Jason/GAS-build/repo/hardware/kicad/export-rev-a-release.ps1:1)
- [rev-a-release-manifest.csv](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-release-manifest.csv:1)

Repeatable capture-progress audit:

- [audit-rev-a-capture.py](C:/Users/Jason/GAS-build/repo/hardware/kicad/audit-rev-a-capture.py:1)
- [rev-a-capture-audit.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-capture-audit.md:1)

Run:

```powershell
python hardware/kicad/audit-rev-a-capture.py
```

Current baseline from the latest `2026-06-29` audit:

- top-level hierarchy: `6 / 6` child sheets present
- populated schematic refs: `88 / 88`
- explicit manifest net labels: `82 / 82`

Current release-export / ERC baseline from the same session:

- capture audit: `88 / 88` planned refs present and `82 / 82` manifest labels present
- top-level ERC: `650` known intermediate violations after the I/O-board center-short cleanup pass on `2026-06-29`
- the I/O child sheet dropped from `404` to `376` local violations in the same pass, and its multiple-net-name collisions dropped from `8` to `2`
- the remaining I/O multiple-net-name warnings are the intentional `WD_L_LO <-> WET_SUM_L` and `WD_R_LO <-> WET_SUM_R` wet-return aliases
- the remaining ERC debt is still dominated by top-level unconnected sheet pins, placeholder wire endpoints, off-grid legacy symbol endpoints, and still-unwired child-sheet labels on the non-power sheets
- the power/backplane page itself still stands as the most electrically assigned sheet, but it is not yet the final ripple-decoupling or chassis-bond implementation

Current PCB scaffold baseline:

- `crossfade-feedback-wet.kicad_pcb`: `100 mm x 70 mm`, 8 electrical footprints, 4x M3 mounting holes, DRC clean
- `ext-tank-routing.kicad_pcb`: `120 mm x 80 mm`, 12 electrical footprints, 4x M3 mounting holes, DRC clean
- `filter-clipper.kicad_pcb`: `140 mm x 90 mm`, 19 electrical footprints, 4x M3 mounting holes, DRC clean
- `io-board.kicad_pcb`: `160 mm x 75 mm`, 50 electrical footprints, 4x M3 mounting holes, DRC clean
- `power-backplane.kicad_pcb`: `150 mm x 95 mm`, 14 electrical footprints, 4x M3 mounting holes, DRC clean
- `tank-driver-recovery.kicad_pcb`: `170 mm x 110 mm`, 11 electrical footprints, 4x M3 mounting holes, DRC clean
- these are **placement scaffolds only** and are not routed fabrication outputs

Repeatable PCB footprint placement helper:

- [place-rev-a-board-footprints.py](C:/Users/Jason/GAS-build/repo/hardware/kicad/place-rev-a-board-footprints.py:1)

Current scripted output root:

- `hardware/kicad/release-exports/rev-a-release`

## Order Readiness Gate

Before ordering boards, run:

```powershell
.\hardware\kicad\test-rev-a-order-readiness.ps1
```

The gate writes:

- [rev-a-order-readiness.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-order-readiness.md:1)
- [GAS-Hardware-erc-current.json](C:/Users/Jason/GAS-build/repo/hardware/kicad/GAS-Hardware-erc-current.json:1)

It intentionally fails while any of these are true:

- no `*.kicad_pcb` board layout files exist
- top-level ERC has violations
- non-virtual schematic symbols have empty footprint fields
- KiCad/SPICE simulation model properties are absent

The current project is therefore **not order-ready**. It remains in schematic-capture cleanup before PCB layout, DRC, Gerber/drill export, and simulation setup.

## Planned Export Set

- fabrication Gerbers
- drill files
- schematic PDFs
- `BOM.csv`
- centroid / position files
- assembly drawings
- bring-up and calibration notes
