# GAS Rev A Open Issues

This file keeps the remaining unresolved items visible so they do not get mistaken for completed design decisions.

## 1. Combo Jack Output Convention

The project requirement is combo `XLR / TRS` jacks for both input and output.

Open issue:

- standard combo-jack families are most conventional on inputs
- using them on balanced outputs may force a less-common female-XLR output convention

Status:

- requirement preserved
- needs final mechanical sanity-check before enclosure metalwork is frozen

## 2. Primary Tank Driver Final Topology

Current rev-A starting point:

- split-rail `OPA1656IDR` predriver plus `BD139-16` / `BD140-16` emitter-follower output stage

Open issue:

- this is more aligned with the audio-path capacitor preference
- but it is more complex and needs bias/stability tuning
- the old LM386 path remains as a fallback if bench results force a simpler first build

Status:

- preferred direction is now the direct-coupled split-rail stage
- final bias/stability details still need schematic and bench work

## 3. Exact Stereo Pot Families

Open issue:

- final panel hardware families for the multi-control stereo sections are not fully frozen

Status:

- architecture is stable
- exact panel hardware can be finalized after enclosure spacing is more concrete

## 4. Endcap Density And Preferred Diameter

Resolved 2026-07-04:

- diameter decided: `10 in` nominal, chosen for off-the-shelf pipe/cap availability (`9 in` fits the layout but is rarely stocked)
- hole-table positions finalized: toggles moved inboard/down, wet/dry and HPF cutoff raised `1/4 in`, DC jack at `(95, -18.35)` after two clash corrections

Status:

- the endcap drilling pattern passes all spacing rules on both `10 in` and `9 in` faces
- remaining before metalwork freeze: measured face diameter of the purchased cap, exact Neutrik cutout geometry, and final bushing diameters

## 5. Final Filter Values

Open issue:

- HPF/LPF values and Q ranges still need listening-based tuning against the real tanks

Status:

- topology is defined
- value freezing waits for prototype evaluation

## 6. Real KiCad Capture

Open issue:

- the package now has a real top-level hierarchical KiCad shell plus full first-pass symbol coverage, but five of the six rev-A child sheets are still largely un-wired electrically

Status:

- hierarchy and PDF export workflow are now real
- manifest net-label coverage is now `82 / 82`
- all six rev-A child sheets now have first-pass real symbols (`88 / 88` required refs across the full manifest)
- overall schematic symbol coverage is now `88 / 88` refs on the latest capture audit
- the power/backplane page now has a first-pass real electrical capture for DC entry, split-rail generation, and harness fanout
- the I/O page now has an explicit schematic-ready electrical definition in [rev-a-io-schematic-ready-definition.md](rev-a-io-schematic-ready-definition.md) that freezes unit allocation, passive naming, and connector ownership before the eventual KiCad multi-unit pass
- the current top-level ERC intentionally remains an intermediate failure (`650` known violations on the latest `2026-06-29` rerun), still dominated by top-level unconnected sheet pins, placeholder wire endpoints, off-grid legacy symbol endpoints, and still-unwired child-sheet labels on the non-power sheets
- the latest contained cleanup pass was on the I/O board, where removal of accidental center-short stubs reduced that child sheet from `404` to `376` local violations and dropped its multiple-net-name collisions from `8` to `2`
- actual pin-level wiring, footprint confirmation, ERC cleanup, and PCB layout are still the next major phase

## 7. External Wall Adapter: Regulated vs Unregulated Confirmation

Current rev-A direction:

- external `+30 VDC` wall-adapter strategy, with `Jameco DDU300050E9340` currently the user-preferred candidate at 500 mA / 15 W
- on-board DC-DC + +5V regulator generate the audio rails per [rev-a-external-dc-power.md](rev-a-external-dc-power.md)

Open issue:

- the current live Jameco page for `DDU300050E9340` explicitly describes the SKU as an `unregulated linear wall adapter`
- if the received sample is unregulated, open-circuit voltage at light load can exceed `+34 V` and damage the `URB2415YMD-10WR3` DC-DC module (rated 36 V max input)
- the current `2026-06-29` source snapshot still indicates a `5.5 x 2.5 mm` barrel plug, which means all power-entry jack references must stay on that size unless the adapter choice changes
- the checked-in KiCad power page now assumes the current barrel-jack and DC-DC-module pin ordering, but the exact `PJ-005B` footprint pin map and the `PS500` enable-pin treatment still need one final datasheet-to-footprint sanity pass before layout freeze

Status:

- first-sample verification step is documented in [rev-a-bench-test-procedures.md](rev-a-bench-test-procedures.md) at P-0
- if verification fails on the first sample, substitute a confirmed-regulated `+30 VDC` wall adapter from the approved-alternate list before powering the DC-DC

## 8. Control Backplane Versus Direct Panel Wiring

Open issue:

- the filter and mode sections have enough controls that several small direct-control JST links are not the cleanest final wiring strategy
- the currently checked-in grouped placeholders for `P307`, `P403`, and `P405` are still electrically compressed relative to a fully honest passive off-board control harness
- the current frozen control-backplane contract does not support putting `U601` in charge of ext-routing relay coils without changing the inter-board harness definition
- rev A likely wants either board-mounted controls or a power/control/backplane landing board for the denser control groups

Status:

- the audio harness map is now stable
- the ext-routing control landing is now electrically frozen with the raw stereo amount pot plus encoded two-bit mode control
- the crossfade feedback and filter-Q control groups now have explicit schematic-ready definitions, and the new control-backplane companion makes the compressed-placeholder status explicit instead of implicit
- `U601` is now treated as a reserve-only option until a future revision changes the harness contract
- the final panel-control landing strategy still needs enclosure-driven freeze

## 9. Clip-Mode +5V Feed (Rev-B PCB Change Recorded)

Found in the 2026-07-04 pre-order review:

- the filter board's clip relays (K401-K403) are energized from `+5VAUX`
  via the panel clip rotary, but the filter board never receives `+5VAUX`
  (its H13/`P404` power feed is ±15V only) — `P405` pin 9 is a sourceless
  spare, and a `PWR_FLAG` masks the undriven-rail ERC error
- the ext board handles the same pattern correctly (5V in on `P207.4`,
  exported to its rotary on `P206.7`)

Rev-A resolution (chosen 2026-07-04, no PCB change):

- panel jumper from the ext-mode rotary +5V common to the clip rotary
  common; `P405.9` left unwired or tied to the same bus (harmless)
- H33 in [rev-a-control-harnesses.md](rev-a-control-harnesses.md) and the
  connector schedule now document this explicitly

Rev-B fix (do with the next respin):

- make `P404`/`P504` 4-position VH like `P207`/`P506`, route `+5VAUX` to
  `P405.9` with local decoupling (mirror ext `C295`), and restore `P405.9`
  as the true source per the original H33 intent
