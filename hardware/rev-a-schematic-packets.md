# GAS Rev A Schematic Packets

This file is the direct capture packet for the first real KiCad pass. It sits between the board briefs and the final `.kicad_sch` population.

The goal is simple:

- every board gets a concrete stage breakdown
- every connector gets a pin-level job
- every major active device gets channel ownership
- every high-risk analog node gets a test and layout note

## Global Capture Rules

- Use `+15VA`, `-15VA`, `AGND`, `+5VAUX`, and `CHASSIS` exactly as named elsewhere in the hardware package.
- Keep external balanced I/O differential only at the panel boundary. Internal inter-board audio remains single-ended unless a board packet says otherwise.
- Prefer direct coupling in the audio path first.
- If an audio-path capacitor is required, prefer film, PPS-film, polypropylene, polyester, or mica where practical.
- Every op-amp package gets local rail decoupling and at least one nearby rail test pad.
- Rev A should preserve trim, DNP, and compensation footprints instead of optimizing them away.

## 1. Input / Output Board Packet

### Functional Summary

- balanced line receive for left and right inputs
- mono-input to stereo duplication after the balanced receiver
- dry split and wet send handoff
- final wet/dry summing
- fully active balanced line output for left and right outputs

### Active Allocation

- `U1` `OPA1644AIDR`
  - `U1A` left balanced receiver
  - `U1B` right balanced receiver
  - `U1C` mono/stereo routing buffer left
  - `U1D` mono/stereo routing buffer right
- `U2` `OPA1656IDR`
  - `U2A` left wet/dry summer
  - `U2B` right wet/dry summer
- `U3` `OPA1656IDR`
  - `U3A` left balanced output hot leg
  - `U3B` left balanced output cold leg
- `U4` `OPA1656IDR`
  - `U4A` right balanced output hot leg
  - `U4B` right balanced output cold leg

### External Connector Intent

- `J1` left combo `XLR / TRS` input
  - `XLR pin 1` and `TRS sleeve` to chassis entry strategy
  - `XLR pin 2` and `TRS tip` = `IN_BAL_L_P`
  - `XLR pin 3` and `TRS ring` = `IN_BAL_L_N`
- `J2` right combo `XLR / TRS` input
  - `XLR pin 1` and `TRS sleeve` to chassis entry strategy
  - `XLR pin 2` and `TRS tip` = `IN_BAL_R_P`
  - `XLR pin 3` and `TRS ring` = `IN_BAL_R_N`
- `J3` left combo `XLR / TRS` output
  - `XLR pin 1` and `TRS sleeve` to chassis entry strategy
  - `XLR pin 2` and `TRS tip` = `OUT_BAL_L_P`
  - `XLR pin 3` and `TRS ring` = `OUT_BAL_L_N`
- `J4` right combo `XLR / TRS` output
  - `XLR pin 1` and `TRS sleeve` to chassis entry strategy
  - `XLR pin 2` and `TRS tip` = `OUT_BAL_R_P`
  - `XLR pin 3` and `TRS ring` = `OUT_BAL_R_N`

### Recommended First-Pass Circuit Blocks

#### Input Protection And RF Boundary

- `R1-R4` `100R`
  - series in each balanced input leg
- `C1-C4` `220 pF` DNP by default
  - RF shunt footprints at the connector boundary
- reserve clamp footprints near `J1/J2`
  - DNP unless EMC testing requires them

#### Balanced Receiver

- `U1A` and `U1B`
- `R11-R18`
  - `10k`
  - `0.1%`
  - matched ratio network per channel
- target gain
  - unity differential receive

#### Mono To Stereo Switch

- `SW1`
  - dedicated rev-A mono-input to stereo switch
  - switch single-ended audio after `U1A/U1B`
- `Stereo`
  - `IN_L` stays left
  - `IN_R` stays right
- `Mono -> Stereo`
  - left internal source drives both left and right wet/dry paths

#### Dry Split And Wet Send

