# GAS Hardware Requirements Traceability

This file maps the user-provided hardware constraints to the current hardware package so the design can be reviewed for drift.

## Scope

The goal is to design the analog hardware package for the GAS device as far as possible in this session, including:

- board architecture
- schematic-ready board definitions
- sourced BOM with current pricing/vendor links
- manufacturing handoff recommendations

## Constraint Matrix

| Requirement | Current Decision | Primary Evidence |
| --- | --- | --- |
| Real device is analog, no MCU / Arduino / Raspberry Pi | Locked as analog-only architecture | [README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:7), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:9) |
| Predelay + convolution are simulation-only stand-ins for real tanks | Locked as the only software-only substitution | [README.md](C:/Users/Jason/GAS-build/repo/README.md:16), [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:37) |
| Primary tanks are `4AB1C1B` / `4AB1C1B` | Locked in architecture and board briefs | [README.md](C:/Users/Jason/GAS-build/repo/README.md:18), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:20) |
| Secondary tanks are `9EB2C1B` left and `9EB3C1B` right | Locked in architecture and board briefs | [README.md](C:/Users/Jason/GAS-build/repo/README.md:19), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:22) |
| External I/O is balanced line level | Locked at `+4 dBu`, 600-ohm capable | [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:10), [input-output-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/input-output-board.md:5) |
| External jacks are combo `XLR / TRS` | Locked in architecture, panel spec, and mechanical BOM | [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:11), [rev-a-controls-and-panel.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-controls-and-panel.md:5), [rev-a-panel-and-mechanical-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-and-mechanical-reference-bom.csv:1) |
| Rev A needs a dedicated mono-input to stereo switch | Locked on the I/O board and panel spec | [input-output-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/input-output-board.md:10), [rev-a-controls-and-panel.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-controls-and-panel.md:24) |
| Input buffer should be JFET or BiFET | Current rev-A pick is `OPA1644AIDR` | [input-output-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/input-output-board.md:29), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:41), [rev-a-core-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-core-priced-bom.csv:1) |
| Prefer `+/-18V` tolerant parts where practical | Locked for the audio op-amp families | [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:17), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:53) |
| Avoid ceramic / tantalum / electrolytic capacitors in the audio path if possible | Locked as an audio-path-only capacitor policy | [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:12), [rev-a-capacitor-policy.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-capacitor-policy.md:1), [rev-a-common-passives-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-common-passives-reference-bom.csv:1) |
| Power may use practical ceramics/electrolytics | Explicitly allowed in power policy and passive BOM | [rev-a-layout-rules.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-layout-rules.md:17), [rev-a-common-passives-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-common-passives-reference-bom.csv:5) |
| Tanks are purchased separately from the PCB assembly | Locked in manufacturing handoff | [rev-a-manufacturing.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-manufacturing.md:127), [rev-a-manufacturing.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-manufacturing.md:155) |

## Deliverable Matrix

| Deliverable | Current Evidence |
| --- | --- |
| Board architecture | [hardware/README.md](C:/Users/Jason/GAS-build/repo/hardware/README.md:19), [rev-a-system-architecture.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-system-architecture.md:57) |
| Board-by-board definitions | [boards/input-output-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/input-output-board.md:1), [boards/ext-tank-routing-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/ext-tank-routing-board.md:1), [boards/crossfade-feedback-wet-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/crossfade-feedback-wet-board.md:1), [boards/filter-clipper-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/filter-clipper-board.md:1), [boards/system-remaining.md](C:/Users/Jason/GAS-build/repo/hardware/boards/system-remaining.md:1) |
| Signal ownership / interconnects | [interfaces.md](C:/Users/Jason/GAS-build/repo/hardware/interfaces.md:1), [rev-a-interconnects.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnects.md:1) |
| Schematic starting points | [rev-a-circuit-starting-points.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-circuit-starting-points.md:1), [rev-a-board-implementation-matrix.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-implementation-matrix.md:1), [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1), [rev-a-capture-value-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-capture-value-tables.md:1), [rev-a-mode-truth-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-mode-truth-tables.md:1) |
| Hardware control ranges mapped from the plugin | [rev-a-control-ranges-and-laws.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-ranges-and-laws.md:1), [PluginProcessor.cpp](C:/Users/Jason/GAS-build/repo/Source/PluginProcessor.cpp:606) |
| Layout-facing board zoning | [rev-a-board-placement-and-zones.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-placement-and-zones.md:1), [rev-a-layout-rules.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-layout-rules.md:1) |
| Numeric electrical targets | [rev-a-numeric-targets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-numeric-targets.md:1), [rev-a-power-budget.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-power-budget.md:1) |
| Current priced BOMs | [bom/README.md](C:/Users/Jason/GAS-build/repo/hardware/bom/README.md:1), [bom/rev-a-core-priced-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-core-priced-bom.csv:1), [bom/rev-a-common-passives-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-common-passives-reference-bom.csv:1), [bom/rev-a-connectors-and-harness-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-connectors-and-harness-reference-bom.csv:1), [bom/rev-a-panel-and-mechanical-reference-bom.csv](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-panel-and-mechanical-reference-bom.csv:1), [bom/rev-a-supply-watch.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-supply-watch.md:1) |
| Manufacturing handoff | [rev-a-manufacturing.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-manufacturing.md:1), [rev-a-validation-checklist.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-validation-checklist.md:1), [kicad/README.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/README.md:1) |
| Real KiCad project scaffolding | [kicad/GAS-Hardware.kicad_pro](C:/Users/Jason/GAS-build/repo/hardware/kicad/GAS-Hardware.kicad_pro:1), [kicad/GAS-Hardware.kicad_sch](C:/Users/Jason/GAS-build/repo/hardware/kicad/GAS-Hardware.kicad_sch:1), [rev-a-schematic-capture-plan.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-capture-plan.md:1) |
| Verified schematic placeholders | [kicad/README.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/README.md:1), `kicad-cli sch export pdf` run outputs in `hardware/kicad/exports` |

## Remaining Reality Check

What is strong right now:

- the architecture and constraints are explicit
- the BOM package is split in a builder-friendly way
- the board boundaries and control ownership are defined

What is not yet complete enough to call "finished hardware design":

- the KiCad project is real and hierarchical, but several audio/control sheets are still intermediate first-pass captures rather than fully finished schematics
- there are not yet finished PCB layouts or clean fabrication-ready DRC/ERC artifacts
- some stage-level component values still need bench-tuning rather than pretending to be final

That means the package is materially advanced, but the thread goal is not yet proven complete.
