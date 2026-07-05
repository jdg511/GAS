# GAS Rev A Filter / Clipper Schematic-Ready Definition

This file is the direct electrical definition for the rev-A filter / clipper board.

It is more specific than [boards/filter-clipper-board.md](C:/Users/Jason/GAS-build/repo/hardware/boards/filter-clipper-board.md:1), [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1), and [rev-a-electrical-capture-worksheet.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-electrical-capture-worksheet.md:1), but it still leaves the exact listening-tuned filter values open.

Use this file when:

- promoting the current KiCad `filter-clipper.kicad_sch` page from single-unit placeholder capture to a true multi-unit schematic
- freezing the first-pass stage ownership and clip-network insertion points before the later KiCad wiring pass
- checking that the filter/clipper board still honors the no-ceramic/no-electrolytic audio-path preference where capacitors are actually in the signal path

## 1. Assumed First-Pass Circuit Strategy

This definition freezes the first-pass topology as:

- one active high-pass stage per channel using `U401A` and `U401B`
- one variable-gain drive stage per channel using `U401C` and `U401D`
- selectable clip networks around the drive stage
- one active low-pass stage per channel using `U402A` and `U402B`
- one final output buffer per channel using `U402C` and `U402D`

Important note:

- the currently checked-in `P403` and `P405` grouped control headers are sufficient for placeholder capture, but they remain compressed for fully passive off-board stereo Q controls
- if the HPF-Q and LPF-Q controls remain true passive off-board controls, the later KiCad pass must either promote those headers or move those controls onto a dedicated control-backplane PCB that owns the missing endpoints

## 2. Required KiCad Multi-Unit Promotion

The checked-in `filter-clipper.kicad_sch` still has only one symbol unit placed for each quad package. The real capture pass should promote the sheet to this exact unit set:

| Ref | Unit | Job |
| --- | --- | --- |
| `U401` | `1` | `U401A` left HPF |
| `U401` | `2` | `U401B` right HPF |
| `U401` | `3` | `U401C` left drive stage |
| `U401` | `4` | `U401D` right drive stage |
| `U401` | `5` | power pins |
| `U402` | `1` | `U402A` left LPF |
| `U402` | `2` | `U402B` right LPF |
| `U402` | `3` | `U402C` left output buffer |
| `U402` | `4` | `U402D` right output buffer |
| `U402` | `5` | power pins |

## 3. Header Pin Ownership

### P401 `JXF-FILT`

| Pin | Net |
| --- | --- |
| `1` | `XFADE_OUT_L` |
| `2` | `AGND` |
| `3` | `XFADE_OUT_R` |

### P402 `JFILT-WET`

| Pin | Net |
| --- | --- |
| `1` | `FILTCLIP_OUT_L` |
| `2` | `AGND` |
| `3` | `FILTCLIP_OUT_R` |

### P403 `JFILT-CTL-A`

Keep the currently captured pin ownership below for the first real KiCad pass:

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `DRV_HI` | drive pot top end |
| `2` | `DRV_WIPER` | drive pot wiper |
| `3` | `DRV_LO` | drive pot low end |
| `4` | `HPF_F_L_HI` | left HPF frequency top end |
| `5` | `HPF_F_L_WIPER` | left HPF frequency wiper |
| `6` | `HPF_F_L_LO` | left HPF frequency low end |
| `7` | `HPF_F_R_HI` | right HPF frequency top end |
| `8` | `HPF_F_R_WIPER` | right HPF frequency wiper |
| `9` | `HPF_F_R_LO` | right HPF frequency low end |
| `10` | `HPF_Q_L_WIPER` | compressed left HPF-Q landing |
| `11` | `HPF_Q_R_WIPER` | compressed right HPF-Q landing |
| `12` | `AGND` | local control reference |

### P404 `JFILT-PWR`

| Pin | Net |
| --- | --- |
| `1` | `+15VA` |
| `2` | `AGND` |
| `3` | `-15VA` |

### P405 `JFILT-CTL-B`

Keep the currently captured pin ownership below for the first real KiCad pass:

| Pin | Net | Function |
| --- | --- | --- |
| `1` | `LPF_F_L_HI` | left LPF frequency top end |
| `2` | `LPF_F_L_WIPER` | left LPF frequency wiper |
| `3` | `LPF_F_L_LO` | left LPF frequency low end |
| `4` | `LPF_F_R_HI` | right LPF frequency top end |
| `5` | `LPF_F_R_WIPER` | right LPF frequency wiper |
| `6` | `LPF_F_R_LO` | right LPF frequency low end |
| `7` | `LPF_Q_L_WIPER` | compressed left LPF-Q landing |
| `8` | `LPF_Q_R_WIPER` | compressed right LPF-Q landing |
| `9` | `+5VAUX` | clip-mode/control reference rail |
| `10` | `CTL_CLIP_MODE_A` | clip-mode encoded bit A |
| `11` | `CTL_CLIP_MODE_B` | clip-mode encoded bit B |
| `12` | `AGND` | local control reference |

## 4. Internal Audio Nodes

Use these node names when drawing the final KiCad page:

| Node | Meaning |
| --- | --- |
| `HPF_OUT_L` | left high-pass output from `U401A` |
| `HPF_OUT_R` | right high-pass output from `U401B` |
| `DRV_PRE_L` | left drive-stage input node |
| `DRV_PRE_R` | right drive-stage input node |
| `CLIP_NODE_L` | left clip-network insertion node |
| `CLIP_NODE_R` | right clip-network insertion node |
| `LPF_OUT_L` | left low-pass output from `U402A` |
| `LPF_OUT_R` | right low-pass output from `U402B` |
| `BUF_OUT_L` | left final buffered output from `U402C` |
| `BUF_OUT_R` | right final buffered output from `U402D` |

