# GAS Hardware Build

This folder is the starting point for turning the JUCE spring-reverb simulation into a real analog product.

## Core Constraints

- The real unit is primarily analog.
- Use passive parts, transistors, and analog or mixed-signal ICs.
- Do not use an MCU, Arduino, Raspberry Pi, or other general-purpose embedded computer on the production PCB.
- The external audio interfaces should be balanced line level, nominally `+4 dBu`, with 600-ohm capable line I/O behavior.
- The external audio connectors should be combo `XLR / TRS` jacks.
- The enclosure format is now a **user-supplied cylindrical tube**, roughly `8-9 in` diameter and about `48 in` long.
- All external audio connections and DC power entry should land on **one circular service endcap**, in the spirit of the original Great British Spring.
- In the audio path, avoid ceramic, tantalum, and electrolytic capacitors wherever practical; prefer film-based or other non-ceramic/non-electrolytic solutions and use direct coupling where it makes sense. Power-supply and rail-decoupling positions may use ceramics or electrolytics when practical.
- Only the simulation's predelay and convolution blocks are software-only stand-ins for the real spring tanks.
- The real hardware should use the target tanks directly:
  - Primary tanks: `4AB1C1B` left and `4AB1C1B` right
  - Secondary tanks: `9EB2C1B` left and `9EB3C1B` right
- Plan around `+15VA / -15VA`, but prefer parts that can tolerate at least `+18V / -18V` wherever practical.
- Mains conversion lives in an **external `+30 VDC` wall-adapter strategy** (`500 mA / 15 W`, Jameco `DDU300050E9340` candidate or approved regulated alternate). The chassis takes DC at a barrel jack and generates `+15V / -15V / +5V` on-board from that single DC input. No mains-side circuitry inside the enclosure. Do not assume the exact Jameco SKU is regulated without the bench check in [rev-a-external-dc-power.md](rev-a-external-dc-power.md).

## Board Roadmap

We are partitioning the product into analog boards so each section can be designed, tested, and revised independently.

1. Input / Output board
   - Balanced line receiver, dry split, final wet/dry summing, balanced line driver
2. Ext Reverb Tanks Off / Series / Parallel board
   - Secondary tank routing and amount control
3. Filter and Clipping board
   - Drive, HPF, selectable clipping, LPF
4. Tank Driver / Recovery board
   - Real spring tank send and return electronics for primary and secondary tanks
5. Crossfade / Feedback / Mixer board
   - Stereo tank crossfade, feedback loop, phase invert, inter-board summing
6. Power / Control / Interconnect board
   - Analog supply rails, panel controls, board-to-board headers, grounding strategy

## Signal-Path Mapping

The current software path is:

`input -> dry tap + wet path -> tank model -> stereo crossfade -> filter/clipper -> feedback -> wet/dry mix -> output`

The real hardware path should become:

`balanced line receiver -> dry split + wet send -> real tank drive/recovery path -> stereo crossfade -> filter/clipper -> feedback loop -> wet/dry output mixer -> balanced line driver`

The only direct substitution is:

- `predelay + convolution` in software
- replaced by
- real tank drive + real spring tank + recovery stages in hardware

## Design Intent

- Keep the board architecture modular so a third-party PCB house can fabricate repeatable revisions.
- Favor through-hole panel hardware and serviceable connectors where practical.
- Keep the control surface directly analog whenever possible: pots, toggles, rotary switches, relay logic, and analog switch ICs are all acceptable paths.
- Avoid any hardware decision that depends on firmware existing later.

## Build Handoff Entry Points

If you are picking this package up to actually build a unit, start here:

- [rev-a-external-dc-power.md](rev-a-external-dc-power.md) — external wall-adapter power topology and on-board ±15V / +5V generation
- [rev-a-pipe-enclosure-concept.md](rev-a-pipe-enclosure-concept.md) — cylindrical shell, endcap, rail, and tank-mount concept
- [rev-a-endcap-panel-layout.md](rev-a-endcap-panel-layout.md) — service-endcap zoning for combo jacks, DC jack, and controls
- [rev-a-endcap-hole-table.md](rev-a-endcap-hole-table.md) — first drilling/cutout draft for the circular service endcap
- [rev-a-endcap-hole-table.csv](rev-a-endcap-hole-table.csv) — machine-readable companion to the endcap hole table
- [rev-a-board-outline-assumptions.md](rev-a-board-outline-assumptions.md) — target board envelopes and axial placement inside the tube
- [rev-a-board-outline-assumptions.csv](rev-a-board-outline-assumptions.csv) — machine-readable board envelope and station map
- [rev-a-harness-cut-lengths.md](rev-a-harness-cut-lengths.md) — prototype harness cut lengths for boards, tanks, and panel wiring
- [rev-a-harness-cut-lengths.csv](rev-a-harness-cut-lengths.csv) — machine-readable harness-length companion
- [rev-a-board-package-freeze.md](rev-a-board-package-freeze.md) — compact board-by-board freeze for schematic capture and quoting
- [rev-a-electrical-capture-worksheet.md](rev-a-electrical-capture-worksheet.md) — next-pass electrical wiring brief keyed to the actual KiCad refs
- [rev-a-io-schematic-ready-definition.md](rev-a-io-schematic-ready-definition.md) — exact first-pass I/O unit allocation, passive map, and connector/net ownership
- [rev-a-ext-routing-schematic-ready-definition.md](rev-a-ext-routing-schematic-ready-definition.md) — exact first-pass ext-routing relay ownership, control decode, and passive map
- [rev-a-tank-driver-recovery-schematic-ready-definition.md](rev-a-tank-driver-recovery-schematic-ready-definition.md) — exact first-pass tank send/recovery stage ownership, shield strategy, and passive map
- [rev-a-crossfade-feedback-wet-schematic-ready-definition.md](rev-a-crossfade-feedback-wet-schematic-ready-definition.md) — exact first-pass crossfade, wet-return, and feedback-path definition
- [rev-a-filter-clipper-schematic-ready-definition.md](rev-a-filter-clipper-schematic-ready-definition.md) — exact first-pass filter/drive/clip stage ownership and mode truth
- [rev-a-control-backplane-schematic-ready-definition.md](rev-a-control-backplane-schematic-ready-definition.md) — exact first-pass control landing, mode encoding, and backplane reserve policy
- [rev-a-board-connector-schedule.csv](rev-a-board-connector-schedule.csv) — machine-readable connector ownership and harness schedule
- [rev-a-quote-request-packet.md](rev-a-quote-request-packet.md) — exactly which files to send each vendor and template request emails
- [rev-a-total-cost-rollup.md](rev-a-total-cost-rollup.md) — single per-unit cost estimate across electronics, fab, assembly, tanks, enclosure, and labor
- [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) — per-board test procedures with specific signals, equipment, and pass/fail thresholds
- [rev-a-manufacturing.md](rev-a-manufacturing.md) — vendor recommendations and file conventions
- [bom/rev-a-procurement-snapshot.md](bom/rev-a-procurement-snapshot.md) — current exact-part sourcing snapshot and scope split
- [rev-a-bringup-sequence.md](rev-a-bringup-sequence.md) — board-by-board power-up order
- [rev-a-open-issues.md](rev-a-open-issues.md) — what is still genuinely unresolved

## Next Deliverables

- Shared signal naming and connector conventions
- One spec per board
- Schematic packets with stage ownership and pin-level harness maps
- Control-law and circuit-value tables that track the current plugin behavior
- Remaining audio-sheet pin-level wiring, ERC cleanup, and PCB layout in the chosen EDA tool
