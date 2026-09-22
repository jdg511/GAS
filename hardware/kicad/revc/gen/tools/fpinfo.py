import sys, pcbnew
F = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
for spec in sys.argv[1:]:
    lib, name = spec.split(":")
    path = r"C:\Users\Jason\GAS-build\repo\hardware\kicad\GAS_Parts.pretty" if lib == "GAS_Parts" else F + "\\" + lib + ".pretty"
    fp = pcbnew.FootprintLoad(path, name)
    print("==", spec)
    for p in fp.Pads():
        pos = p.GetPosition(); sz = p.GetSize(); dr = p.GetDrillSize()
        print(" pad", p.GetNumber(), round(pcbnew.ToMM(pos.x), 3), round(pcbnew.ToMM(pos.y), 3), "size", round(pcbnew.ToMM(sz.x), 2), round(pcbnew.ToMM(sz.y), 2), "drill", round(pcbnew.ToMM(dr.x), 2), round(pcbnew.ToMM(dr.y), 2))
    for lay in (pcbnew.F_CrtYd, pcbnew.F_Fab):
        bb = None
        for g in fp.GraphicalItems():
            if g.GetLayer() == lay:
                b = g.GetBoundingBox()
                bb = b if bb is None else bb.Merge(b) or bb
        if bb:
            print(" layer", pcbnew.LayerName(lay) if hasattr(pcbnew, "LayerName") else lay, "bbox", round(pcbnew.ToMM(bb.GetX()), 2), round(pcbnew.ToMM(bb.GetY()), 2), round(pcbnew.ToMM(bb.GetRight()), 2), round(pcbnew.ToMM(bb.GetBottom()), 2))
    for g in fp.GraphicalItems():
        if g.GetClass() == "PCB_SHAPE" and g.GetShape() == pcbnew.SHAPE_T_CIRCLE:
            c = g.GetCenter(); print(" circle layer", g.GetLayer(), round(pcbnew.ToMM(c.x), 2), round(pcbnew.ToMM(c.y), 2), "r", round(pcbnew.ToMM(g.GetRadius()), 2))
