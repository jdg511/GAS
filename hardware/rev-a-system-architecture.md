# GAS Rev A System Architecture

This document locks the first practical analog hardware architecture for the real GAS unit.

## Scope

Rev A is the first buildable analog hardware interpretation of the current JUCE simulation.

- The real spring tanks replace only the simulation-only `predelay + convolution` stages.
- The rest of the signal path stays conceptually aligned with the software.
- No MCU, Arduino, Raspberry Pi, or general-purpose embedded computer is used on the production PCBs.

## Chosen Rev A Direction

### Product Topology

- Stereo analog spring reverb processor
- Balanced line-level stereo I/O
- Nominal operating level `+4 dBu`
- Designed for 600-ohm capable professional line interfacing
- External connectors: combo `XLR / TRS`
- Dedicated mono-input to stereo mode on the hardware input stage
- Four real tanks total:
  - Primary left: `4AB1C1B`
  - Primary right: `4AB1C1B`
  - Secondary left: `9EB2C1B`
  - Secondary right: `9EB3C1B`

### Power Strategy

Rev A should keep mains outside the enclosure.

- external wall-adapter candidate:
  - Jameco `DDU300050E9340`
  - nominal `+30 VDC`
  - `500 mA`
  - `15 W`
  - current live page must be treated as unverified for regulation status until bench-checked
- on-board conversion:
  - isolated DC-DC to `+15VA / -15VA`
  - local `+5VAUX` generation for relays and control support

This keeps every custom board low-voltage only and aligns with the user's request to keep the dangerous `110 VAC` side at the wall outlet, but the exact Jameco SKU still needs verification or replacement with a confirmed regulated alternate before it should be frozen for production handoff.

### Capacitor Strategy

Rev A should be designed around an audio-path capacitor-avoidance preference:

- in the audio path, avoid ceramic capacitors where practical
- in the audio path, avoid tantalum capacitors
- in the audio path, avoid electrolytic capacitors where practical
- for power-supply filtering and rail decoupling, practical ceramic or electrolytic parts are acceptable
- prefer film, PPS-film, polypropylene, polyester, mica, or direct-coupled solutions when those are practical

This especially affects:

- filter timing capacitors
- tank send/return coupling strategy
- any audio-path DC-blocking or AC-coupling positions
- whether the primary tank driver remains single-supply or moves toward a direct-coupled split-rail approach later

### Core Active Devices

- JFET / BiFET input front-end stage:
  - `Texas Instruments OPA1644AIDR`
- High-fidelity analog signal stages:
  - `Texas Instruments OPA1656IDR`
  - `Texas Instruments OPA1679IDR`
- Primary low-impedance spring send output pair:
  - `STMicroelectronics BD139-16`
  - `STMicroelectronics BD140-16`
- Secondary tank mode switching:
  - `Omron G6K-2F-Y-DC5` DPDT signal relays

These parts were chosen because they are current-production analog parts with verified distributor availability during this session.

### Rail-Tolerance Preference

Rev A should prefer devices that can survive at least `+18V / -18V` where practical.

- `OPA1656IDR` and `OPA1679IDR` satisfy that preference
- `OPA1644AIDR` also satisfies that preference and is the current preferred JFET-input front-end device
- the primary send output pair should also be chosen for safe operation in the planned split-rail environment

## Final Board Partition

### 1. Input / Output Board

Functions:

- balanced line receiver and protection
- mono-input to stereo switching
- dry split
- wet send feed
- final wet/dry blend
- balanced line driver

Chosen active parts:

- `1x OPA1644AIDR`
- `3x OPA1656IDR`

Rev A design notes:

- Keep this board clean and high-headroom.
- No intentional clipping belongs here.
- The final wet/dry blend should stay here so the output stage remains self-contained.
- Use a JFET or BiFET input device for the balanced receiver / input buffer side; `OPA1644AIDR` is the current rev-A choice.
- Convert the external balanced input to the local single-ended internal domain here.
- Implement the mono-input to stereo switch here, after the balanced receiver.
- Regenerate the final balanced output here.
- Use four op-amp channels across stereo for the final active balanced output stage.
- Design for at least `+20 dBu` internal analog headroom on `+/-15V` rails where reasonable.
- The external panel connection format is now fixed as combo `XLR / TRS`.
- The rev-A output is explicitly balanced line output, not an optional future variant.

### 2. Tank Driver / Recovery Board

Functions:

- primary send driver for the two `4AB1C1B` tanks
- secondary send driver for the `9EB2C1B` and `9EB3C1B` tanks
- low-noise recovery preamps for all four tanks
- RCA tank harness interface

Chosen active parts:

- `4x OPA1656IDR`
  - 1 dual for the two primary send predriver stages
  - 1 dual for secondary send drive
  - 2 duals for four recovery channels
