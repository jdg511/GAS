#!/usr/bin/env python3
"""GAS Rev C service endcap on a 6 in DWV PVC cap: layout, fit check, drawings.

Coordinates: origin at the face centre, +X right, +Y up, mm, viewed from outside.
Usable face = the cap's socket bore = 6 in pipe OD = 168.3 mm (Charlotte 6 in
DWV cap 00116). Everything (hole, counterbore, flange, knob, nut) must stay inside
that circle with a margin, because the cap's inner corner has a fillet and the
counterbores need wall.
"""
import csv, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
import ezdxf

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
FACE_D = 168.3                 # mm, cap socket bore = pipe OD
R = FACE_D / 2.0
WALL_MARGIN = 3.0              # mm, minimum from any envelope to the bore

# Part envelopes (datasheet / catalogue values, see rev-c-endcap-fit-check.md)
PARTS = {
    # kind: dict(hole=Ø drill, cbore=Ø counterbore from inside, env=(w,h) rectangular
    #            envelope centred on the hole (flange or nut or body), knob=Ø on the face)
    "combo":  dict(hole=24.0, cbore=None, env=(27.0, 30.0), knob=None,
                   mpn="Neutrik NCJ6FI-V (XLR/TRS combo, vertical PCB, jack deck)",
                   note="D-cutout: 24.0 hole + 2x 3.2 at (-10,+11.5)/(+10,-11.5); flange 27x30; 25.4 deep + pins; panel max 7 mm"),

    "pot_q":  dict(skin=3.0, hole=7.5, cbore=18.0, env=(11.0, 11.0), knob=16.0,
                   mpn="Bourns PTD904-2015K-B503 (4-gang 50k lin, M7x0.75, hand-wired)",
                   note="body 9.5 x 11, 17.2 deep, 6 mm shaft; counterbore to 3 mm; knob 16 mm"),
    "pot_d":  dict(skin=1.5, hole=9.5, cbore=14.0, env=(12.5, 12.5), knob=16.0,
                   mpn="Alps RK09L1240015 dual 10k lin, M9x0.75 x 5 (control deck)",
                   note="leave 1.5 mm skin (control deck at 15.0 mm); 6 mm flatted shaft; knob 16 mm"),
    "toggle": dict(skin=4.0, hole=6.5, cbore=14.0, env=(11.5, 11.5), knob=None,
                   mpn="Dailywell 1M series PC pins (C&K 7000 style), 1/4-40 x 8.89 bushing (control deck)",
                   note="leave 2.1 mm skin; bat 10.4; nut about 11.5 across"),
    "dc":     dict(skin=3.7, hole=8.2, cbore=14.0, env=(12.5, 12.5), knob=None,
                   mpn="Same Sky PJ-064B (5.5/2.5 mm, 5/16-32 x 5.7 bushing, control deck)",
                   note="leave 3.7 mm skin, nut only (10.8 mm), no washer"),
    "fsjack": dict(skin=5.0, hole=6.4, cbore=16.0, env=(10.5, 12.2), knob=None,
                   mpn="XKB PJ-301C 3.5 mm TRS, vertical PCB mount, M6 bushing (control deck, LCSC C692433)",
                   note="counterbore to a 5.0 mm skin so the bushing nose is a slip fit in the 6.4 hole and the "
                        "jack mouth sits flush with the face; body 8.5 x 10.2, 14.1 mm tall; PCB soldered, no nut "
                        "needed. Check the thread length on the first sample: if it is 5.5 mm or more, thin the "
                        "skin to 3 mm and fit the supplied M6 nut."),
}

# ref, kind, label, x, y
ITEMS = [
    ("J1", "combo",  "IN L",              -49.5, 15.0),
    ("J2", "combo",  "IN R",              -16.5, 15.0),
    ("J3", "combo",  "OUT L",              16.5, 15.0),
    ("J4", "combo",  "OUT R",              49.5, 15.0),
    ("J5", "dc",     "24-30 VDC",           0.0, 66.0),
    ("J6", "fsjack", "FOOTSWITCH",           0.0, -14.0),
    ("S1", "toggle", "SOURCE Mono/Stereo/MEGA", -51.0, 43.0),
    ("S5", "toggle", "TUBE",                    -34.0, 43.0),
    ("S6", "toggle", "DIRT",                    -17.0, 43.0),
    ("S7", "toggle", "TAPE",                      0.0, 43.0),
    ("S2", "toggle", "EXT TANKS Ser/Off/Par",    17.0, 43.0),
    ("S3", "toggle", "FB DYN Comp/Off/Limit",    34.0, 43.0),
    ("S4", "toggle", "FB PHASE",                 51.0, 43.0),
    ("VR1", "pot_d", "VOL",                  -59.20, -21.55),
    ("VR2", "pot_q",  "HPF",                 -36.14, -51.60),
    ("VR3", "pot_d", "GAIN",                   0.0, -63.0),
    ("VR4", "pot_q",  "LPF",                  36.14, -51.60),
    ("VR5", "pot_d", "OUTPUT",                59.20, -21.55),
    ("VR6", "pot_d",  "EXT MIX",            -25.5, -23.5),
    ("VR7", "pot_d",  "FEEDBACK",             0.0, -37.0),
    ("VR8", "pot_d",  "WET/DRY",             25.5, -23.5),
]

