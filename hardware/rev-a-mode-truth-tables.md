# GAS Rev A Mode Truth Tables

This file captures the intended analog behavior of the switchable rev-A functions before exact switch or relay implementation details are frozen.

It is meant to keep schematic capture aligned with behavior, even if the exact relay contact numbering changes later.

## 1. Mono Source To Stereo

| Control State | Left Internal Path | Right Internal Path | Notes |
| --- | --- | --- | --- |
| `Stereo` | left balanced receiver output | right balanced receiver output | normal stereo operation |
| `Mono -> Stereo` | left balanced receiver output | copy of left balanced receiver output | switch after the balanced receivers |

## 2. Ext Reverb Tanks Routing

| Mode | Primary Send Source | Secondary Send Source | Downstream Wet Source | Notes |
| --- | --- | --- | --- | --- |
| `Off` | `WET_SEND_L/R` | none | primary returns only | secondary tanks fully bypassed |
| `Series` | `WET_SEND_L/R` | primary recovery path | primary plus secondary series result under amount control | secondary follows the primary path |
| `Parallel` | `WET_SEND_L/R` | split from `WET_SEND_L/R` | primary and secondary blended in parallel | plugin default behavior |

## 3. Ext Reverb Tanks Amount

| Mode | `0%` Intent | `100%` Intent |
| --- | --- | --- |
| `Off` | no audible effect | no audible effect |
| `Series` | minimum secondary contribution or makeup path only | full intended secondary contribution in the cascaded path |
| `Parallel` | primary-dominant wet image | full secondary parallel contribution available |

The exact transfer law can be tuned later, but the user-facing meaning should stay consistent:

- lower settings reduce the secondary contribution
- higher settings increase the secondary contribution

## 4. Feedback Phase Invert

| Switch State | Feedback Polarity | Main Dry/Wet Path |
| --- | --- | --- |
| `Normal` | non-inverted | unchanged |
| `Invert` | inverted in the feedback loop only | unchanged |

## 5. Clipping Mode

| Mode | Clip Network | Intended Behavior |
| --- | --- | --- |
| `Clean` | no intentional clip network engaged | filter-only tone shaping |
| `Silicon` | anti-parallel silicon pair | tighter, earlier symmetrical clipping |
| `LED` | anti-parallel LED pair | higher-threshold clipping with more headroom |
| `Germanium` | asymmetrical germanium pair | softer, lower-threshold asymmetric clipping |

## 6. Wet / Dry

| Control Region | Intended Mix Behavior |
| --- | --- |
| full dry end | output dominated by `DRY_L/R` |
| center region | nominal equal wet/dry balance |
| full wet end | output dominated by `WET_SUM_L/R` |

The rev-A implementation should aim for a useful perceived blend law rather than a mathematically simple but subjectively awkward midpoint.
