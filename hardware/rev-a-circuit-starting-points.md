# GAS Rev A Circuit Starting Points

This file is the bridge between the board briefs and real schematics. It does not pretend to be the final tuned schematic, but it locks the first-pass analog topologies and starting values that should go into KiCad.

## 1. Balanced Input / Output Board

## Capacitor Interpretation

In this file:

- the audio path should avoid ceramic, tantalum, and electrolytic capacitors where practical
- power-supply and rail-decoupling positions may use practical ceramic or electrolytic parts

### Balanced Input Receiver

Per channel:

- topology: precision differential receiver
- active device: `OPA1644AIDR`
- resistor strategy:
  - use matched 0.1% resistor ratios
  - start with `10k / 10k / 10k / 10k`
- input protection:
  - `100R` series per leg
  - `220 pF` RF shunt placeholders, preferably PPS-film or mica if fitted
  - clamp network footprint placeholders if needed after EMC testing

Intent:

- convert balanced `+4 dBu` nominal line input into the local single-ended wet/dry domain
- maintain good CMRR without relying on scarce specialty analog front-end ICs
- satisfy the JFET / BiFET preference on the input buffer stage

### Mono-Input To Stereo Switch

Rev A requirement:

- add a dedicated analog mono-input to stereo switch after the balanced receiver

Starting behavior:

- `Stereo`: left receiver feeds left channel, right receiver feeds right channel
- `Mono -> Stereo`: selected mono source feeds both left and right internal channels

Preferred implementation:

- switch the already-received single-ended audio, not the balanced external lines
- default the selected mono source to the left input path unless later product decisions require left/right source selection

### Wet/Dry Mix

Per channel:

- topology: active inverting summer
- active device: `OPA1656IDR`
- starting values:
  - `20k` dry input resistor
  - `20k` wet input resistor
  - `20k` feedback resistor
- make the control law adjustable by changing the wet/dry pot taper later if listening tests call for it

### Balanced Output Driver

Per channel:

- topology: fully active dual-op-amp balanced line driver
- active devices:
  - `2x OPA1656IDR` total for stereo output
- starting values:
  - gain of `1`
  - `49.9R` series output resistor on each leg
  - optional RF shunt footprint at the connector-facing side

Intent:

- deliver balanced line output
- tolerate 600-ohm style professional interfacing
- keep common SMD active parts consistent with the rest of the design
- do not treat the rev-A output as optional, pseudo-balanced, or unbalanced

## 2. Tank Driver / Recovery Board

### Primary 4AB1C1B Send Driver

Per primary tank:

- topology: split-rail op-amp predriver plus complementary emitter-follower output stage
- active devices:
  - `OPA1656IDR`
  - `BD139-16`
  - `BD140-16`
- supply: `+15VA` and `-15VA`
- starting values:
  - op-amp stage gain: start near unity to modest gain
  - emitter resistors: start around `0.22R` to `0.47R` placeholders
  - base-stopper resistors: include footprints on both transistor bases
  - bias spreader / diode-bias network: include trim or selection option
  - zobel: `10R + 47 nF`, with film preferred for the capacitor
  - series trim resistor footprint between driver and tank input

Intent:

- drive the low-impedance 8-ohm primary tank input from the existing split rails
- avoid a large audio-path coupling capacitor if practical
- keep the stage simple enough for rev A while aligning better with the audio-path capacitor policy

### Secondary 9EBxC1B Send Driver

Per secondary tank:

- topology: non-inverting op-amp driver
- active device: `OPA1656IDR`
- starting values:
  - gain: start at `2.0` to `2.2`
  - feedback resistor: `12k`
  - ground resistor: `10k`
  - output series resistor: `220R`
  - keep this stage direct-coupled on split rails if stability and DC conditions allow
  - if a coupling capacitor is still required, prefer film and treat electrolytics as an exception rather than the default

Intent:

- drive the 800-ohm-input secondary tanks cleanly from standard high-headroom audio op-amp stages

