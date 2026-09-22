"""Remove dangling vias/tracks listed in a kicad-cli DRC report. usage: cleanup.py board.kicad_pcb drc.rpt out.kicad_pcb"""
import sys, os, re, math
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all

PCB, RPT, DST = sys.argv[1:4]
txt = open(RPT).read()
vias, tracks = [], []
for m in re.finditer(r"\[(via_dangling|track_dangling)\][^\n]*\n[^\n]*\n\s*@\(([-\d.]+) mm, ([-\d.]+) mm\): (Via|Track) \[([^\]]+)\]", txt):
    kind, x, y, _, net = m.groups()
    (vias if kind == "via_dangling" else tracks).append((float(x), float(y), net))
t = parse(open(PCB).read())[0]
out = []; nv = nt = 0
for c in t:
    if isinstance(c, list) and c[0] == "via":
        at = find(c, "at"); x, y = float(at[1]), float(at[2]); net = find(c, "net")[1]
        if any(math.hypot(x - vx, y - vy) < 0.05 and net == vn for vx, vy, vn in vias):
            nv += 1; continue
    if isinstance(c, list) and c[0] == "segment":
        a, b = find(c, "start"), find(c, "end"); net = find(c, "net")[1]
        pts = [(float(a[1]), float(a[2])), (float(b[1]), float(b[2]))]
        if any(math.hypot(px - tx, py - ty) < 0.05 and net == tn for tx, ty, tn in tracks for px, py in pts):
            nt += 1; continue
    out.append(c)
open(DST, "w").write(dump(out) + "\n")
print("removed vias", nv, "tracks", nt, "of", len(vias), len(tracks))
