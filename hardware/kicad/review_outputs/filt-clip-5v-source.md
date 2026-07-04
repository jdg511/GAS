# Review: filter-clipper clip-mode +5V source (2026-07-04)

Instance: K401–K403 coil supply path, filter-clipper.kicad_sch
Severity: high (system integration) | Confidence: high
Evidence: fresh pin/net extraction of filter-clipper.kicad_sch;
rev-a-board-connector-schedule.csv (P405 row); rev-a-control-harnesses.md H33;
power-backplane extraction (no P611/P614 populated).

## Finding

- `+5VAUX` on the filter board consists of exactly one pin: P405.9, plus a
  PWR_FLAG (which is what silences the ERC undriven-power error).
- P404 (power input, H13) is 3-wire ±15V/AGND — the board never receives 5V.
- H33 documents the clip rotary's +5VAUX conductor as sourced from P405.9.
- Result as documented: CTL_CLIP_MODE_A/B can never be driven high; K401–K403
  never energize; clip modes 01/10/11 (Si/LED/Ge) are dead, 00 (Clean) works.
- Contrast: ext board receives 5V at P207.4, decouples it (C295), exports it
  to the panel at P206.7 — correct pattern.

## Result labels

- Coil wiring, flyback diodes (D421/D422), decode truth table: pass
- Coil supply source per documented harness: **fail**
- ERC status: pass-but-masked (PWR_FLAG on a sourceless power net)

## Recommendation

Zero-PCB-change: jumper the panel +5VAUX bus (present at the ext-mode rotary
common via P206.7) to the clip rotary common; update H33 and the harness map
so P405.9 is not treated as a source (leave it unwired or feed it from the
same bus — harmless stub either way).
Cleaner alternative (respin): make P404/P504 4-position like P207/P506.
