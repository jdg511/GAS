import sys, pcbnew
for spec in sys.argv[1:]:
    lib, name = spec.split(":")
    path = r"C:\Users\Jason\GAS-build\repo\hardware\kicad\GAS_Parts.pretty" if lib == "GAS_Parts" else r"C:\Program Files\KiCad\10.0\share\kicad\footprints" + "\\" + lib + ".pretty"
    fp = pcbnew.FootprintLoad(path, name)
    print(name, "loaded" if fp else "FAILED", [ (p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x),2), round(pcbnew.ToMM(p.GetPosition().y),2)) for p in fp.Pads()] if fp else "", flush=True)
