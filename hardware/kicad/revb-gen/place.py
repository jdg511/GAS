"""Place footprints in circuit-board.kicad_pcb by functional block, add outline, holes, AGND zones."""
import sys, os, math, collections
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym
import design

SRC = sys.argv[1]
DST = sys.argv[2]

t = parse(open(SRC).read())[0]


def fp_ref(f):
    for p in find_all(f, "property"):
        if p[1] == "Reference":
            return p[2]
    return None

fps = {fp_ref(f): f for f in find_all(t, "footprint")}
print("footprints:", len(fps))

def crtyd(f):
    xs, ys = [], []
    for it in f:
        if not isinstance(it, list):
            continue
        if it[0] in ("fp_line", "fp_rect"):
            lay = find(it, "layer")
            if lay and lay[1] in ("F.CrtYd", "B.CrtYd"):
                for k in ("start", "end"):
                    p = find(it, k)
                    xs.append(float(p[1])); ys.append(float(p[2]))
        if it[0] == "fp_poly":
            lay = find(it, "layer")
            if lay and lay[1] in ("F.CrtYd",):
                for xy in find_all(find(it, "pts"), "xy"):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
    if not xs:
        for p in find_all(f, "pad"):
            at = find(p, "at"); sz = find(p, "size")
            xs += [float(at[1]) - float(sz[1]) / 2, float(at[1]) + float(sz[1]) / 2]
            ys += [float(at[2]) - float(sz[2]) / 2, float(at[2]) + float(sz[2]) / 2]
    return min(xs), min(ys), max(xs), max(ys)

GAP = 2.6   # extra spacing between courtyards (mm)

def shelf_pack(refs, width, rot=0):
    """Pack refs (already sorted) into shelves of given width. Returns dict ref->(x,y,rot) relative and (w,h)."""
    pos = {}
    x = y = 0.0
    shelf_h = 0.0
    maxw = 0.0
    for r in refs:
        x1, y1, x2, y2 = crtyd(fps[r])
        w = x2 - x1 + GAP
        h = y2 - y1 + GAP
        if rot in (90, 270):
            w, h = h, w
        if x + w > width and x > 0:
            y += shelf_h
            x = 0.0
            shelf_h = 0.0
        # footprint origin offset so courtyard min corner sits at (x,y)
        if rot == 0:
            ox, oy = -x1 + GAP / 2, -y1 + GAP / 2
        elif rot == 90:   # KiCad rotates CCW: (x,y)->(y,-x)
            ox, oy = -(-y2) + GAP / 2, -x1 + GAP / 2
        elif rot == 180:
            ox, oy = x2 + GAP / 2, y2 + GAP / 2
        else:
            ox, oy = y2 + GAP / 2, x2 + GAP / 2
        pos[r] = (x + ox, y + oy, rot)
        x += w
        shelf_h = max(shelf_h, h)
        maxw = max(maxw, x)
    return pos, (maxw, y + shelf_h)

def order(refs):
    """ICs first, then trimmers/relays, THT caps, then small parts, sorted by ref."""
    def key(r):
        pri = 0 if r.startswith("U") else 1 if r.startswith(("K", "VT", "RV", "Q")) else 2 if fps[r][1].startswith("Capacitor_THT") else 3
        num = int("".join(ch for ch in r if ch.isdigit()) or 0)
        return (pri, num)
    return sorted(refs, key=key)

# ---------------------------------------------------------------- block membership
by_block = collections.OrderedDict()
for p in design.parts:
    if p["ref"].startswith("#") or p["ref"].startswith("H"):
        continue
    by_block.setdefault(p["block"], []).append(p["ref"])
blocks = list(by_block.keys())
for b in blocks:
    print(f"{len(by_block[b]):4d}  {b}")

# Layout regions (mm). Board origin at (0,0) top-left. Width fixed, rows computed.
BOARD_W = 190.0
MARGIN = 6.0
placed = {}

def place_region(refs, x0, y0, width, rot=0):
    pos, (w, h) = shelf_pack(order(refs), width, rot)
    for r, (x, y, rr) in pos.items():
        placed[r] = (x0 + x, y0 + y, rr)
    return w, h

connectors = by_block.pop("Connectors")
power = by_block.pop("Power / +9VC / VBIAS")
mainL = by_block.pop("Main path L: Drive, HPF, pad, LPF, output")
mainR = by_block.pop("Main path R: Drive, HPF, pad, LPF, output")
tubeL = by_block.pop("Tube L (J201 stage) + Tape L (record EQ, diff pair, repro EQ) on +9VC")
tubeR = by_block.pop("Tube R (J201 stage) + Tape R (record EQ, diff pair, repro EQ) on +9VC")
tsL = by_block.pop("Tube Screamer L: Rf 51k / Rg 4.7k, 1N4148 pair, +9VC")
tsR = by_block.pop("Tube Screamer R: Rf 51k / Rg 4.7k, 1N4148 pair, +9VC")
opto = by_block.pop("Opto compressor: VTL5C3 shunt divider per channel, linked feed-forward sidechain")
fet = by_block.pop("FET compressor: 2N5457 shunt divider per channel, x11 make-up, linked feedback sidechain")
vca = by_block.pop("VCA limiter: THAT2180 x2, THAT2252 RMS detector (feedback), ratio 10:1")
relays = by_block.pop("Mode select: 7 x TQ2-5V relays, one energised per rotary position")
assert not by_block, list(by_block)

