"""Rip up non-AGND tracks around an isolated AGND via, route the via to the main AGND, then repair ripped nets."""
import sys, os, math, json, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym

PCB, ISO, DST = sys.argv[1], sys.argv[2], sys.argv[3]
R = float(sys.argv[4]) if len(sys.argv) > 4 else 2.0
iso = json.load(open(ISO))
HR = os.path.join(os.path.dirname(__file__), "handroute.py")
FX = os.path.join(os.path.dirname(__file__), "fixnet.py")

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0: return math.hypot(px - x1, py - y1)
    u = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + u * dx), py - (y1 + u * dy))

cur = PCB
step = 0
for o in iso:
    t = parse(open(cur).read())[0]
    ripped = set(); out = []
    for c in t:
        if isinstance(c, list) and c[0] == "segment" and find(c, "net")[1] != "AGND":
            a, b = find(c, "start"), find(c, "end")
            if seg_dist(o["x"], o["y"], float(a[1]), float(a[2]), float(b[1]), float(b[2])) < R:
                ripped.add(find(c, "net")[1]); continue
        if isinstance(c, list) and c[0] == "via" and find(c, "net")[1] != "AGND":
            at = find(c, "at")
            if math.hypot(float(at[1]) - o["x"], float(at[2]) - o["y"]) < R:
                ripped.add(find(c, "net")[1]); continue
        out.append(c)
    tmp = f"/opt/kicad10/work/rip_{step}.kicad_pcb"; step += 1
    open(tmp, "w").write(dump(out) + "\n")
    print("island at", o["x"], o["y"], "ripped nets:", sorted(ripped))
    dst = f"/opt/kicad10/work/rip_{step}.kicad_pcb"; step += 1
    r = subprocess.run(["python3", HR, tmp, dst, "AGND", str(o["x"]), str(o["y"]), o["layer"], str(o["tx"]), str(o["ty"]), "B.Cu"], capture_output=True, text=True)
    print("  AGND:", r.stdout.strip())
    if "routed" not in r.stdout:
        print("  giving up on this island"); continue
    cur = dst
    for net in sorted(ripped):
        dst = f"/opt/kicad10/work/rip_{step}.kicad_pcb"; step += 1
        r = subprocess.run(["python3", FX, cur, net, dst], capture_output=True, text=True)
        print("  ", r.stdout.strip().replace("\n", " | "))
        if os.path.exists(dst):
            cur = dst
import shutil; shutil.copy(cur, DST); print("->", DST)