- split each received channel into:
  - `DRY_L` or `DRY_R`
  - `WET_SEND_L` or `WET_SEND_R`
- allow small source resistors at each split output
  - start with `100R`

#### Wet/Dry Summing

- `U2A` left
- `U2B` right
- starting values per channel:
  - dry input resistor `20k`
  - wet input resistor `20k`
  - feedback resistor `20k`
- `P5`
  - off-board wet/dry pot if not board-mounted
  - use a full 6-wire stereo control connection, not a compressed 2-wire or 3-wire shortcut

#### Balanced Output Driver

- fully active balanced output, not unbalanced and not pseudo-balanced
- each channel uses two op-amp stages:
  - hot leg non-inverting buffer or gain stage
  - cold leg inverting stage matched to unity gain
- starting values per leg:
  - gain-setting resistors `10k / 10k`
  - series output resistor `49.9R`
  - optional small RF shunt footprint at the jack-facing side

### Board Connectors

- `P1` power `JIO-PWR`
- `P2` wet send `JIO-WETSEND`
- `P3` wet return `JIO-WETRET`
- `P4` dry reference `JIO-DRY`
- `P5` wet/dry control
- `P6` mono/stereo switch

### Layout Priorities

- put `J1/J2` and their RF boundary parts on one edge
- keep `R11-R18` tightly clustered around `U1`
- keep `U3/U4` and their output resistor pairs close to `J3/J4`
- do not route output leg returns through input ground copper

### Bring-Up Test Points

- `TP_IO_P15`, `TP_IO_N15`, `TP_IO_GND`
- `TP_IN_L`, `TP_IN_R`
- `TP_WETSEND_L`, `TP_WETSEND_R`
- `TP_WETSUM_L`, `TP_WETSUM_R`
- `TP_OUT_L_P`, `TP_OUT_L_N`, `TP_OUT_R_P`, `TP_OUT_R_N`

## 2. Tank Driver / Recovery Board Packet

### Functional Summary

- primary send drive for left and right `4AB1C1B`
- secondary send drive for left `9EB2C1B` and right `9EB3C1B`
- four recovery preamps
- shielded tank cabling boundary

### Active Allocation

- `U101` `OPA1656IDR`
  - `U101A` primary left predriver
  - `U101B` primary right predriver
- `Q101/Q102`
  - primary left `BD139-16` / `BD140-16`
- `Q103/Q104`
  - primary right `BD139-16` / `BD140-16`
- `U102` `OPA1656IDR`
  - `U102A` secondary left send
  - `U102B` secondary right send
- `U103` `OPA1656IDR`
  - `U103A` primary left recovery
  - `U103B` primary right recovery
- `U104` `OPA1656IDR`
  - `U104A` secondary left recovery
  - `U104B` secondary right recovery

### Primary Send Block

- direct-coupled split-rail output stage
- start with:
  - op-amp gain near `1`
  - base stoppers `47R` to `100R`
  - emitter resistors `0.22R` to `0.47R`
  - zobel `10R + 47 nF`
  - trim footprint between driver and tank input
- include footprints for:
  - bias diode string or Vbe multiplier
  - idle-current measurement resistor or jumper

### Secondary Send Block

- `U102A/U102B`
- non-inverting drive stage
- starting values per channel:
  - feedback `12k`
  - gain-to-ground `10k`
  - series output `220R`

### Recovery Blocks

- one stage per tank return
- preferred direction:
  - direct coupling if DC behavior is clean
  - otherwise small film input coupler
- starting values per channel:
  - input bias-to-ground `2.2M`
  - gain-to-ground `1k`
  - feedback `33k`
  - feedback capacitor footprint `47 pF` to `100 pF`

### Tank Connector Intent

- `J101/J102`
  - primary left send and return
- `J103/J104`
  - primary right send and return
- `J105/J106`
  - secondary left send and return
- `J107/J108`
  - secondary right send and return

Use isolated RCA or equivalent shielded-cable connectors and keep shield termination consistent with the recovery ground strategy.

### Board Connectors

