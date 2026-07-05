# GAS Rev A KiCad Sheet Population Plan

This file is the practical bridge between the current placeholder schematics and real KiCad capture.

It does not replace the higher-level hardware docs. It turns them into a concrete capture sequence with completion gates.

## Capture Inputs

Use these files together while entering symbols and nets:

- [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1)
- [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1)
- [rev-a-io-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-io-schematic-ready-definition.md:1)
- [rev-a-ext-routing-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-ext-routing-schematic-ready-definition.md:1)
- [rev-a-tank-driver-recovery-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-tank-driver-recovery-schematic-ready-definition.md:1)
- [rev-a-crossfade-feedback-wet-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-crossfade-feedback-wet-schematic-ready-definition.md:1)
- [rev-a-filter-clipper-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-filter-clipper-schematic-ready-definition.md:1)
- [rev-a-control-backplane-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-schematic-ready-definition.md:1)
- [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
- [rev-a-capture-value-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-capture-value-tables.md:1)
- [rev-a-control-backplane-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-definition.md:1)
- [rev-a-control-harnesses.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-harnesses.md:1)
- [rev-a-board-outline-assumptions.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.md:1)
- [rev-a-symbol-manifest.csv](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-symbol-manifest.csv:1)
- [rev-a-net-label-manifest.csv](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-net-label-manifest.csv:1)
- [audit-rev-a-capture.py](C:/Users/Jason/GAS-build/repo/hardware/kicad/audit-rev-a-capture.py:1)
- [rev-a-capture-audit.md](C:/Users/Jason/GAS-build/repo/hardware/kicad/rev-a-capture-audit.md:1)

## Progress Gate

Before and after each schematic-capture pass, run:

```powershell
python hardware/kicad/audit-rev-a-capture.py
```

Use the generated report as the objective gate for whether a pass actually moved the project forward:

- top-level hierarchy should stay at `6 / 6`
- sheet-level ref counts should rise from `0 / N` toward full population
- manifest net-label coverage should rise as real inter-board and control nets are entered
- do not rely on visual inspection alone when deciding whether a sheet is "started"

Practical note:

- interface-label coverage can reach `100%` before symbol placement begins
- that is useful progress, but it will not by itself produce a clean ERC because floating hierarchical labels still need real wires and circuitry

## Minimal Top-Level Goal

The top-level KiCad schematic should at least evolve from "title block only" to:

- one hierarchical sheet per board
- shared global power labels
- a notes block identifying the external tanks, endcap format, and wall-adapter power entry

That alone makes the project structurally real instead of just a filename placeholder.

## Sheet Entry Order

### 1. Power Backplane

Current status:

- `J500`, `D500`, `F500`, `TVS500`, `C500`
- `PS500`, `PS501`
- `FB500`, `FB501`
- `P501-P506`, `P601`
- first-pass rail-anchor `PWR_FLAG` symbols for `+15VA`, `-15VA`, `+5VAUX`, `AGND`, `CHASSIS`
- first-pass net assignment for DC entry, split-rail generation, `+5VAUX`, and board-power fanout is now checked in

Still to do on this sheet:

- explicit star-ground / chassis-bond network
- post-conversion ripple-decoupling part capture around the `FB500/FB501` cleanup stage
- exact `PJ-005A` symbol/footprint pin mapping freeze (jack changed from `PJ-005B` on `2026-07-04`; same mounting family, 2.1 mm center pin) and the final `PS500` enable-pin handling decision
- final power-sheet ERC cleanup
- `P610-P614` style control-landings if the control-backplane path is retained

Original entry target:

- `J500`, `D500`, `F500`, `TVS500`, `C500`
- `PS500`, `PS501`
- `FB500`, `FB501`
- `P501-P506`
- star-ground and chassis bond note

Completion gate:

- all power outputs named exactly per the net-label manifest
- no anonymous rail aliases

### 2. Input / Output

Current status:

- `U1-U4`
- `J1-J4`
- `P1-P6`
- first-pass symbol-only capture is now in the checked-in sheet

Still to do on this sheet:

- actual balanced receiver pin-level wiring
- mono/stereo switch implementation wiring
- wet/dry summer and balanced-output leg wiring
- test points, passives, protection parts, and local decoupling
- final combo-jack mechanical/footprint sanity-check for `NCJ6FI-S`

Completion gate:

- balanced input/output net names match the manifest
- wet/dry and mono functions represented, even if some values remain DNP or tentative

### 3. Tank Driver / Recovery

Current status:

- `U101-U104`
- `Q101-Q104`
- `P101-P103`
- `J101-J108`
- first-pass symbol-only capture is now in the checked-in sheet

Still to do on this sheet:

- primary direct-coupled send-stage wiring and bias network
- secondary send-stage wiring and stability parts
- recovery input, gain, and compensation networks
- exact tank shield-bond implementation and connector footprint freeze
- local decoupling, trim footprints, and bias-current measurement pads

Completion gate:

- primary and secondary send/return nets exist exactly once
- bias/stability trim footprints are represented, not omitted

### 4. Ext Tank Routing

Current status:

- `U201`
- `K201-K204`
- `P201-P207`
- first-pass relay/contact ownership, wet-send sheet ports, and connector net landings are now in the checked-in sheet

Still to do on this sheet:

- coil flyback, local decoupling, and relay-drive support parts
- primary-send isolators, secondary-send isolators, and the active summing/buffer network
- amount-control insertion and any series-mode makeup network wiring
- explicit feedback reinjection resistor capture and output handoff wiring
- final decision on whether the control harness lands directly here or is always routed through the control backplane

Completion gate:

- Off / Series / Parallel relay states and sheet-level wet-send ownership can be traced from the schematic
- relay coil nets and contact nets are visually separable

### 5. Crossfade / Feedback / Wet

Current status:

- `U301`
- `P301-P307`
- first-pass symbol-only capture is now in the checked-in sheet

Still to do on this sheet:

- crossfade summing and output handoff wiring
- feedback loop gain path and compensation footprints
- polarity-invert implementation strategy around `CTL_FB_INV`
- final decision on whether crossfade/feedback controls land locally or always via the control backplane

Completion gate:

- crossfade, filter send/return, and feedback reinjection all exist as explicit named nets

### 6. Filter / Clipper

Current status:

- `U401`, `U402`
- `D401-D412`
- `P401-P405`
- first-pass symbol-only capture is now in the checked-in sheet

Still to do on this sheet:

- actual HPF, drive, clip-mode, and LPF pin-level wiring
- alternate clip-part footprints and DNP strategy around the silicon, LED, and germanium networks
- local decoupling, compensation, and bring-up test pads
- final germanium device or adapter footprint freeze

Completion gate:

- all clip modes exist as physical networks or selectable landings
- HPF/LPF controls are represented with their intended grouped-control strategy

## Control-Landing Honesty Rule

Do not force fake physical connector counts just to get symbols onto the sheet.

For `P206`, `P307`, `P403`, and `P405`:

- they may begin life as logical control landings on the sheet
- the exact physical connector family and pin count should follow the chosen control-backplane strategy
- if direct board-mounted controls are chosen instead, remove the placeholder connector rather than leaving a misleading header in the released schematic

## First ERC Expectations

The first real ERC pass does not need to prove analog correctness yet.

It should prove:

- every board has power entry
- every connector exists with the right pin count
- inter-board nets are named consistently
- every major active device in the symbol manifest is instantiated

Current status:

- this proof point is now met at the manifest level
- the next KiCad phase should focus on real wiring rather than adding more placeholder symbols

Intermediate warning:

- the current partial-capture phase is expected to raise `label_dangling` ERC errors
- do not spend time "fixing" those by deleting labels
- clear them only when the corresponding symbols and wires are really being entered

## Before Any PCB Layout

Do not start board layout until these are true:

- top-level hierarchy exists
- connector naming is frozen against the interconnect pin map
- the power-backplane sheet no longer refers to obsolete mains hardware
- the preferred panel/control strategy is reflected in the connector count actually used

## Honest Remaining Gap After This Plan

Even after these manifests exist, the project still needs:

- manual symbol placement and wiring across the remaining non-power sheets inside KiCad
- footprint assignment confirmation
- real ERC cleanup
- eventual PCB layout and DRC

That is the remaining work between the current package and a true fabrication release.
