"""GAS Rev C: inside a 6 in PVC DWV pipe. Side view + cross sections, PNG/PDF/DXF + fit report.
Frame: Z along the pipe from the inside of the service cap face (Z = 0), X right, Y up (seen from outside the service cap)."""
import math, json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
import ezdxf

BORE = 154.0           # 6 in Sch 40 / DWV ID 6.065 in
R = BORE / 2
OD = 168.3
CAP_FACE = 8.0

P = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {}
# 2026-09-21: jacks are on the jack deck, not the io-board. Front stack (z from the OUTER face of the cap):
# control deck PCB top 15.0, jack deck PCB top 31.0 (jack flange contact 7.0). Here Z = 0 is the INSIDE of the
# cap face, so with a CAP_FACE mm thick cap the decks sit at Z = 15 - CAP_FACE and Z = 31 - CAP_FACE.
JACK_Y = 15.0                                 # jack bar on the cap drawing
DECK_D = 152.4                                # both decks are 6 in circles
ctrl_z = 15.0 - CAP_FACE
jack_z = 31.0 - CAP_FACE
io_top = -3.0                                 # unused placeholder, the io-board now sits on the plate
PCB = 1.6
PLATE_T = 3.0
boards = P.get("boards", {"io-board": (136, 180), "circuit-board": (120, 175), "tank-board": (120, 150), "power-board": (120, 62)})

# ---- electronics cartridge
io_bot = io_top - PCB
plate_top = io_bot - 6.0        # 6 mm standoffs under the io-board
plate_bot = plate_top - PLATE_T
top_std, bot_std = 6.0, 5.0
top_board_bot = plate_top + top_std
bot_board_top = plate_bot - bot_std
parts_top_h, parts_bot_h = 14.0, 20.0     # tallest parts: film caps / VH headers on top boards; TEL12 12 mm, RCA 13 mm, VH 13 mm below
PLATE_Z0, PLATE_Z1 = 45.0, 430.0          # plate starts behind the pot bodies (35 mm deep)
plate_w = 2 * math.sqrt(R ** 2 - plate_bot ** 2) - 12.0

items = []   # (name, z0, z1, y0, y1, width, color)
def add(name, z0, length, y0, y1, width, color):
    items.append(dict(name=name, z0=z0, z1=z0 + length, y0=y0, y1=y1, w=width, color=color))

io_w, io_l = boards["io-board"]
cb_w, cb_l = boards["circuit-board"]
tb_w, tb_l = boards["tank-board"]
pb_w, pb_l = boards["power-board"]
add("control deck (6 in round, controls to the cap)", ctrl_z, PCB, -DECK_D / 2, DECK_D / 2, DECK_D, "#8d6e63")
add("jack deck (6 in band, jacks to the cap) + plugs", jack_z, PCB + 17.0, -40.0, 49.0, DECK_D, "#8d6e63")
add("io-board", PLATE_Z0, io_l, top_board_bot, top_board_bot + PCB + parts_top_h, io_w, "#3a7d44")
add("circuit-board", PLATE_Z0 + io_l + 5, cb_l, top_board_bot, top_board_bot + PCB + parts_top_h, cb_w, "#3a7d44")
add("power-board (under)", 60.0, pb_l, bot_board_top - PCB - parts_bot_h, bot_board_top, pb_w, "#4a6fa5")
add("tank-board (under, RCA at rear edge)", PLATE_Z1 - tb_l - 10, tb_l, bot_board_top - PCB - parts_bot_h, bot_board_top, tb_w, "#4a6fa5")
PLATE_Z1 = max(PLATE_Z1, PLATE_Z0 + io_l + 5 + cb_l + 25)

