"""Grid A* router for one net between two points on a KiCad board (2 layers, vias allowed)."""
import sys, os, math, heapq, uuid
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym

SRC, DST, NET = sys.argv[1], sys.argv[2], sys.argv[3]
ax, ay, alayer = float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
bx, by, blayer = float(sys.argv[7]), float(sys.argv[8]), sys.argv[9]
G = 0.2             # grid
W = 0.2             # track width
CLR = float(os.environ.get('CLR', '0.3'))   # clearance (design rule 0.2 + grid margin)
BCU_COST = float(os.environ.get('BCU_COST', '0'))  # extra per-step cost on B.Cu (keeps the AGND plane intact)
VIA_D, VIA_DR = 0.8, 0.4

t = parse(open(SRC).read())[0]
rect = [g for g in find_all(t, "gr_rect") if find(g, "layer")[1] == "Edge.Cuts"][0]
BX2, BY2 = float(find(rect, "end")[1]), float(find(rect, "end")[2])
NX, NY = int(BX2 / G) + 1, int(BY2 / G) + 1
layers = ["F.Cu", "B.Cu"]
blocked = [bytearray(NX * NY) for _ in layers]   # per layer
blocked_via = bytearray(NX * NY)                 # via keepout (both layers)

def idx(ix, iy): return iy * NX + ix

def mark_disc(arr, x, y, r):
    ix0, ix1 = max(0, int((x - r) / G)), min(NX - 1, int((x + r) / G) + 1)
    iy0, iy1 = max(0, int((y - r) / G)), min(NY - 1, int((y + r) / G) + 1)
    for iy in range(iy0, iy1 + 1):
        for ix in range(ix0, ix1 + 1):
            if (ix * G - x) ** 2 + (iy * G - y) ** 2 <= r * r:
                arr[idx(ix, iy)] = 1

def mark_seg(arr, x1, y1, x2, y2, r):
    L = math.hypot(x2 - x1, y2 - y1)
    n = max(1, int(L / (G / 2)))
    for i in range(n + 1):
        mark_disc(arr, x1 + (x2 - x1) * i / n, y1 + (y2 - y1) * i / n, r)

def rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)

# obstacles: everything not on NET
for s in find_all(t, "segment"):
    if find(s, "net")[1] == NET: continue
    a, b = find(s, "start"), find(s, "end"); w = float(find(s, "width")[1]); lay = find(s, "layer")[1]
    r_track = w / 2 + CLR + W / 2
    if lay in layers:
        mark_seg(blocked[layers.index(lay)], float(a[1]), float(a[2]), float(b[1]), float(b[2]), r_track)
    mark_seg(blocked_via, float(a[1]), float(a[2]), float(b[1]), float(b[2]), w / 2 + CLR + VIA_D / 2)
for v in find_all(t, "via"):
    at = find(v, "at"); x, y = float(at[1]), float(at[2]); sz = float(find(v, "size")[1])
    if find(v, "net")[1] == NET:
        mark_disc(blocked_via, x, y, 0.9)
        continue
    for L in range(2):
        mark_disc(blocked[L], x, y, sz / 2 + CLR + W / 2)
    mark_disc(blocked_via, x, y, sz / 2 + CLR + VIA_D / 2)
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        net = find(p, "net"); net = net[1] if net else None
        pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr)
        x, y = fx + rx, fy - ry
        sz = find(p, "size"); r = math.hypot(float(sz[1]), float(sz[2])) / 2
        plays = [str(l) for l in find(p, "layers")[1:]]
        tht = p[2] == "thru_hole" or any(l.startswith("*") for l in plays)
        if net == NET:
            if tht:
                mark_disc(blocked_via, x, y, r + 0.9)
            continue
        for L, ln in enumerate(layers):
            if tht or ln in plays or any(l.endswith(".Cu") and l.startswith("*") for l in plays):
                mark_disc(blocked[L], x, y, r + CLR + W / 2)
        mark_disc(blocked_via, x, y, r + CLR + VIA_D / 2)
through = []
for v in find_all(t, "via"):
    if find(v, "net")[1] == NET:
        at = find(v, "at"); through.append((float(at[1]), float(at[2])))
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        net = find(p, "net")
        if net and net[1] == NET and p[2] == "thru_hole":
            pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr); through.append((fx + rx, fy - ry))
def is_through(x, y):
    return any(math.hypot(x - tx, y - ty) < 0.3 for tx, ty in through)
