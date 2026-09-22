"""Rip segments/vias of the given nets within radius R of (x,y). usage: rip_nets.py src dst x y R NET [NET...]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all

SRC, DST = sys.argv[1], sys.argv[2]
X, Y, R = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
NETS = set(sys.argv[6:])

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0: return math.hypot(px - x1, py - y1)
    u = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + u * dx), py - (y1 + u * dy))

t = parse(open(SRC).read())[0]
out = []; n = 0
for c in t:
    if isinstance(c, list) and c[0] == "segment" and find(c, "net")[1] in NETS:
        a, b = find(c, "start"), find(c, "end")
        if seg_dist(X, Y, float(a[1]), float(a[2]), float(b[1]), float(b[2])) < R:
            n += 1; continue
    if isinstance(c, list) and c[0] == "via" and find(c, "net")[1] in NETS:
        at = find(c, "at")
        if math.hypot(float(at[1]) - X, float(at[2]) - Y) < R:
            n += 1; continue
    out.append(c)
open(DST, "w").write(dump(out) + "\n")
print("ripped", n, "items")
