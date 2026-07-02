# GAS Rev A Capacitor Policy

This project now has an explicit audio-path capacitor-selection preference:

- in the audio path, avoid ceramic capacitors where practical
- in the audio path, avoid tantalum capacitors
- in the audio path, avoid electrolytic capacitors where practical

## Preferred Order

1. direct coupling with correct biasing if no capacitor is needed
2. film
3. PPS-film
4. polypropylene
5. polyester
6. mica

## What This Means In Practice

- balanced I/O and internal gain stages should be direct-coupled where sensible
- filter timing positions should use film-family parts where practical
- large-value coupling caps should be treated as a warning sign to revisit the circuit topology
- power-supply filtering and rail decoupling may use ceramic or electrolytic parts where that is the practical engineering choice

## Expected Exceptions

The biggest likely exception zone is the primary `4AB1C1B` send driver if the design keeps a single-supply, capacitor-coupled approach.

If a ceramic, tantalum, or electrolytic capacitor becomes truly unavoidable in the audio path:

- document the exact reason
- document the location
- document why the non-ceramic alternative was not practical for rev A

## Design Consequences

- board area may increase
- some boards may become mixed through-hole / SMD
- the first prototype may prioritize capacitor policy over density

That tradeoff is acceptable for rev A.
