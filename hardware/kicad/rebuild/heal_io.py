#!/usr/bin/env python3
"""Post-route ground healing for io-board: strap boxed-in AGND SMD pads
(U3/U4 pin 5) to the plane, then grid-stitch F/B ground pours.
Run with KiCad's python after route_board.py import."""
import pcbnew

P = r"C:\Users\Jason\GAS-build\repo\hardware\kicad\io-board.kicad_pcb"
b = pcbnew.LoadBoard(P)
agnd = b.GetNetsByName()["AGND"].GetNetCode()
mm = pcbnew.FromMM

# remove the known-bad first-generation U2 strap (clearance to +15VA track)
_bad = pcbnew.VECTOR2I(mm(101.275), mm(73.905))
for _t in list(b.GetTracks()):
    if _t.GetNetCode() == agnd and (_t.GetPosition() - _bad).EuclideanNorm() < mm(3):
        b.Remove(_t)

allpads = [pad for fp in b.GetFootprints() for pad in fp.Pads()]
obst_t = [t for t in list(b.GetTracks()) if t.GetNetCode() != agnd]
obst_p = [pad for pad in allpads if pad.GetNetCode() != agnd]

def clear_path(a, bpt, margin):
    for s in range(13):
        v = pcbnew.VECTOR2I(a.x + (bpt.x - a.x) * s // 12,
                            a.y + (bpt.y - a.y) * s // 12)
        for t in obst_t:
            if t.HitTest(v, margin):
                return False
        for pad in obst_p:
            if pad.HitTest(v, margin):
                return False
    return True

zones0 = [z for z in b.Zones() if z.GetNetCode() == agnd]

def zfill(lay, pt):
    return any(z.HitTestFilledArea(lay, pt, 0) for z in zones0
               if lay in z.GetLayerSet().Seq())

def already_connected(pad):
    pos = pad.GetPosition()
    if zfill(pcbnew.F_Cu, pos):
        return True
    for t in b.GetTracks():
        if t.GetNetCode() == agnd and t.GetClass() == "PCB_TRACK" \
                and t.HitTest(pos, mm(0.05)):
            return True
    return False

def strap(pad):
    pt = pad.GetPosition()
    import math
    dirs = [(math.cos(a * math.pi / 8), math.sin(a * math.pi / 8))
            for a in range(16)]
    best = None
    for dist in (1.2, 1.6, 2.2, 3.0, 4.0, 5.0):
        for d in dirs:
            v = pcbnew.VECTOR2I(int(pt.x + d[0] * mm(dist)),
                                int(pt.y + d[1] * mm(dist)))
            if not clear_path(pt, v, mm(0.38)):
                continue
            if zfill(pcbnew.F_Cu, v):
                best = (v, False)   # reachable top-layer pour: track only
                break
            # a via endpoint needs clearance from tracks on BOTH layers:
            # via radius 0.3 + clearance 0.2 + power track half-width 0.4
            if zfill(pcbnew.B_Cu, v) and clear_path(v, v, mm(0.95)):
                best = (v, True)    # via down to the bottom plane
                break
        if best:
            break
    # last resort: via-in-pad straight down to the bottom plane
    if not best and zfill(pcbnew.B_Cu, pt):
        via = pcbnew.PCB_VIA(b)
        via.SetPosition(pt); via.SetDrill(mm(0.3)); via.SetWidth(mm(0.6))
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNetCode(agnd)
        b.Add(via)
        return True
    if not best:
        return False
    v, need_via = best
    tr = pcbnew.PCB_TRACK(b)
    tr.SetStart(pt); tr.SetEnd(v); tr.SetWidth(mm(0.25))
    tr.SetLayer(pcbnew.F_Cu); tr.SetNetCode(agnd); b.Add(tr)
    if need_via:
        via = pcbnew.PCB_VIA(b)
        via.SetPosition(v); via.SetDrill(mm(0.3)); via.SetWidth(mm(0.6))
        via.SetViaType(pcbnew.VIATYPE_THROUGH)
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNetCode(agnd)
        b.Add(via)
    return True

for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetCode() == agnd and not pad.HasHole():
            if not already_connected(pad):
                ok = strap(pad)
                print(fp.GetReference(), pad.GetNumber(), "strap:", ok)

f = pcbnew.ZONE_FILLER(b)
f.Fill(b.Zones())

zones = [z for z in b.Zones() if z.GetNetCode() == agnd]

def fillat(lay, pt):
    return any(z.HitTestFilledArea(lay, pt, 0) for z in zones
               if lay in z.GetLayerSet().Seq())

gvias = [t.GetPosition() for t in b.GetTracks()
         if t.GetClass() == "PCB_VIA" and t.GetNetCode() == agnd]
obst_t = [t for t in b.GetTracks() if t.GetNetCode() != agnd]

def clear(v, margin):
    for t in obst_t:
        if t.HitTest(v, margin):
            return False
    for pad in obst_p:
        if pad.HitTest(v, margin):
            return False
    for gv in gvias:
        if abs(gv.x - v.x) < mm(1.2) and abs(gv.y - v.y) < mm(1.2):
            return False
    return True

added = 0
x = mm(32)
while x < mm(188):
    y = mm(32)
    while y < mm(103):
        pt = pcbnew.VECTOR2I(x, y)
        if fillat(pcbnew.F_Cu, pt) and fillat(pcbnew.B_Cu, pt) and clear(pt, mm(0.7)):
            v = pcbnew.PCB_VIA(b)
            v.SetPosition(pt); v.SetDrill(mm(0.4)); v.SetWidth(mm(0.8))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNetCode(agnd)
            b.Add(v); gvias.append(pt); added += 1
        y += mm(8)
    x += mm(8)
print("grid vias added:", added)
f = pcbnew.ZONE_FILLER(b)
f.Fill(b.Zones())
pcbnew.SaveBoard(P, b)
print("saved")
