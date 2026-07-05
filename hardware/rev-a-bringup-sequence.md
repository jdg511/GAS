# GAS Rev A Bring-Up Sequence

This is the intended order for first-power and first-audio work once the real boards exist.

## 1. Power / Backplane Only

- verify wall-adapter polarity and service-endcap DC jack wiring with the unit unplugged
- power the backplane with no audio boards connected
- verify:
  - `+15VA`
  - `-15VA`
  - `+5VAUX`
  - single controlled `AGND` to `CHASSIS` bond
- confirm no abnormal DC-DC or `+5V` regulator heating

## 2. I/O Board Standalone

- connect only `H1`
- inject balanced `+4 dBu` at `1 kHz`
- verify:
  - balanced receiver output is clean
  - mono-to-stereo duplicates the left internal source as intended
  - `DRY_L/R` and `WET_SEND_L/R` are present
  - balanced outputs produce equal and opposite hot/cold legs

## 3. Tank Driver / Recovery Board Standalone

- connect only board power
- verify quiescent rail current before tanks are attached
- trim or inspect primary send idle current at zero signal
- inject a small bench signal into each send stage and verify no oscillation
- short recovery inputs through a safe test network and verify gain/noise floor

## 4. Ext-Routing Board Plus Tank Driver / Recovery

- connect `H5`, `H6`, and `H14`
- exercise `Off`, `Series`, and `Parallel`
- confirm relay logic and contact routing before real tanks are attached
- then attach tanks and verify send level stays within a safe starting range

## 5. Crossfade / Feedback / Wet Board

- connect `H7`, `H10`, and `H12`
- verify crossfade reaches both extremes cleanly
- start with minimum feedback and increase slowly
- confirm phase invert changes loop polarity and does not pop excessively

## 6. Filter / Clipper Board

- connect `H8`, `H9`, and `H13`
- verify clean mode first
- then verify silicon, LED, and germanium clip paths one at a time
- sweep HPF and LPF controls to confirm stereo tracking is at least acceptable for rev A

## 7. Full-System Audio Pass

- reconnect the full chain
- verify:
  - dry-only output
  - wet-only output
  - ext tanks `Off`
  - ext tanks `Series`
  - ext tanks `Parallel`
  - mono-to-stereo on and off
  - feedback stable across the intended control range

## First Measurements To Archive

- rail voltages at every board
- quiescent current per rail
- primary send DC offset and idle current
- balanced output amplitude at nominal `+4 dBu`
- noise floor with tanks connected and with tanks disconnected
