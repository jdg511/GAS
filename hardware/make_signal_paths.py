"""Generates a draw.io file of the GAS Rev C plugin wet-path routing.

One page per Ext Tanks setting (Off / Series / Parallel), each drawn in stereo.
Routing is read straight off PluginProcessor::processBlock; supplies and part
numbers are read off hardware/kicad/revc/circuit-board/circuit-board.kicad_sch.

Supplies, per the Rev C schematic:
  +9VC   L78L09 on the circuit board. Feeds ONLY the VBIAS buffer and the two
         Tube Screamer channels (TL072H, 1N4148W pair). Clips at +/-4.5 V.
  +/-15V Everything else. OPA1679 swings to within 800 mV of the rail, so a
         board node runs out at about 14 V. Comp (MMBF5457 FET + OPA1679) and
         Limit (Coolaudio V2181 VCA + OPA1679 detector) are both on these.

Layout rules, so nothing ever sits on top of anything else:
  * strict left-to-right column grid, one cursor, columns never share x space
  * stereo stages fill a tall band; L rows live in the top half, R rows below
  * every gain is a real box, never an edge label, so it occupies grid space
  * feedback gets its own empty corridor above the band, dry its own below
  * every edge carries jumpStyle=arc, so a crossing draws as a hop, not a join
"""

import html

OUT = r"C:\Users\Jason\GAS-build\repo\hardware\gas-revc-signal-paths.drawio"

X0 = 60
GAP = 44
Y_BAND, H_BAND = 200, 320
ROW_H = 50
SPAN_H = 120
ROWS = {"LM": 205, "LA": 275, "RM": 395, "RA": 465}
Y_FB, Y_DRY = 90, 600
Y_TITLE, Y_NOTE, Y_LEG = 30, 680, 900

# Predelay lanes. Every lane has its own window, so L and R no longer share a
# range and the image widens. These four match PluginProcessor.cpp exactly:
# predelayLaneMinMs { 20, 22, 30, 25 } / predelayLaneMaxMs { 30, 35, 42, 40 },
# in lane order primary L, primary R, secondary L, secondary R.
PD = {
    "LM": "Predelay 1 (L)\n20 to 30 ms",     # short tank L
    "RM": "Predelay 3 (R)\n22 to 35 ms",     # short tank R
    "LA": "Predelay 2 (L)\n30 to 42 ms",     # long tank L
    "RA": "Predelay 4 (R)\n25 to 40 ms",     # long tank R
}

PD_NOTE = ("Predelay windows are one per lane, implemented 2026-09-30 in PluginProcessor.cpp "
           "(predelayLaneMinMs / predelayLaneMaxMs).\nBefore that, L and R shared one window per "
           "pair (both short lanes 20 to 30, both long lanes 30 to 42). Each lane still wanders\n"
           "independently inside its own window, so L and R are now decorrelated from each other "
           "as well as from the long tanks.")


def rc(row):
    """Vertical centre of a named row."""
    return ROWS[row] + ROW_H // 2


STEREO = "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;"
NINEV = "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffcccc;strokeColor=#b85450;"
MONO = "rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;"
TANK = "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontStyle=1;"
GAIN = "rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;"
SUM = "rhombus;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;"
METER = "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=11;"
NOTE = "text;html=1;whiteSpace=wrap;align=left;verticalAlign=top;fontSize=13;"
TITLE = "text;html=1;whiteSpace=wrap;align=left;fontSize=26;fontStyle=1;"

JUMP = "jumpStyle=arc;jumpSize=10;"
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;" + JUMP
BYP = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=4 4;"
       "strokeColor=#9673a6;") + JUMP
FBE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=8 8;"
       "strokeColor=#b85450;") + JUMP
DRYE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;dashPattern=8 8;"
        "strokeColor=#6a9153;") + JUMP


