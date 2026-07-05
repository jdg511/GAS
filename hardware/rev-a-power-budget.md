# GAS Rev A Power Budget

This is the first-pass low-voltage power budget for the analog design.

## Rail Source

Rev A now sources DC externally and converts on-board. See [rev-a-external-dc-power.md](rev-a-external-dc-power.md) for the full topology and parts.

- External wall adapter: `Triad Magnetics WSU240-0750` (selected `2026-07-04`), regulated SMPS, `+24 VDC`, 750 mA / 18 W, UL 62368-1, from DigiKey
- On-board isolated DC-DC: `Mornsun URA2415YMD-10WR3` (9-36 V in, 24 V nominal) generates `+15VA` and `-15VA`
- On-board switching regulator: `RECOM R-78E5.0-0.5` generates `+5VAUX` from `+15VA`
- Per-rail LC ripple filter (ferrite + bulk + film) between the DC-DC and the audio harness

Audio-side rail budget below is unchanged from the original analysis; the wall-side total is `~10.3 W` against the adapter's 18 W capacity, leaving ~43 percent headroom (`~0.43 A` draw against the `0.75 A` rating).

## Datasheet-Based Quiescent Current Inputs

These values were checked from TI product or datasheet pages during this session:

- `OPA1644AIDR`
  - `1.8 mA / channel`
  - source: TI OPA1644 datasheet/product page
- `OPA1656IDR`
  - `3.9 mA / channel`
  - source: TI OPA1656 datasheet/product page
- `OPA1679IDR`
  - `2.0 mA / channel`
  - source: TI OPA1679 datasheet/product page
- `BD139` / `BD140`
  - no single fixed quiescent number should be assumed here because the final idle current depends on the class-AB bias choice
  - source for the device family: ST BD139 / BD140 datasheet and product pages

## Estimated Static Current By Board

### Input / Output Board

- `1x OPA1644AIDR` = `4 channels x 1.8 mA` = `7.2 mA`
- `3x OPA1656IDR` = `6 channels x 3.9 mA` = `23.4 mA`

Estimated quiescent total:

- about `30.6 mA` from the split analog rails, excluding line-drive output signal current

### Tank Driver / Recovery Board

- `4x OPA1656IDR` = `8 channels x 3.9 mA` = `31.2 mA`
- primary output transistor idle current:
  - depends on the chosen bias point
  - reserve at least `20 mA` to `60 mA` total as a first-pass placeholder until the class-AB bias is fixed

Estimated quiescent total:

- about `51.2 mA` to `91.2 mA`, excluding spring-drive signal current

### Ext Tank Routing Board

- `1x OPA1679IDR` = `4 channels x 2.0 mA` = `8 mA`
- `1x OPA1656IDR` (U202 send summers, added in the `2026-07-04` re-spin) = `2 channels x 3.9 mA` = `7.8 mA`
- `4x G6K-2F-Y-DC5` relay coils
  - driven from `+5VAUX`
  - only energized according to selected mode

Estimated analog quiescent total:

- about `15.8 mA` from the split analog rails

Estimated relay coil budget:

- treat `100 mA` on `+5VAUX` as a safe rev-A allowance until the exact coil current is frozen

### Crossfade / Feedback / Wet Summing Board

- `1x OPA1679IDR` = `8 mA`

### Filter / Clipping Board

- `2x OPA1679IDR` = `16 mA`

## Total First-Pass Static Budget

Ignoring signal-drive load and assuming relays are active:

- analog split rails:
  - about `30.6 + (51.2 to 91.2) + 15.8 + 8 + 16 = 121.6 to 161.6 mA` (updated `2026-07-04` for the ext-routing U202 addition)
- auxiliary `+5V`:
  - allocate roughly `100 mA` for relays and control overhead

## Design Recommendation

Rev A should budget at least:

- `250 mA` available on each analog rail after local decoupling and margin
- `250 mA` available on the `+5V` auxiliary rail

This leaves comfortable headroom for:

- line-drive current
- spring send current
- relay operation
- future utility stages or indicators

## What To Verify In Schematic Capture

- actual relay coil current from the exact Omron part
- actual worst-case line-output current into the intended external load
- actual primary tank send current under strong signal conditions
- DC-DC module ripple spectrum after the LC filter
- thermal margin on the +5V switching regulator at worst-case relay load