def env_radius(kind):
    p = PARTS[kind]
    r = 0.0
    if p["knob"]: r = max(r, p["knob"] / 2)
    if p["cbore"]: r = max(r, p["cbore"] / 2)
    w, h = p["env"]
    r = max(r, math.hypot(w / 2, h / 2))
    return r

def face_radius(kind):
    """Radius of the visible/finger envelope on the face (knob, nut, flange)."""
    p = PARTS[kind]
    if p["knob"]: return p["knob"] / 2
    w, h = p["env"]
    return max(w, h) / 2

results = []
ok = True
for ref, kind, label, x, y in ITEMS:
    r = math.hypot(x, y)
    er = env_radius(kind)
    wall = R - (r + er)
    p = PARTS[kind]
    results.append((ref, kind, label, x, y, r, er, wall))
    if wall < WALL_MARGIN:
        ok = False
        print(f"FAIL wall: {ref} {label}: envelope reaches {r+er:.1f} of {R:.1f} (margin {wall:.1f})")

# pairwise gaps on the face (knob to knob, flange to nut, etc.), rectangles for combos
def gap(a, b):
    (ra, ka, la, xa, ya, *_), (rb, kb, lb, xb, yb, *_) = a, b
    d = math.hypot(xa - xb, ya - yb)
    if ka == "combo" and kb == "combo":
        return abs(xa - xb) - 27.0 if abs(ya - yb) < 30 else abs(ya - yb) - 30.0
    if ka == "combo" or kb == "combo":
        # rectangle (27x30) to circle
        (xc, yc, kc), (xr, yr) = ((xa, ya, ka), (xb, yb)) if kb == "combo" else ((xb, yb, kb), (xa, ya))
        dx = max(abs(xc - xr) - 13.5, 0); dy = max(abs(yc - yr) - 15.0, 0)
        return math.hypot(dx, dy) - face_radius(kc)
    return d - face_radius(ka) - face_radius(kb)

MIN_GAP = 5.0
pairs = []
for i in range(len(results)):
    for j in range(i + 1, len(results)):
        g = gap(results[i], results[j])
        pairs.append((g, results[i][0], results[j][0]))
        if g < MIN_GAP:
            ok = False
            print(f"FAIL gap: {results[i][0]} to {results[j][0]}: {g:.1f} mm")
pairs.sort()
print("Tightest face gaps (mm):")
for g, a, b in pairs[:12]:
    print(f"  {a:4s} - {b:4s}: {g:5.1f}")
print("Wall margins (mm):")
for ref, kind, label, x, y, r, er, wall in results:
    print(f"  {ref:4s} {label:28s} r={r:5.1f} env={er:4.1f} margin={wall:5.1f}")
print("FIT OK" if ok else "FIT FAILED")

# ---- hole table CSV
with open(os.path.join(OUT, "rev-c-endcap-hole-table.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Ref", "Function", "Part", "X_mm", "Y_mm", "Drill_mm", "Counterbore_from_inside_mm",
                "Extra_holes", "Knob_or_face_dia_mm", "Radius_from_centre_mm", "Margin_to_bore_mm", "Notes"])
    for ref, kind, label, x, y, r, er, wall in results:
        p = PARTS[kind]
        extra = "2x 3.2 at (X-10, Y+11.5) and (X+10, Y-11.5)" if kind == "combo" else ""
        cb = "" if p["cbore"] is None else f"{p['cbore']:.0f} (leave {p.get('skin', 3.0):.1f} mm of face)"
        w.writerow([ref, label, p["mpn"], f"{x:.1f}", f"{y:.1f}", f"{p['hole']:.1f}", cb, extra,
                    p["knob"] or max(p["env"]), f"{r:.1f}", f"{wall:.1f}", p["note"]])

