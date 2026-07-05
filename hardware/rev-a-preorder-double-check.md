# Rev A Pre-Order Double-Check (2026-07-04)

Independent re-verification of the **READY TO ORDER** claim in
`kicad/rev-a-order-readiness.md`, done against the files as they exist today
(including the 2026-07-04 ext-tank-routing respin). Method summary at the end.

## Verdict

**Bare PCB fabrication: ready after one 10-minute fix (io-board).**
**Assembly ordering: NOT ready — five of six BOM files are missing their DNP flags.**
One system-level wiring gap (clip-mode 5V) must be recorded now, before
harnesses are built, but it does not affect the PCBs.

---

## Fix before uploading (blockers)

### 1. io-board: orphaned AGND copper island — in the shipped gerbers

- The last io-board DRC (`rebuild/io-drc.json`, 05:06:52) reports one
  `unconnected_items` **error**: the F.Cu AGND zone fills as two islands.
  The board was re-saved 25 s *after* that DRC and gerbers were cut from the
  newer save, so the gate evidence never covered the shipped file.
- I re-checked the saved board copper independently: the island is still
  there (a via + two small zone slivers near x=117.1, y=96.5, no pads), and
  the copper appears in `fab/io-board/gerbers/io-board-F_Cu.gtl`
  (flash at X117.10 / Y-96.48).
- Impact: no component pad floats, so this is not electrically fatal — it is
  a floating copper sliver. But it is a real DRC error, it contradicts the
  "0 unconnected" row in the readiness table, and a fab will not flag it.
- Fix: enable "remove islands" / min-island area on that zone (or stitch the
  sliver), refill, re-run DRC to 0, re-export **io-board** gerbers only.
- The readiness table's io-board row should only say 0/0 after this.

### 2. BOM CSVs: DNP column missing on 5 of 6 boards (assembly blocker only)

- `fab/ORDER-PACKET.md` promises "the BOM CSVs flag DNP parts — do not
  populate them." Only `ext-tank-routing-bom.csv` (regenerated 07-04) has a
  DNP column. The other five (07-02) have none.
- If these go to JLC/PCBWay assembly as-is, the assembler will populate parts
  the design explicitly keeps out:
  - tank-driver-recovery: **D101 D102 D121 D122** (class-B bias diodes the
    design review froze as DNP) and C175–C178 (DC-block trim slots)
  - io-board: C1–C4 (220p RF caps on the balanced inputs)
  - filter-clipper: C405 C425; crossfade: C321 C322
- Fix: regenerate all six BOMs (and pos files for consistency) with the
  current exporter — the 07-04 exporter already does this correctly.
