import pcbnew
F=r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
G=r"C:\Users\Jason\GAS-build\repo\hardware\kicad\GAS_Parts.pretty"
def show(lib,name):
    fp=pcbnew.FootprintLoad(lib,name)
    bb=fp.GetCourtyard(pcbnew.F_CrtYd).BBox() if fp.GetCourtyard(pcbnew.F_CrtYd).OutlineCount() else fp.GetBoundingBox(False)
    print(name, 'crtyd', round(pcbnew.ToMM(bb.GetWidth()),2), round(pcbnew.ToMM(bb.GetHeight()),2), [(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x),2), round(pcbnew.ToMM(p.GetPosition().y),2), p.GetAttribute()) for p in fp.Pads()])
show(G,"Jack_RCA_SameSky_RCJ-041_Horizontal")
show(F+r"\Package_TO_SOT_SMD.pretty","SOT-223-3_TabPin2")
show(F+r"\Relay_SMD.pretty","Relay_DPDT_Omron_G6K-2F-Y")
show(F+r"\Connector_Audio.pretty","Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal")
show(F+r"\Converter_DCDC.pretty","Converter_DCDC_RECOM_R-78E-0.5_THT")
show(F+r"\Potentiometer_SMD.pretty","Potentiometer_Bourns_3314J_Vertical")
show(F+r"\Capacitor_THT.pretty","C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2")
show(F+r"\Package_SIP.pretty","SIP-8_19x3mm_P2.54mm")