# ---- drawing (matplotlib): preview PNG and 1:1 PDF
def draw(ax, annotate=True):
    ax.add_patch(Circle((0, 0), R, fill=False, lw=1.2, color="k"))
    ax.add_patch(Circle((0, 0), R - WALL_MARGIN, fill=False, lw=0.5, ls="--", color="gray"))
    ax.plot([-R, R], [0, 0], lw=0.3, color="gray"); ax.plot([0, 0], [-R, R], lw=0.3, color="gray")
    for ref, kind, label, x, y, r, er, wall in results:
        p = PARTS[kind]
        ax.add_patch(Circle((x, y), p["hole"] / 2, fill=False, lw=0.9, color="k"))
        if p["cbore"]:
            ax.add_patch(Circle((x, y), p["cbore"] / 2, fill=False, lw=0.4, ls=":", color="tab:red"))
        if p["knob"]:
            ax.add_patch(Circle((x, y), p["knob"] / 2, fill=False, lw=0.7, color="tab:blue"))
        w, h = p["env"]
        if kind == "combo":
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fill=False, lw=0.7, color="tab:blue"))
            for dx, dy in ((-10, 11.5), (10, -11.5)):
                ax.add_patch(Circle((x + dx, y + dy), 1.6, fill=False, lw=0.7, color="k"))
        else:
            ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fill=False, lw=0.4, ls="--", color="tab:green"))
        ax.plot([x - 2, x + 2], [y, y], lw=0.5, color="k"); ax.plot([x, x], [y - 2, y + 2], lw=0.5, color="k")
        if annotate:
            off = (p["knob"] or max(p["env"])) / 2 + 2.5
            ax.text(x, y - off, f"{ref}\n{label}", ha="center", va="top", fontsize=5.5)
    ax.set_aspect("equal"); ax.set_xlim(-R - 8, R + 8); ax.set_ylim(-R - 8, R + 8)
    ax.set_xlabel("mm"); ax.set_ylabel("mm")

fig, ax = plt.subplots(figsize=(9, 9), dpi=150)
draw(ax)
ax.set_title("GAS Rev C service endcap, 6 in DWV cap (168.3 mm bore), viewed from outside\n"
             "black = drill, red dotted = counterbore from inside, blue = knob / flange, green dashed = body behind panel")
fig.savefig(os.path.join(OUT, "rev-c-endcap-preview.png"), bbox_inches="tight")

# 1:1 PDF on Letter (needs 168 mm: fits in 215.9 x 279.4)
fig2 = plt.figure(figsize=(8.5, 11))
ax2 = fig2.add_axes([(215.9 - 190) / 2 / 215.9, (279.4 - 190) / 2 / 279.4, 190 / 215.9, 190 / 279.4])
draw(ax2, annotate=True)
ax2.set_xlim(-95, 95); ax2.set_ylim(-95, 95)
ax2.axis("off")
fig2.text(0.5, 0.94, "GAS Rev C endcap drill template, 1:1 (print at 100 %, check the 100 mm bar)", ha="center", fontsize=9)
ax2.plot([-50, 50], [-90, -90], lw=1.5, color="k"); ax2.text(0, -88, "100 mm", ha="center", fontsize=7)
fig2.savefig(os.path.join(OUT, "rev-c-endcap-template-1to1.pdf"))

# ---- DXF (layers: OUTLINE, DRILL, CBORE, KNOB, BODY, TEXT)
doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
for name, color in (("OUTLINE", 7), ("DRILL", 1), ("CBORE", 6), ("KNOB", 5), ("BODY", 3), ("TEXT", 7)):
    doc.layers.add(name, color=color)
msp = doc.modelspace()
msp.add_circle((0, 0), R, dxfattribs={"layer": "OUTLINE"})
for ref, kind, label, x, y, r, er, wall in results:
    p = PARTS[kind]
    msp.add_circle((x, y), p["hole"] / 2, dxfattribs={"layer": "DRILL"})
    if p["cbore"]: msp.add_circle((x, y), p["cbore"] / 2, dxfattribs={"layer": "CBORE"})
    if p["knob"]: msp.add_circle((x, y), p["knob"] / 2, dxfattribs={"layer": "KNOB"})
    w, h = p["env"]
    msp.add_lwpolyline([(x - w / 2, y - h / 2), (x + w / 2, y - h / 2), (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)],
                       close=True, dxfattribs={"layer": "BODY"})
    if kind == "combo":
        for dx, dy in ((-10, 11.5), (10, -11.5)):
            msp.add_circle((x + dx, y + dy), 1.6, dxfattribs={"layer": "DRILL"})
    msp.add_text(f"{ref} {label}", dxfattribs={"layer": "TEXT", "height": 2.0}).set_placement((x, y - (p["knob"] or max(p["env"])) / 2 - 3))
doc.saveas(os.path.join(OUT, "rev-c-endcap-layout.dxf"))
print("wrote", OUT)