# ---- tanks: Accutronics type 4 (425.5 x 120.3 x 33.4) and type 9 (425.5 x 111.1 x 33.4), horizontal, open side down
T_L, T_H = 425.5, 33.4
GAP = 14.0         # between the stacked tanks (grommet brackets live at the ends, not in this gap)
BULK = 6.0         # HDPE bulkhead discs
END = 22.0         # bracket + grommet space at each tank end
cage_len = T_L + 2 * END + 2 * BULK
cage1_z = PLATE_Z1 + 30.0
cage2_z = cage1_z + cage_len + 15.0
tanks = []
for cz, w, names in ((cage1_z, 120.3, ("4AB1C1B main L (upper)", "4AB1C1B main R (lower)")),
                     (cage2_z, 111.1, ("9EB2C1B 2nd L (upper)", "9EB3C1B 2nd R (lower)"))):
    y_up0 = GAP / 2
    tanks.append(dict(name=names[0], z0=cz + BULK + END, z1=cz + BULK + END + T_L, y0=y_up0, y1=y_up0 + T_H, w=w))
    tanks.append(dict(name=names[1], z0=cz + BULK + END, z1=cz + BULK + END + T_L, y0=-y_up0 - T_H, y1=-y_up0, w=w))
far_face = cage2_z + cage_len + 15.0
pipe_len = far_face

def corner_r(w, y0, y1):
    return max(math.hypot(w / 2, y0), math.hypot(w / 2, y1))

report = []
def chk(name, w, y0, y1):
    # the two front decks are round and live inside the cap socket (OD 168.3); everything else is a
    # rectangular board in the pipe bore
    r = w / 2 if "deck" in name else corner_r(w, y0, y1)
    lim = OD / 2 - 1.0 if "deck" in name else R
    report.append((name, w, round(y0, 1), round(y1, 1), round(r, 1), round(lim - r, 1)))

for it in items:
    chk(it["name"], it["w"], it["y0"], it["y1"])
chk("sled plate (3 mm aluminium)", plate_w, plate_bot, plate_top)
for t in tanks:
    chk(t["name"], t["w"], t["y0"], t["y1"])
# rods of the tank cages
rod = (30.0, 60.0)
report.append(("cage rods M6 at (+/-30, +/-60)", 6, 60, 60, round(math.hypot(33, 60), 1), round(R - math.hypot(33, 60), 1)))

# ---------------------------------------------------------------- drawing
def side(ax):
    ax.add_patch(Rectangle((-CAP_FACE, -OD / 2), CAP_FACE, OD, color="#bbbbbb"))
    ax.add_patch(Rectangle((far_face, -OD / 2), CAP_FACE, OD, color="#bbbbbb"))
    ax.plot([0, far_face], [R, R], "k-", lw=1); ax.plot([0, far_face], [-R, -R], "k-", lw=1)
    ax.plot([0, far_face], [OD / 2, OD / 2], "k:", lw=0.6); ax.plot([0, far_face], [-OD / 2, -OD / 2], "k:", lw=0.6)
    ax.add_patch(Rectangle((PLATE_Z0, plate_bot), PLATE_Z1 - PLATE_Z0, PLATE_T, color="#999999"))
    ax.text(PLATE_Z0 + 5, plate_bot - 6, "sled plate", fontsize=6)
    for it in items:
        ax.add_patch(Rectangle((it["z0"], it["y0"]), it["z1"] - it["z0"], it["y1"] - it["y0"], fc=it["color"], alpha=0.55, ec="k", lw=0.5))
        ax.text(it["z0"] + 3, (it["y0"] + it["y1"]) / 2, it["name"], fontsize=5.5, va="center")
    for cz in (cage1_z, cage2_z):
        for zz in (cz, cz + cage_len - BULK):
            ax.add_patch(Rectangle((zz, -R + 2), BULK, BORE - 4, fc="#e0c070", ec="k", lw=0.5))
        ax.plot([cz, cz + cage_len], [60, 60], "k--", lw=0.5); ax.plot([cz, cz + cage_len], [-60, -60], "k--", lw=0.5)
    for t in tanks:
        ax.add_patch(Rectangle((t["z0"], t["y0"]), T_L, T_H, fc="#8c8c8c", ec="k", lw=0.5))
        ax.text(t["z0"] + 10, (t["y0"] + t["y1"]) / 2, t["name"], fontsize=6, va="center", color="w")
    # control bodies behind the face (pots 13.5 mm, toggles 12.9 mm, 3.5 mm footswitch jack 14.1 mm)
    ax.add_patch(Rectangle((ctrl_z - 13.5, -70), 13.5, 60, fc="#d98c5f", alpha=0.5, ec="k", lw=0.4))
    ax.add_patch(Rectangle((ctrl_z - 12.9, 38), 12.9, 14, fc="#d98c5f", alpha=0.5, ec="k", lw=0.4))
    for z, lab in ((0, "0"), (PLATE_Z1, f"{PLATE_Z1:.0f}"), (cage1_z, f"{cage1_z:.0f}"), (cage2_z, f"{cage2_z:.0f}"), (far_face, f"{far_face:.0f}")):
        ax.annotate(lab, (z, -OD / 2 - 4), fontsize=6, ha="center")
    ax.set_xlim(-30, far_face + 30); ax.set_ylim(-OD / 2 - 15, OD / 2 + 10); ax.set_aspect("equal")
    ax.set_title(f"Side view (service cap on the left). Pipe length between cap faces {pipe_len:.0f} mm ({pipe_len/25.4:.1f} in)", fontsize=8)
    ax.set_xlabel("Z from inside of the service cap face, mm", fontsize=7); ax.tick_params(labelsize=6)

