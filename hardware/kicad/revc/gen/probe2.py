import re
s=open(r"C:\Program Files\KiCad\10.0\share\kicad\symbols\Relay.kicad_sym",encoding='utf8').read()
for m in re.finditer(r'\(symbol "([^"]*G6K[^"]*|[^"]*G6S[^"]*)"',s): print(m.group(1))
i=s.find('(symbol "G6K-2')
print(s[i:i+6000])
