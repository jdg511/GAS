#!/usr/bin/env python3
"""Fast surgical fix: remove the bad U2 strap via (clearance to +15VA track)
and re-strap U2 pad 5 with obstacle prefiltering so it runs in seconds."""
import math
import sys
import pcbnew

P = r"C:\Users\Jason\GAS-build\repo\hardware\kicad\io-board.kicad_pcb"
b = pcbnew.LoadBoard(P)
agnd = b.GetNetsByName()["AGND"].GetNetCode()
mm = pcbnew.FromMM

MODE = sys.argv[1] if len(sys.argv) > 1 else "strap"

if MODE == "remove":
    bad = pcbnew.VECTOR2I(mm(101.275), mm(73.905))
    removed = 0
    for t in list(b.GetTracks()):
        if t.GetNetCode() == agnd and (t.GetPosition() - bad).EuclideanNorm() < mm(3):
            b.Remove(t)
            removed += 1
    print("removed near bad point:", removed)
    pcbnew.SaveBoard(P, b)
    print("saved")
    sys.exit(0)

pad5 = None
for fp in b.GetFootprints():
    if fp.GetReference() == "U2":
        for pad in fp.Pads():
            if pad.GetNumber() == "5":
                pad5 = pad
pt = pad5.GetPosition()

R = mm(9)
obst_t = [t for t in b.GetTracks()
          if t.GetNetCode() != agnd and (t.GetPosition() - pt).EuclideanNorm() < mm(25)]
obst_p = [pad for fp in b.GetFootprints() for pad in fp.Pads()
          if pad.GetNetCode() != agnd and (pad.GetPosition() - pt).EuclideanNorm() < R]
zones = [z for z in b.Zones() if z.GetNetCode() == agnd]

def zfill(lay, p):
    return any(z.HitTestFilledArea(lay, p, 0) for z in zones
               if lay in z.GetLayerSet().Seq())

def clear_point(v, margin):
    for t in obst_t:
        if t.HitTest(v, margin):
            return False
    for pad in obst_p:
        if pad.HitTest(v, margin):
            return False
    return True

def clear_path(a, bpt, margin):
    return all(clear_point(pcbnew.VECTOR2I(a.x + (bpt.x - a.x) * s // 12,
                                           a.y + (bpt.y - a.y) * s // 12), margin)
               for s in range(13))

placed = False
for dist in (1.2, 1.6, 2.2, 3.0, 4.0, 5.0):
    for a in range(16):
        d = (math.cos(a * math.pi / 8), math.sin(a * math.pi / 8))
        v = pcbnew.VECTOR2I(int(pt.x + d[0] * mm(dist)), int(pt.y + d[1] * mm(dist)))
        if not clear_path(pt, v, mm(0.38)):
            continue
        if zfill(pcbnew.F_Cu, v):
            tr = pcbnew.PCB_TRACK(b)
            tr.SetStart(pt); tr.SetEnd(v); tr.SetWidth(mm(0.25))
            tr.SetLayer(pcbnew.F_Cu); tr.SetNetCode(agnd); b.Add(tr)
            placed = "track"
        elif zfill(pcbnew.B_Cu, v) and clear_point(v, mm(0.95)):
            tr = pcbnew.PCB_TRACK(b)
            tr.SetStart(pt); tr.SetEnd(v); tr.SetWidth(mm(0.25))
            tr.SetLayer(pcbnew.F_Cu); tr.SetNetCode(agnd); b.Add(tr)
            via = pcbnew.PCB_VIA(b)
            via.SetPosition(v); via.SetDrill(mm(0.3)); via.SetWidth(mm(0.6))
            via.SetViaType(pcbnew.VIATYPE_THROUGH)
            via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNetCode(agnd)
            b.Add(via)
            placed = "via"
        if placed:
            break
    if placed:
        break
if not placed and zfill(pcbnew.B_Cu, pt):
    via = pcbnew.PCB_VIA(b)
    via.SetPosition(pt); via.SetDrill(mm(0.3)); via.SetWidth(mm(0.6))
    via.SetViaType(pcbnew.VIATYPE_THROUGH)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNetCode(agnd)
    b.Add(via)
    placed = "via-in-pad"
print("U2.5 strap:", placed)
f = pcbnew.ZONE_FILLER(b)
f.Fill(b.Zones())
pcbnew.SaveBoard(P, b)
print("saved")