def section(ax, title, rects):
    ax.add_patch(Circle((0, 0), OD / 2, fc="#dddddd", ec="k", lw=0.8))
    ax.add_patch(Circle((0, 0), R, fc="white", ec="k", lw=0.8))
    for (w, y0, y1, fc, lab) in rects:
        ax.add_patch(Rectangle((-w / 2, y0), w, y1 - y0, fc=fc, alpha=0.6, ec="k", lw=0.5))
        ax.text(0, (y0 + y1) / 2, lab, fontsize=5.5, ha="center", va="center")
    ax.set_xlim(-OD / 2 - 5, OD / 2 + 5); ax.set_ylim(-OD / 2 - 5, OD / 2 + 5); ax.set_aspect("equal")
    ax.set_title(title, fontsize=8); ax.tick_params(labelsize=6)

secA = [(io_w, top_board_bot, top_board_bot + PCB + parts_top_h, "#3a7d44", "io-board"), (plate_w, plate_bot, plate_top, "#999999", "plate"),
        (pb_w, bot_board_top - PCB - parts_bot_h, bot_board_top, "#4a6fa5", "power / tank board")]
secB = [(cb_w, top_board_bot, top_board_bot + PCB + parts_top_h, "#3a7d44", "circuit-board"), (plate_w, plate_bot, plate_top, "#999999", "plate"),
        (tb_w, bot_board_top - PCB - parts_bot_h, bot_board_top, "#4a6fa5", "tank-board")]
secC = [(t["w"], t["y0"], t["y1"], "#8c8c8c", t["name"].split(" ")[0]) for t in tanks[:2]]
secD = [(t["w"], t["y0"], t["y1"], "#8c8c8c", t["name"].split(" ")[0]) for t in tanks[2:]]

