"""Add AGND stitching vias on a grid, avoiding tracks/pads/vias, then let DRC refill."""
import sys, os, math, uuid
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym

SRC, DST = sys.argv[1], sys.argv[2]
PITCH = float(sys.argv[3]) if len(sys.argv) > 3 else 7.0
t = parse(open(SRC).read())[0]

# board outline
rect = [g for g in find_all(t, "gr_rect") if find(g, "layer")[1] == "Edge.Cuts"][0]
bx1, by1 = float(find(rect, "start")[1]), float(find(rect, "start")[2])
bx2, by2 = float(find(rect, "end")[1]), float(find(rect, "end")[2])

segs = []
for s in find_all(t, "segment"):
    a, b = find(s, "start"), find(s, "end")
    segs.append((float(a[1]), float(a[2]), float(b[1]), float(b[2]), float(find(s, "width")[1]), find(s, "net")[1]))
vias = [(float(find(v, "at")[1]), float(find(v, "at")[2]), float(find(v, "size")[1]), find(v, "net")[1]) for v in find_all(t, "via")]

def rot(px, py, ang):
    a = math.radians(ang)
    return px * math.cos(a) - py * math.sin(a), px * math.sin(a) + py * math.cos(a)

pads = []  # (x, y, radius, net, tht)
for f in find_all(t, "footprint"):
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        pa = find(p, "at"); px, py = float(pa[1]), float(pa[2])
        rx, ry = rot(px, py, -fr) if False else rot(px, py, fr)
        # KiCad footprint rotation: pad offsets rotate by footprint angle (CCW positive, y down -> use -angle)
        rx, ry = rot(px, -py, fr)
        ax, ay = fx + rx, fy - ry
        sz = find(p, "size"); r = max(float(sz[1]), float(sz[2])) / 2
        net = find(p, "net"); net = net[1] if net else None
        pads.append((ax, ay, r, net, p[2] == "thru_hole"))
    # also keep out courtyard? skip; pads suffice with margins

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - x1, py - y1)
    u = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + u * dx), py - (y1 + u * dy))

VIA_D, VIA_DRILL, CLR = 0.8, 0.4, 0.25
added = 0
new = []
y = by1 + 3.5
row = 0
while y < by2 - 3:
    x = bx1 + 3.5 + (PITCH / 2 if row % 2 else 0)
    while x < bx2 - 3:
        ok = True
        for (x1, y1, x2, y2, w, net) in segs:
            if seg_dist(x, y, x1, y1, x2, y2) < VIA_D / 2 + w / 2 + CLR + 0.1:
                ok = False; break
        if ok:
            for (vx, vy, vs, net) in vias:
                if math.hypot(x - vx, y - vy) < VIA_D / 2 + vs / 2 + CLR + 0.1:
                    ok = False; break
        if ok:
            for (px, py, r, net, tht) in pads:
                margin = VIA_D / 2 + r + CLR + (0.6 if tht else 0.3)
                if math.hypot(x - px, y - py) < margin:
                    ok = False; break
        if ok:
            new.append([Sym("via"), [Sym("at"), round(x, 3), round(y, 3)], [Sym("size"), VIA_D], [Sym("drill"), VIA_DRILL],
                        [Sym("layers"), "F.Cu", "B.Cu"], [Sym("net"), "AGND"], [Sym("uuid"), str(uuid.uuid4())]])
            added += 1
        x += PITCH
    y += PITCH * 0.866
    row += 1
t.extend(new)
# --- per-pad vias next to every top-side SMD AGND pad
allvias = vias + [(float(find(v, "at")[1]), float(find(v, "at")[2]), VIA_D, "AGND") for v in new]
def free(x, y, extra_pads):
    if not (bx1 + 1.5 < x < bx2 - 1.5 and by1 + 1.5 < y < by2 - 1.5):
        return False
    for (x1, y1, x2, y2, w, net) in segs:
        if seg_dist(x, y, x1, y1, x2, y2) < VIA_D / 2 + w / 2 + CLR + 0.05:
            return False
    for (vx, vy, vs, net) in allvias:
        if math.hypot(x - vx, y - vy) < VIA_D / 2 + vs / 2 + CLR + 0.05:
            return False
    for (px, py, r, net, tht) in pads:
        if (px, py) in extra_pads:
            continue
        m = VIA_D / 2 + r + CLR + (0.4 if tht else 0.15)
        if math.hypot(x - px, y - py) < m:
            return False
    return True
padvias = 0
for f in (find_all(t, "footprint") if os.environ.get('PAD_VIAS','1')=='1' else []):
    if find(f, "layer")[1] != "F.Cu":
        continue
    at = find(f, "at"); fx, fy = float(at[1]), float(at[2]); fr = float(at[3]) if len(at) > 3 else 0.0
    for p in find_all(f, "pad"):
        net = find(p, "net")
        if not net or net[1] != "AGND" or p[2] == "thru_hole":
            continue
        pa = find(p, "at"); rx, ry = rot(float(pa[1]), -float(pa[2]), fr)
        ax, ay = fx + rx, fy - ry
        sz = find(p, "size"); r = max(float(sz[1]), float(sz[2])) / 2
        d = r + 0.35
        placed = False
        for k in range(24):
            for dd in (d, d + 0.4, d + 0.8, d + 1.3):
                ang = math.radians(k * 15)
                x, y = ax + dd * math.cos(ang), ay + dd * math.sin(ang)
                if free(x, y, {(ax, ay)}):
                    v = [Sym("via"), [Sym("at"), round(x, 3), round(y, 3)], [Sym("size"), VIA_D], [Sym("drill"), VIA_DRILL],
                         [Sym("layers"), "F.Cu", "B.Cu"], [Sym("net"), "AGND"], [Sym("uuid"), str(uuid.uuid4())]]
                    t.append(v); allvias.append((x, y, VIA_D, "AGND")); padvias += 1; placed = True
                    break
            if placed:
                break
        if not placed:
            print('NO VIA SPOT for', [q[2] for q in find_all(f,'property') if q[1]=='Reference'][0], p[1], round(ax,2), round(ay,2))
open(DST, "w").write(dump(t) + "\n")
print("stitching vias added:", added, "pad vias:", padvias)