class Node:
    def __init__(self, ident, x, y, w, h):
        self.id = ident
        self.x, self.y, self.w, self.h = x, y, w, h

    def fy(self, ycoord):
        """Fraction down this box's own height for an absolute y."""
        return round((ycoord - self.y) / float(self.h), 4)

    @property
    def cx(self):
        return self.x + self.w // 2


class Page:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self.n = 0
        self.x = X0

    def _id(self):
        self.n += 1
        return "c%d" % self.n

    def col(self, w):
        """Claim the next column of width w and return its x."""
        x = self.x
        self.x += w + GAP
        return x

    def gap_mid(self):
        """Midpoint of the empty gap that follows the column just claimed."""
        return self.x - GAP // 2

    def box(self, label, x, y, w, h, style):
        i = self._id()
        self.cells.append(
            '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%d" y="%d" width="%d" height="%d" as="geometry"/></mxCell>'
            % (i, html.escape(label).replace("\n", "&#10;"), style, x, y, w, h))
        return Node(i, x, y, w, h)

    def stereo(self, label, w, style=STEREO):
        return self.box(label, self.col(w), Y_BAND, w, H_BAND, style)

    def edge(self, a, b, style=EDGE, ay=None, by=None, pts=None):
        """a -> b. ay / by are absolute y coords for the exit / entry points."""
        ey = 0.5 if ay is None else a.fy(ay)
        ny = 0.5 if by is None else b.fy(by)
        s = (style
             + "exitX=1;exitY=%g;exitDx=0;exitDy=0;" % ey
             + "entryX=0;entryY=%g;entryDx=0;entryDy=0;" % ny)
        geo = '<mxGeometry relative="1" as="geometry"/>'
        if pts:
            geo = ('<mxGeometry relative="1" as="geometry"><Array as="points">'
                   + "".join('<mxPoint x="%d" y="%d"/>' % (px, py) for px, py in pts)
                   + '</Array></mxGeometry>')
        i = self._id()
        self.cells.append(
            '<mxCell id="%s" style="%s" edge="1" parent="1" source="%s" target="%s">%s'
            '</mxCell>' % (i, s, a.id, b.id, geo))

    def corridor(self, a, b, y, style):
        """a -> b the long way round, along an empty horizontal corridor at y."""
        side = 0 if y < Y_BAND else 1
        s = (style
             + "exitX=0.5;exitY=%d;exitDx=0;exitDy=0;" % side
             + "entryX=0.5;entryY=%d;entryDx=0;entryDy=0;" % side)
        i = self._id()
        self.cells.append(
            '<mxCell id="%s" style="%s" edge="1" parent="1" source="%s" target="%s">'
            '<mxGeometry relative="1" as="geometry"><Array as="points">'
            '<mxPoint x="%d" y="%d"/><mxPoint x="%d" y="%d"/>'
            '</Array></mxGeometry></mxCell>'
            % (i, s, a.id, b.id, a.cx, y, b.cx, y))

    def xml(self):
        pw = self.x + 160
        return ('<diagram name="%s"><mxGraphModel dx="2200" dy="1200" grid="1" gridSize="10" '
                'page="1" pageWidth="%d" pageHeight="1040" math="0" shadow="0"><root>'
                '<mxCell id="0"/><mxCell id="1" parent="0"/>%s</root></mxGraphModel></diagram>'
                % (html.escape(self.name), pw, "".join(self.cells)))


