# Remaining System Work

The rev-A board set is now defined at the architecture and schematic-ready level. What remains is not deciding *which* boards exist, but finishing the capture, layout, and quote package so a builder can act on it cleanly.

## Remaining Electrical Work

### 1. Finish audio-sheet KiCad capture

- Promote the remaining placeholder multi-unit op-amp sheets into fully wired first-pass schematics
- Reduce the known intermediate ERC debt on the non-power pages
- Keep the inter-board connector ownership aligned with [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)

### 2. Freeze first-pass passive populations

- Crossfade / feedback resistor sets
- Filter and clipper passives
- Tank-driver stability / compensation parts
- Power-backplane ripple-filter support parts

### 3. Complete PCB layout

- Place the six electrical boards against the current pipe-end mechanical assumptions
- Separate noisy DC conversion and relay current loops from recovery and wet-return nodes
- Preserve serviceable internal harness routing from the service endcap inward

## Remaining Mechanical Work

### 1. Finalize the service-endcap package

- Confirm the `10 inch` nominal pipe-end layout against the measured cap face
- Freeze combo `XLR / TRS` jack spacing and the low-voltage DC entry
- Confirm switch / pot spacing against the circular panel geometry

### 2. Finalize internal mounting assumptions

- Rail or bracket approach for the six boards
- Tank mounting geometry and cable reach
- Clearance around any user-supplied tube hardware

## Remaining Manufacturing Work

### 1. Build the final quote bundle

- Per-board Gerbers, drill, BOM, and CPL exports
- System-level readme and fab notes
- Separate electrical and mechanical quote packets

### 2. Bench-verify the external DC strategy

- Confirm whether the preferred Jameco `DDU300050E9340` sample behaves as a regulated supply
- Verify barrel polarity and open-circuit voltage
- Measure post-filter `+/-15VA` ripple at realistic load

## Practical Next Steps

1. Continue converting the remaining placeholder KiCad pages into real first-pass circuits
2. Re-run ERC after each contained sheet-level pass instead of destabilizing the top-level shell
3. Move to PCB layout only after the passive starting values and connector ownership are frozen
