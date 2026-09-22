"""Import a Specctra SES (from a KiCad-exported DSN) into a .kicad_pcb: adds segments and vias."""
import sys, os, uuid, re
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym

PCB, SES, DST = sys.argv[1], sys.argv[2], sys.argv[3]
t = parse(open(PCB).read())[0]
s = parse(open(SES).read())[0]
res = find(find(s, "placement"), "resolution")
scale = 1.0 / (float(res[2]) * 1000.0)   # units per um -> mm
routes = find(s, "routes")
netout = find(routes, "network_out")
# drop existing routing
t = [c for c in t if not (isinstance(c, list) and c[0] in ("segment", "via"))]
nseg = nvia = 0
for net in find_all(netout, "net"):
    name = str(net[1])
    for w in find_all(net, "wire"):
        path = find(w, "path")
        layer = str(path[1]); width = float(path[2]) * scale
        coords = [float(v) for v in path[3:]]
        pts = [(coords[i] * scale, -coords[i + 1] * scale) for i in range(0, len(coords), 2)]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            t.append([Sym("segment"), [Sym("start"), round(a[0], 4), round(a[1], 4)], [Sym("end"), round(b[0], 4), round(b[1], 4)],
                      [Sym("width"), round(width, 3)], [Sym("layer"), layer], [Sym("net"), name], [Sym("uuid"), str(uuid.uuid4())]])
            nseg += 1
    for v in find_all(net, "via"):
        m = re.match(r"Via\[\d+-\d+\]_(\d+):(\d+)_um", str(v[1]))
        size, drill = float(m.group(1)) / 1000, float(m.group(2)) / 1000
        x, y = float(v[2]) * scale, -float(v[3]) * scale
        t.append([Sym("via"), [Sym("at"), round(x, 4), round(y, 4)], [Sym("size"), size], [Sym("drill"), drill],
                  [Sym("layers"), "F.Cu", "B.Cu"], [Sym("net"), name], [Sym("uuid"), str(uuid.uuid4())]])
        nvia += 1
open(DST, "w").write(dump(t) + "\n")
print("segments", nseg, "vias", nvia)
