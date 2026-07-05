# GAS Rev A Validation Checklist

Use this after the first schematic capture and again after the first assembled boards arrive.

## Schematic Review

- balanced receiver topology matches combo `XLR / TRS` pinout
- mono-to-stereo switch occurs after the balanced receiver
- no digital control dependency has crept into the design
- all audio op amps except the intentional exception tolerate `+/-18V`
- primary and secondary tank paths match the correct tank models
- feedback phase invert is only in the feedback loop

## Layout Review

- recovery nodes are far from PSU and relay-coil traces
- combo-jack routing keeps balanced legs paired
- star ground and chassis bond are intentional
- all tuning footprints and DNP options are still present

## Bring-Up

- verify `+15V`, `-15V`, `+5V`
- verify no relay control faults
- inject balanced `+4 dBu` and confirm clean internal level
- confirm mono-to-stereo switch duplicates the selected mono input
- confirm primary and secondary tank send levels are safe
- confirm no unexpected oscillation in the feedback loop

## Audio Validation

- Off / Series / Parallel routing behaves as intended
- ext-tank amount means the same thing perceptually in series and parallel
- balanced output level is correct and stable at nominal `+4 dBu`
- filter ranges are useful with the real tanks
- clipping modes sound intentional rather than merely louder

## Manufacturing Package

- KiCad project opens cleanly
- ERC and DRC reports are archived
- Gerbers, drills, BOM, and position files are exported
- assembly notes clearly separate SMD-house parts from consigned/mechanical parts
- connector and harness BOM is exported separately from the SMD core BOM
- schematic packet, interconnect pin map, and bring-up notes are bundled with the quote package
