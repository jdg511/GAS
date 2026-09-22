"""Route a placed board with Freerouting, add AGND pours + stitching vias, fill, save."""
import os, sys, subprocess, time
sys.path.insert(0, os.path.dirname(__file__))
import pcbnew

MM = pcbnew.FromMM
JAR = r"C:\Users\Jason\GAS-build\tools\freerouting-1.9.0.jar"


def unrouted(pcb_path):
    brd = pcbnew.LoadBoard(pcb_path)
    brd.BuildConnectivity()
    return brd.GetConnectivity().GetUnconnectedCount(True)


def autoroute(pcb_path, passes=40, timeout=2400, tries=3):
    for t in range(tries):
        _autoroute(pcb_path, passes, timeout)
        u = unrouted(pcb_path)
        print("unrouted after pass", t + 1, ":", u)
        if u == 0:
            return


def _autoroute(pcb_path, passes=40, timeout=2400):
    brd = pcbnew.LoadBoard(pcb_path)
    base = os.path.splitext(pcb_path)[0]
    dsn, ses = base + ".dsn", base + ".ses"
    for f in (ses,):
        if os.path.exists(f):
            os.remove(f)
    ok = pcbnew.ExportSpecctraDSN(brd, dsn)
    if not ok:
        raise RuntimeError("DSN export failed")
    t = time.time()
    proc = subprocess.run(["java", "-jar", JAR, "-de", dsn, "-do", ses, "-mp", str(passes), "-mt", "0"],
                          capture_output=True, text=True, timeout=timeout)
    print("freerouting rc", proc.returncode, "in", round(time.time() - t), "s")
    if not os.path.exists(ses):
        print(proc.stdout[-2000:], proc.stderr[-2000:])
        raise RuntimeError("no SES produced")
    brd = pcbnew.LoadBoard(pcb_path)
    pcbnew.ImportSpecctraSES(brd, ses)
    pcbnew.SaveBoard(pcb_path, brd)


def pour(pcb_path, net="AGND", stitch=8.0):
    brd = pcbnew.LoadBoard(pcb_path)
    for z in list(brd.Zones()):
        if not z.GetIsRuleArea():
            brd.Remove(z)
    bb = brd.GetBoardEdgesBoundingBox()
    x1, y1, x2, y2 = bb.GetX(), bb.GetY(), bb.GetRight(), bb.GetBottom()
    ni = brd.FindNet(net)
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(brd)
        z.SetLayer(layer)
        z.SetNet(ni)
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        z.SetThermalReliefGap(MM(0.5))
        z.SetThermalReliefSpokeWidth(MM(0.5))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for (x, y) in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            ol.Append(x, y)
        brd.Add(z)
    filler = pcbnew.ZONE_FILLER(brd)
    filler.Fill(brd.Zones())
    # stitching vias: only where the via fits fully inside the AGND fill on both layers, away from other holes
    added = 0
    if stitch:
        polys = {}
        for z in brd.Zones():
            if z.GetIsRuleArea() or z.GetNetname() != net:
                continue
            ps = z.GetFilledPolysList(z.GetLayer()).CloneDropTriangulation()
            ps.Deflate(MM(0.4), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.02))
            polys[z.GetLayer()] = ps
        holes = [(p.GetPosition(), max(p.GetDrillSize().x, p.GetSize(pcbnew.F_Cu).x)) for p in brd.GetPads()]
        holes += [(v.GetPosition(), v.GetWidth(pcbnew.F_Cu)) for v in brd.GetTracks() if v.Type() == pcbnew.PCB_VIA_T]
        keep = []
        for z in brd.Zones():
            if z.GetIsRuleArea() and z.GetDoNotAllowVias():
                keep.append(z.Outline())
        step = MM(stitch)
        y = y1 + MM(4)
        while y < y2 - MM(3):
            x = x1 + MM(4)
            while x < x2 - MM(3):
                pt = pcbnew.VECTOR2I(int(x), int(y))
                if all(l in polys and polys[l].Contains(pt) for l in (pcbnew.F_Cu, pcbnew.B_Cu)) and \
                        not any(k.Contains(pt) or k.Collide(pt, MM(0.5)) for k in keep):
                    if all((pt - hp).EuclideanNorm() > MM(1.2) + d / 2 for hp, d in holes):
                        v = pcbnew.PCB_VIA(brd)
                        v.SetPosition(pt); v.SetWidth(MM(0.6)); v.SetDrill(MM(0.3)); v.SetNet(ni)
                        brd.Add(v); added += 1
                        holes.append((pt, MM(0.6)))
                x += step
            y += step
        filler.Fill(brd.Zones())
    pcbnew.SaveBoard(pcb_path, brd)
    print("stitching vias", added)
