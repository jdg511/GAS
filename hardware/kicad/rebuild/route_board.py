#!/usr/bin/env python3
"""Generic routing pipeline for GAS Rev A boards (generalized from route_tdr.py).
Run with KiCad's bundled python.

  route_board.py <board-stem> export   -> DSN with net-class width rules
  route_board.py <board-stem> import   -> import SES, fill zones, stitch, save

Per-board config lives in CONFIGS below."""
import sys, os, re
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_tdr as g

CONFIGS = {
    "power-backplane": dict(
        power=["+30V_RAW", "+30V_D", "+30V_F", "GND_IN",
               "+15VRAW", "-15VRAW", "+15VA", "-15VA", "+5VAUX"],
        power_w=0.8, gnd=["AGND"]),
    "crossfade-feedback-wet": dict(
        power=["+15VA", "-15VA"], power_w=0.8, gnd=["AGND"]),
    "filter-clipper": dict(
        power=["+15VA", "-15VA", "+5VAUX"], power_w=0.8, gnd=["AGND"]),
    "ext-tank-routing": dict(
        power=["+15VA", "-15VA", "+5VAUX"], power_w=0.8, gnd=["AGND"]),
    "io-board": dict(
        power=["+15VA", "-15VA"], power_w=0.8, gnd=["AGND"]),
}

def mm(v):
    return pcbnew.FromMM(v)

def patch_dsn(dsn, power_nets, power_w, gnd_nets):
    with open(dsn, encoding="utf-8") as f:
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
    units_per_mm = base_w / 0.2
    for n in power_nets + gnd_nets:
        block = re.sub(r'(?<=\s)"?%s"?(?=\s)' % re.escape(n), "", block, count=1)
    names = " ".join('"%s"' % n for n in power_nets)
    block += ('\n    (class power %s\n      %s\n'
              '      (rule (width %.1f) (clearance %s))\n    )'
              % (names, circuit, power_w * units_per_mm, clear))
    text = text[:i] + block + text[j + 1:]
    for n in gnd_nets:
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
    with open(dsn, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("DSN patched: power=%.1fmm, gnd zone-owned" % power_w)

def clear_of_foreign_copper(board, pt, code, margin):
    for t in board.GetTracks():
        if t.GetNetCode() != code and t.HitTest(pt, margin):
            return False
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if (pad.GetNetCode() != code or
                    pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH):
                if pad.HitTest(pt, margin):
                    return False
    return True

def stitch(board, gnd):
    code = board.GetNetsByName()[gnd].GetNetCode()
    added = 0
    for zone in board.Zones():
        if zone.GetNetCode() != code:
            continue
        for layer in zone.GetLayerSet().Seq():
            polys = zone.GetFilledPolysList(layer)
            for i in range(polys.OutlineCount()):
                ol = polys.Outline(i)
                n = ol.PointCount()
                cx = sum(ol.CPoint(k).x for k in range(n)) // n
                cy = sum(ol.CPoint(k).y for k in range(n)) // n
                cands = [pcbnew.VECTOR2I(cx, cy)]
                for k in range(0, n, max(1, n // 12)):
                    a, b = ol.CPoint(k), ol.CPoint((k + 1) % n)
                    mx, my = (a.x + b.x) // 2, (a.y + b.y) // 2
                    for f in (0.15, 0.3, 0.5):
                        cands.append(pcbnew.VECTOR2I(int(mx + (cx - mx) * f),
                                                     int(my + (cy - my) * f)))
                # dense grid over the fragment's bounding box as fallback
                xs = [ol.CPoint(k).x for k in range(n)]
                ys = [ol.CPoint(k).y for k in range(n)]
                step = mm(2.0)
                gx = min(xs) + step
                while gx < max(xs):
                    gy = min(ys) + step
                    while gy < max(ys):
                        cands.append(pcbnew.VECTOR2I(int(gx), int(gy)))
                        gy += step
                    gx += step
                for pt in cands:
                    if not zone.HitTestFilledArea(layer, pt, 0):
                        continue
                    if not clear_of_foreign_copper(board, pt, code, mm(0.65)):
                        continue
                    v = pcbnew.PCB_VIA(board)
                    v.SetPosition(pt)
                    v.SetDrill(mm(0.4))
                    v.SetWidth(mm(0.8))
                    v.SetViaType(pcbnew.VIATYPE_THROUGH)
                    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
                    v.SetNetCode(code)
                    board.Add(v)
                    added += 1
                    break
    print("stitch vias added:", added)

def main():
    stem, mode = sys.argv[1], sys.argv[2]
    cfg = CONFIGS[stem]
    board_path = os.path.abspath(os.path.join(HERE, "..", stem + ".kicad_pcb"))
    dsn = os.path.join(HERE, stem + ".dsn")
    ses = os.path.join(HERE, stem + ".ses")
    board = pcbnew.LoadBoard(board_path)
    if mode == "export":
        ok = pcbnew.ExportSpecctraDSN(board, dsn)
        print("DSN export:", ok)
        patch_dsn(dsn, cfg["power"], cfg["power_w"], cfg["gnd"])
    elif mode == "import":
        ok = pcbnew.ImportSpecctraSES(board, ses)
        print("SES import:", ok)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        stitch(board, cfg["gnd"][0])
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(board_path, board)
        print("board saved")
    elif mode == "stitch":
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        stitch(board, cfg["gnd"][0])
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(board_path, board)
        print("board saved")

main()