def frontstack(ax):
    """Zoom on the service end: cap face, control deck, jack deck, filter-pot riser, sled bracket."""
    ax.add_patch(Rectangle((-CAP_FACE, -OD / 2), CAP_FACE, OD, color="#bbbbbb"))
    ax.text(-CAP_FACE + 0.5, OD / 2 + 3, f"cap face {CAP_FACE:.0f} mm", fontsize=5.5)
    ax.plot([0, 60], [R, R], "k-", lw=1); ax.plot([0, 60], [-R, -R], "k-", lw=1)
    ax.add_patch(Rectangle((ctrl_z, -DECK_D / 2), PCB, DECK_D, fc="#8d6e63", alpha=0.6, ec="k", lw=0.5))
    ax.text(ctrl_z + 2.5, -DECK_D / 2 - 6, "control deck", fontsize=5.5)
    ax.add_patch(Rectangle((jack_z, -40.0), PCB, 89.0, fc="#8d6e63", alpha=0.6, ec="k", lw=0.5))
    ax.text(jack_z + 2.5, 52, "jack deck", fontsize=5.5)
    ax.add_patch(Rectangle((jack_z + PCB, -40.0), 17.0, 89.0, fc="#cfc0b8", alpha=0.5, ec="k", lw=0.4))
    ax.text(jack_z + 4, 44, "harness plugs", fontsize=5)
    for (y0, y1, lab) in ((-2.7, 27.7, "combo jacks"),):
        ax.add_patch(Rectangle((0, y0), jack_z, y1 - y0, fc="#9fb8c8", alpha=0.6, ec="k", lw=0.4))
        ax.text(2, (y0 + y1) / 2, lab, fontsize=5.5, va="center")
    ax.add_patch(Rectangle((ctrl_z - 13.5, -72), 13.5, 62, fc="#d98c5f", alpha=0.5, ec="k", lw=0.4))
    ax.text(ctrl_z - 12, -66, "pot bodies (in the counterbores)", fontsize=5)
    # filter-pot riser: PTD904 shoulder on the counterbore floor 3 mm inside the outer face (Z = 3 - CAP_FACE),
    # body 17.2 mm behind it, carrier board 46 x 15 mm running back past the deck to the XH-8.
    riser_z0 = 3.0 - CAP_FACE
    ax.add_patch(Rectangle((riser_z0, -62.0), 17.2, 11.0, fc="#7fa87f", alpha=0.55, ec="k", lw=0.4))
    ax.add_patch(Rectangle((riser_z0 + 1.0, -63.6), 46.0, 1.6, fc="#4a6fa5", alpha=0.7, ec="k", lw=0.4))
    ax.add_patch(Rectangle((riser_z0 + 23.0, -72.0), 21.0, 8.4, fc="#cfc0b8", alpha=0.6, ec="k", lw=0.4))
    ax.text(riser_z0 + 1.5, -58.0, "PTD904 on its filter-pot riser", fontsize=5)
    ax.text(riser_z0 + 23.5, -70.0, "XH-8 to circuit P5 / P6", fontsize=5)
    ax.add_patch(Rectangle((ctrl_z - 12.9, 38), 12.9, 14, fc="#d98c5f", alpha=0.5, ec="k", lw=0.4))
    ax.text(ctrl_z - 12, 45, "toggles", fontsize=5)
    # 3.5 mm footswitch jack (XKB PJ-301C) soldered to the control deck: 10.2 mm body from the deck top
    # forward to the counterbore floor, then the M6 bushing into the 6.4 mm hole, ending 0.9 mm shy of the face.
    ax.add_patch(Rectangle((ctrl_z - 10.0, -19.7), 10.0, 10.2, fc="#c9a0dc", alpha=0.45, ec="k", lw=0.4))
    ax.add_patch(Rectangle((-7.1, -17.6), 4.1, 6.0, fc="#c9a0dc", alpha=0.7, ec="k", lw=0.4))
    ax.text(ctrl_z - 9.5, -23.5, "3.5 mm footswitch jack (PCB mounted)", fontsize=5)
    ax.add_patch(Rectangle((PLATE_Z0, plate_bot), 60 - PLATE_Z0, PLATE_T, color="#999999"))
    ax.plot([jack_z + PCB, PLATE_Z0], [-11.5, plate_top], "k-", lw=0.8)
    ax.text(jack_z + 6, -30, "M3 angle to the sled", fontsize=5)
    ax.set_xlim(-12, 60); ax.set_ylim(-OD / 2 - 8, OD / 2 + 8); ax.set_aspect("equal")
    ax.set_title("Front stack (service end)", fontsize=8); ax.tick_params(labelsize=6)

