"""Write GAS custom footprints for the Rev C control deck / jack deck (2026-09-17)."""
import os
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "GAS_Parts.pretty")


def mod(name, descr, body, ref="REF**", val=None, attr="through_hole"):
    val = val or name
    return (f'(module "{name}" (layer F.Cu)\n  (descr "{descr}")\n  (tags "GAS Illicit Apothecary")\n  (attr {attr})\n'
            f'  (fp_text reference {ref} (at 0 -9) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))\n'
            f'  (fp_text value "{val}" (at 0 9) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))\n' + body + ")\n")


def rect(x0, y0, x1, y1, layer, w):
    return "".join(f"  (fp_line (start {a} {b}) (end {c} {d}) (layer {layer}) (width {w}))\n"
                   for (a, b, c, d) in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)))


def circ(x, y, r, layer, w):
    return f"  (fp_circle (center {x} {y}) (end {x + r} {y}) (layer {layer}) (width {w}))\n"


def pad(num, x, y, size=2.6, drill=1.6, shape="circle"):
    return f'  (pad "{num}" thru_hole {shape} (at {x} {y}) (size {size} {size}) (drill {drill}) (layers *.Cu *.Mask))\n'


def write(name, text):
    open(os.path.join(OUT, name + ".kicad_mod"), "w").write(text)
    print("wrote", name)


# C&K 7000 style mini toggle, straight PC pins (Dailywell 1M ... M2): pins 4.70 mm pitch along the bat travel (Y),
# DPDT rows 4.83 mm apart; origin = bushing axis. Bat toward pin 1 (top, -Y) closes 2-3; bat toward pin 3 closes 2-1.
b = rect(-3.43, -6.35, 3.43, 6.35, "F.Fab", 0.1) + circ(0, 0, 3.17, "F.Fab", 0.1) + rect(-3.93, -6.85, 3.93, 6.85, "F.CrtYd", 0.05)
b += rect(-3.55, -6.47, 3.55, 6.47, "F.SilkS", 0.12) + "  (fp_text user \"1\" (at -2.4 -6.2) (layer F.SilkS) (effects (font (size 0.8 0.8) (thickness 0.12))))\n"
b += pad(1, 0, -4.7, shape="rect") + pad(2, 0, 0) + pad(3, 0, 4.7)
write("SW_Toggle_CK7000_SPDT_PC_Vertical", mod("SW_Toggle_CK7000_SPDT_PC_Vertical",
      "Mini toggle SPDT, C&K 7000 / Dailywell 1M / E-Switch 100 straight PC terminals (M2), 1/4-40 bushing, origin = bushing axis. Pins 4.70 mm. Bat toward pin 1 closes 2-3.", b))
b = rect(-5.715, -6.35, 5.715, 6.35, "F.Fab", 0.1) + circ(0, 0, 3.17, "F.Fab", 0.1) + rect(-6.2, -6.85, 6.2, 6.85, "F.CrtYd", 0.05)
b += rect(-5.84, -6.47, 5.84, 6.47, "F.SilkS", 0.12) + "  (fp_text user \"1\" (at -4.6 -6.2) (layer F.SilkS) (effects (font (size 0.8 0.8) (thickness 0.12))))\n"
b += pad(1, -2.415, -4.7, shape="rect") + pad(2, -2.415, 0) + pad(3, -2.415, 4.7) + pad(4, 2.415, -4.7) + pad(5, 2.415, 0) + pad(6, 2.415, 4.7)
b += '  (pad "" np_thru_hole circle (at 0 0) (size 1.0 1.0) (drill 1.0) (layers *.Cu *.Mask))\n'
write("SW_Toggle_CK7000_DPDT_PC_Vertical", mod("SW_Toggle_CK7000_DPDT_PC_Vertical",
      "Mini toggle DPDT, C&K 7000 / Dailywell 1M straight PC terminals (M2), rows 4.83 mm, pins 4.70 mm, origin = bushing axis (1 mm centre mark hole). Bat toward pin 1/4 closes 2-3 and 5-6.", b))

# Same Sky PJ-064B: 5.5 x 2.5 mm panel DC jack, terminals parallel to the axis. Origin = axis.
b = circ(0, 0, 5.4, "F.Fab", 0.1) + circ(0, 0, 6.2, "F.CrtYd", 0.05) + circ(0, 0, 6.0, "F.SilkS", 0.12)
b += '  (pad "3" thru_hole oval (at 0 -4.2) (size 2.5 1.3) (drill oval 2.0 0.8) (layers *.Cu *.Mask))\n'
b += '  (pad "1" thru_hole oval (at 0 3.8) (size 2.5 1.3) (drill oval 2.0 0.8) (layers *.Cu *.Mask))\n'
b += '  (pad "2" thru_hole oval (at 3.8 0) (size 1.3 2.5) (drill oval 0.8 2.0) (layers *.Cu *.Mask))\n'
b += '  (pad "" np_thru_hole circle (at 0 0) (size 1.0 1.0) (drill 1.0) (layers *.Cu *.Mask))\n'
write("BarrelJack_SameSky_PJ-064B_Vertical", mod("BarrelJack_SameSky_PJ-064B_Vertical",
      "Same Sky PJ-064B DC jack 5.5 x 2.5 mm, 5/16-32 bushing, PCB layout per pj-064x.pdf (1 centre pin, 3 sleeve, 2 switch). Origin = axis, 1 mm centre mark hole.", b))

