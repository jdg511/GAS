"""Find the disconnected fragments of a net and route between the closest pair of fragment points using handroute.py."""
import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym

PCB, NET, DST = sys.argv[1], sys.argv[2], sys.argv[3]
t = parse(open(PCB).read())[0]

def rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)

nodes = []   # (x, y, layers:set, kind)
edges = []
def add(x, y, layers, kind):
    nodes.append((round(x, 3), round(y, 3), layers, kind)); return len(nodes) - 1

for s in find_all(t, "segment"):
    if find(s, "net")[1] != NET: continue
    a, b = find(s, "start"), find(s, "end"); L = find(s, "layer")[1]
    i = add(float(a[1]), float(a[2]), {L}, "seg"); j = add(float(b[1]), float(b[2]), {L}, "seg"); edges.append((i, j))
for v in find_all(t, "via"):
    if find(v, "net")[1] != NET: continue
    at = find(v, "at"); add(float(at[1]), float(at[2]), {"F.Cu", "B.Cu"}, "via")
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        n = find(p, "net")
        if not n or n[1] != NET: continue
        pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr)
        lays = [str(l) for l in find(p, "layers")[1:]]
        ls = {"F.Cu", "B.Cu"} if p[2] == "thru_hole" or any(l.startswith("*") for l in lays) else {l for l in lays if l.endswith(".Cu")}
        add(fx + rx, fy - ry, ls, "pad")

parent = list(range(len(nodes)))
def fnd(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
def uni(i, j):
    parent[fnd(i)] = fnd(j)
for i, j in edges: uni(i, j)
# coincident points on a shared layer are connected (pad centres vs track ends: allow 0.05 mm)
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        a, b = nodes[i], nodes[j]
        if abs(a[0] - b[0]) < 0.06 and abs(a[1] - b[1]) < 0.06 and (a[2] & b[2]):
            uni(i, j)
# track endpoints landing inside a pad (within 0.9 mm) count as connected
for i, a in enumerate(nodes):
    if a[3] != "pad": continue
    for j, b in enumerate(nodes):
        if b[3] == "seg" and math.hypot(a[0] - b[0], a[1] - b[1]) < 0.9 and (a[2] & b[2]):
            uni(i, j)
groups = {}
for i in range(len(nodes)):
    groups.setdefault(fnd(i), []).append(i)
comps = sorted(groups.values(), key=len, reverse=True)
print(NET, "fragments:", len(comps), [len(c) for c in comps])
if len(comps) < 2:
    sys.exit(0)
# route the closest pair between fragment 0 and each other fragment (largest first)
cur = PCB
for k in range(1, len(comps)):
    pairs = []
    for i in comps[0]:
        for j in comps[k]:
            pairs.append((math.hypot(nodes[i][0] - nodes[j][0], nodes[i][1] - nodes[j][1]), i, j))
    pairs.sort()
    # prefer pads/vias as endpoints, then track ends; try up to 12 candidates
    ok = False
    for d, i, j in pairs[:12]:
        a, b = nodes[i], nodes[j]
        la = "B.Cu" if "B.Cu" in a[2] else "F.Cu"
        lb = "B.Cu" if "B.Cu" in b[2] else "F.Cu"
        r = subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "handroute.py"), cur, DST, NET,
                            str(a[0]), str(a[1]), la, str(b[0]), str(b[1]), lb], capture_output=True, text=True)
        if "routed" in r.stdout:
            print(f"routed {a[:2]} {la} -> {b[:2]} {lb} ({d:.1f} mm): {r.stdout.strip()}")
            ok = True; break
    if not ok:
        print("NO PATH for", NET); sys.exit(1)
    cur = DST
    comps[0] = comps[0] + comps[k]
