s=open(r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Relay.kicad_sym",encoding='utf8').read()
i=s.find('(symbol "G6K-2"'); j=s.find('(symbol "G6K-2_1_1"',i)
import re
blk=s[i:j]
for m in re.finditer(r'\((polyline|rectangle|circle|arc)(.*?)\(stroke',blk,re.S):
    print(m.group(1), ' '.join(re.findall(r'\(xy ([-\d. ]+)\)|\(start ([-\d. ]+)\)|\(end ([-\d. ]+)\)|\(center ([-\d. ]+)\)',m.group(2)).__str__().split())[:300])
