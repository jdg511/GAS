# GAS Rev A Electrical Capture Worksheet

This file is the direct bridge between the symbol-populated KiCad sheets and the next real wiring pass.

Use it when:

- drawing the first true analog connections inside the KiCad child sheets
- deciding which designator reservations from [rev-a-capture-value-tables.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-capture-value-tables.md:1) get used first
- checking that the stage ownership in [rev-a-schematic-packets.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-schematic-packets.md:1) still matches the actual symbol references now present in KiCad

This worksheet is intentionally more concrete than the board briefs, but it still stops short of pretending all bench-tuned values are already known.

## Global Wiring Rules

- Keep all inter-board audio single-ended on the frozen harness nets.
- Keep the external balanced domain only at the combo-jack boundary on the I/O board.
- Prefer direct coupling first.
- If an audio-path capacitor is required, prefer film, PPS-film, polypropylene, polyester, or mica where practical.
- Every op-amp package needs local rail decoupling footprints close to the package.
- Every board should expose at least one local rail test reference and one or more stage-level audio test points.
- Do not use the current symbol-only sheets as proof of analog correctness; they are the canvas for the wiring work, not the finished result.

## 1. Input / Output Board

Current companion:

- use [rev-a-io-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-io-schematic-ready-definition.md:1) as the authority for the exact multi-unit promotion, passive map, and connector pin ownership on this page

### Active-Stage Ownership

| Ref / Unit | Job | Mandatory I/O Relationship |
| --- | --- | --- |
| `U1A` | left balanced receiver | converts `IN_BAL_L_P/N` to local single-ended left program source |
| `U1B` | right balanced receiver | converts `IN_BAL_R_P/N` to local single-ended right program source |
| `U1C` | left mono/stereo routing buffer | drives left internal source after mono switch logic |
| `U1D` | right mono/stereo routing buffer | passes right source in stereo mode, left source in mono mode |
| `U2A` | left wet/dry summer | combines `DRY_L` and `WET_SUM_L` under `P5` control law |
| `U2B` | right wet/dry summer | combines `DRY_R` and `WET_SUM_R` under `P5` control law |
| `U3A` | left balanced hot driver | drives `OUT_BAL_L_P` |
| `U3B` | left balanced cold driver | drives `OUT_BAL_L_N` with matched unity inversion |
| `U4A` | right balanced hot driver | drives `OUT_BAL_R_P` |
| `U4B` | right balanced cold driver | drives `OUT_BAL_R_N` with matched unity inversion |

### Wiring Directives

| Block | Directive |
| --- | --- |
| balanced receiver | use one classic unity-gain differential receiver network per channel with `R11-R18` matched at `0.1%` |
| mono switch | `MONO_A/C/B` must switch only the post-receiver single-ended source, never the balanced boundary |
| dry split | the received left/right sources must feed both `DRY_L/R` and `WET_SEND_L/R`; start with `100R` isolation footprints |
| wet/dry law | keep `P5` as the full 6-wire raw stereo control landing; do not collapse it into pseudo-control nets |
| balanced output | keep the hot and cold legs fully active and resistor-matched; use per-leg `49.9R` build-out resistors near the jack side |
| RF boundary | keep `R1-R4` and `C1-C4` physically closest to `J1/J2` |

### Connector Content That Must Not Drift

| Ref | Signals |
| --- | --- |
| `P1` | `+15VA`, `AGND`, `-15VA` |
| `P2` | `WET_SEND_L`, `AGND`, `WET_SEND_R` |
| `P3` | `WET_SUM_L`, `AGND`, `WET_SUM_R` |
| `P4` | `DRY_L`, `AGND`, `DRY_R` |
| `P5` | `WD_L_HI`, `WD_L_WIPER`, `WD_L_LO`, `WD_R_HI`, `WD_R_WIPER`, `WD_R_LO` |
| `P6` | `MONO_A`, `MONO_C`, `MONO_B` |

## 2. Tank Driver / Recovery Board

Current companion:

- use [rev-a-tank-driver-recovery-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-tank-driver-recovery-schematic-ready-definition.md:1) as the authority for the exact first-pass send, recovery, and shield-bond ownership on this page

### Active-Stage Ownership

| Ref / Unit | Job | Mandatory I/O Relationship |
| --- | --- | --- |
| `U101A` | primary left send predriver | conditions `PRI_SEND_L` for the left push-pull output pair |
| `U101B` | primary right send predriver | conditions `PRI_SEND_R` for the right push-pull output pair |
| `Q101/Q102` | primary left current stage | deliver the low-impedance left `4AB1C1B` send drive |
| `Q103/Q104` | primary right current stage | deliver the low-impedance right `4AB1C1B` send drive |
| `U102A` | secondary left send | drives the left `9EB2C1B` input path |
| `U102B` | secondary right send | drives the right `9EB3C1B` input path |
| `U103A` | primary left recovery | amplifies the recovered signal from `J102` to `PRI_RET_L` |
| `U103B` | primary right recovery | amplifies the recovered signal from `J104` to `PRI_RET_R` |
| `U104A` | secondary left recovery | amplifies the recovered signal from `J106` to `SEC_RET_L` |
| `U104B` | secondary right recovery | amplifies the recovered signal from `J108` to `SEC_RET_R` |

