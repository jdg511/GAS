"""Bridge disconnected AGND pour islands with vias. Input: a board saved by kicad-cli with --refill-zones (has filled_polygon)."""
import sys, os, math, uuid
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

PCB, DST = sys.argv[1], sys.argv[2]
NET = "AGND"
t = parse(open(PCB).read())[0]

def rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)

# --- islands
islands = []   # (layer, Polygon)
for z in find_all(t, "zone"):
    if find(z, "net")[1] != NET: continue
    for fp in find_all(z, "filled_polygon"):
        lay = find(fp, "layer")[1]
        pts = [(float(xy[1]), float(xy[2])) for xy in find_all(find(fp, "pts"), "xy")]
        if len(pts) >= 3:
            poly = Polygon(pts).buffer(0)
            if poly.area > 0.01:
                islands.append((lay, poly))
print("islands:", len(islands), "top:", sum(1 for l, _ in islands if l == "F.Cu"), "bottom:", sum(1 for l, _ in islands if l == "B.Cu"))

# --- conductors of the net
items = []  # (kind, x, y, layers)
for v in find_all(t, "via"):
    if find(v, "net")[1] == NET:
        at = find(v, "at"); items.append(("via", float(at[1]), float(at[2]), {"F.Cu", "B.Cu"}))
segs = []
for s in find_all(t, "segment"):
    if find(s, "net")[1] == NET:
        a, b = find(s, "start"), find(s, "end")
        segs.append(((float(a[1]), float(a[2])), (float(b[1]), float(b[2])), find(s, "layer")[1]))
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        n = find(p, "net")
        if not n or n[1] != NET: continue
        pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr)
        lays = [str(l) for l in find(p, "layers")[1:]]
        ls = {"F.Cu", "B.Cu"} if p[2] == "thru_hole" or any(l.startswith("*") for l in lays) else {l for l in lays if l.endswith(".Cu")}
        items.append(("pad", fx + rx, fy - ry, ls))

# union-find over islands + items + segment endpoints
N = len(islands) + len(items)
parent = list(range(N + 2 * len(segs)))
def fnd(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
def uni(i, j): parent[fnd(i)] = fnd(j)

def island_at(x, y, layer):
    for k, (l, poly) in enumerate(islands):
        if l == layer and poly.buffer(0.35).contains(Point(x, y)):
            return k
    return None

for idx, (kind, x, y, ls) in enumerate(items):
    for l in ls:
        k = island_at(x, y, l)
        if k is not None:
            uni(len(islands) + idx, k)
for si, (a, b, l) in enumerate(segs):
    ia, ib = N + 2 * si, N + 2 * si + 1
    uni(ia, ib)
    for (pt, node) in ((a, ia), (b, ib)):
        k = island_at(pt[0], pt[1], l)
        if k is not None: uni(node, k)
        for idx, (kind, x, y, ls) in enumerate(items):
            if l in ls and math.hypot(x - pt[0], y - pt[1]) < 0.6:
                uni(node, len(islands) + idx)
# items coincident with each other (via on a pad centre etc.)
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a, b = items[i], items[j]
        if (a[3] & b[3]) and math.hypot(a[1] - b[1], a[2] - b[2]) < 0.6:
            uni(len(islands) + i, len(islands) + j)

groups = {}
for i in range(N):
    groups.setdefault(fnd(i), []).append(i)
main = max(groups.values(), key=lambda g: sum(islands[i][1].area for i in g if i < len(islands)))
main_root = fnd(main[0])
print("groups:", len(groups))

# obstacles for via placement (everything not AGND)
obst = []
for s in find_all(t, "segment"):
    if find(s, "net")[1] == NET: continue
    a, b = find(s, "start"), find(s, "end")
    obst.append(LineString([(float(a[1]), float(a[2])), (float(b[1]), float(b[2]))]).buffer(float(find(s, "width")[1]) / 2 + 0.25 + 0.4))
for v in find_all(t, "via"):
    at = find(v, "at"); obst.append(Point(float(at[1]), float(at[2])).buffer(float(find(v, "size")[1]) / 2 + 0.25 + 0.4))
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr)
        sz = find(p, "size"); r = math.hypot(float(sz[1]), float(sz[2])) / 2
        n = find(p, "net")
        extra = 0.7 if p[2] == "thru_hole" else 0.4
        obst.append(Point(fx + rx, fy - ry).buffer(r + 0.25 + extra))
OB = unary_union(obst)

added = []
def try_bridge(g):
    """Place a via inside an island of group g that also lies in an island of another group on the other layer."""
    my_islands = [i for i in g if i < len(islands)]
    for i in my_islands:
        lay, poly = islands[i]
        other = "B.Cu" if lay == "F.Cu" else "F.Cu"
        for k, (l2, p2) in enumerate(islands):
            if l2 != other or fnd(k) == fnd(i): continue
            inter = poly.buffer(-0.5).intersection(p2.buffer(-0.5))
            if inter.is_empty: continue
            free = inter.difference(OB)
            if free.is_empty: continue
            pt = free.representative_point()
            return (pt.x, pt.y, i, k)
    return None

changed = True; rounds = 0
while changed and rounds < 20:
    changed = False; rounds += 1
    groups = {}
    for i in range(N):
        groups.setdefault(fnd(i), []).append(i)
    for root, g in list(groups.items()):
        if fnd(root) == fnd(main_root): continue
        res = try_bridge(g)
        if res:
            x, y, i, k = res
            added.append((x, y)); uni(i, k); changed = True
            OB = OB.union(Point(x, y).buffer(0.4 + 0.25 + 0.4))
groups = {}
for i in range(N):
    groups.setdefault(fnd(i), []).append(i)
left = [g for r, g in groups.items() if fnd(r) != fnd(main_root)]
print("bridging vias added:", len(added), "unbridged groups left:", len(left))
for g in left[:10]:
    desc = [("island", islands[i][0], round(islands[i][1].area, 1)) if i < len(islands) else items[i - len(islands)][:3] for i in g][:4]
    print("  ", desc)
import json
iso = []
for g in left:
    vias_g = [items[i - len(islands)] for i in g if i >= len(islands) and items[i - len(islands)][0] == "via"]
    pads_g = [items[i - len(islands)] for i in g if i >= len(islands) and items[i - len(islands)][0] == "pad"]
    src = vias_g[0] if vias_g else pads_g[0]
    iso.append({"x": src[1], "y": src[2], "layer": "B.Cu" if "B.Cu" in src[3] else "F.Cu"})
main_vias = [items[i - len(islands)] for i in groups[fnd(main_root)] if i >= len(islands) and items[i - len(islands)][0] == "via"]
for o in iso:
    best = min(main_vias, key=lambda v: math.hypot(v[1] - o["x"], v[2] - o["y"]))
    o["tx"], o["ty"] = best[1], best[2]
json.dump(iso, open(DST + ".iso.json", "w"))
for (x, y) in added:
    t.append([Sym("via"), [Sym("at"), round(x, 3), round(y, 3)], [Sym("size"), 0.8], [Sym("drill"), 0.4],
              [Sym("layers"), "F.Cu", "B.Cu"], [Sym("net"), NET], [Sym("uuid"), str(uuid.uuid4())]])
open(DST, "w").write(dump(t) + "\n")
