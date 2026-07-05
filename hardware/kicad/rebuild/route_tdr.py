#!/usr/bin/env python3
"""Routing pipeline for tank-driver-recovery.kicad_pcb.
Run with KiCad's bundled python:  "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe"

  route_tdr.py export  -> DSN with net-class width rules for Freerouting
  route_tdr.py import  -> import SES, fill zones, stitch pour fragments, save
"""
import sys, os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tdr as g  # s-expression parser

BOARD = os.path.abspath(os.path.join(HERE, "..", "tank-driver-recovery.kicad_pcb"))
DSN = os.path.join(HERE, "tdr.dsn")
SES = os.path.join(HERE, "tdr.ses")

POWER_NETS = ["+15VA", "-15VA", "PRI_OUT_L", "PRI_OUT_R",
              "N_Q101_E", "N_Q102_E", "N_Q103_E", "N_Q104_E"]
POWER_W_MM = 0.8
GND_NETS = ["AGND"]
GND_W_MM = 0.5
# excluded from the autorouter; hand-routed in the right-edge corridor
SHIELD_NETS = ["TANK_SHIELD_SEND", "TANK_SHIELD_RET"]

def mm(v):
    return pcbnew.FromMM(v)

def patch_dsn():
    """Minimal text-level patch: keep KiCad's own DSN formatting untouched,
    just remove the wide nets from the default class and append two class
    blocks with width rules."""
    import re
    with open(DSN, encoding="utf-8") as f:
        text = f.read()
    i = text.index("(class ")
    depth, j = 0, i
    while True:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    block = text[i:j + 1]
    via = re.search(r'use_via\s+"?([^\s")]+)', block).group(1)
    circuit = '(circuit (use_via "%s"))' % via
    base_w = float(re.search(r"\(width\s+([0-9.]+)\)", block).group(1))
    clear = re.search(r"\(clearance\s+([0-9.]+)", block).group(1)
    units_per_mm = base_w / 0.2  # board default track width is 0.2 mm
    for n in POWER_NETS + GND_NETS:
        pat = r'(?<=\s)"?%s"?(?=\s)' % re.escape(n)
        block = re.sub(pat, "", block, count=1)

    def mkclass(name, nets, w_mm):
        names = " ".join('"%s"' % n for n in nets)
        return ('    (class %s %s\n      %s\n'
                '      (rule (width %.1f) (clearance %s))\n    )'
                % (name, names, circuit, w_mm * units_per_mm, clear))

    block += "\n" + mkclass("power", POWER_NETS, POWER_W_MM)
    text = text[:i] + block + text[j + 1:]
    # ground is NOT routed: pours + stitching vias own it; cut its net block
    for n in GND_NETS + SHIELD_NETS:
        k = text.index('(net %s' % n)
        depth, e = 0, k
        while True:
            if text[e] == "(":
                depth += 1
            elif text[e] == ")":
                depth -= 1
                if depth == 0:
                    break
            e += 1
        text = text[:k] + text[e + 1:]
    with open(DSN, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("DSN patched: power=%.1fmm gnd=%.1fmm (units/mm=%.0f)"
          % (POWER_W_MM, GND_W_MM, units_per_mm))

def clear_of_foreign_copper(board, pt, agnd_code, margin):
    for t in board.GetTracks():
        if t.GetNetCode() != agnd_code:
            if t.HitTest(pt, margin):
                return False
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetCode() != agnd_code or pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                if pad.HitTest(pt, margin):
                    return False
    return True

def stitch(board):
    """Add an AGND via inside every filled fragment of every AGND zone."""
    agnd = board.GetNetsByName()["AGND"].GetNetCode()
    added = 0
    for zone in board.Zones():
        if zone.GetNetCode() != agnd:
            continue
        for layer in zone.GetLayerSet().Seq():
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                ol = polys.Outline(i)
                n = ol.PointCount()
                # candidate points: centroid, then vertex-adjacent probes
                cx = sum(ol.CPoint(j).x for j in range(n)) // n
                cy = sum(ol.CPoint(j).y for j in range(n)) // n
                cands = [pcbnew.VECTOR2I(cx, cy)]
                for j in range(0, n, max(1, n // 12)):
                    a, b = ol.CPoint(j), ol.CPoint((j + 1) % n)
                    mx, my = (a.x + b.x) // 2, (a.y + b.y) // 2
                    # nudge toward centroid
                    for f in (0.15, 0.3, 0.5):
                        cands.append(pcbnew.VECTOR2I(int(mx + (cx - mx) * f),
                                                     int(my + (cy - my) * f)))
                placed = False
                for pt in cands:
                    if not zone.HitTestFilledArea(layer, pt, 0):
                        continue
                    if not clear_of_foreign_copper(board, pt, agnd, mm(0.65)):
                        continue
                    v = pcbnew.PCB_VIA(board)
                    v.SetPosition(pt)
                    v.SetDrill(mm(0.4))
                    v.SetWidth(mm(0.8))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetNetCode(agnd)
                    board.Add(v)
                    added += 1
                    placed = True
                    break
                if not placed:
                    print("  fragment on layer %d #%d: no via spot found" % (layer, i))
    print("stitch vias added:", added)

def add_track(board, netcode, layer, x1, y1, x2, y2, w=0.3):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(mm(x1), mm(y1)))
    t.SetEnd(pcbnew.VECTOR2I(mm(x2), mm(y2)))
    t.SetWidth(mm(w))
    t.SetLayer(layer)
    t.SetNetCode(netcode)
    board.Add(t)

def add_via_at(board, netcode, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    v.SetDrill(mm(0.3))
    v.SetWidth(mm(0.6))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNetCode(netcode)
    board.Add(v)

def route_shields(board):
    """Deterministic right-edge corridor routing for the two shield nets.
    Jack shield pads sit at x~186; shield parts at x=193 in pad gaps.
    SEND rail at x=183.5 (F.Cu), RET rail at x=188.5 (F.Cu)."""
    F, B = pcbnew.F_Cu, pcbnew.B_Cu

    def pads_of(netname):
        out = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetNetname() == netname:
                    p = pad.GetPosition()
                    out.append((pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)))
        return out

    for netname, rail_x in (("TANK_SHIELD_RET", 188.5), ("TANK_SHIELD_SEND", 183.5)):
        code = board.GetNetsByName()[netname].GetNetCode()
        pads = pads_of(netname)
        jacks = [p for p in pads if 184.0 < p[0] < 187.5]
        parts = [p for p in pads if p[0] >= 190.0]
        ys = [p[1] for p in jacks]
        if netname == "TANK_SHIELD_RET":
            ys += [p[1] for p in parts]
            add_track(board, code, F, rail_x, min(ys), rail_x, max(ys))
            for x, y in jacks:
                add_track(board, code, F, x, y, rail_x, y)
            for x, y in parts:
                add_track(board, code, F, rail_x, y, x, y)
        else:
            # SEND: entirely on B.Cu at x=191 (right of the RET rail, which is
            # on F.Cu), jack pads are PTH so they connect on B.Cu; one via up
            # to the SMD pad of R206.
            rail_x = 191.0
            (px, py) = parts[0]
            add_track(board, code, B, rail_x, min(ys), rail_x, max(ys + [py]))
            for x, y in jacks:
                add_track(board, code, B, x, y, rail_x, y)
            add_via_at(board, code, rail_x, py)
            add_track(board, code, F, rail_x, py, px, py)
    print("shield nets hand-routed")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "export"
    board = pcbnew.LoadBoard(BOARD)
    if mode == "export":
        ok = pcbnew.ExportSpecctraDSN(board, DSN)
        print("DSN export:", ok)
        patch_dsn()
    elif mode == "import":
        ok = pcbnew.ImportSpecctraSES(board, SES)
        print("SES import:", ok)
        route_shields(board)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        stitch(board)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(BOARD, board)
        print("board saved")
    else:
        raise SystemExit("unknown mode")

main()
