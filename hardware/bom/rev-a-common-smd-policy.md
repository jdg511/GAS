# Rev A Common SMD Policy

This file exists so the assembler-facing BOM can stay sane even before every tuned passive value is frozen.

## Goal

Use common, easily substitutable SMD passives wherever possible so the builder can source them from normal inventory.

The main exception is capacitor selection: in the audio path, this project prefers to avoid ceramic, tantalum, and electrolytic capacitors wherever practical.

## Preferred Default Packages

- resistors:
  - `0603` for most signal-path values
  - `0805` where extra voltage margin, power, or hand-rework ease helps
- capacitors:
  - audio-path capacitors should prefer PPS-film or other film packages where practical
  - through-hole film parts are acceptable on rev A if that is the cleanest way to honor the audio-path capacitor preference
  - larger footprints and mixed-technology assembly are acceptable tradeoffs in the audio path
  - power-supply and rail-decoupling capacitors may use practical ceramic or electrolytic parts

## Preferred Value / Tolerance Policy

- gain-setting and general audio resistors:
  - `1%`
- matched-ratio balanced I/O networks:
  - `0.1%`
- preferred capacitor families:
  - audio path: film, PPS-film, polypropylene, polyester, mica
  - power path: practical ceramics and electrolytics are allowed

## What The Assembly House Can Usually Source Freely

- generic thick-film resistors
- generic MLCC decouplers for power rails
- common small-signal silicon diodes
- common LEDs

## What Should Usually Stay Explicit In The BOM

- op amps
- relays
- power module
- any unusual germanium device choice
- any matched resistor network if a discrete 0.1% approach is replaced by a network part
- any audio-path capacitor that violates the capacitor-avoidance preference

## Suggested Builder Message

When requesting prototype assembly, tell the builder:

- common passive values may be builder-stock equivalents
- active devices and relays should match the specified manufacturer part numbers
- audio-path capacitor substitutions should not move the design back to ceramic, tantalum, or electrolytic parts without an explicit review
- DNP footprints are intentional and should remain unstuffed unless the BOM explicitly calls for them
