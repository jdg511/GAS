# GAS Rev A Capture Value Tables

This file is the schematic-capture companion to [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1).

Use it to reserve designator blocks and populate the first real schematic sheets with consistent starting values.

These are not claimed-final production values. They are the first capture values that should exist on the sheet instead of leaving whole analog sections unnamed or blank.

## 1. Input / Output Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| balanced input boundary and RF parts | `R1-R10`, `C1-C10` |
| left/right balanced receiver ratios | `R11-R18` |
| mono/stereo routing and split isolation | `R21-R30` |
| wet/dry summing | `R31-R40` |
| balanced output left | `R41-R50`, `C41-C44` |
| balanced output right | `R51-R60`, `C51-C54` |
| local decoupling and rail bulk | `C91-C99` |

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| input series protection | `R1-R4` | `100R` | one per balanced leg |
| RF shunt footprints | `C1-C4` | `220 pF`, DNP default | keep at the connector boundary |
| balanced receiver ratios | `R11-R18` | `10k`, `0.1%` | matched differential receiver ratios |
| split isolation | `R21-R24` | `100R` | one per dry/wet branch output if needed |
| wet input summing | `R31`, `R33` | `20k` | left dry and wet summing inputs |
| wet input summing | `R32`, `R34` | `20k` | right dry and wet summing inputs |
| summing feedback | `R35`, `R36` | `20k` | left/right summer feedback |
| balanced output gain set | `R41-R48` | `10k` | start with unity hot/cold stages |
| output build-out | `R49-R50`, `R59-R60` | `49.9R` | one per output leg |
| output RF footprints | `C41-C44`, `C51-C54` | DNP default | optional connector-facing suppression |

## 2. Tank Driver / Recovery Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| primary left send | `R101-R119`, `C101-C109`, `D101-D104` |
| primary right send | `R121-R139`, `C121-C129`, `D121-D124` |
| secondary left/right sends | `R151-R169`, `C151-C159` |
| primary recoveries | `R171-R189`, `C171-C179` |
| secondary recoveries | `R191-R209`, `C191-C199` |
| local decoupling and rail bulk | `C291-C299` |

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| primary base stoppers | `R101`, `R102`, `R121`, `R122` | `47R` to `100R` | one at each transistor base |
| primary emitter resistors | `R103`, `R104`, `R123`, `R124` | `0.22R` to `0.47R` | start with footprints that allow either value |
| primary zobel resistor | `R105`, `R125` | `10R` | pair with film cap |
| primary zobel capacitor | `C101`, `C121` | `47 nF` film preferred | tank-send stabilization |
| secondary send feedback | `R151`, `R152` | `12k` | left/right non-inverting gain |
| secondary send gain-to-ground | `R153`, `R154` | `10k` | gives about `2.2x` gain |
| secondary send series output | `R155`, `R156` | `220R` | one per secondary send |
| recovery input bias | `R171-R174` | `2.2M` | one per recovery input |
| recovery gain-to-ground | `R175-R178` | `1k` | one per recovery stage |
| recovery feedback | `R179-R182` | `33k` | one per recovery stage |
| recovery feedback comp | `C171-C174` | `47 pF` to `100 pF`, DNP-friendly | stability tuning footprint |
| recovery input coupler if required | `C175-C178` | `22 nF` film preferred | only if direct coupling proves impractical |

## 3. Ext Tank Routing Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| left routing / summing | `R201-R219`, `C201-C209` |
| right routing / summing | `R221-R239`, `C221-C229` |
| series makeup and feedback injection | `R241-R259`, `C241-C249` |
| relay coil suppression and housekeeping | `D261-D268`, `R261-R269`, `C261-C269` |
| local decoupling and rail bulk | `C291-C299` |

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| routing/summing inputs | `R201-R208`, `R221-R228` | `20k` | primary, secondary, and wet summing starts |
| routing feedback | `R209`, `R229` | `20k` | unity-gain active sums |
| series makeup trim | `R241` | `20k` nominal plus trim footprint | only if series mode needs lift |
| feedback reinjection resistor | `R242`, `R243` | `20k` | left/right feedback return entry |
| relay flyback | `D261-D264` | diode footprint or suppression network | required if coils are transistor-driven |

## 4. Crossfade / Feedback / Wet Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| left/right crossfade network | `R301-R319`, `C301-C309` |
| feedback loop | `R321-R339`, `C321-C329` |
| wet output handoff | `R341-R349`, `C341-C344` |
| local decoupling and rail bulk | `C391-C399` |

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| crossfade summing resistors | `R301-R308` | `20k` | equal-value network start |
| feedback pot series floor | `R321`, `R322` | `10k` | prevents hard-zero instability |
| feedback return resistors | `R323`, `R324` | `20k` to `100k` capture placeholders | tune loop gain on bench |
| feedback compensation footprints | `C321`, `C322` | `47 pF`, DNP default | one per channel or shared utility stage |
| wet output isolators | `R341`, `R342` | `100R` | useful if the return harness loading changes |

## 5. Filter / Clipper Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| left HPF | `R401-R419`, `C401-C409` |
| right HPF | `R421-R439`, `C421-C429` |
| left/right drive and clip | `R441-R469`, `C441-C449`, `D401-D412` |
| left LPF | `R471-R489`, `C471-C479` |
| right LPF | `R491-R509`, `C491-C499` |
| output buffers and local utility | `R511-R519`, `C511-C519` |
| local decoupling and rail bulk | `C591-C599` |

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| filter timing footprints | `C401-C409`, `C421-C429`, `C471-C479`, `C491-C499` | fit `10 nF`, `22 nF`, and `47 nF` options | keep the board flexible during tuning |
| general filter resistor space | `R401-R419`, `R421-R439`, `R471-R509` | start around `10k` to `33k` capture values | exact values depend on chosen topology |
| clip silicon pair | `D401-D404` | `1N4148W` | symmetrical silicon option |
| clip LED pair | `D405-D408` | red SMD LED pair | higher threshold clip option |
| clip germanium pair | `D409-D412` | germanium or adapter footprints | asymmetrical option if needed |
| drive gain placeholder resistors | `R441-R448` | choose values that allow `0 dB` to `+20 dB` range | bench-tune around actual clip feel |

## 6. Power / Backplane Board

### Recommended Designator Reservations

| Block | Recommended RefDes Block |
| --- | --- |
| DC entry and protection | `J500`, `D500`, `F500`, `TVS500`, `C500` |
| low-voltage conversion | `PS500`, `PS501`, `FB500-FB501`, `C501-C514` |
| board power fan-out and test | `P501-P506`, `TP501-TP509` |
| chassis bond / star point | `R551`, `C551`, `L551` if used | 

### Starting Circuit Table

| Stage | Part Group | Start Value / Part | Notes |
| --- | --- | --- | --- |
| split-rail outputs | `P501-P505` | `3-position JST VH` | `+15VA`, `AGND`, `-15VA` |
| ext-routing power | `P506` | `4-position JST VH` | includes `+5VAUX` |
| chassis bond placeholder | `R551/C551` | reserve for bond strategy parts if used | only one controlled bond point |
| local rail bulk | `C501-C519` | power-only ceramic/electrolytic set | not in the audio path |

## What This File Intentionally Leaves Open

- exact final filter topology values
- exact primary send bias network values
- exact feedback loop gain values
- any final compensation part that only real bench work can justify

That is intentional. The goal is to freeze what is already known while keeping honest room for the small set of values that still depend on the real spring hardware.
