# GAS Rev A Layout Rules

These rules should be followed once the KiCad PCB layouts start.

## Highest Priority

- Keep tank recovery inputs physically far from AC/DC power conversion
- Keep relay coil currents and their return paths away from recovery and balanced line receiver traces
- Keep balanced input and output traces paired and symmetric as they approach the panel connectors

## Grounding

- Use a clear analog ground strategy on every board
- Join `AGND` to `CHASSIS` at one controlled star point only
- Do not let tank shield returns wander through the same copper that carries PSU ripple currents

## Power Decoupling

- Every op-amp package gets local rail decoupling to each rail
- Every board gets local bulk capacitance on `+15VA` and `-15VA`
- Ceramic and electrolytic parts are acceptable in power-supply and rail-decoupling positions
- Route decoupling returns directly to the local analog ground reference

## Audio-Path Capacitors

- In the audio path, prefer direct coupling first
- If an audio-path capacitor is required, prefer film, PPS-film, polypropylene, polyester, or mica where practical
- Avoid ceramic, tantalum, and electrolytic capacitors in the audio path unless an explicit exception is documented

## Balanced I/O

- Keep resistor ratios physically close in the balanced receiver and driver stages
- Use matched-routing discipline on positive and negative legs near the connectors
- Put EMI/RFI footprints right at the external interface boundary

## Tank Send / Return

- Separate send and return routing where practical
- Tank return traces should be short, quiet, and guarded from relay or supply noise
- If board-to-tank cables run near power wiring, use shielded cable and avoid parallel runs where possible

## Filter / Clipping

- Keep left and right filter sections mirrored as much as possible
- Keep clipping diodes and their surrounding feedback loops compact
- Leave room for alternate stuffing options in the clip-mode section

## Testability

- Add test pads for:
  - each board rail
  - primary send outputs
  - secondary send outputs
  - each recovery output
  - feedback inject/return nodes
  - balanced output legs

## Prototype Friendliness

- Leave footprints for gain-trim resistors where send and recovery levels are uncertain
- Prefer footprints that allow easy resistor substitution during bench tuning
- Do not optimize away debug access on rev A