- `P101` primary bundle from routing board
- `P102` secondary bundle from routing board
- `P103` power

### Layout Priorities

- put recovery stages farthest from the power entry and relay wiring
- keep primary send power transistors on an edge with heat-spreading copper
- keep send and return traces physically separate

### Bring-Up Test Points

- `TP_PRI_SEND_L`, `TP_PRI_SEND_R`
- `TP_SEC_SEND_L`, `TP_SEC_SEND_R`
- `TP_PRI_RET_L`, `TP_PRI_RET_R`
- `TP_SEC_RET_L`, `TP_SEC_RET_R`
- primary bias current measurement pads for both channels

## 3. Ext Tank Routing Board Packet

### Functional Summary

- `Off / Series / Parallel` routing
- secondary-tank amount blend
- primary/secondary summing and series makeup gain
- feedback reinjection boundary

### Active Allocation

- `K201-K204` `G6K-2F-Y-DC5`
  - hard analog relay contacts for secondary-path engage and source selection
- `U201` `OPA1679IDR`
  - `U201A` left wet/routing buffer
  - `U201B` right wet/routing buffer
  - `U201C` left secondary-send buffer
  - `U201D` right secondary-send buffer

### Recommended Mode Architecture

- `Off`
  - primary returns only
- `Series`
  - primary recovery feeds secondary send path
  - secondary contribution returned through controlled blend
- `Parallel`
  - wet send splits to primary and secondary paths in parallel

### First-Pass Control Decode

- `CTL_EXT_MODE_A`
  - secondary-path engage / bypass
- `CTL_EXT_MODE_B`
  - series-versus-parallel source select
- freeze the first-pass decode as:
  - `00` = `Off`
  - `10` = `Series`
  - `11` = `Parallel`
  - `01` = reserved / off-equivalent

### Starting Values

- unity or summing resistors `20k`
- optional series makeup trim position `20k` nominal with trim footprint
- feedback reinjection resistor start `20k`

### Board Connectors

- `P201` wet input from I/O board, `3-position JST XH`
- `P202` primary tank bundle, `6-position JST XH`
- `P203` secondary tank bundle, `6-position JST XH`
- `P204` routed output to crossfade board, `3-position JST XH`
- `P205` feedback reinjection input, `3-position JST XH`
- `P206` mode and amount control or panel-backplane header
- `P207` power, `4-position JST VH`

### Layout Priorities

- keep relay coils and flyback parts on the power side of the board
- keep relay contact routing compact and obvious for bench debugging
- isolate high-impedance return summing nodes from relay current loops

### Bring-Up Test Points

- `TP_ROUT_WET_L`, `TP_ROUT_WET_R`
- `TP_ROUT_PRIRET_L`, `TP_ROUT_PRIRET_R`
- `TP_ROUT_SECRET_L`, `TP_ROUT_SECRET_R`
- `TP_ROUT_OUT_L`, `TP_ROUT_OUT_R`

## 4. Crossfade / Feedback / Wet Board Packet

### Functional Summary

- stereo wet crossfade
- feedback amount and polarity loop
- final wet handoff back to the I/O board

### Active Allocation

- `U301` `OPA1679IDR`
  - `U301A` left crossfade summer
  - `U301B` right crossfade summer
  - `U301C` feedback loop gain stage
  - `U301D` wet output summing or feedback utility stage

### Starting Values

- crossfade summing resistors `20k`
- feedback pot `100k`
- series floor resistor in loop `10k`
- compensation footprint `47 pF` DNP by default

### Board Connectors

- `P301` input from routing board
- `P302` output to filter board
- `P303` filter return from filter/clipper board
- `P304` wet return to I/O board
- `P305` feedback reinjection output to routing board
- `P306` power
- `P307` control or panel-backplane header if controls are not board-mounted

### Layout Priorities

- keep feedback loop physically local and readable
- do not place feedback switch wiring next to low-level return nodes

### Bring-Up Test Points

