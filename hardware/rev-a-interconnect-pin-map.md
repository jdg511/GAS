# GAS Rev A Interconnect Pin Map

This file freezes the rev-A harness intent at the pin level.

Unless otherwise noted, connector numbering is defined as:

- board viewed from component side
- through-hole header facing up
- pin `1` at the left with the latch or polarization feature at the top

## Audio Harnesses

### H1 `JIO-PWR`

- from: power/backplane `P501`
- to: I/O board `P1`
- connector: `JST VH` 3-position
- pinout:
  - `1` `+15VA`
  - `2` `AGND`
  - `3` `-15VA`

### H2 `JIO-WETSEND`

- from: I/O board `P2`
- to: ext-routing board `P201`
- connector: `JST XH` 3-position
- pinout:
  - `1` `WET_SEND_L`
  - `2` `AGND`
  - `3` `WET_SEND_R`

### H3 `JIO-DRY`

- from: I/O board `P4`
- to: reserved dry-distribution landing
- connector: `JST XH` 3-position
- pinout:
  - `1` `DRY_L`
  - `2` `AGND`
  - `3` `DRY_R`

### H4 `JIO-WETRET`

- from: crossfade/feedback/wet board `P304`
- to: I/O board `P3`
- connector: `JST XH` 3-position
- pinout:
  - `1` `WET_SUM_L`
  - `2` `AGND`
  - `3` `WET_SUM_R`

### H5 `JTR-PRI`

- from: ext-routing board `P202`
- to: tank driver/recovery board `P101`
- connector: `JST XH` 6-position
- pinout:
  - `1` `PRI_SEND_L`
  - `2` `PRI_RET_L`
  - `3` `AGND`
  - `4` `PRI_SEND_R`
  - `5` `PRI_RET_R`
  - `6` `AGND`

### H6 `JTR-SEC`

- from: ext-routing board `P203`
- to: tank driver/recovery board `P102`
- connector: `JST XH` 6-position
- pinout:
  - `1` `SEC_SEND_L`
  - `2` `SEC_RET_L`
  - `3` `AGND`
  - `4` `SEC_SEND_R`
  - `5` `SEC_RET_R`
  - `6` `AGND`

### H7 `JTR-XFADE`

- from: ext-routing board `P204`
- to: crossfade/feedback/wet board `P301`
- connector: `JST XH` 3-position
- pinout:
  - `1` `TANK_MIX_L`
  - `2` `AGND`
  - `3` `TANK_MIX_R`

### H8 `JXF-FILT`

- from: crossfade/feedback/wet board `P302`
- to: filter/clipper board `P401`
- connector: `JST XH` 3-position
- pinout:
  - `1` `XFADE_OUT_L`
  - `2` `AGND`
  - `3` `XFADE_OUT_R`

### H9 `JFILT-WET`

- from: filter/clipper board `P402`
- to: crossfade/feedback/wet board `P303`
- connector: `JST XH` 3-position
- pinout:
  - `1` `FILTCLIP_OUT_L`
  - `2` `AGND`
  - `3` `FILTCLIP_OUT_R`

### H10 `JFB-INJ`

- from: crossfade/feedback/wet board `P305`
- to: ext-routing board `P205`
- connector: `JST XH` 3-position
- pinout:
  - `1` `FB_RET_L`
  - `2` `AGND`
  - `3` `FB_RET_R`

## Power Harnesses

### H11 Tank Board Power

- from: power/backplane `P502`
- to: tank driver/recovery board `P103`
- connector: `JST VH` 3-position
- pinout:
  - `1` `+15VA`
  - `2` `AGND`
  - `3` `-15VA`

### H12 Crossfade Board Power

- from: power/backplane `P503`
- to: crossfade/feedback/wet board `P306`
- connector: `JST VH` 3-position
- pinout:
  - `1` `+15VA`
  - `2` `AGND`
  - `3` `-15VA`

### H13 Filter Board Power

- from: power/backplane `P504`
- to: filter/clipper board `P404`
- connector: `JST VH` 3-position
- pinout:
  - `1` `+15VA`
  - `2` `AGND`
  - `3` `-15VA`

### H14 Ext-Routing Board Power

- from: power/backplane `P506`
- to: ext-routing board `P207`
- connector: `JST VH` 4-position
- pinout:
  - `1` `+15VA`
  - `2` `AGND`
  - `3` `-15VA`
  - `4` `+5VAUX`

## Tank Harnesses

Use shielded two-conductor or equivalent quiet spring-tank cable assemblies.

### T1 Primary Left `4AB1C1B`

- board send: `J101`
- board return: `J102`
- shield termination:
  - preferred single-point shield bond at the recovery-side strategy

### T2 Primary Right `4AB1C1B`

- board send: `J103`
- board return: `J104`

### T3 Secondary Left `9EB2C1B`

- board send: `J105`
- board return: `J106`

### T4 Secondary Right `9EB3C1B`

- board send: `J107`
- board return: `J108`

## Control Wiring Note

The high-control-count sections should not be spread across many tiny audio-board headers unless enclosure geometry forces it.

Preferred rev-A approach:

- mount simple local controls directly where practical
- use the power/control/backplane board as the landing point for dense filter and mode-control wiring
- keep long control harnesses physically away from tank recovery runs