## 5. First-Pass Stage Definition

### HPF Stages

Use `U401A` and `U401B` as the left and right active high-pass stages.

First-pass capture intent:

- inverting active HPF or MFB HPF per channel
- timing-cap footprint family kept open across `10 nF`, `22 nF`, and `47 nF`
- `HPF_F_*` nets define the main cutoff control element
- `HPF_Q_*_WIPER` remains the currently compressed resonance control landing

Reserve the following first-pass passive anchors:

| Ref Block | Role |
| --- | --- |
| `R401-R409` | left HPF input, timing, and Q-setting resistors |
| `C401-C409` | left HPF timing and compensation capacitors |
| `R421-R429` | right HPF input, timing, and Q-setting resistors |
| `C421-C429` | right HPF timing and compensation capacitors |

### Drive Stages

Use `U401C` and `U401D` as the variable-gain drive stages.

First-pass capture intent:

- non-inverting variable-gain op-amp stage per channel
- `DRV_HI`, `DRV_WIPER`, and `DRV_LO` own the raw drive-pot landing
- clean mode must still route through the drive stage, but bypass intentional diode clipping

Reserve the following first-pass passive anchors:

| Ref | Value | Function |
| --- | --- | --- |
| `R441-R444` | `10k` to `33k` start range | drive gain-setting placeholders |
| `R445-R448` | `10k` to `33k` start range | clip-loop insertion / limiter-network placeholders |
| `C441-C444` | DNP-friendly small comp footprints | drive-stage stability reserves |

### Clip Networks

The diode families should be wired as board-owned clip options around the drive stage, not as vague later notes.

| Ref Block | Family | First-Pass Meaning |
| --- | --- | --- |
| `D401-D404` | silicon | tighter, lower-threshold symmetrical clip option |
| `D405-D408` | LED | higher-threshold clip option |
| `D409-D412` | germanium or adapter | softer, asymmetrical option |

Clip-mode truth should stay:

| `CTL_CLIP_MODE_A` | `CTL_CLIP_MODE_B` | Mode |
| --- | --- | --- |
| `0` | `0` | `Clean` |
| `0` | `1` | `Silicon` |
| `1` | `0` | `LED` |
| `1` | `1` | `Germanium` |

Important note:

- the exact local decode hardware that turns those two mode lines into the selected clip network is still an implementation detail for the later KiCad pass
- what is frozen here is the ownership of the clip families and the mode truth table

### LPF Stages

Use `U402A` and `U402B` as the left and right low-pass stages.

First-pass capture intent:

- inverting active LPF or MFB LPF per channel
- timing-cap footprint family kept open across `10 nF`, `22 nF`, and `47 nF`
- `LPF_F_*` nets define the main cutoff control element
- `LPF_Q_*_WIPER` remains the currently compressed resonance control landing

Reserve the following first-pass passive anchors:

| Ref Block | Role |
| --- | --- |
| `R471-R479` | left LPF timing and damping network |
| `C471-C479` | left LPF timing and compensation caps |
| `R491-R499` | right LPF timing and damping network |
| `C491-C499` | right LPF timing and compensation caps |

### Output Buffers

Use `U402C` and `U402D` as the final low-impedance output buffers.

| Ref | Value | From | To | Notes |
| --- | --- | --- | --- | --- |
| `R511` | `100R` | `U402C out` | `P402 pin 1` | left output isolator |
| `R512` | `100R` | `U402D out` | `P402 pin 3` | right output isolator |

Wire the output buffers as:

- `U402C+` from `LPF_OUT_L`, `U402C-` tied to `U402C out`
- `U402D+` from `LPF_OUT_R`, `U402D-` tied to `U402D out`

## 6. Functional Wiring Summary By Stage

### Left Channel

- `XFADE_OUT_L` enters `U401A`
- `U401A` high-passes into `U401C`
- `U401C` provides drive and clip-network insertion
- the clipped or clean result feeds `U402A`
- `U402A` low-passes into `U402C`
- `U402C` outputs `FILTCLIP_OUT_L`

### Right Channel

- `XFADE_OUT_R` enters `U401B`
- `U401B` high-passes into `U401D`
- `U401D` provides drive and clip-network insertion
- the clipped or clean result feeds `U402B`
- `U402B` low-passes into `U402D`
- `U402D` outputs `FILTCLIP_OUT_R`

## 7. Local Decoupling Intent

Reserve `C591-C599` for local rail decoupling.

First-pass intent:

- one `100 nF` from `+15VA` to `AGND` per op-amp package
- one `100 nF` from `-15VA` to `AGND` per op-amp package
- one local `10 uF` to `22 uF` bulk footprint per rail pair is acceptable because these are power-path parts

Any capacitor that actually lands in the audio path should follow the current project preference:

- film, PPS, polyester, polypropylene, or mica first
- avoid ceramic, tantalum, and electrolytic parts in the audio path where practical

## 8. Verification Gate For The Later KiCad Pass

When this definition is translated into the final multi-unit KiCad page, verify all of the following:

1. `U401` and `U402` each have all four signal units plus their power unit instantiated.
2. `D401-D412` are captured as actual selectable clip families, not left floating as decorative placeholders.
3. Clean mode truly bypasses intentional clipping and does not simply set the drive control low.
4. `P402` remains the only board output back to the wet board.
5. Audio-path capacitor footprints in the actual signal chain are film-friendly.

## 9. Explicitly Deferred Items

These are intentionally deferred:

- final HPF and LPF values after listening against the real tanks
- the exact decode hardware behind `CTL_CLIP_MODE_A/B`
- whether the compressed `HPF_Q_*_WIPER` and `LPF_Q_*_WIPER` control landings are promoted to fuller raw passive headers in the later KiCad pass
