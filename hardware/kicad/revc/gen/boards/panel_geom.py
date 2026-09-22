"""Rev C front stack geometry (2026-09-21), panel coordinates: X right, Y up, mm from the endcap centre, seen from outside.
Both decks are 6 in (152.4 mm) circles; KiCad F side faces the endcap, so the F-side view = the outside view.

2026-09-21: the three push-pull pots are gone (no dual-gang linear push-pull is stocked anywhere). Vol, Gain and
Output are now plain dual pots on the control deck, each with its own mini toggle in the switch row (7 toggles).

2026-09-21b (edge pass): every footprint and cut-out now sits wholly inside the 76.2 mm radius with at least
2 mm of board beyond its courtyard. Toggle row pitch 18.5 -> 17.0 mm (outer pair 55.5 -> 51.0), outer pot arc
66 -> 63 mm, Feedback pot -40 -> -37, and the 16 x 24 mm filter-pot windows are now radial capsules (two 7.5 mm
circles) that stay inside the edge. The footswitch jack is a PCB-mounted 3.5 mm PJ-301C, so its 21 mm body
window is gone from both decks.
"""
import math

R = 76.2


def K(X, Y):
    return (round(R + X, 3), round(R - Y, 3))


JACKS = {"J1": (-49.5, 15.0), "J2": (-16.5, 15.0), "J3": (16.5, 15.0), "J4": (49.5, 15.0)}
# switch row, left to right: Source, Tube (Vol), Dirt (Gain), Tape (Output), Ext tanks, FB Dyn, FB Phase
TOGGLES = {"S1": (-51.0, 43.0), "S5": (-34.0, 43.0), "S6": (-17.0, 43.0), "S7": (0.0, 43.0),
           "S2": (17.0, 43.0), "S3": (34.0, 43.0), "S4": (51.0, 43.0)}
DC = (0.0, 66.0)
FS = (0.0, -14.0)
QUADS = {"VR2": (-36.14, -51.60), "VR4": (36.14, -51.60)}                           # HPF, LPF on risers, r 63
DUALS = {"VR1": (-59.20, -21.55), "VR3": (0.0, -63.0), "VR5": (59.20, -21.55),      # Vol, Gain, Output, r 63
         "VR6": (-25.5, -23.5), "VR7": (0.0, -37.0), "VR8": (25.5, -23.5)}          # Ext Mix, Feedback, Wet/Dry
QUAD_CUT_R = 9.0      # 18 mm clear: passes the 15 mm wide filter-pot riser with its PTD904 on it
QUAD_CUT_IN = 8.0     # second circle, this far inboard, clears the riser and the terminal field
FS_HOLE = 6.4         # endcap hole for the 3.5 mm jack bushing (M6 x 0.5)
JACK_DECK_TOP_Y = 49.0
JACK_DECK_BOTTOM_Y = -40.0
POT_HEADERS = {"P1": (-26.0, -16.0), "P2": (26.0, -16.0)}   # control-deck headers whose plugs pass through the jack deck

# Alps RK09L double vertical: KiCad footprint origin at pad 1, shaft axis at (10, 2.5), courtyard x -1.18..15.12,
# y -4.53..9.53 (KiCad frame, y down).
RK09_AXIS = (10.0, 2.5)
RK09_CRT = (-1.18, -4.53, 15.12, 9.53)


def cut_circle(X, Y, r):
    x, y = K(X, Y)
    return ("circle", x, y, r)


def cut_rect(X, Y, w, h):
    x, y = K(X, Y)
    return ("rect", x - w / 2, y - h / 2, x + w / 2, y + h / 2)


def quad_cuts():
    """Radial capsule (two circles) through each deck for a 4-gang filter pot body plus its terminal field."""
    out = []
    for (X, Y) in QUADS.values():
        d = math.hypot(X, Y)
        ux, uy = X / d, Y / d
        out.append(cut_circle(X, Y, QUAD_CUT_R))
        out.append(cut_circle(X - ux * QUAD_CUT_IN, Y - uy * QUAD_CUT_IN, QUAD_CUT_R))
    return out


def rot_xy(x, y, deg):
    """KiCad footprint orientation: local (x, y) -> board offset, y down, positive angle counterclockwise."""
    import math
    a = math.radians(deg)
    return (x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a))


def rk09_place(X, Y, prefer=None):
    """Footprint origin and rotation for an RK09L whose shaft axis is at panel (X, Y): pins point inward,
    or in the forced direction when prefer is given (90 = pin field below the shaft on the panel)."""
    ax, ay = K(X, Y)
    best = None
    for deg in ((prefer,) if prefer is not None else (0, 90, 180, 270)):
        ox, oy = rot_xy(RK09_AXIS[0], RK09_AXIS[1], deg)
        px, py = ax - ox, ay - oy
        far = 0.0
        for cx in (RK09_CRT[0], RK09_CRT[2]):
            for cy in (RK09_CRT[1], RK09_CRT[3]):
                gx, gy = rot_xy(cx, cy, deg)
                far = max(far, ((px + gx - R) ** 2 + (py + gy - R) ** 2) ** 0.5)
        if best is None or far < best[0]:
            best = (far, px, py, deg)
    return (round(best[1], 3), round(best[2], 3), best[3], round(best[0], 2))