# wire pad rows for hand-wired panel parts
for n in range(2, 11):
    L = (n - 1) * 3.0
    b = rect(-1.8, -1.8, L + 1.8, 1.8, "F.CrtYd", 0.05) + rect(-1.7, -1.7, L + 1.7, 1.7, "F.SilkS", 0.12)
    b += "".join(pad(i + 1, i * 3.0, 0, size=2.3, drill=1.2, shape="rect" if i == 0 else "circle") for i in range(n))
    write(f"WirePads_1x{n:02d}_P3.0mm_D1.2mm", mod(f"WirePads_1x{n:02d}_P3.0mm_D1.2mm",
          "Solder pads for hand-wired leads (22-26 AWG), 3.0 mm pitch, 1.2 mm holes", b))

# XKB PJ-301C 3.5 mm TRS jack, vertical (LCSC C692433): land pattern taken from the LCSC/EasyEDA
# library drawing AUDIO-TH_PJ-301C, slots widened from 0.70 to 0.90 mm for PCBWay's plated-slot minimum.
# Origin = jack axis (the M6 bushing centre) so panel_geom can place it like every other panel part.
# Pad names match the Connector_Audio:AudioJack3 symbol pins: S = sleeve, R = ring, T = tip.
b = rect(-4.0, -4.5, 4.5, 5.7, "F.Fab", 0.1) + circ(0, 0, 3.0, "F.Fab", 0.1)
b += rect(-4.5, -5.0, 5.7, 6.2, "F.CrtYd", 0.05) + rect(-4.12, -4.62, 4.62, 5.82, "F.SilkS", 0.12)
b += '  (pad "S" thru_hole oval (at 4.4 -0.74) (size 1.5 3.2) (drill oval 0.9 2.6) (layers *.Cu *.Mask))\n'
b += '  (pad "R" thru_hole oval (at 0 -3.3) (size 3.2 1.5) (drill oval 2.6 0.9) (layers *.Cu *.Mask))\n'
b += '  (pad "T" thru_hole oval (at 0 4.5) (size 3.2 1.5) (drill oval 2.6 0.9) (layers *.Cu *.Mask))\n'
write("Jack_3.5mm_PJ-301C_Vertical", mod("Jack_3.5mm_PJ-301C_Vertical",
      "XKB PJ-301C 3.5 mm TRS jack, vertical PCB mount, M6 x 0.5 bushing, body 8.5 x 10.2 mm, 14.1 mm tall. Origin = bushing axis. Pads S / R / T.", b))

# Bourns PTD904 4-gang 9 mm pot, SIDE ADJUST: pins leave the body at 90 degrees to the shaft, so the board that
# carries it stands perpendicular to the panel. Datasheet PTD90 recommended PCB layout: 12 holes 1.0 +0.2/-0,
# gang columns 5.0 / 7.5 / 12.5 / 15.0 mm behind the mounting shoulder, pin rows 1-2-3 on 5.0 mm.
# Origin = the shaft axis projected onto the board, at the mounting shoulder. +x runs away from the panel.
COLS = ((1, 5.0), (2, 7.5), (3, 12.5), (4, 15.0))
b = rect(0.0, -5.5, 17.2, 5.5, "F.Fab", 0.1) + rect(-7.0, -3.5, 0.0, 3.5, "F.Fab", 0.1)
b += rect(-7.5, -6.6, 18.0, 6.6, "F.CrtYd", 0.05) + rect(0.0, -5.62, 17.32, 5.62, "F.SilkS", 0.12)
b += "  (fp_text user \"PANEL\" (at -3.5 0) (layer F.Fab) (effects (font (size 0.8 0.8) (thickness 0.12))))\n"
for g, x in COLS:
    for pn, y in ((3, -5.0), (2, 0.0), (1, 5.0)):
        b += pad(f"{g}{pn}", x, y, size=1.8, drill=1.1, shape="rect" if (g, pn) == (1, 1) else "circle")
write("Pot_Bourns_PTD904_SideAdjust", mod("Pot_Bourns_PTD904_SideAdjust",
      "Bourns PTD904-2015K-B503 4-gang 9 mm pot, side adjust, M7x0.75 bushing. Board stands perpendicular to the panel; origin = shaft axis at the mounting shoulder, +x away from the panel. Pads gp: g = gang 1..4 from the panel, p = 1 CCW / 2 wiper / 3 CW.", b))

# template centre mark: 1 mm NPTH + crosshair on silk (drill guide for the endcap)
b = '  (pad "" np_thru_hole circle (at 0 0) (size 1.0 1.0) (drill 1.0) (layers *.Cu *.Mask))\n'
b += "  (fp_line (start -2.5 0) (end -1 0) (layer F.SilkS) (width 0.15))\n  (fp_line (start 1 0) (end 2.5 0) (layer F.SilkS) (width 0.15))\n"
b += "  (fp_line (start 0 -2.5) (end 0 -1) (layer F.SilkS) (width 0.15))\n  (fp_line (start 0 1) (end 0 2.5) (layer F.SilkS) (width 0.15))\n"
b += circ(0, 0, 1.6, "F.CrtYd", 0.05)
write("TemplateMark_1mm", mod("TemplateMark_1mm", "1 mm drill centre mark for using the bare PCB as an endcap drilling template", b, attr="exclude_from_pos_files exclude_from_bom"))
