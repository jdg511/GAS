# GAS Rev A — PCB Order Packet

All six boards passed the gate: **ERC 0 violations, simulation-verified,
routed, DRC 0 errors / 0 unconnected**. Everything a fab needs is in this
folder, one subfolder per board.

Re-verified 2026-07-04 pm after the independent pre-order review:
io-board gerbers/drill/pos re-exported (AGND island fix — discard any
earlier io-board upload), and **all six BOM CSVs regenerated with the DNP
column** (five previously lacked it; do not use BOMs dated before
2026-07-04 pm for assembly).

## The six boards

| Board | Size (mm) | What it does |
| --- | --- | --- |
| tank-driver-recovery | 170 x 110 | Drives the four spring tanks, recovers their returns |
| power-backplane | 120 x 80 | +24V wall-adapter entry -> isolated +/-15V + 5V rails |
| crossfade-feedback-wet | 100 x 70 | Crossfade summers, wet handoff, feedback phase relay |
| filter-clipper | 140 x 90 | HPF, drive, 4-mode clip networks, LPF, output buffers |
| ext-tank-routing | 120 x 80 | Off/Series/Parallel external tank relay routing |
| io-board | 160 x 75 | Balanced I/O, mono switch, wet/dry blend, line drivers |

## Fab spec (same for all six)

- 2 layers, 1.6 mm FR-4, 1 oz copper
- HASL (lead-free) finish, green mask, white silk
- Smallest drill 0.3 mm, min trace/space used ~0.2 mm — standard capability
- Quantity suggestion: 5 of each (typical minimum order)

## Per-board files

Each `fab/<board>/` contains:

- `<board>-gerbers.zip` — upload this for PCB fabrication (includes drill files)
- `<board>-bom.csv` — parts list (Reference, Value, Footprint, DNP)
- `<board>-pos.csv` — pick-and-place positions for assembly quoting

## Where to send it (JLCPCB path, per rev-a-manufacturing.md)

1. jlcpcb.com -> "Order now" -> upload `<board>-gerbers.zip`
2. Confirm the auto-detected size/layers; pick the spec above
3. For assembly: enable "PCB Assembly" (SMT), upload `<board>-bom.csv`
   and `<board>-pos.csv` when prompted
4. Repeat per board (6 uploads), or use PCBWay the same way

## Things a human must decide at checkout

- **Assembly scope:** SMD-only assembly is cheapest; the TH parts
  (JST headers, relays, TO-126 transistors, DC-DC module, radial caps)
  can be hand-soldered or added to JLC's "Standard" assembly for more cost.
- **BOM part matching:** JLC will ask to match each BOM line to their
  catalog. Key exact parts: OPA1656IDR, OPA1679IDR, OPA1644AIDR (I/O board),
  BD139-16/BD140-16, G5V-2 DC5/DC12 relays, URA2415YMD-10WR3 (the DC-DC —
  buy from Mouser/DigiKey if JLC lacks it; footprint is on the board),
  R-78E5.0-0.5, JST XH/VH headers.
- **DNP lines:** the BOM CSVs flag DNP parts (bias-diode reserves, RF caps,
  gain-trim slots) — do not populate them.
- **Harness/panel note (not a fab item):** the clip-mode rotary's +5V
  common is fed by a panel jumper from the ext-mode rotary's 5V bus —
  NOT from filter board P405 pin 9, which is a sourceless spare. See H33
  in `hardware/rev-a-control-harnesses.md` (recorded 2026-07-04; rev-B
  PCB fix is open issue #9).
- **Separate purchases (not on any PCB):** spring tanks 2x 4AB1C