import re, pcbnew
s=open(r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Converter_DCDC.kicad_sym",encoding='utf8').read()
names=re.findall(r'\(symbol "(TEL12[^"_]*|TEL10[^"_]*)"',s); print(names)
fp=pcbnew.FootprintLoad(r"C:\Program Files\KiCad\10.0\share\kicad\footprints\Converter_DCDC.pretty","Converter_DCDC_TRACO_TEL12-xxxx_THT")
print([(p.GetNumber(), round(pcbnew.ToMM(p.GetPosition().x),2), round(pcbnew.ToMM(p.GetPosition().y),2)) for p in fp.Pads()])
print(fp.GetLibDescription(), fp.GetKeywords())
