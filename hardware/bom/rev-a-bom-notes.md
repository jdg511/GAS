# Rev A BOM Notes

The priced BOM in `rev-a-core-priced-bom.csv` is intentionally the current, quote-friendly SMD core set rather than a fake "100% frozen" production BOM.

## What Is Already Strong

- main op-amps
- relay family
- power module
- non-ceramic audio-path capacitor direction
- fully active balanced stereo output direction

These are the decisions most likely to affect the electrical and mechanical architecture, so they were locked first.

## What Still Needs Order-Time Confirmation

- exact stereo control hardware part numbers for crossfade and filter controls
- exact direct-panel versus control-backplane implementation for the denser control groups
- exact RCA harness or custom shielded cable part numbers
- final passive value list after tank-send, recovery, and filter tuning
- exact balanced external connector hardware once the enclosure format is frozen
- any audio-path capacitor exception that still ends up being ceramic, tantalum, or electrolytic

## Why The Passives Are Not Pretended Final Yet

The biggest unknown in this build is not "which 10k resistor do we buy." It is:

- the exact send level each tank wants
- the exact recovery gain/noise tradeoff
- the exact filter corner values that sound right with the real tanks
- where a truly practical non-ceramic solution exists for each audio-path coupling, timing, and compensation position

Those are bench-tuning tasks. Once the first schematic and prototype come together, the full passive BOM can be frozen quickly.

## Practical Cost Read

Even before the fully frozen passive list:

- the verified SMD active / relay / PSU core is relatively modest
- enclosure, connector hardware, tank hardware, harnessing, and assembly labor will dominate the total prototype cost
- balanced line I/O and tank wiring discipline matter more to success than penny-optimizing common passives