fig = plt.figure(figsize=(18.5, 11.7))
gs = fig.add_gridspec(2, 5, height_ratios=[1.1, 1])
side(fig.add_subplot(gs[0, :]))
frontstack(fig.add_subplot(gs[1, 0]))
for i, (t, r) in enumerate(((f"A: io-board station (Z {PLATE_Z0:.0f}-{PLATE_Z0 + io_l:.0f})", secA),
                            (f"B: circuit + tank board (Z {PLATE_Z0 + io_l + 5:.0f}-{PLATE_Z1:.0f})", secB),
                            ("C: main tank cage", secC), ("D: 2nd tank cage", secD))):
    ax = fig.add_subplot(gs[1, i + 1]); section(ax, t, r)
    if i >= 2:
        for sx in (-30, 30):
            for sy in (-60, 60):
                ax.add_patch(Circle((sx, sy), 3, fc="k"))
fig.suptitle("Illicit Apothecary - The Great American Spring Rev C - internal layout in 6 in PVC DWV pipe (154 mm bore)", fontsize=10)
fig.tight_layout()
fig.savefig("rev-c-tube-layout.png", dpi=150)
with PdfPages("rev-c-tube-layout.pdf") as pdf:
    pdf.savefig(fig)

# DXF: side view + sections as layers
doc = ezdxf.new("R2010"); msp = doc.modelspace()
for L in ("PIPE", "BOARDS", "PLATE", "TANKS", "CAGE", "TEXT"):
    doc.layers.add(L)
def rect(x0, y0, x1, y1, layer):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})
msp.add_line((0, R), (far_face, R), dxfattribs={"layer": "PIPE"}); msp.add_line((0, -R), (far_face, -R), dxfattribs={"layer": "PIPE"})
rect(-CAP_FACE, -OD / 2, 0, OD / 2, "PIPE"); rect(far_face, -OD / 2, far_face + CAP_FACE, OD / 2, "PIPE")
rect(PLATE_Z0, plate_bot, PLATE_Z1, plate_top, "PLATE")
for it in items:
    rect(it["z0"], it["y0"], it["z1"], it["y1"], "BOARDS")
    msp.add_text(it["name"], dxfattribs={"layer": "TEXT", "height": 3}).set_placement((it["z0"] + 2, it["y1"] + 2))
for t in tanks:
    rect(t["z0"], t["y0"], t["z1"], t["y1"], "TANKS")
    msp.add_text(t["name"], dxfattribs={"layer": "TEXT", "height": 3}).set_placement((t["z0"] + 5, t["y0"] + 12))
for cz in (cage1_z, cage2_z):
    rect(cz, -R + 2, cz + BULK, R - 2, "CAGE"); rect(cz + cage_len - BULK, -R + 2, cz + cage_len, R - 2, "CAGE")
# bulkhead disc drawing (2D, offset below)
ox, oy = 300, -300
msp.add_circle((ox, oy), R - 1.5, dxfattribs={"layer": "CAGE"})
for sx in (-30, 30):
    for sy in (-60, 60):
        msp.add_circle((ox + sx, oy + sy), 3.3, dxfattribs={"layer": "CAGE"})
msp.add_text("bulkhead disc 151 mm, 6 mm HDPE, 4 x 6.6 mm rod holes", dxfattribs={"layer": "TEXT", "height": 4}).set_placement((ox - 70, oy - 90))
doc.saveas("rev-c-tube-layout.dxf")

out = dict(io_top=io_top, plate_top=plate_top, plate_bot=plate_bot, plate_w=round(plate_w, 1), plate_z=(PLATE_Z0, PLATE_Z1),
           top_board_bot=top_board_bot, bot_board_top=bot_board_top, cage_len=cage_len, cage1_z=cage1_z, cage2_z=cage2_z,
           pipe_len=round(pipe_len), report=report, tanks=tanks, items=items)
json.dump(out, open("rev-c-tube-layout.json", "w"), indent=1)
for r in report:
    print(r)
print({k: v for k, v in out.items() if k not in ("report", "tanks", "items")})