### Wiring Directives

| Block | Directive |
| --- | --- |
| primary send | wire `U101A/B` into complementary emitter-follower stages using `Q101-Q104`, with base stoppers, emitter resistors, zobel footprints, and a reserved bias-trim implementation |
| secondary send | keep `U102A/B` as lower-current op-amp send stages with series output resistors and gain footprints |
| recovery input | reserve both direct-coupled and film-coupled entry options; use the high-value input bias resistors from the value table |
| tank shield strategy | keep send and return shield handling explicit and local to the tank board; do not let shield-current assumptions hide inside harness notes |
| thermal layout intent | the primary send transistor pairs should stay on the board edge with thermal copper and short loop area |

### Tank Boundary Ownership

| Ref | Role |
| --- | --- |
| `J101` | primary left send landing |
| `J102` | primary left return landing |
| `J103` | primary right send landing |
| `J104` | primary right return landing |
| `J105` | secondary left send landing |
| `J106` | secondary left return landing |
| `J107` | secondary right send landing |
| `J108` | secondary right return landing |

Current capture note:

- these landings are still intentionally provisional as coaxial connector symbols until the exact isolated RCA or shielded-wire hardware is frozen

## 3. Ext Tank Routing Board

Current companion:

- use [rev-a-ext-routing-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-ext-routing-schematic-ready-definition.md:1) as the authority for the exact relay role split, control decode, and passive map on this page

### Active-Stage Ownership

| Ref / Unit | Job | Mandatory I/O Relationship |
| --- | --- | --- |
| `U201A` | left routing buffer/summer | combines left wet-source and return-path selections toward `TANK_MIX_L` |
| `U201B` | right routing buffer/summer | combines right wet-source and return-path selections toward `TANK_MIX_R` |
| `U201C` | left secondary-send buffer | drives `SEC_SEND_L` from the engaged left source-select path |
| `U201D` | right secondary-send buffer | drives `SEC_SEND_R` from the engaged right source-select path |
| `K201` | left source-select relay | chooses left secondary source between `PRI_RET_L` and `WET_SEND_L` |
| `K202` | right source-select relay | chooses right secondary source between `PRI_RET_R` and `WET_SEND_R` |
| `K203` | left engage/bypass relay | enables or bypasses left secondary send/return behavior |
| `K204` | right engage/bypass relay | enables or bypasses right secondary send/return behavior |

### Wiring Directives

| Block | Directive |
| --- | --- |
| `Off` mode | `WET_SEND_L/R` must drive only the primary send path, and only primary returns may reach `TANK_MIX_L/R` |
| `Series` mode | primary recovery must feed the secondary send path before the final amount-controlled return blend |
| `Parallel` mode | `WET_SEND_L/R` must split to both primary and secondary send paths in parallel |
| ext amount | keep the amount control on the raw 6-wire stereo pot nets plus the encoded mode pair on `P206`; do not reintroduce the old single-net `CTL_EXT_MIX` abstraction |
| relay support | reserve flyback or suppression parts for all four coils if the final control-backplane strategy drives them with semiconductors |

### Frozen Control Header

`P206` is now the practical electrical definition for the ext-tank control landing:

- `EXTMIX_L_HI`
- `EXTMIX_L_WIPER`
- `EXTMIX_L_LO`
- `EXTMIX_R_HI`
- `EXTMIX_R_WIPER`
- `EXTMIX_R_LO`
- `+5VAUX`
- `AGND`
- `CTL_EXT_MODE_A`
- `CTL_EXT_MODE_B`

## 4. Crossfade / Feedback / Wet Board

Current companion:

- use [rev-a-crossfade-feedback-wet-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-crossfade-feedback-wet-schematic-ready-definition.md:1) as the authority for the exact first-pass crossfade, wet-return, and feedback-path ownership on this page

### Active-Stage Ownership

| Ref / Unit | Job | Mandatory I/O Relationship |
| --- | --- | --- |
| `U301A` | left crossfade summer | processes left `TANK_MIX_L` into the filter send path |
| `U301B` | right crossfade summer | processes right `TANK_MIX_R` into the filter send path |
| `U301C` | feedback loop gain stage | generates controlled feedback return |
| `U301D` | wet handoff / utility stage | presents final `WET_SUM_L/R` back to the I/O board |

### Wiring Directives

| Block | Directive |
| --- | --- |
| crossfade network | keep left/right resistor sets matched and centered around the `20k` starting values |
| feedback floor | include the `10k` minimum loop-floor resistors so the feedback pot cannot hard-open to an unstable corner |
| polarity invert | `CTL_FB_INV` must affect only the loop polarity path, never the direct wet output path |
| wet handoff | `P304` is the only final wet return handed back to the I/O board |
| control landing | `P307` remains the grouped 10-wire control landing unless a direct board-mount decision replaces it completely |

