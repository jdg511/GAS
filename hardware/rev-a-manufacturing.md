# GAS Rev A Manufacturing Handoff

This file records where to send the finished design files once the KiCad project is complete.

Current vendor guidance in this file was rechecked on `2026-06-29`.

The current exact-part sourcing snapshot for the frozen rev-A fixed parts lives in:

- [bom/rev-a-procurement-snapshot.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-procurement-snapshot.md:1)

Current package status:

- board architecture, connector schedule, harness/endcap assumptions, and schematic-ready definitions are in place
- the KiCad project is still an intermediate capture, not a final fabrication release
- top-level ERC was rerun on `2026-06-29` and currently reports `650` known intermediate violations dominated by unconnected sheet pins and placeholder child-sheet wiring on the non-power audio/control pages
- the latest I/O-board cleanup pass removed the accidental center-short stubs in the first-pass receiver / blend / output-driver capture and reduced that child sheet from `404` to `376` local violations

## Recommended Build Path

### Best Prototype Path

1. Use `KiCad 10` for schematic capture and PCB layout
2. Send SMT-heavy analog boards for fabrication/assembly
3. Hand-install or consigned-install the bulky mechanical parts:
   - spring tanks
   - any user-supplied vacuum tubes
   - combo `XLR / TRS` panel jacks
   - panel switches
   - panel potentiometers
   - service-endcap DC barrel jack
   - user-supplied enclosure tube

Note: rev A no longer carries any mains-side circuitry. The internal `Mean Well RT-50C` AC/DC module is gone; DC arrives via an external `+30VDC` wall-adapter strategy and is converted to `+/-15V / +5V` on the power-backplane PCB by an isolated DC-DC + small +5V switching regulator. The currently user-preferred `Jameco DDU300050E9340` page still has to be treated as an unverified adapter candidate because the live listing describes it as an unregulated linear adapter. See [rev-a-external-dc-power.md](rev-a-external-dc-power.md). This eliminates the IEC inlet, fuse holder, mains creepage rules, and the chassis-bond safety-test step that earlier revisions of this document called out.
4. Perform bench tuning on the tank send/recovery and filter sections
5. Only then freeze the production BOM

### Where To Send The Files

#### JLCPCB

Best fit:

- fast prototype PCB fab
- SMT assembly for the op-amp / relay / passive-heavy boards

Current JLCPCB assembly handoff guidance says to provide:

- `Gerber`
- `BOM`
- `CPL / centroid / positions`

Relevant current source:

- [JLCPCB KiCad BOM/CPL guide](https://jlcpcb.com/help/article/how-to-generate-the-bom-and-centroid-file-from-kicad)
- [JLCPCB BOM requirements](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly)

Recommendation:

- Use JLCPCB for the first board spins
- Treat the service endcap hardware and the user-supplied tube as separate mechanical work

#### PCBWay

Best fit:

- PCB fab plus broader assembly support
- more realistic option when through-hole and odd mechanical parts begin to matter

Current PCBWay assembly guidance says to provide:

- `Gerber` files
- `Centroid` / pick-and-place file
- `BOM`

Relevant current source:

- [PCBWay assembly file requirements](https://www.pcbway.com/assembly-file-requirements.html)

Recommendation:

- Use PCBWay when the design moves past bare/SMT prototype boards and you want more help with mixed-technology assembly

#### MacroFab

Best fit:

- low-volume turnkey manufacturing
- U.S.-friendly handoff
- better candidate for a semi-turnkey production build once the design is stable

Current MacroFab guidance says it accepts:

- native project files
- `Gerber` / `ODB++`
- `BOM`

Relevant current source:

- [MacroFab required design files](https://support.macrofab.com/s/article/macrofab-required-design-files)
- [MacroFab platform overview](https://www.macrofab.com/platform/)

Recommendation:

- If the goal is "I want a company to own more of the sourcing and assembly workflow", MacroFab is the strongest final-build target from the options researched in this session

#### Endcap / Mechanical Vendors

Best fit:

- `Front Panel Express` for engraved or printed circular endcap artwork
- `SendCutSend` for simple cut/drill circular plates and internal brackets
- `Protocase` for a more turnkey custom-mechanical package when the project is ready to hand a vendor the endcaps, brackets, and internal mounting hardware together

Relevant current sources:

- [Front Panel Express](https://www.frontpanelexpress.com/)
- [SendCutSend custom metal parts](https://sendcutsend.com/)
- [Protocase custom enclosures](https://www.protocase.com/)

Recommendation:

- For rev-A prototype work, keep the user-supplied tube outside the vendor quote and send only the circular endcaps, reinforcement plates, and brackets to the mechanical vendor
- If later revisions need a more turnkey enclosure package, `Protocase` is the best fit from the researched vendors. This is an inference from its custom-enclosure service model, not a claim that it has a stock cylindrical product

## Files To Generate From KiCad

When the KiCad project is ready, generate:

- schematic PDF set
- fabrication `Gerbers`
- drill files
- IPC netlist or design archive
- assembly `BOM.csv`
- pick-and-place / `positions.csv`
- board stackup note
- assembly drawings
- test notes and calibration notes

For rev A, also include:

- [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1)
- [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
- [rev-a-board-package-freeze.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-package-freeze.md:1)
- [rev-a-board-connector-schedule.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-connector-schedule.csv:1)
- [rev-a-bringup-sequence.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-bringup-sequence.md:1)
- [rev-a-endcap-hole-table.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-hole-table.md:1)
- [rev-a-endcap-hole-table.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-hole-table.csv:1)
- [rev-a-board-outline-assumptions.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.md:1)
- [rev-a-board-outline-assumptions.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.csv:1)
- [rev-a-harness-cut-lengths.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-harness-cut-lengths.md:1)
- [rev-a-harness-cut-lengths.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-harness-cut-lengths.csv:1)

Supporting manufacturing references already in the repo:

- [rev-a-pcb-fabrication-assumptions.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-pcb-fabrication-assumptions.md:1)
- [bom/rev-a-cost-summary.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-cost-summary.md:1)
- [bom/rev-a-board-priced-summary.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-board-priced-summary.md:1)
- [bom/rev-a-procurement-snapshot.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-procurement-snapshot.md:1)

For the mechanical vendor, also include:

- circular service-endcap drill schedule
- preferred board-outline/rail assumptions
- harness cut-length assumptions so the shop understands why the service end needs accessible routing space

## Recommended Quote Package Split

For rev A, the cleanest handoff is to treat the build as three BOM layers:

1. `SMD core BOM`
   - active ICs
   - relays
   - critical passives
   - board-mount support parts
2. `Connector / internal harness BOM`
   - JST board headers
   - mating housings
   - crimp contacts
3. `Mechanical / consigned BOM`
   - spring tanks
   - combo `XLR / TRS` jacks
   - service-endcap DC jack
   - panel switches
   - panel potentiometers
   - endcap plates and reinforcement hardware
   - user-supplied enclosure tube

This keeps the SMT assembly quote realistic while still preserving a complete manufacturing package.

## Parts That Should Usually Be Consigned Or Purchased Separately

- the four spring tanks
- any user-supplied vacuum tubes
- tank RCA cabling
- user-supplied enclosure tube
- any custom faceplate or screened panel

## Preferred Sourcing Pattern

The latest project direction is:

- let the PCB build company place the common SMD parts
- keep the design centered on widely available analog ICs, relays, and passives
- treat tanks and enclosure hardware separately from the SMD assembly quote

The current approved alternates and supply-risk notes live in:

- [bom/rev-a-supply-watch.md](C:/Users/Jason/GAS-build/repo/hardware/bom/rev-a-supply-watch.md:1)

For the common SMD semiconductors and support parts, the best mainstream sources found during this session were:

- [DigiKey](https://www.digikey.com/)
- [Mouser](https://www.mouser.com/)

Use these as the reference market for:

- TI op-amps
- ST BD139 / BD140 primary send transistors
- LM386 driver ICs if the fallback path is ever needed
- Omron relays
- low-voltage conversion parts and the service-endcap DC jack

Panel hardware, tanks, endcaps, and the enclosure tube can stay outside the SMD house BOM until the mechanical package is frozen.

If this build uses tubes, keep them consigned as well. The current rev-A fixed PCB package does not yet carry frozen tube SKUs, so the assembler should not source tubes from the main BOM.

The spring tanks are explicitly separate-purchase items and should stay outside the SMD assembly quote.

The external balanced I/O format is now fixed:

- combo `XLR / TRS` jacks for input and output

One practical note from Neutrik's combo-jack family documentation:

- the standard combo receptacle family is positioned as an XLR receptacle plus 1/4-inch jack solution commonly used for balanced mic or line inputs

Because the project requirement is combo jacks for both input and output, rev A should keep the combo format but sanity-check the female-XLR output convention before the chassis metalwork is frozen.

## Practical Recommendation

For the first real hardware pass:

- send the SMT board files to JLCPCB or PCBWay
- keep the BOM centered on common SMD parts
- let the builder quote the common passives directly from its house supply chain
- use MacroFab only after the first tuned prototype proves the circuits and connector strategy

## Best Current Recommendation

As of `2026-06-29`:

- `JLCPCB` is still the cleanest first stop for bare-board plus common-SMD prototype spins
- `PCBWay` is the better next step if the build starts leaning harder on mixed through-hole, odd connectors, or more hands-on assembly support
- `MacroFab` is the best handoff target if you want a U.S.-based company to absorb more of the sourcing and assembly workflow once the analog design is proven