- Bare-PCB fabrication is unaffected (gerbers don't read the BOM).

---

## Record now, fix at harness build (does not block PCBs)

### 3. Clip-mode relays have no +5V source as documented

- Filter board: K401–K403 coils energize from `CTL_CLIP_MODE_A/B`, which the
  panel rotary drives from `+5VAUX`. Harness H33 sources that +5VAUX from
  filter board **P405 pin 9** — but on the filter board that pin is a dead
  stub: the board's power input P404/H13 is 3-wire (±15V only) and nothing
  else on the board connects to +5VAUX. A PWR_FLAG masks the ERC error.
- The ext board does this correctly (5V arrives on P207.4 and is exported to
  its panel switch at P206.7). The filter board has no equivalent feed, and
  the current power-backplane PCB has no P611/P614 control landings either.
- As documented, clip modes Si / LED / Ge would never engage; only Clean
  works. This survives ERC, DRC, and per-board simulation, and would first
  appear at system bring-up.
- Zero-PCB-change fix: on the panel, jumper the +5VAUX bus from the ext-mode
  rotary common (fed by P206.7) to the clip rotary common, and update H33 /
  the harness map so the builder doesn't wire pin 9 as the source.
  Alternative (cleaner, needs respin): make P404/P504 4-pin like P207/P506.

---

## Refresh the paper trail (10 minutes, no design change)

4. **tank-driver-recovery ERC is stale**: last ERC 00:07:50, schematic saved
   00:34:41. My independent extraction of the current file shows every pin
   attached and labeled, and the 02:37 DRC passed schematic parity against
   the newer file, so risk is low — but re-run ERC so the gate is honest.
5. **Superseded reports still look current**: `kicad/*.drc.json` (all dated
   07-01, older than every board) and `GAS-Hardware-erc-current.json`
   (303 errors — it audits the *abandoned* hierarchical top level) should be
   deleted or moved under an `archive/` folder. Same for the `tmp-*` ERC
   files. Anyone (including a vendor engineer, or you in three months)
   opening `GAS-Hardware.kicad_sch` will see a broken design unless it's
   clearly marked as abandoned.

---

## Carried risks (already documented; restating so they don't get lost)

6. **Wall adapter regulation (open issue #7) — RESOLVED `2026-07-04`.**
   The adapter is now the regulated Triad `WSU240-0750` (+24 V / 0.75 A /
   18 W, UL 62368-1). Worst case +25.2 V sits far below the URA2415's 36 V
   input ceiling, so the sustained-overvoltage risk is retired. Keep the
   P-0 open-circuit receiving check (accept 22.8–25.2 V, reject above 27 V).
   Jack changes PJ-005B -> PJ-005A (5.5 x 2.1 mm center positive).
7. **G5V-2 coil variants at order time** (flagged in the datasheet summary):
   confirm DC5 coil current (30 vs 40 mA). Worst case 7 coils energized
   (Parallel + Ge) = 210–280 mA on the 500 mA R-78E — fine either way, but
   the power-budget doc's 210 mA figure assumes the 30 mA coil. If the DC12
   (K301) coil is the 720R variant, change R351 240R → 150R.
8. **BD139/BD140 datasheet was never cached** — ratings used are
   industry-standard values (sim shows wide margin). Confirm SOA and hFE bin
   (-16) when ordering parts.
9. **+15VA rail worst-case stack** (audio quiescent 114–154 mA + R-78E input
   ~110 mA + K301 ~13 mA + peak line drive) can brush the URA's 333 mA/rail
   limit under pathological simultaneous conditions. The bring-up current
   measurement already covers this; just don't skip it.

---

## Verified clean (independent evidence, not just re-reading the docs)

- **Netlists**: my own extraction of all six current schematics is
  geometrically exact (every pin lands on exactly one labeled stub; 0
  isolated pins, 0 dangling labels, 0 double-named nets per board).
- **Op-amp supplies**: every quad (OPA1679, OPA1644) has pin 4 = +15VA /
  pin 11 = −15VA; every dual (OPA1656) has pin 8 = +15VA / pin 4 = −15VA.
  Verified against cached TI datasheets. All parts rated ±18 V (checklist).
- **Output stage**: BD139 collectors → +15VA, BD140 → −15VA; feedback taken
  from PRI_OUT (in-loop, post-follower) as the design review froze it.
- **Power entry**: P500 → SS34 series reverse protection → 1.1 A PTC →
  SMAJ33A TVS → bulk (C500/C509) → URA2415YMD-10WR3 with pin map 1=GND_IN,
  2=+30V_F, 3=+15VRAW, 4=AGND, 5=−15VRAW, 6=Ctrl NC — matches the Mornsun
  drawing; URA (dual) confirmed, not URB. R-78E fed from +15VRAW (fix F1
  applied); C512/C507/C508 externals present. R500 0R single-point
  GND_IN↔AGND bond.
- **Relay logic**: clip decode traces 00 Clean / 01 Si / 10 LED / 11 Ge;
  ext decode traces 00 Off / 10 Series / 11 Parallel with Off isolating
  secondary sends and returns. Flyback diodes present and correctly oriented
  on all four coil control lines (D261 D262 D421 D422 D301).
- **Mono fix F2**: R25 1M MONO_C→R_RX present. XLR pin 2 = hot per AES.
- **Harness contract**: every inter-board pair matches pin-for-pin in the
  current files, including post-respin P205↔P305 (FB_RET), P201↔P2,
  P202↔P101, P203↔P102, P204↔P301, P302↔P401, P303↔P402, P304↔P3, and the
  power fanout (P501-P506↔P1/P103/P306/P404/P207).
- **Copper**: my net-aware connectivity audit of all six saved boards finds
  zero split nets except the known io-board island. Min track 0.2 mm, min
  drill 0.3 mm, min annular 0.15 mm, Edge.Cuts present — all within
  PCBWay/JLC standard capability, matching the ORDER-PACKET fab spec.
- **Fab packets**: gerber/drill exports are newer than their boards on all
  six (io-board needs re-export only because of finding 1).
- **Tank sends**: primary sized for 8R (4AB1C1B), secondary for 800R
  (9EB2C1B/9EB3C1B — the 2/3 suffix is decay time, so unequal L/R decay is
  the documented intent, not an error).

## Method / verification basis

- Parsed all six current `.kicad_sch` files directly (S-expression level)
  and rebuilt every pin→net assignment; validated geometrically (every pin,
  wire, label accounted for). Did not rely on the stale
  `rebuild/review-extract-*.json` (three of six predate current schematics,
  and their extractor merges power rails through PWR_FLAG aliases).
- Parsed all six current `.kicad_pcb` files and ran a net-aware copper
  connectivity audit (zones/tracks/vias/pads with real geometry), plus
  min-feature stats; cross-checked one finding against the exported gerber.
- Verified IC pin maps against the cached datasheet summaries and PDFs in
  `kicad/datasheet_cache/` (OPA1656/1644/1679, URA2415YMD-10WR3, R-78E5.0,
  G5V-2, JST XH/VH). BD139/140 remains the one uncached datasheet.
- Applied `rev-a-validation-checklist.md` (Schematic Review + Manufacturing
  Package sections) and cross-read the harness/connector schedule docs.
- Timestamp-audited every ERC/DRC/gerber artifact against its source file.
- Not covered here: audio-quality judgments (filter values, clip voicing),
  enclosure/endcap mechanics, and anything requiring powered hardware.
