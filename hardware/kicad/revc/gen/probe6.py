import pcbnew
fp=pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_Audio.pretty","Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal")
for g in fp.GraphicalItems():
    try:
        l=g.GetLayerName()
        if l in ("F.Fab","F.CrtYd","Dwgs.User","Cmts.User"):
            print(l, g.ShowShape(), round(pcbnew.ToMM(g.GetStart().x),2), round(pcbnew.ToMM(g.GetStart().y),2), round(pcbnew.ToMM(g.GetEnd().x),2), round(pcbnew.ToMM(g.GetEnd().y),2))
    except Exception as e: print(e)
for p in fp.Pads(): print('pad', p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x),2), round(pcbnew.ToMM(p.GetPosition().y),2), round(pcbnew.ToMM(p.GetDrillSize().x),2))
print(fp.GetLibDescription())
