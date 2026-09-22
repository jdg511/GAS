import sys, pcbnew
print(sys.version, pcbnew.Version())
fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Relay_SMD.pretty", "Relay_DPDT_Omron_G6K-2F-Y")
print(fp.GetReference(), [ (p.GetNumber(), pcbnew.ToMM(p.GetPosition().x), pcbnew.ToMM(p.GetPosition().y)) for p in fp.Pads()])
fp = pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Connector_Audio.pretty", "Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal")
print([ (p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x),2), round(pcbnew.ToMM(p.GetPosition().y),2)) for p in fp.Pads()])
bb=fp.GetBoundingBox(False); print('bbox', pcbnew.ToMM(bb.GetX()),pcbnew.ToMM(bb.GetY()),pcbnew.ToMM(bb.GetWidth()),pcbnew.ToMM(bb.GetHeight()))
import os
for d in os.listdir(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Converter_DCDC.pretty"):
    if 'TRACO' in d.upper(): print(d)
