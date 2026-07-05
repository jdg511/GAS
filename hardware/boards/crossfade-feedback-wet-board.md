# Crossfade / Feedback / Wet Board

## Purpose

This board owns the post-routing stereo crossfade, the filtered wet return handoff, and the feedback send path back toward the tank-routing board.

## Functions

- Stereo crossfade between left and right routed tank blends
- Low-impedance send from crossfade stage into the filter / clipper board
- Direct post-filter wet return back to the I/O board
- Feedback amount reinjection path
- Feedback phase invert selection for the loop send only

## Software Features Mapped Here

- `Crossfade`
- `Feedback`
- `Feedback Phase Invert`

## Hardware Interpretation

- The crossfade control is a mirrored dual-gang passive landing that lets each channel move between its own routed tank mix and the opposite channel's routed tank mix.
- The filter / clipper board is the authoritative "post-tone / post-clip" wet source.
- The direct wet return to the I/O board stays independent from the phase-invert function.
- `Feedback Phase Invert` only changes which signal is sent back toward the routing board:
  - normal phase uses the direct `FILTCLIP_OUT_L/R` path
  - inverted phase uses the dedicated inverting feedback-driver stages

## Recommended Analog Blocks

1. Crossfade landing
   - Dual-gang passive crossfade pot
   - Left track: `TANK_MIX_L` to `TANK_MIX_R`
   - Right track: `TANK_MIX_R` to `TANK_MIX_L`
2. Crossfade summers
   - `U301A` left inverting summer
   - `U301B` right inverting summer
   - Unity-gain feedback around each stage
   - Small output isolators into the filter board
3. Direct wet-return handoff
   - Post-filter wet source from `FILTCLIP_OUT_L/R`
   - Small series isolators into the I/O-board wet-return harness
4. Feedback-driver stages
   - `U301C` left feedback driver / inverter
   - `U301D` right feedback driver / inverter
   - Adjustable loop-gain starting point with optional stability capacitors
5. Feedback phase selector
   - Analog switch or relay choice is acceptable
   - Must affect only the feedback send path, never the direct wet return

## Proposed Connectors

- `P301` routed tank input from ext-routing board:
  - `TANK_MIX_L`, `AGND`, `TANK_MIX_R`
- `P302` send to filter / clipper board:
  - `XFADE_OUT_L`, `AGND`, `XFADE_OUT_R`
- `P303` return from filter / clipper board:
  - `FILTCLIP_OUT_L`, `AGND`, `FILTCLIP_OUT_R`
- `P304` direct wet return to I/O board:
  - `WET_SUM_L`, `AGND`, `WET_SUM_R`
- `P305` feedback reinjection output to ext-routing board:
  - `FB_RET_L`, `AGND`, `FB_RET_R`
- `P306` board power:
  - `+15VA`, `AGND`, `-15VA`
- `P307` control landing:
  - `XFD_L_HI`, `XFD_L_WIPER`, `XFD_L_LO`
  - `XFD_R_HI`, `XFD_R_WIPER`, `XFD_R_LO`
  - `FB_L_WIPER`, `FB_R_WIPER`, `CTL_FB_INV`, `AGND`

## Preferred Rev A Direction

- Keep the wet-return path visually and electrically separate from the feedback loop path.
- Use one quad audio op amp for the whole board so left/right channel behavior stays tightly matched.
- Reserve the feedback compensation capacitors as DNP default footprints instead of hard-populating them before the first real tank session.
- Treat `P307` as acceptable for rev-A capture, but still acknowledge that it compresses the true raw passive feedback-pot wiring.

## Risks

- If the feedback amount range is too aggressive, loop stability and noise build-up will dominate quickly with the real tanks.
- If the phase selector shares circuitry with the direct wet return, polarity changes will become audible even when feedback is low.
- If the final control implementation keeps every endpoint off-board, `P307` may need to grow or split in a later revision.

## Rev A Schematic Checklist

- Promote `U301` into four signal units plus the power unit
- Freeze `20k` crossfade-summer start values and `100R` isolators
- Keep `WET_SUM_L/R` sourced from the post-filter return only
- Keep `CTL_FB_INV` out of the direct wet-return path
- Reserve `47 pF` DNP stability footprints across the feedback-driver stages