- `TP_XFADE_IN_L`, `TP_XFADE_IN_R`
- `TP_XFADE_OUT_L`, `TP_XFADE_OUT_R`
- `TP_FB_SEND_L`, `TP_FB_SEND_R`
- `TP_WETSUM_L`, `TP_WETSUM_R`

## 5. Filter / Clipper Board Packet

### Functional Summary

- pre-clipping HPF
- drive gain
- clip-mode selection
- post-clipping LPF
- output buffer to feedback/wet board

### Active Allocation

- `U401` `OPA1679IDR`
  - `U401A` left HPF
  - `U401B` right HPF
  - `U401C` left drive stage
  - `U401D` right drive stage
- `U402` `OPA1679IDR`
  - `U402A` left LPF
  - `U402B` right LPF
  - `U402C` left output buffer
  - `U402D` right output buffer

### Clip Networks

- `D401-D404`
  - silicon pair positions
- `D405-D408`
  - LED pair positions
- `D409-D412`
  - germanium or adapter positions
- clean mode should hard-bypass clip elements rather than merely reducing drive

### Starting Values

- keep `10 nF`, `22 nF`, and `47 nF` timing capacitor options available
- drive stage range target `0 dB` to `+20 dB`
- filter resistor starts can center around `10k` to `33k` ranges depending final topology

### Board Connectors

- `P401` audio in from crossfade board
- `P402` audio out to crossfade/feedback board
- `P403` control group A or panel-backplane header
  - drive and HPF group
- `P405` control group B or panel-backplane header
  - LPF and clip-mode group
- `P404` power

### Control Wiring Recommendation

This board has too many controls for several small JST tails to be elegant. Rev A should prefer one of these:

- board-mounted pots and rotary if the enclosure supports it
- two grouped control headers that mirror the `P613` and `P614` backplane split

### Layout Priorities

- mirror left and right filter sections
- keep diode networks and their surrounding feedback loops tight
- leave DNP space for alternate clip-part footprints

### Bring-Up Test Points

- `TP_FILT_IN_L`, `TP_FILT_IN_R`
- `TP_DRIVE_L`, `TP_DRIVE_R`
- `TP_CLIP_L`, `TP_CLIP_R`
- `TP_FILT_OUT_L`, `TP_FILT_OUT_R`

## 6. Power / Backplane Packet

### Functional Summary

- low-voltage distribution from the external `+24 VDC` input
- isolated conversion to `+15VA / -15VA`
- local `+5VAUX` generation
- controlled `AGND` to `CHASSIS` bond
- board power fan-out
- relay auxiliary power
- preferred landing place for off-board control wiring

### Core Parts

- `J500` service-endcap `5.5 x 2.1 mm` DC-jack landing
- `D500` reverse-polarity protection
- `F500` low-voltage polyfuse
- `TVS500` input surge clamp
- `C500` bulk input cap
- `PS500` `URA2415YMD-10WR3`
- `PS501` `R-78E5.0-0.5`
- rail bulk and local decoupling capacitors

### Power Outputs

- `P501` I/O board power
- `P502` tank driver/recovery board power
- `P503` crossfade/feedback/wet board power
- `P504` filter/clipper board power
- `P505` spare utility power
- `P506` ext-routing board power with `+5VAUX`

### Recommended Ground Strategy

- create one explicit star node near the PSU distribution center
- join `AGND` to `CHASSIS` at one controlled point only
- do not share tank shield return current with rectifier or relay current loops

### Control Backplane Role

If front-panel controls are not mounted directly to each audio board, this board should also host:

- the panel harness landing headers
- grouped control distribution headers
- shield or chassis termination points for long control runs

Practical note:

- under the current frozen rev-A harness, any `ULN2003ADR` footprint on the control/backplane side should remain reserve-only unless a later revision expands the control interface beyond the current encoded control-bit scheme

### Bring-Up Test Points

- `TP_PSU_P15`
- `TP_PSU_N15`
- `TP_PSU_5V`
- `TP_PSU_AGND`
- `TP_CHASSIS_BOND`
