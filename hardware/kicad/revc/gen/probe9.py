import re
for lib in ("Device","Transistor_BJT"):
    s=open(rf"C:\Program Files\KiCad\10.0\share\kicad\symbols\{lib}.kicad_sym",encoding='utf8').read()
    print(lib, sorted(set(re.findall(r'\(symbol "(Q_[NP]PN_[A-Z]+)"',s))))