# Row 0: connectors along the top edge
y = MARGIN
# P3 power (VH) left, P1 in, P2 out, then P4, P5 (16-pin XH, ~41 mm long) on the top edge
xcur = MARGIN + 6
for ref in ["P3", "P1", "P2", "P4", "P5"]:
    x1, y1, x2, y2 = crtyd(fps[ref])
    placed[ref] = (xcur - x1, y - y1, 0)
    xcur += (x2 - x1) + 4.0
row0_h = 12.0
y += row0_h + 2

# Row 1: power | main L | main R
colw = (BOARD_W - 2 * MARGIN) / 3
w, h1 = place_region(power, MARGIN, y, colw - 2)
w, h2 = place_region(mainL, MARGIN + colw, y, colw - 2)
w, h3 = place_region(mainR, MARGIN + 2 * colw, y, colw - 2)
y += max(h1, h2, h3) + 3

# Row 2: tube/tape L | tube/tape R | TS L+R
w, h1 = place_region(tubeL, MARGIN, y, colw - 2)
w, h2 = place_region(tubeR, MARGIN + colw, y, colw - 2)
w, h3 = place_region(tsL + tsR + opto, MARGIN + 2 * colw, y, colw - 2)
y += max(h1, h2, h3) + 3

# Row 3: opto | fet | vca
tot = BOARD_W - 2 * MARGIN
w2, w3 = tot * 0.40, tot * 0.60
h1 = 0
w, h2 = place_region(fet, MARGIN, y, w2 - 2)
w, h3 = place_region(vca, MARGIN + w2, y, w3 - 2)
y += max(h1, h2, h3) + 3

# Row 4: relays across the bottom
w, h = place_region(relays, MARGIN, y, BOARD_W - 2 * MARGIN)
y += h + 2
BOARD_H = math.ceil((y + MARGIN) / 5) * 5
print("board:", BOARD_W, "x", BOARD_H)

# mounting holes
holes = {"H1": (4, 4), "H2": (BOARD_W - 4, 4), "H3": (4, BOARD_H - 4), "H4": (BOARD_W - 4, BOARD_H - 4)}
for r, (x, yy) in holes.items():
    placed[r] = (x, yy, 0)

# apply
for r, (x, yy, rot) in placed.items():
    f = fps[r]
    at = find(f, "at")
    at[1:] = [round(x, 3), round(yy, 3)] + ([rot] if rot else [])
    if rot:
        # rotate pads/text too? KiCad stores pad positions relative and unrotated; footprint 'at' rotation applies. Text items carry own angle; fine.
        pass
missing = [r for r in fps if r not in placed]
print("unplaced:", missing)

# outline
def gr_rect(x1, y1, x2, y2, layer, width):
    return [Sym("gr_rect"), [Sym("start"), x1, y1], [Sym("end"), x2, y2],
            [Sym("stroke"), [Sym("width"), width], [Sym("type"), Sym("default")]], [Sym("fill"), Sym("no")],
            [Sym("layer"), layer], [Sym("uuid"), "b0a7d000-0000-4000-8000-000000000011"]]
t.append(gr_rect(0, 0, BOARD_W, BOARD_H, "Edge.Cuts", 0.1))

# zones: AGND on both copper layers
def zone(layer, name):
    pts = [[Sym("xy"), 0.5, 0.5], [Sym("xy"), BOARD_W - 0.5, 0.5], [Sym("xy"), BOARD_W - 0.5, BOARD_H - 0.5], [Sym("xy"), 0.5, BOARD_H - 0.5]]
    return [Sym("zone"), [Sym("net"), "AGND"], [Sym("layer"), layer], [Sym("uuid"), "c0a7d000-0000-4000-8000-0000000000" + ("01" if layer == "F.Cu" else "02")],
            [Sym("name"), name], [Sym("hatch"), Sym("edge"), 0.5],
            [Sym("connect_pads"), Sym("yes"), [Sym("clearance"), 0.3]], [Sym("min_thickness"), 0.25],
            [Sym("fill"), Sym("yes"), [Sym("thermal_gap"), 0.5], [Sym("thermal_bridge_width"), 0.5], [Sym("island_removal_mode"), 0]],
            [Sym("polygon"), [Sym("pts")] + pts]]
if os.environ.get("NO_ZONES") != "1":
    t.append(zone("F.Cu", "AGND_top"))
    t.append(zone("B.Cu", "AGND_bottom"))

# title block
tb = find(t, "title_block")
tb[:] = [Sym("title_block"), [Sym("title"), "GAS Rev B - Circuit Board"], [Sym("date"), "2026-09-13"], [Sym("rev"), "B"],
         [Sym("company"), "Illicit Apothecary"], [Sym("comment"), 1, "Drive, HPF, 7-mode circuit (Clean/Tube/Tape/TS/Opto/FET/VCA), LPF"],
         [Sym("comment"), 2, "Replaces Rev A filter-clipper. 2-layer, AGND pours both sides."]]

# silkscreen text
t.append([Sym("gr_text"), "Illicit Apothecary  GAS  Rev B  circuit-board", [Sym("at"), BOARD_W / 2, BOARD_H - 2.5, 0], [Sym("layer"), "F.SilkS"],
          [Sym("uuid"), "d0a7d000-0000-4000-8000-000000000001"],
          [Sym("effects"), [Sym("font"), [Sym("size"), 1.5, 1.5], [Sym("thickness"), 0.2]]]])
open(DST, "w").write(dump(t) + "\n")
print("written", DST)
