# Instance review: DC entry path at +24 VDC (P500/D500/F500/TVS500/C500/C509, power-backplane)

Supersedes `pwr-entry-path.md` (written for the +30 V Jameco candidate).
Re-reviewed 2026-07-04 after the adapter change to the Triad `WSU240-0750`
(+24 VDC / 750 mA / 18 W regulated SMPS, `rev-a-external-dc-power.md`).

Wall-side worst-case load: ~10.3 W → ~0.43 A at 24 V.

| Item | Net / value | Check | Result |
| --- | --- | --- | --- |
| P500 XH-2 | +30V_RAW/GND_IN (names historical, now +24 V nominal) | 0.43 A vs 3 A rating (14%) | pass |
| D500 SS34 | series reverse protection | 3 A / 40 V, ~0.17 W at 0.43 A | pass (family spec, needs-human-check) |
| F500 MF-MSMF110 (1812 SMD) | 1.1 A hold | 0.43 A steady, adapter OLP is primary protection | pass |
| TVS500 SMAJ33A | 33 V standoff | 25.2 V worst-case rail (24 V +5%) — margin improved vs 30 V design | pass |
| C500 220u bulk | +24 V input | purchasing BOM spec'd a 25 V part (EEU-FR1E221) — below the 25.2 V worst-case input | **fail → fixed: 50 V part (EEU-FR1H221) spec'd in BOM 2026-07-04** |
| C509 100u Cin | +24 V input at PS500 | URA datasheet Fig.2 requires 50 V class Cin | **fail → fixed: 50 V part spec'd (EEU-FR1H221 fits the D10/P5 footprint; an 8 mm 100u/50 V needs lead-forming on the 5 mm pitch)** |
| inrush | ~440 uF total input bulk | current-limited 18 W adapter (OVP/OLP/SCP auto-recovery) + PTC; bench P-0 plug-in scope check retained | pass (note, bench) |

## Notes

- The 25 V input-cap spec predates the adapter change and was **also wrong for
  the old +30 V design** — it was never caught because the 2026-07-02 entry-path
  review checked pin-nets and current but not capacitor voltage ratings.
  Rail-side electrolytics (C501/C504 100u, C510/C511/C512 10u, C507 47u) sit on
  +/-15 V or +5 V and are fine at 25 V.
- F500 on the board is the SMD `MF-MSMF110` (1812), not the radial `MF-R100`
  the docs BOM listed; the docs BOM was corrected 2026-07-04. Buy the SMD part.
- Receiving check (P-0): open-circuit +22.8 V to +25.2 V, reject above +27 V.
- KiCad net names `+30V_RAW` / `+30V_F` are historical labels now carrying
  +24 V nominal; rename at the next capture pass (tracked in
  `rev-a-external-dc-power.md` open items). Cosmetic only; does not affect the
  fab package.

Evidence: raw power-backplane.kicad_sch value extraction (2026-07-04),
fab/power-backplane/power-backplane-bom.csv footprints,
datasheet_cache/ura2415ymd.summary.md, rebuild/pwr-erc.json + pwr-drc.json
(2026-07-04T13:32 gate), Triad WSU240-0750 datasheet (docs BOM link).
Confidence: high unless noted.
