#!/usr/bin/env python3
"""Regenerate tank-driver-recovery.kicad_pcb in sync with the rebuilt schematic.

Places every footprint grouped by functional stage on a 170x110mm board,
adds board outline, M3 mounting holes, and AGND pours on both copper layers.
Routing is done as a separate pass. Run on the Windows machine with KiCad 10.
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

FP_DIR = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
OUT = os.path.join(g.OUT_DIR, "tank-driver-recovery.kicad_pcb")

BOARD_W, BOARD_H = 170.0, 110.0
OX, OY = 30.0, 30.0  # board origin on sheet

# ------------------------------------------------------------------ collect parts
def merged_components():
    """Merge multi-unit schematic entries into one physical part per reference."""
    parts = {}
    for _, cs in g.SECTIONS:
        for c in cs:
            ref = c["ref"].split("_")[0]
            if ref.startswith("#"):
                continue
            p = parts.setdefault(ref, dict(ref=ref, fp=c["fp"], value=c["value"],
                                           dnp=c["dnp"], pads={}))
            for unit, netmap in c["units"].items():
                # here keys may be pin names for BJTs; translate via symbol pins

                pins = g.symbol_pins(c["lib"], c["name"])
                upins = pins.get(unit, []) + pins.get(0, [])
                for num, name, _, _, _ in upins:
                    net = netmap.get(num) or netmap.get(name)
                    if net:
                        p["pads"][num] = net
    return parts

# ------------------------------------------------------------------ footprints
_fp_cache = {}

def load_footprint(fpid):
    if fpid in _fp_cache:
        return _fp_cache[fpid]
    lib, name = fpid.split(":")
    path = os.path.join(FP_DIR, lib + ".pretty", name + ".kicad_mod")
    with open(path, encoding="utf-8") as f:
        _fp_cache[fpid] = f.read()
    return _fp_cache[fpid]

def place_footprint(fpid, ref, value, x, y, rot, padnets, netcodes, dnp=False):
    """Return footprint s-expression placed at (x,y) with nets bound to pads."""
    sx = load_footprint(fpid)
    tree = g.parse(sx)[0]
    # rename header
    tree[1] = g.q(fpid)
    # strip file-level version/generator, keep everything else
    out = g.Sexp([t for t in tree if not (isinstance(t, g.Sexp) and t and
                                          t[0] in ("version", "generator", "generator_version"))])
    # insert placement + uuid after layer
    idx = 2
    for i, t in enumerate(out):
        if isinstance(t, g.Sexp) and t and t[0] == "layer":
            idx = i + 1
            break
    out.insert(idx, g.parse('(uuid "%s")' % g.uid())[0])
    out.insert(idx + 1, g.parse("(at %.3f %.3f %d)" % (x, y, rot))[0])
    if dnp:
        attr = g.find(out, "attr")
        if attr is not None:
            attr.append("dnp")
        else:
            out.insert(idx + 2, g.parse("(attr dnp)")[0])
    # properties
    for t in out:
        if isinstance(t, g.Sexp) and t and t[0] == "property":
            if t[1] == '"Reference"':
                t[2] = g.q(ref)
            elif t[1] == '"Value"':
                t[2] = g.q(value)
    # fp_text reference legacy
    for t in out:
        if isinstance(t, g.Sexp) and t and t[0] == "fp_text" and len(t) > 2:
            if t[1] == "reference":
                t[2] = g.q(ref)
            elif t[1] == "value":
                t[2] = g.q(value)
    # rotate pads/text with footprint: KiCad pad (at ...) angles are absolute-relative;
    # we add rot to each pad's angle
    def fix_angles(node):
        for t in node:
            if isinstance(t, g.Sexp):
                if t and t[0] == "pad":
                    at = g.find(t, "at")
                    if at is not None and rot:
                        if len(at) == 3:
                            at.append(str(rot))
                        else:
                            at[3] = str((float(at[3]) + rot) % 360)
                fix_angles(t) if False else None
    if rot:
        fix_angles(out)
    # bind nets
    for t in out:
        if isinstance(t, g.Sexp) and t and t[0] == "pad":
            num = t[1].strip('"')
            if num in padnets:
                net = padnets[num]
                t.append(g.parse('(net %d "%s")' % (netcodes[net], net))[0])
            # add uuid to each pad
            t.append(g.parse('(uuid "%s")' % g.uid())[0])
    return g.dump(out, 1)

# ------------------------------------------------------------------ placement map
def layout(parts):
    """Assign (x, y, rot) per reference. Coordinates relative to board origin."""
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            if r not in parts:
                raise KeyError("layout ref %s missing" % r)
            pos[r] = (OX + x0 + (i % ncols) * dx, OY + y0 + (i // ncols) * dy, rot)

    # Harness headers, left edge
    grid(["P101"], 8, 25, 0, 0, 1, rot=90)
    grid(["P102"], 8, 60, 0, 0, 1, rot=90)
    grid(["P103"], 8, 92, 0, 0, 1, rot=90)
    # Tank jacks, right edge column (send/return interleaved, top->bottom)
    grid(["J101", "J102", "J103", "J104", "J105", "J106", "J107", "J108"],
         156, 16, 0, 11, 1, rot=270)
    # Primary send L (top-left block)
    grid(["U101"], 32, 22, 0, 0, 1)
    grid(["R107", "R106", "R108", "R101", "R102"], 24, 10, 8, 6, 5)
    grid(["D101", "D102"], 64, 10, 8, 0, 2)
    grid(["Q101", "Q102"], 46, 26, 12, 0, 2)
    grid(["R103", "R104", "R105"], 70, 22, 8, 0, 3)
    grid(["C101"], 94, 22, 0, 0, 1)
    # Primary send R (second row block)
    grid(["R127", "R126", "R128", "R121", "R122"], 24, 38, 8, 6, 5)
    grid(["D121", "D122"], 64, 38, 8, 0, 2)
    grid(["Q103", "Q104"], 46, 50, 12, 0, 2)
    grid(["R123", "R124", "R125"], 70, 46, 8, 0, 3)
    grid(["C121"], 94, 46, 0, 0, 1)
    # Secondary sends (middle band)
    grid(["U102"], 32, 66, 0, 0, 1)
    grid(["R157", "R153", "R151", "R155"], 24, 74, 8, 0, 4)
    grid(["R158", "R154", "R152", "R156"], 24, 82, 8, 0, 4)
    # Recovery (right-center, near return jacks)
    grid(["U103"], 118, 22, 0, 0, 1)
    grid(["R171", "R183", "R175", "R179"], 106, 10, 8, 0, 4)
    grid(["C171", "C175"], 138, 10, 8, 0, 2)
    grid(["R172", "R184", "R176", "R180"], 106, 32, 8, 0, 4)
    grid(["C172", "C176"], 138, 32, 8, 0, 2)
    grid(["U104"], 118, 56, 0, 0, 1)
    grid(["R173", "R185", "R177", "R181"], 106, 44, 8, 0, 4)
    grid(["C173", "C177"], 138, 44, 8, 0, 2)
    grid(["R174", "R186", "R178", "R182"], 106, 66, 8, 0, 4)
    grid(["C174", "C178"], 138, 66, 8, 0, 2)
    # Shield strategy, bottom-right near jacks
    grid(["R205", "C191", "R206"], 128, 96, 10, 0, 3)
    # Power + decoupling (bottom band)
    grid(["C291", "C295", "C292", "C296", "C293", "C297", "C294", "C298"],
         28, 96, 9, 6, 8)
    grid(["C299", "C300"], 104, 96, 10, 0, 2)
    return pos

# ------------------------------------------------------------------ build board
def main():
    parts = merged_components()
    pos = layout(parts)
    missing = [r for r in parts if r not in pos]
    if missing:
        raise SystemExit("no layout position for: %s" % ", ".join(sorted(missing)))

    # net codes
    nets = sorted({n for p in parts.values() for n in p["pads"].values()})
    netcodes = {n: i + 1 for i, n in enumerate(nets)}

    hdr = []
    hdr.append('(kicad_pcb')
    hdr.append('\t(version 20260206)')
    hdr.append('\t(generator "pcbnew")')
    hdr.append('\t(generator_version "10.0")')
    hdr.append('\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)')
    hdr.append('\t(paper "A3")')
    hdr.append('\t(title_block\n\t\t(title "GAS Rev A - Tank Driver Recovery Board")'
               '\n\t\t(company "Illicit Apothecary")\n\t\t(comment 1 "Generated by rebuild/gen_tdr_pcb.py")\n\t)')
    hdr.append('\t(layers\n'
               '\t\t(0 "F.Cu" signal)\n\t\t(2 "B.Cu" signal)\n'
               '\t\t(9 "F.Adhes" user "F.Adhesive")\n\t\t(11 "B.Adhes" user "B.Adhesive")\n'
               '\t\t(13 "F.Paste" user)\n\t\t(15 "B.Paste" user)\n'
               '\t\t(5 "F.SilkS" user "F.Silkscreen")\n\t\t(7 "B.SilkS" user "B.Silkscreen")\n'
               '\t\t(1 "F.Mask" user)\n\t\t(3 "B.Mask" user)\n'
               '\t\t(17 "Dwgs.User" user "User.Drawings")\n\t\t(19 "Cmts.User" user "User.Comments")\n'
               '\t\t(21 "Eco1.User" user "User.Eco1")\n\t\t(23 "Eco2.User" user "User.Eco2")\n'
               '\t\t(25 "Edge.Cuts" user)\n\t\t(27 "Margin" user)\n'
               '\t\t(31 "F.CrtYd" user "F.Courtyard")\n\t\t(29 "B.CrtYd" user "B.Courtyard")\n'
               '\t\t(35 "F.Fab" user)\n\t\t(33 "B.Fab" user)\n\t)')
    hdr.append('\t(setup\n\t\t(pad_to_mask_clearance 0)\n\t\t(allow_soldermask_bridges_in_footprints no)\n'
               '\t\t(tenting front back)\n'
               '\t\t(pcbplotparams\n\t\t\t(layerselection 0x00000000_00000000_55555555_5755f5ff)\n'
               '\t\t\t(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)\n'
               '\t\t\t(disableapertmacros no)\n\t\t\t(usegerberextensions no)\n\t\t\t(usegerberattributes yes)\n'
               '\t\t\t(usegerberadvancedattributes yes)\n\t\t\t(creategerberjobfile yes)\n'
               '\t\t\t(dashed_line_dash_ratio 12.000000)\n\t\t\t(dashed_line_gap_ratio 3.000000)\n'
               '\t\t\t(svgprecision 4)\n\t\t\t(plotframeref no)\n\t\t\t(mode 1)\n'
               '\t\t\t(useauxorigin no)\n\t\t\t(hpglpennumber 1)\n\t\t\t(hpglpenspeed 20)\n'
               '\t\t\t(hpglpendiameter 15.000000)\n\t\t\t(pdf_front_fp_property_popups yes)\n'
               '\t\t\t(pdf_back_fp_property_popups yes)\n\t\t\t(pdf_metadata yes)\n\t\t\t(pdf_single_document no)\n'
               '\t\t\t(dxfpolygonmode yes)\n\t\t\t(dxfimperialunits yes)\n\t\t\t(dxfusepcbnewfont yes)\n'
               '\t\t\t(psnegative no)\n\t\t\t(psa4output no)\n\t\t\t(plot_black_and_white yes)\n'
               '\t\t\t(sketchpadsonfab no)\n\t\t\t(plotpadnumbers no)\n\t\t\t(hidednponfab no)\n'
               '\t\t\t(sketchdnponfab yes)\n\t\t\t(crossoutdnponfab yes)\n\t\t\t(subtractmaskfromsilk no)\n'
               '\t\t\t(outputformat 1)\n\t\t\t(mirror no)\n\t\t\t(drillshape 1)\n\t\t\t(scaleselection 1)\n'
               '\t\t\t(outputdirectory "")\n\t\t)\n\t)')
    hdr.append('\t(net 0 "")')
    for n in nets:
        hdr.append('\t(net %d "%s")' % (netcodes[n], n))

    body = []
    # footprints
    for ref, p in sorted(parts.items()):
        x, y, rot = pos[ref]
        body.append(place_footprint(p["fp"], ref, p["value"], x, y, rot,
                                    p["pads"], netcodes, dnp=p["dnp"]))
    # mounting holes
    for i, (mx, my) in enumerate([(6, 6), (BOARD_W - 6, 6), (6, BOARD_H - 6),
                                  (BOARD_W - 6, BOARD_H - 6)]):
        body.append(place_footprint("MountingHole:MountingHole_3.2mm_M3",
                                    "H%d" % (i + 1), "M3", OX + mx, OY + my, 0, {}, netcodes))
    # board outline
    cs = [(OX, OY), (OX + BOARD_W, OY), (OX + BOARD_W, OY + BOARD_H), (OX, OY + BOARD_H)]
    for a, b in zip(cs, cs[1:] + cs[:1]):
        body.append('\t(gr_line\n\t\t(start %.2f %.2f)\n\t\t(end %.2f %.2f)\n'
                    '\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type default)\n\t\t)\n'
                    '\t\t(layer "Edge.Cuts")\n\t\t(uuid "%s")\n\t)' % (a[0], a[1], b[0], b[1], g.uid()))
    # AGND zones both layers
    agnd = netcodes["AGND"]
    for layer in ("F.Cu", "B.Cu"):
        body.append(
            '\t(zone\n\t\t(net %d)\n\t\t(net_name "AGND")\n\t\t(layer "%s")\n\t\t(uuid "%s")\n'
            '\t\t(hatch edge 0.5)\n\t\t(connect_pads\n\t\t\t(clearance 0.4)\n\t\t)\n'
            '\t\t(min_thickness 0.25)\n\t\t(filled_areas_thickness no)\n'
            '\t\t(fill yes\n\t\t\t(thermal_gap 0.5)\n\t\t\t(thermal_bridge_width 0.5)\n\t\t)\n'
            '\t\t(polygon\n\t\t\t(pts\n\t\t\t\t(xy %.2f %.2f) (xy %.2f %.2f) (xy %.2f %.2f) (xy %.2f %.2f)\n\t\t\t)\n\t\t)\n\t)'
            % (agnd, layer, g.uid(),
               OX + 1, OY + 1, OX + BOARD_W - 1, OY + 1,
               OX + BOARD_W - 1, OY + BOARD_H - 1, OX + 1, OY + BOARD_H - 1))
    body.append('\t(embedded_fonts no)')
    body.append(')')

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(hdr + body) + "\n")
    print("Wrote %s: %d footprints, %d nets" % (OUT, len(parts) + 4, len(nets)))

if __name__ == "__main__":
    main()
