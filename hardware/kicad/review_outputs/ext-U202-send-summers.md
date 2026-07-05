# Instance review: U202 (OPA1656IDR send summers, ext-tank-routing)

Added in the 2026-07-04 re-spin (feedback reinjection moved pre-tank). Not covered
by the 2026-07-02 review pass; reviewed 2026-07-04 against
`datasheet_cache/opa1656.summary.md` (status: verified).

Connectivity evidence: fresh post-re-spin SPICE export `rebuild/ext-sim.cir`
(2026-07-04), cross-checked against the ERC/DRC pm gate (`rebuild/ext-erc.json`,
`rebuild/ext-drc.json`, 0 errors / 0 unconnected).

| Pin (SOIC-8) | Net | Check | Result |
| --- | --- | --- | --- |
| 1 OUT_A | SEND_MIX_L | inverting summer output, 20k feedback via R208 | pass |
| 2 IN_A- | N_SND_L_M | virtual ground: R207 20k (WET_SEND_L) + R204 20k (FB_RET_L) + R208 20k fb | pass |
| 3 IN_A+ | AGND | non-inverting input grounded | pass |
| 4 V- | -15VA | within +/-18 V abs max per datasheet summary | pass |
| 5 IN_B+ | AGND | non-inverting input grounded | pass |
| 6 IN_B- | N_SND_R_M | R227 20k (WET_SEND_R) + R224 20k (FB_RET_R) + R228 20k fb | pass |
| 7 OUT_B | SEND_MIX_R | mirror of channel A | pass |
| 8 V+ | +15VA | within abs max | pass |

## Required externals

- Rail decoupling: C291/C296 (100n, +15VA), C292/C297 (100n, -15VA) — two 100n
  per rail for the two op-amp packages (U201, U202), plus C293/C294 22u bulk: pass.
- Output loading: OUT_A/B drive 100R series isolators (R201/R221) into the
  tank-driver board send inputs (~10k) in parallel with the 20k feedback path.
  Worst-case load >> spec'd 100 mA output capability: pass.
- Stability: unity-gain inverting (20k/20k), no direct capacitive load on the
  outputs (series 100R first). OPA1656 is unity-gain stable: pass.
- Quiescent current: +7.8 mA/package added to both analog rails.
  `rev-a-power-budget.md` updated 2026-07-04 to include it.

## Findings

- **Note (bench):** the new send summers are inverting, and feedback now
  reinjects before the springs instead of at the TANK_MIX output summers, so the
  net feedback-loop sign differs from the pre-re-spin topology. The crossfade
  board's `Feedback Phase Invert` selector covers either sense; verify at bench
  which panel labeling matches positive-feedback build-up and swap the label if
  needed. Severity: note. Confidence: high.

Evidence: rebuild/ext-sim.cir (post-re-spin netlist), rebuild/ext-erc.json +
ext-drc.json (2026-07-04T13:32 gate), datasheet_cache/opa1656.summary.md.
