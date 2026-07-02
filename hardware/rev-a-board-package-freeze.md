# GAS Rev A Board Package Freeze

This file is the compact "what each board is" reference for the current hardware package.

Use it when:

- populating the KiCad child sheets
- building per-board quote bundles
- checking that the mechanical, harness, and BOM layers still agree

The goal is not to replace the board briefs. It is to freeze the minimum board facts that should not drift casually.

## Global Rev-A Freeze

- Analog-only product electronics. No MCU, Arduino, Raspberry Pi, DSP module, or general-purpose embedded computer.
- External I/O is balanced line level, nominal `+4 dBu`, with 600-ohm capable line-interface behavior.
- External panel connectors are combo `XLR / TRS` jacks.
- The real tank set is `4AB1C1B x2`, `9EB2C1B x1`, `9EB3C1B x1`.
- Predelay and convolution remain software-only study tools and do not appear on the PCB set.
- Main supply architecture is external `+30 VDC` wall adapter into on-board conversion for `+15VA`, `-15VA`, and `+5VAUX`.
- The main cylindrical enclosure tube is user-supplied.

## Board Freeze Table

| Board | Target Envelope | Placement Zone | Main Active Set | Power | Main Connectors | Controls | Install Scope |
|---|---|---|---|---|---|---|---|
| Input / Output | `160 x 75 mm` | `25-100 mm` from service endcap | `1x OPA1644AIDR`, `3x OPA1656IDR` | `+15VA`, `AGND`, `-15VA` | `J1-J4`, `P1-P6` | wet/dry, mono-to-stereo | SMT core plus panel-handwired combo jacks |
| Power / Control Backplane | `150 x 95 mm` | `105-200 mm` | `1x URB2415YMD-10WR3`, `1x R-78E5.0-0.5`, optional `ULN2003ADR` | `+30VDC` input, generates `+15VA`, `-15VA`, `+5VAUX` | `J500`, `P501-P506`, optional `P601`, `P610-P614` | none directly; preferred control landing | mixed-tech or SMT plus handwired panel DC jack |
| Ext Tank Routing | `120 x 80 mm` | `225-305 mm` | `4x G6K-2F-Y-DC5`, `1x OPA1679IDR` | `+15VA`, `AGND`, `-15VA`, `+5VAUX` | `P201-P207` | ext mode, ext amount | SMT board, controls via backplane or local wiring |
| Crossfade / Feedback / Wet | `100 x 70 mm` | `325-395 mm` | `1x OPA1679IDR` | `+15VA`, `AGND`, `-15VA` | `P301-P307` | crossfade, feedback, feedback invert | SMT board, controls via backplane or local wiring |
| Filter / Clipper | `140 x 90 mm` | `415-505 mm` | `2x OPA1679IDR` | `+15VA`, `AGND`, `-15VA` | `P401-P405` | drive, HPF F/Q, LPF F/Q, clip mode | SMT board plus film-cap-heavy analog section |
| Tank Driver / Recovery | `170 x 110 mm` | `575-685 mm` | `4x OPA1656IDR`, `2x BD139-16`, `2x BD140-16` | `+15VA`, `AGND`, `-15VA` | `P101-P103`, `J101-J108` | no front-panel controls | mixed-tech board with shielded tank landing |

Placement zones above come from:

- [rev-a-board-outline-assumptions.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-board-outline-assumptions.csv:1)

## Per-Board Capture Freeze

### Input / Output

- `J1` and `J2` are balanced stereo inputs.
- `J3` and `J4` are balanced stereo outputs.
- Mono mode is a dedicated rev-A panel function and lives after the balanced receiver.
- Output stage is fully active balanced, not unbalanced and not pseudo-balanced.
- Audio-path capacitor choices should honor the non-ceramic/non-electrolytic preference where coupling is required.

### Power / Control Backplane

- No mains circuitry on-board.
- DC entry is `5.5 x 2.5 mm` barrel.
- One controlled `AGND` to `CHASSIS` bond only.
- This board is the preferred landing zone for dense front-panel controls if the panel is not directly board-mounted.
- `U601` remains reserve-only under the current frozen 2-bit ext-mode interface and should not be assumed populated in the fixed rev-A BOM.

### Ext Tank Routing

- Supports `Off`, `Series`, and `Parallel` for the secondary tanks only.
- Must preserve distinct left and right secondary tank identities:
  - left secondary = `9EB2C1B`
  - right secondary = `9EB3C1B`
- Relay current loops stay away from high-gain recovery nodes.

### Crossfade / Feedback / Wet

- This board owns the feedback loop gain and polarity function.
- The wet return sent back to the I/O board comes from here, not from the filter board directly.

### Filter / Clipper

- Clean mode bypasses intentional clipping rather than merely turning gain down.
- Keep mirrored left/right analog geometry as much as the film-cap footprint density allows.
- Reserve DNP footprints for alternate diode families and compensation parts.

### Tank Driver / Recovery

- This board is the real-world replacement for the software-only predelay/convolution surrogate.
- Primary sends are the highest-current analog path in the product and need thermal and loop-stability headroom.
- Recovery stages must stay physically quiet and separated from relay and DC-DC noise.

## Preferred Assembly Split

### Board-House Population

- op amps
- relays
- small passives
- low-voltage protection parts
- the DC-DC and +5V regulator modules if the selected assembler accepts them

### Hand Install Or Consigned Install

- combo `XLR / TRS` jacks
- panel DC jack
- panel pots, toggles, and rotaries
- TO-126 primary send transistors if the chosen assembler does not support them economically
- shielded tank cabling
- the four spring tanks
- the user-supplied enclosure tube

## Drift Checks

Before freezing any schematic sheet or PCB outline, confirm it still agrees with:

- [rev-a-interconnect-pin-map.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-interconnect-pin-map.md:1)
- [rev-a-control-harnesses.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-harnesses.md:1)
- [rev-a-endcap-panel-layout.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-endcap-panel-layout.md:1)
- [rev-a-harness-cut-lengths.csv](C:/Users/Jason/GAS-build/repo/hardware/rev-a-harness-cut-lengths.csv:1)
