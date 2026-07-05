# GAS Rev A Primary Tank Driver Options

This document compares the leading rev-A options for driving the primary `4AB1C1B` tanks.

## Why This Matters

The primary tanks are the hardest part of the analog hardware package because:

- the input impedance is low
- they need more drive current than the secondary tanks
- the project prefers to avoid ceramic, tantalum, and electrolytic capacitors in the audio path where practical

## Option A: LM386 Single-Supply Driver

### Description

- `LM386MX-1/NOPB`
- single-supply driver
- simple and common
- easy first prototype path

### Strengths

- very simple
- inexpensive
- available from mainstream distributors

### Weaknesses

- usually wants an output coupling capacitor in the audio path
- that pushes against the audio-path capacitor preference
- less elegant fit with the split-rail analog architecture used elsewhere

### Status

- keep as fallback reference only
- not the preferred rev-A direction anymore

## Option B: Direct-Coupled Split-Rail Driver

### Description

- `OPA1656IDR` voltage-gain / predriver stage
- complementary emitter-follower output pair
- proposed transistor pair:
  - `BD139-16`
  - `BD140-16`
- powered from the existing `+15VA / -15VA` rails

### Strengths

- can be direct-coupled
- aligns better with the audio-path capacitor preference
- fits the existing split-rail analog architecture
- uses common, widely available transistor parts designed for audio-amplifier/driver use

### Weaknesses

- more parts
- more bias/stability work
- more bench tuning than the LM386 path

### Status

- current preferred rev-A direction

## Source Evidence

### OPA1656

- TI product page: [OPA1656](https://www.ti.com/product/OPA1656)
- TI datasheet: [OPA165x datasheet PDF](https://www.ti.com/lit/ds/symlink/opa1656.pdf)

Important points used here:

- wide supply range up to `+/-18V`
- high output current capability called out by TI

### BD139 / BD140

- ST product page: [BD139](https://www.st.com/en/power-transistors/bd139.html)
- ST product page: [BD140](https://www.st.com/en/power-transistors/bd140.html)
- ST datasheet: [BD135/136/139/140 datasheet PDF](https://www.st.com/resource/en/datasheet/cd00001225.pdf)

ST explicitly describes these complementary devices as being designed for audio amplifiers and drivers utilizing complementary or quasi-complementary circuits.

### Current Distributor Pricing Used In This Session

- DigiKey `BD139-16`: [link](https://www.digikey.com/en/products/detail/stmicroelectronics/BD139-16/2529325)
- DigiKey `BD140-16`: [link](https://www.digikey.com/en/products/detail/stmicroelectronics/BD140-16/3945995)

## Recommended Rev A Decision

Use Option B as the preferred primary-tank send stage:

- `OPA1656IDR` predriver
- `BD139-16` / `BD140-16` emitter-follower current stage
- split-rail operation from `+15VA / -15VA`
- direct-coupled if the DC operating point is controlled properly

Retain Option A only as a fallback path if:

- the direct-coupled stage proves unstable
- the bench build timeline requires a simpler emergency substitute