### Tank Recovery Preamps

Per tank return:

- topology: AC-coupled non-inverting recovery stage
- topology note: if recovery biasing can be arranged cleanly, direct coupling is preferred over unnecessary coupling capacitors
- active device: `OPA1656IDR`
- starting values:
  - input coupling capacitor: `22 nF`, film preferred if coupling is required
  - bias to ground: `2.2M`
  - gain resistor to ground: `1k`
  - feedback resistor: start at `33k`
  - small feedback capacitor footprint: `47 pF` to `100 pF`, preferably mica or PPS-film where practical
  - output DC blocking only if later testing shows offset problems

Intent:

- prioritize low noise and stable recovery before trying to maximize raw gain

## 3. Ext Tank Routing Board

### Mode Switching

- use `G6K-2F-Y-DC5` relays in the audio path
- keep relay control separate from audio wiring
- add local flyback suppression if the coils are transistor-driven

### Series / Parallel Gain Staging

Starting approach:

- route audio with relays
- use unity-gain buffer points around switch nodes
- use one OPA1679 quad to cover:
  - left primary/secondary blend
  - right primary/secondary blend
  - optional series-path makeup gain
  - spare test or utility stage

Starting resistor values:

- unity-gain summers: `20k` input resistors, `20k` feedback
- series-path makeup trim footprint: `20k` nominal plus trim option

## 4. Crossfade / Feedback / Wet Summing Board

### Stereo Crossfade

Per stereo pair:

- topology: dual cross-mix around one OPA1679
- start with equal-value resistor network:
  - `20k` nominal summing resistors
  - crossfade control implemented by variable split between own-channel and opposite-channel contribution

Intent:

- preserve constant-ish level while moving between isolated stereo and crossfed stereo

### Feedback Loop

Per channel:

- topology: inverting feedback send/return mix
- start with:
  - `100k` feedback amount pot
  - `10k` series floor resistor so the loop never hard-shorts into instability
  - DPDT phase-invert switch in the loop
  - optional compensation footprint: `47 pF` across the feedback resistor, preferably mica or PPS-film where practical

Intent:

- make loop stability adjustable on the bench instead of forcing a second PCB spin for compensation alone

## 5. Filter / Clipping Board

### Filter Topology

Rev A recommendation:

- use active 2-pole state-variable or multiple-feedback sections
- keep the PCB flexible enough to tune between the two during capture if one is mechanically easier

First-pass target:

- per channel:
  - one pre-clipping HPF section
  - one post-clipping LPF section
- active device family: `OPA1679IDR`

Starting capacitor family:

- audio-path timing caps should begin with film, PPS-film, polypropylene, polyester, or mica choices
- avoid ceramic timing caps where practical
- start with `10 nF`, `22 nF`, and `47 nF` footprints available around the filter equations

### Drive And Clipping

Per channel:

- op-amp gain stage ahead of clip network
- start drive control around a `0 dB` to `+20 dB` range
- clip mode selection:
  - `Clean`: bypass clip network
  - `Silicon`: anti-parallel small-signal silicon diodes
  - `LED`: anti-parallel LEDs
  - `Germanium`: asymmetrical germanium pair

Suggested starting diode footprints:

- silicon: `1N4148W`
- germanium: SMD germanium availability varies, so leave both SMD and leaded-adapter footprints if board area permits
- LED: small SMD red LED pair

## Parts Families To Keep Common

- 0.1% resistor values for balanced receiver/output stages
- 1% resistor values for general audio gain stages
- practical local rail decouplers at every IC
- practical bulk rail capacitors per board
- `OPA1656IDR` and `OPA1679IDR` as the default audio op-amp family

## What To Tune First On The Bench

1. Primary send level into `4AB1C1B`
2. Recovery gain and noise floor
3. Series versus parallel level matching
4. Feedback loop stability
5. HPF / LPF ranges against listening tests
