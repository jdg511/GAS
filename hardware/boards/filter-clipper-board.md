# Filter And Clipping Board

## Purpose

This board implements the analog tone-shaping and nonlinear stage after the tank system and stereo crossfade.

## Functions

- Pre-clipping high-pass filter with adjustable frequency and resonance behavior
- Drive control
- Selectable clipping character
- Post-clipping low-pass filter with adjustable frequency and resonance behavior

## Software Features Mapped Here

- `Drive`
- `Mode`: Clean / Silicon / LED / Germanium
- `HPF Cutoff`
- `HPF Q`
- `LPF Cutoff`
- `LPF Q`

## Hardware Interpretation

- `Clean`
  - Filter stages active, no intentional clipping network engaged
- `Silicon`
  - Symmetrical silicon-diode feedback clipping
- `LED`
  - Higher-threshold feedback clipping using LEDs
- `Germanium`
  - Lower-threshold, asymmetrical germanium clipping path

## Recommended Analog Blocks

1. Input buffer
   - Receives `XFADE_OUT_L` / `XFADE_OUT_R`
2. Pre-HPF stage
   - State-variable or multiple-feedback topology
   - Dual-ganged control scheme for stereo tracking
3. Drive stage
   - Variable gain op-amp stage ahead of the clipping network
4. Clipping selector
   - Switchable diode networks or separate clipping cells
   - Keep left and right component matching tight
5. Post-LPF stage
   - State-variable or multiple-feedback topology
6. Output buffer
   - Feeds feedback and final wet mixer stages

## Proposed Connectors

- `P1` input from crossfade board: `XFADE_OUT_L`, `XFADE_OUT_R`, `AGND`
- `P2` output to feedback/mixer board: `FILTCLIP_OUT_L`, `FILTCLIP_OUT_R`, `AGND`
- `P3A` controls group A: `DRV_*`, `HPF_F_*`, `HPF_Q_*`
- `P3B` controls group B: `LPF_F_*`, `LPF_Q_*`, `CTL_CLIP_MODE_A`, `CTL_CLIP_MODE_B`
- `P4` power: `+15VA`, `-15VA`, `AGND`

## Preferred Rev A Direction

- Start with op-amp based active filters and diode clipping because they map cleanly to the existing software controls.
- Use passive component values that make the clean mode still useful as a tone-shaping stage.
- Keep clipping-mode selection entirely analog via rotary or toggle switching.
- Lay the board out symmetrically so stereo matching is easier.

## Risks

- Resonant stereo filters can drift between channels if pots are not matched well.
- Germanium parts may vary a lot; rev A may need selection bins or trim options.
- Switching clipping networks can pop if DC conditions are not controlled.

## Rev A Schematic Checklist

- Pick filter topology for stereo tracking and available Q range
- Decide whether control pots live on-board or off-board
- Keep the filter-control landing split honest instead of compressing all controls into one unrealistic header
- Define clipping selector hardware
- Define nominal internal signal level through the drive stage