# board edge keepout
for iy in range(NY):
    for ix in range(NX):
        x, y = ix * G, iy * G
        if x < 1.0 or y < 1.0 or x > BX2 - 1.0 or y > BY2 - 1.0:
            for L in range(2): blocked[L][idx(ix, iy)] = 1
            blocked_via[idx(ix, iy)] = 1

def node(x, y, lay):
    return (int(round(x / G)), int(round(y / G)), layers.index(lay))

start, goal = node(ax, ay, alayer), node(bx, by, blayer)
# free the start/goal neighbourhoods on their own layers
for (nx_, ny_, L) in (start, goal):
    blocked[L][idx(nx_, ny_)] = 0

VIA_COST = 12
def h(n):
    return math.hypot(n[0] - goal[0], n[1] - goal[1])
openq = [(h(start), 0, start, None)]
came = {start: None}
cost = {start: 0}
found = None
while openq:
    f, g, n, _ = heapq.heappop(openq)
    if n == goal:
        found = n; break
    if g > cost.get(n, 1e18): continue
    ix, iy, L = n
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        jx, jy = ix + dx, iy + dy
        if 0 <= jx < NX and 0 <= jy < NY and not blocked[L][idx(jx, jy)] and not (dx and dy and (blocked[L][idx(ix + dx, iy)] or blocked[L][idx(ix, iy + dy)])):
            m = (jx, jy, L); ng = g + math.hypot(dx, dy) * (1 + (BCU_COST if L == 1 else 0))
            if ng < cost.get(m, 1e18):
                cost[m] = ng; came[m] = n; heapq.heappush(openq, (ng + h(m), ng, m, n))
    at_through = ((ix, iy) == (start[0], start[1]) and is_through(ax, ay)) or ((ix, iy) == (goal[0], goal[1]) and is_through(bx, by))
    if not blocked_via[idx(ix, iy)] or at_through:
        m = (ix, iy, 1 - L); ng = g + (0 if at_through else VIA_COST)
        if ng < cost.get(m, 1e18) and not blocked[1 - L][idx(ix, iy)]:
            cost[m] = ng; came[m] = n; heapq.heappush(openq, (ng + h(m), ng, m, n))
if not found:
    print("NO PATH; reached", len(cost), "cells; start blocked nbrs:", sum(blocked[start[2]][idx(start[0]+dx,start[1]+dy)] for dx in (-1,0,1) for dy in (-1,0,1)), "goal blocked nbrs:", sum(blocked[goal[2]][idx(goal[0]+dx,goal[1]+dy)] for dx in (-1,0,1) for dy in (-1,0,1)), "via ok at start:", not blocked_via[idx(start[0],start[1])]); sys.exit(1)
path = []
n = found
while n:
    path.append(n); n = came[n]
path.reverse()
# compress collinear runs into segments
items = []
def xy(p):
    if (p[0], p[1]) == (start[0], start[1]): return (round(ax, 4), round(ay, 4))
    if (p[0], p[1]) == (goal[0], goal[1]): return (round(bx, 4), round(by, 4))
    return (round(p[0] * G, 3), round(p[1] * G, 3))
def seg(p, q, L):
    return [Sym("segment"), [Sym("start"), *xy(p)], [Sym("end"), *xy(q)],
            [Sym("width"), W], [Sym("layer"), layers[L]], [Sym("net"), NET], [Sym("uuid"), str(uuid.uuid4())]]
i = 0
while i < len(path) - 1:
    if path[i][2] != path[i + 1][2]:
        if ((path[i][0], path[i][1]) == (start[0], start[1]) and is_through(ax, ay)) or \
           ((path[i][0], path[i][1]) == (goal[0], goal[1]) and is_through(bx, by)):
            i += 1; continue   # layer change at a via/THT endpoint: no new via needed
        items.append([Sym("via"), [Sym("at"), *xy(path[i])], [Sym("size"), VIA_D], [Sym("drill"), VIA_DR],
                      [Sym("layers"), "F.Cu", "B.Cu"], [Sym("net"), NET], [Sym("uuid"), str(uuid.uuid4())]])
        i += 1; continue
    j = i + 1
    d0 = (path[j][0] - path[i][0], path[j][1] - path[i][1])
    while j + 1 < len(path) and path[j + 1][2] == path[i][2] and (path[j + 1][0] - path[j][0], path[j + 1][1] - path[j][1]) == d0:
        j += 1
    items.append(seg(path[i], path[j], path[i][2]))
    i = j
t.extend(items)
open(DST, "w").write(dump(t) + "\n")
print("routed with", len(items), "items, path nodes", len(path))