def build(mode):
    p = Page("Ext Tanks: " + mode)
    p.box("GAS Rev C  |  wet path  |  Ext Tanks = " + mode, X0, Y_TITLE, 1400, 40, TITLE)

    host = p.stereo("Host In\nL / R", 100)
    pre = p.stereo("Pre Input\n-48 to +18 dB", 120)
    vol = p.stereo("In\n-18 to +18 dB", 120)
    tube = p.stereo("Tube\nJ201\n(switch)", 100)
    rail1 = p.stereo("rail 14 V\n(+/-15 V)", 80)

    x = p.col(110)
    inL = p.box("L In meter", x, ROWS["LM"], 110, ROW_H, METER)
    inR = p.box("R In meter", x, ROWS["RM"], 110, ROW_H, METER)

    fbin = p.stereo("Fb In\n(sum)", 90)

    p.edge(host, pre)
    p.edge(pre, vol)
    p.edge(vol, tube)
    p.edge(tube, rail1)
    p.edge(rail1, inL, ay=rc("LM"))
    p.edge(rail1, inR, ay=rc("RM"))
    p.edge(inL, fbin, by=rc("LM"))
    p.edge(inR, fbin, by=rc("RM"))

    x = p.col(150)
    pdL = p.box(PD["LM"], x, ROWS["LM"], 150, ROW_H, MONO)
    pdR = p.box(PD["RM"], x, ROWS["RM"], 150, ROW_H, MONO)
    pd_x, pd_gap = x, p.gap_mid()
    p.edge(fbin, pdL, ay=rc("LM"))
    p.edge(fbin, pdR, ay=rc("RM"))

    lanes = (("L", "LM", "LA", pdL), ("R", "RM", "RA", pdR))
    outs = {}

    if mode == "Off":
        x = p.col(150)
        for tag, main, alt, lane_in in lanes:
            t = p.box("SHORT tank %s\nGBS-%s IR" % (tag, tag), x, ROWS[main], 150, ROW_H, TANK)
            p.edge(lane_in, t)
            outs[tag] = (t, rc(main))
        p.box("Ext Tanks Off: the long (Ext) tanks are out of circuit entirely, and the\n"
              "Short/Long Reverb mix knob does nothing in this mode.\n\n" + PD_NOTE,
              X0, Y_NOTE, 1100, 140, NOTE)

    elif mode == "Series":
        x = p.col(150)
        short = {}
        for tag, main, alt, lane_in in lanes:
            short[tag] = p.box("SHORT tank %s\nGBS-%s IR" % (tag, tag),
                               x, ROWS[main], 150, ROW_H, TANK)
            p.edge(lane_in, short[tag])

        x = p.col(130)
        g1, b1 = {}, {}
        for tag, main, alt, lane_in in lanes:
            g1[tag] = p.box("x Short%", x, ROWS[main], 130, ROW_H, GAIN)
            b1[tag] = p.box("x (1 - Short%)\nbypass", x, ROWS[alt], 130, ROW_H, GAIN)
            p.edge(short[tag], g1[tag])
            p.edge(lane_in, b1[tag], style=BYP,
                   pts=[(pd_gap, rc(alt)), (x - GAP // 2, rc(alt))])

        x = p.col(110)
        sum1 = {}
        for tag, main, alt, lane_in in lanes:
            s = p.box("sum\nstage 1", x, ROWS[main], 110, SPAN_H, SUM)
            sum1[tag] = s
            p.edge(g1[tag], s, by=rc(main))
            p.edge(b1[tag], s, style=BYP, by=rc(alt))

        x = p.col(150)
        pd2 = {}
        for tag, main, alt, lane_in in lanes:
            pd2[tag] = p.box(PD[alt], x, ROWS[main], 150, ROW_H, MONO)
            p.edge(sum1[tag], pd2[tag], ay=rc(main))

        x = p.col(110)
        mk = {}
        for tag, main, alt, lane_in in lanes:
            mk[tag] = p.box("x 2.0\n(+6 dB makeup)", x, ROWS[main], 110, ROW_H, GAIN)
            p.edge(pd2[tag], mk[tag])

        x = p.col(150)
        lng = {}
        for tag, main, alt, lane_in in lanes:
            lng[tag] = p.box("LONG tank %s\nGAS-%s IR" % (tag, tag),
                             x, ROWS[main], 150, ROW_H, TANK)
            p.edge(mk[tag], lng[tag])

        x = p.col(130)
        g2, b2 = {}, {}
        for tag, main, alt, lane_in in lanes:
            g2[tag] = p.box("x Long%", x, ROWS[main], 130, ROW_H, GAIN)
            b2[tag] = p.box("x (1 - Long%)\nbypass", x, ROWS[alt], 130, ROW_H, GAIN)
            p.edge(lng[tag], g2[tag])
            p.edge(sum1[tag], b2[tag], style=BYP, ay=rc(alt))

        x = p.col(110)
        for tag, main, alt, lane_in in lanes:
            s = p.box("sum\nstage 2", x, ROWS[main], 110, SPAN_H, SUM)
            p.edge(g2[tag], s, by=rc(main))
            p.edge(b2[tag], s, style=BYP, by=rc(alt))
            outs[tag] = (s, s.y + SPAN_H // 2)

        p.box("Series, as built. Each tank is blended against a bypass that goes around it.\n"
              "Hard left  = Short 100 / Long 0   : stage 2 passes stage 1 through, so short tank only.\n"
              "Noon       = Short 100 / Long 100 : a true cascade, short tank into long tank.\n"
              "Hard right = Short 0 / Long 100   : short bypassed, long tank fed the raw wet signal.\n"
              "NOTE: the +6 dB makeup sits before the long tank at EVERY knob position, so the\n"
              "hard-right (long only) end runs about 6 dB hotter than the hard-left (short only) end.\n"
              "NOTE: the long tank keeps convolving even when it is mixed all the way out.\n\n" + PD_NOTE,
              X0, Y_NOTE, 1200, 200, NOTE)

    else:
        second = {}
        for tag, main, alt, lane_in in lanes:
            second[tag] = p.box(PD[alt], pd_x, ROWS[alt], 150, ROW_H, MONO)
            p.edge(fbin, second[tag], style=BYP, ay=rc(alt))

        x = p.col(150)
        short, lng = {}, {}
        for tag, main, alt, lane_in in lanes:
            short[tag] = p.box("SHORT tank %s\nGBS-%s IR" % (tag, tag),
                               x, ROWS[main], 150, ROW_H, TANK)
            lng[tag] = p.box("LONG tank %s\nGAS-%s IR" % (tag, tag),
                             x, ROWS[alt], 150, ROW_H, TANK)
            p.edge(lane_in, short[tag])
            p.edge(second[tag], lng[tag])

        x = p.col(130)
        gs, gl = {}, {}
        for tag, main, alt, lane_in in lanes:
            gs[tag] = p.box("x Short%", x, ROWS[main], 130, ROW_H, GAIN)
            gl[tag] = p.box("x Long%", x, ROWS[alt], 130, ROW_H, GAIN)
            p.edge(short[tag], gs[tag])
            p.edge(lng[tag], gl[tag])

        x = p.col(110)
        for tag, main, alt, lane_in in lanes:
            s = p.box("sum", x, ROWS[main], 110, SPAN_H, SUM)
            p.edge(gs[tag], s, by=rc(main))
            p.edge(gl[tag], s, by=rc(alt))
            outs[tag] = (s, s.y + SPAN_H // 2)

        p.box("Parallel, as built. The two tanks run side by side and are summed.\n"
              "Hard left = short only, noon = both at full, hard right = long only.\n"
              "No +6 dB makeup here, unlike Series.\n"
              "NOTE: the long branch taps the wet input BEFORE the short lane's predelay and uses\n"
              "only its own window, so the two tanks are not fed the same timing.\n\n" + PD_NOTE,
              X0, Y_NOTE, 1200, 180, NOTE)

    # --- the old single "Gain + Dirt + Comp / Limit" block, split into its real
    # stages so each one shows the supply the Rev C schematic puts it on.
    hpf = p.stereo("HPF\nSallen-Key\nQ 0.71", 100)
    for tag, main, alt, lane_in in lanes:
        node, ycoord = outs[tag]
        p.edge(node, hpf, ay=ycoord, by=ycoord)

    gain = p.stereo("Gain\n-18 to +18 dB", 120)
    dirt = p.stereo("Dirt (Gain pull)\nTS808, TL072H\n1N4148W pair\n\n+9VC\nclips at +/-4.5 V",
                    150, NINEV)
    dyn = p.stereo("Comp / Off / Limit\n\nComp: MMBF5457 FET\n(1176 territory)\n"
                   "Limit: V2181 VCA\n10:1\n\n+/-15 V", 170)
    lpf = p.stereo("LPF\nSallen-Key\nQ 0.74", 100)
    rail2 = p.stereo("rail 14 V\n(+/-15 V)", 80)
    p.edge(hpf, gain)
    p.edge(gain, dirt)
    p.edge(dirt, dyn)
    p.edge(dyn, lpf)
    p.edge(lpf, rail2)

    x = p.col(120)
    wetL = p.box("L Wet meter", x, ROWS["LM"], 120, ROW_H, METER)
    wetR = p.box("R Wet meter", x, ROWS["RM"], 120, ROW_H, METER)
    p.edge(rail2, wetL, ay=rc("LM"))
    p.edge(rail2, wetR, ay=rc("RM"))

    fb = p.stereo("Feedback\nFb %\n(swaps L and R\nin MEGAVERB)", 130)
    p.edge(wetL, fb, by=rc("LM"))
    p.edge(wetR, fb, by=rc("RM"))

    wd = p.stereo("Wet / Dry", 110)
    p.edge(fb, wd)

    out = p.stereo("Out\n-18 to +18 dB\n+ Tape", 130)
    p.edge(wd, out)
    rail3 = p.stereo("rail 14 V\n(+/-15 V)", 80)
    p.edge(out, rail3)
    post = p.stereo("Post Output\n-48 to +18 dB", 130)
    p.edge(rail3, post)

    x = p.col(120)
    omL = p.box("L Out meter", x, ROWS["LM"], 120, ROW_H, METER)
    omR = p.box("R Out meter", x, ROWS["RM"], 120, ROW_H, METER)
    p.edge(post, omL, ay=rc("LM"))
    p.edge(post, omR, ay=rc("RM"))

    hostout = p.stereo("Host Out\nL / R", 100)
    p.edge(omL, hostout, by=rc("LM"))
    p.edge(omR, hostout, by=rc("RM"))

    p.corridor(fb, fbin, Y_FB, FBE)
    p.corridor(host, wd, Y_DRY, DRYE)
    p.box("red dashed: Fb Out, back round to Fb In", fbin.cx + 140, Y_FB + 12, 360, 24, NOTE)
    p.box("green dashed: dry tap, Host In straight to Wet / Dry",
          host.cx + 140, Y_DRY + 12, 420, 24, NOTE)

    p.box("Orange = spring tank convolution.   Blue = a stereo stage on +/-15 V.   "
          "RED = the only block on the +9VC rail.   Green = per channel.\n"
          "Yellow = a gain.   Purple diamond = a sum.   Purple dashed = a path that skips a stage.   "
          "Lines that cross without joining hop over the one underneath.\n"
          "Supplies (circuit-board.kicad_sch): the L78L09 makes +9VC for the VBIAS buffer and the two "
          "Tube Screamer channels, and nothing else. Comp (MMBF5457 + OPA1679)\n"
          "and Limit (Coolaudio V2181 + OPA1679 detector) are both on +/-15 V, where a board node runs "
          "out of rail at about 14 V.\n"
          "Short% and Long% both come from the one Short/Long Reverb mix knob: Short% is 100 until "
          "noon then falls to 0, Long% rises from 0 to 100 by noon then stays 100.",
          X0, Y_LEG, 1900, 110, NOTE)
    return p


pages = [build(m) for m in ("Off", "Series", "Parallel")]
xml = '<mxfile host="Electron" type="device">%s</mxfile>' % "".join(p.xml() for p in pages)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(xml)

print("wrote", OUT)
for pg in pages:
    print("  %-22s %3d cells, width %d" % (pg.name, pg.n, pg.x + 160))
