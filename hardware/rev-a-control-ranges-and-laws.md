# GAS Rev A Control Ranges And Laws

This file maps the current JUCE control behavior into rev-A hardware control recommendations.

The intent is not to force the first analog prototype to feel identical to the plugin on day one. The intent is to stop the hardware controls from drifting into arbitrary ranges or tapers while schematic capture is still in progress.

Source for the current software ranges and defaults:

- [PluginProcessor.cpp](C:/Users/Jason/GAS-build/repo/Source/PluginProcessor.cpp:606)
- [applyDefaultGasSettings()](C:/Users/Jason/GAS-build/repo/Source/PluginProcessor.cpp:757)

There are two relevant "defaults" in the software:

1. the parameter-layout defaults used when the parameters are declared
2. the curated `applyDefaultGasSettings()` preset that the processor applies as the GAS startup/default state

For rev-A hardware panel marks and startup assumptions, the curated `applyDefaultGasSettings()` values are the better reference unless the product direction changes later.

## Main Control Table

| Control | Plugin Range | Layout Default | GAS Default | Rev-A Hardware Element | Recommended Hardware Law | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `Crossfade Amount` | `0.0` to `1.0` | `0.2` | `0.0` | dual-gang pot | electrical law set by resistor network around a linear pot | the curated startup state is fully uncrossfed |
| `Mode` | `Clean / Silicon / LED / Germanium` | `Clean` | `Clean` | 4-position rotary | hard switched | make `Clean` the fully bypassed clip mode |
| `Drive` | `0 dB` to `+30 dB` | `+6 dB` | `+6 dB` | pot | audio/log-like gain feel | the plugin has a wide gain span, so reserve enough gain before clipping |
| `HPF Cutoff` | `1 Hz` to `4000 Hz` | `120 Hz` | `100 Hz` | dual-gang pot | log-like sweep | do not use a raw linear-feeling frequency sweep |
| `HPF Q` | `0.25` to `8.0` | `0.707` | `1.0` | dual-gang pot | low-end resolution favored | keep the useful range around `0.5` to `2.0` physically easy to hit |
| `LPF Cutoff` | `500 Hz` to `20000 Hz` | `16000 Hz` | `12000 Hz` | dual-gang pot | log-like sweep | keep most of the travel above a few kilohertz |
| `LPF Q` | `0.25` to `8.0` | `0.707` | `1.0` | dual-gang pot | low-end resolution favored | same handling recommendation as HPF Q |
| `Ext Reverb Tanks` | `Off / Series / Parallel` | `Parallel` | `Off` | 3-position rotary or equivalent relay logic | hard switched | the curated startup state bypasses the secondary tanks |
| `Ext Reverb Tanks Amount` | `0.0` to `1.0` | `1.0` | `1.0` | dual-gang pot | near-linear blend behavior | keep full secondary contribution available when engaged |
| `Feedback` | `0.0` to `1.0` | `0.2` | `0.1` | dual-gang pot | controlled build-up near the low end | add fixed floor/series resistance so the loop never hard-shorts into instability |
| `Feedback Phase Invert` | `false / true` | `false` | `false` | toggle or pushbutton plus relay | hard switched | keep this in the feedback loop only |
| `Wet / Dry` | `0.0` to `1.0` | `0.5` | `0.5` | dual-gang pot | mix law set by summing network | center should sound like the nominal balanced mix point |
| `Mono Source To Stereo` | `false / true` | `false` | `false` | toggle | hard switched | switch after the balanced receiver |

## Software-Law Implications

The plugin already tells us something important about how the hardware controls should feel.

### Frequency Controls

The JUCE cutoff controls use a skewed `NormalisableRange` rather than a simple linear sweep.

That means rev A should not use:

- a pot law that feels linear in Hertz
- a control that crams the useful low-end range into a tiny travel region

Preferred rev-A approach:

- implement the frequency controls with a circuit law that feels roughly logarithmic
- use resistor padding, cap-range selection, or filter-law shaping so the lower frequencies get more panel travel

### Q Controls

The raw parameter defaults park both filter Q controls at `0.707`, while the curated GAS default preset moves them to `1.0`.

Preferred rev-A approach:

- make both `0.707` and `1.0` easy to hit repeatably
- do not optimize the control around only extreme resonance settings

### Blend Controls

`Crossfade`, `Ext Reverb Tanks Amount`, `Feedback`, and `Wet / Dry` are normalized in software.

That does not mean the hardware should use plain passive linear pots with no surrounding law shaping.

Preferred rev-A approach:

- use active summing or cross-mix resistor networks
- let the pot position control the weighting inside that network
- tune perceived balance on the bench instead of pretending a raw `50kB` pot automatically gives the right subjective law

## Default Positions Worth Marking On The Panel

These are the curated GAS defaults that are the best candidates for rev-A reference marks or calibration targets:

| Control | Plugin Default | Hardware Interpretation |
| --- | --- | --- |
| `Crossfade Amount` | `0%` | fully uncrossfed starting point |
| `Drive` | `+6 dB` | light push into the nonlinear stage |
| `HPF Cutoff` | `100 Hz` | useful low-frequency cleanup without obvious thinning |
| `HPF Q` | `1.0` | slightly more pointed than Butterworth |
| `LPF Cutoff` | `12 kHz` | open but not maximum-bright |
| `LPF Q` | `1.0` | slightly more pointed than Butterworth |
| `Ext Reverb Tanks` | `Off` | secondary tanks bypassed at startup |
| `Ext Reverb Tanks Amount` | `100%` | full secondary-tank contribution available |
| `Feedback` | `10%` | audible but conservative startup value |
| `Wet / Dry` | `50%` | equal starting mix |

## Recommended Pot And Switch Strategy

### High-Density Stereo Controls

Use dual-gang parts for:

- crossfade
- ext tank amount
- feedback
- wet/dry
- HPF cutoff
- HPF Q
- LPF cutoff
- LPF Q

### Best Candidates For Board-Mounted Or Backplane-Landed Controls

- `Drive`
- `HPF Cutoff`
- `HPF Q`
- `LPF Cutoff`
- `LPF Q`
- `Crossfade`
- `Feedback`

### Simple Local Control Exceptions

- `Mono Source To Stereo`
- `Feedback Phase Invert`
- `Mode`
- `Ext Reverb Tanks`

## First-Pass Bench Questions

When the first analog prototype exists, evaluate these before freezing final pot families:

1. Does the wet/dry blend feel level-consistent through the middle third of travel?
2. Does the crossfade control preserve an intentional perceived width change instead of only changing loudness?
3. Is the HPF low-end sweep usable across more than half the travel?
4. Is the LPF high-end sweep useful before the last small slice of pot travel?
5. Does feedback become musically active early enough without becoming unstable too abruptly?