### Frozen Control Header

| Ref | Signals |
| --- | --- |
| `P307` | `XFD_L_HI`, `XFD_L_WIPER`, `XFD_L_LO`, `XFD_R_HI`, `XFD_R_WIPER`, `XFD_R_LO`, `FB_L_WIPER`, `FB_R_WIPER`, `CTL_FB_INV`, `AGND` |

## 5. Filter / Clipper Board

Current companion:

- use [rev-a-filter-clipper-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-filter-clipper-schematic-ready-definition.md:1) as the authority for the exact first-pass filter, drive, and clip-network ownership on this page

### Active-Stage Ownership

| Ref / Unit | Job | Mandatory I/O Relationship |
| --- | --- | --- |
| `U401A` | left HPF | processes left `XFADE_OUT_L` into the drive path |
| `U401B` | right HPF | processes right `XFADE_OUT_R` into the drive path |
| `U401C` | left drive stage | presents left clip-network drive |
| `U401D` | right drive stage | presents right clip-network drive |
| `U402A` | left LPF | filters the post-clip left signal |
| `U402B` | right LPF | filters the post-clip right signal |
| `U402C` | left output buffer | drives `FILTCLIP_OUT_L` back to the wet board |
| `U402D` | right output buffer | drives `FILTCLIP_OUT_R` back to the wet board |

### Clip-Network Ownership

| Ref Block | Meaning |
| --- | --- |
| `D401-D404` | silicon clipping positions |
| `D405-D408` | LED clipping positions |
| `D409-D412` | germanium or adapter positions |

### Wiring Directives

| Block | Directive |
| --- | --- |
| clean mode | must hard-bypass intentional clip elements, not merely reduce gain |
| grouped controls | keep `P403` and `P405` as the honest grouped raw-control headers from the current backplane definition |
| timing caps | preserve flexibility for `10 nF`, `22 nF`, and `47 nF` options in the filter timing footprints |
| germanium path | keep the current footprints explicitly provisional until the exact diode or adapter strategy is frozen |

### Frozen Control Headers

| Ref | Signals |
| --- | --- |
| `P403` | `DRV_HI`, `DRV_WIPER`, `DRV_LO`, `HPF_F_L_HI`, `HPF_F_L_WIPER`, `HPF_F_L_LO`, `HPF_F_R_HI`, `HPF_F_R_WIPER`, `HPF_F_R_LO`, `HPF_Q_L_WIPER`, `HPF_Q_R_WIPER`, `AGND` |
| `P405` | `LPF_F_L_HI`, `LPF_F_L_WIPER`, `LPF_F_L_LO`, `LPF_F_R_HI`, `LPF_F_R_WIPER`, `LPF_F_R_LO`, `LPF_Q_L_WIPER`, `LPF_Q_R_WIPER`, `+5VAUX`, `CTL_CLIP_MODE_A`, `CTL_CLIP_MODE_B`, `AGND` |

## 6. Power / Backplane Board

Current companion:

- use [rev-a-control-backplane-schematic-ready-definition.md](C:/Users/Jason/GAS-build/repo/hardware/rev-a-control-backplane-schematic-ready-definition.md:1) as the authority for the exact first-pass control-landing ownership, mode encoding, and `U601` reserve policy

### Power-Stage Ownership

| Ref | Job |
| --- | --- |
| `J500` | receives external `+24VDC` from the wall adapter at the service endcap |
| `F500` | input overcurrent protection |
| `D500` | reverse-polarity protection |
| `TVS500` | input surge clamp |
| `C500` | bulk input energy storage |
| `PS500` | isolated generation of `+15VA / -15VA` |
| `PS501` | local generation of `+5VAUX` |
| `FB500`, `FB501` | per-rail cleanup/filter points after the DC-DC stage |
| `P501-P506` | board-power fanout |
| `P601` | optional control-backplane feed |
| `U601` | reserve-only relay-driver support if a future revision changes the harness to give the backplane real coil-drive ownership |

### Wiring Directives

| Block | Directive |
| --- | --- |
| rail chain | wire the entry chain explicitly in this order: `J500` -> `F500` -> `D500` -> `TVS500/C500` -> `PS500` |
| auxiliary rail | derive `PS501` from the positive analog rail side per the current power strategy docs |
| star point | keep one explicit `AGND` star region near the supply-distribution center |
| chassis bond | keep only one controlled `AGND` to `CHASSIS` bond implementation on this page |
| control headers | populate `P610-P614` only if the control-backplane path is retained in the next electrical phase |

## Recommended Next KiCad Wiring Order

1. power/backplane pin-level wiring
2. I/O balanced receiver and output-driver wiring
3. ext-routing relay and summing wiring
4. crossfade/feedback/wet loop wiring
5. filter/clipper signal path wiring
6. tank-driver send/recovery wiring

That order keeps the shared rails and inter-board audio definitions stable before the highest-gain tank-recovery work is finalized.