- `2x BD139-16`
- `2x BD140-16`

Why this split:

- `4AB1C1B` presents an 8-ohm input load, so it needs a stronger drive stage than the 800-ohm secondary tanks.
- `9EB2C1B` and `9EB3C1B` can be driven cleanly from op-amp stages with appropriate output resistors and AC coupling.

Primary send starting point:

- split-rail OPA1656 predriver stage
- complementary `BD139-16` / `BD140-16` emitter-follower current stage
- direct-coupled if the bias and offset conditions are controlled properly
- local emitter resistors, bias-trim or bias-set network, and output current-limiting provisions
- bench-trim the send level with series/output trim if needed

Recovery starting point:

- OPA1656 non-inverting gain stage per return
- AC-coupled tank output
- high input impedance
- band-limiting at the recovery amp so spring hiss and RF stay contained

### 3. Ext Reverb Tank Off / Series / Parallel Board

Functions:

- bypass the secondary tanks
- feed them in series after the primary path
- feed them in parallel alongside the primary path
- scale the secondary contribution

Chosen active parts:

- `4x Omron G6K-2F-Y-DC5`
- `1x OPA1679IDR`

Chosen switching strategy:

- audio path switched by relays on-board
- front-panel selector is passive/low-current control only
- no firmware and no logic controller required

Relay truth-table intent:

- `Off`: primary path only
- `Series`: primary recovery feeds the secondary send path
- `Parallel`: wet input splits to primary and secondary send paths

### 4. Crossfade / Feedback / Wet Summing Board

Functions:

- stereo crossfade between left and right wet channels
- feedback amount
- feedback phase invert
- wet summing handoff to the I/O board

Chosen active parts:

- `1x OPA1679IDR`

Rev A design notes:

- Keep the feedback loop entirely analog.
- Put the phase-invert switch in the feedback loop only, not the main signal path.
- Add footprints for loop compensation and damping parts even if the first stuffing option is 0 ohm / DNP.

### 5. Filter / Clipping Board

Functions:

- pre-clipping HPF
- drive
- selectable clipping mode
- post-clipping LPF

Chosen active parts:

- `2x OPA1679IDR`

Chosen clipping modes:

- `Clean`
- `Silicon`
- `LED`
- `Germanium`

Rev A implementation note:

- Use diode-network selection with a rotary switch rather than multiplexing the clip topology in digital control.
- The exact filter value set should be tuned on the bench against the current plugin defaults, but the topology should remain fully analog.

## Controls Strategy

Rev A should use direct analog panel hardware, but not every control has to land directly on the same audio PCB:

- rotary switch for `Off / Series / Parallel`
- rotary switch for clip mode
- potentiometers for wet/dry, ext mix, crossfade, drive, HPF/LPF frequency and Q, feedback
- toggle switch for feedback polarity
- dedicated mono-input to stereo switch

Acceptable rev-A implementations are:

- board-mounted controls where a PCB naturally sits behind the panel
- a power/control/backplane landing board for the denser stereo-control groups

Where a clean, current dual-gang part was already verified, use it. Where sourcing for the exact stereo-ganged linear part still needs a final order-time check, keep the footprint and panel-hole assumptions open until schematic capture.

Because the PCB builder will mainly be assembling SMD content, the panel hardware should be treated as enclosure-level parts rather than as the heart of the electrical BOM.

## Mechanical Strategy

- The enclosure is a user-supplied cylindrical tube, `10 in` nominal diameter and `48 in` long.
- All external I/O and DC power entry land on one circular service endcap.
- Mount the spring tanks to the chassis or an internal subframe, not directly to the signal PCBs.
- Use shielded RCA tank cables internally.
- Keep tank recovery circuitry physically distant from the power-entry and relay-control zone.
- Separate chassis ground from audio ground, then bond them at one controlled location near the service endcap power-entry area.
- Prefer rail-mounted or sled-mounted boards running along the tube axis rather than a flat chassis-floor layout.

## Rev A Risk List

- The primary `4AB1C1B` 8-ohm send path is the highest hardware risk and will need bench tuning
- The preferred direct-coupled primary send stage is more aligned with the audio-path capacitor policy, but it is more complex than the fallback LM386 approach
- Tank recovery noise and grounding will decide whether the unit feels premium or noisy
- Crossfade and feedback stability need analog trim points before the first production spin
- The filter section can be built directly, but HPF/LPF Q ranges should be validated against listening tests before production

## What Is Actually Locked

Locked in this document:

- analog-only architecture
- tank choices
- board split
- external `+30 VDC` wall-adapter plus on-board conversion strategy
- core active devices
- relay-based ext-tank routing approach
- cylindrical one-endcap service format

Still meant to be tuned during schematic capture:

- exact RC values around the tank send/recovery circuits
- exact filter component values
- exact pot law per control where the software response needs listening validation
