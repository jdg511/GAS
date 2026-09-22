"""GAS Rev C control deck (6 in round PCB right behind the endcap face, 2026-09-21).

PCBWay mounts everything, including the two 4-gang filter pots (each on its own filter-pot riser):
7 x mini toggle (Dailywell 1M, C&K 7000 footprint, PC pins), 6 x Alps RK09L dual 10k lin pot
(Vol, Gain, Output, Ext Mix, Feedback, Wet/Dry), Same Sky PJ-064B DC jack, the 3.5 mm footswitch jack
(XKB PJ-301C, vertical, M6 bushing) and JST headers on the back.
Pot and switch harnesses are split so that nothing has to cross the jack bar: the pot headers sit in the
bottom half, the switch headers in the top half, each pin-for-pin with the header it plugs into. The one
exception is FS_TIP, which runs from the footswitch jack at (0, -20) up through the 5 mm bridge between the
two centre jack windows to P8.
The HPF / LPF 4-gang pots are side-adjust, so each rides on a filter-pot riser (see boards/filter_pot_riser.py)
that passes through this deck's capsule window and nut-mounts to the cap. Nothing on this board is hand wired.
Stack: control deck PCB top 15.0 mm behind the outer face of the cap; jack deck 31 mm.
Bare board = endcap drilling template (hole sizes in silkscreen, 1 mm centre marks on the pots and DC jack).
"""
from core import *
from common import *
from panel_geom import *
import io_board, circuit_board, tank_board

FP_SPDT = "GAS_Parts:SW_Toggle_CK7000_SPDT_PC_Vertical"
FP_DPDT = "GAS_Parts:SW_Toggle_CK7000_DPDT_PC_Vertical"
FP_DCJ = "GAS_Parts:BarrelJack_SameSky_PJ-064B_Vertical"
FP_RK09 = "Potentiometer_THT:Potentiometer_Alps_RK09L_Double_Vertical"
FP_MARK = "GAS_Parts:TemplateMark_1mm"
FP_FSJ = "GAS_Parts:Jack_3.5mm_PJ-301C_Vertical"
MPN_SPDT = "1MS3T1B1M2QES-5"      # SPDT ON-OFF-ON, PC pins; LCSC C908270
MPN_DPDT = "1MD3T1B1M2QES"        # DPDT ON-OFF-ON, PC pins


def header_nets(mod, ref):
    b = mod.build()
    p = next(p for p in b.parts if p["ref"] == ref)
    pins = p["units"][1]
    return [pins[str(i + 1)] for i in range(len(pins))]


def place_header(b, ref, X, Y, n, pitch=2.5, side="B"):
    x, y = K(X, Y)
    half = (n - 1) * pitch / 2
    b.fixed[ref] = (x + half if side == "B" else x - half, y, 0, side)


def wirepads(b, ref, label, nets, X, Y, block, vertical=True):
    n = len(nets)
    b.CONN(ref, label, f"GAS_Parts:WirePads_1x{n:02d}_P3.0mm_D1.2mm", nets, block, DNP="yes",
           Description="hand-wired pads (no part fitted)")
    x, y = K(X, Y)
    L = (n - 1) * 3.0
    b.fixed[ref] = ((x, y + L / 2, 90, "F") if vertical else (x - L / 2, y, 0, "F"))


def build():
    b = Board("control-deck", "GAS Rev C - control deck (7 toggles, 6 dual pots, DC jack, harness headers)",
              ["6 in round, controls face the endcap, headers on the back",
               "Pot headers bottom half, switch headers top half: only FS_TIP crosses the jack bar",
               "HPF / LPF 4-gang pots ride on filter-pot risers through the two capsule windows",
               "Bare board = endcap drilling template"], date="2026-09-21")
    b.outline = (2 * R, 2 * R)
    b.power_nets = {"+5VAUX", "VIN_RAW", "PGND"}     # AGND stays thin, the pour carries it
    # the combo jack bodies and the two filter-pot risers (pot + carrier board) pass through this deck
    b.shape = dict(circle=(R, R, R),
                   cutouts=[cut_rect(X, Y, 28.0, 32.0) for (X, Y) in JACKS.values()] + quad_cuts())

    B = "Pot headers (bottom half, 1:1 with the mating board)"
    for ref, label, mod, mref, (X, Y) in (
            ("P1", "to io-board P4 (Vol, Output pots)", io_board, "P4", (-26.0, -16.0)),
            ("P2", "to circuit-board P7 (Ext Mix, Feedback pots)", circuit_board, "P7", (26.0, -16.0)),
            ("P3", "to io-board P5 (Wet/Dry pot)", io_board, "P5", (-18.0, -56.0)),
            ("P4", "to circuit-board P9 (Gain pot)", circuit_board, "P9", (18.0, -56.0))):
        nets = header_nets(mod, mref)
        b.XH(ref, label, nets, B)
        place_header(b, ref, X, Y, len(nets))

    B = "Switch headers and DC (top half)"
    for ref, label, mod, mref, (X, Y) in (
            ("P5", "to io-board P8 (Source, Tube, Tape switch lines)", io_board, "P8", (-34.0, 56.0)),
            ("P6", "to circuit-board P8 (Dirt, FB Dyn, MEGAVERB, FB Phase)", circuit_board, "P8", (-10.0, 56.0)),
            ("P7", "to tank-board P5 (Ext tanks toggle)", tank_board, "P5", (12.0, 56.0))):
        nets = header_nets(mod, mref)
        b.XH(ref, label, nets, B)
        place_header(b, ref, X, Y, len(nets))
    b.XH("P8", "FOOTSWITCH (to jack-board P4): tip, sleeve", ["FS_TIP", "AGND"], B)
    place_header(b, "P8", 40.0, 56.0, 2)
    b.VH("P9", "DC OUT (to power-board P1): centre +, sleeve", ["VIN_RAW", "PGND"], B,
         Description="24-30 V from the DC jack J5, JST VH 3.96 mm")
    place_header(b, "P9", 28.0, 56.0, 2, pitch=3.96)
    b.add("J5", "Connector:Barrel_Jack_Switch", "DC IN 24-30 V centre +", FP_DCJ,
          {1: {"1": "VIN_RAW", "2": "PGND", "3": "PGND"}}, B, pinmap={"1": ["1"], "2": ["3"], "3": ["2"]},
          MPN="PJ-064B", Manufacturer="Same Sky")
    b.fixed["J5"] = K(*DC) + (0, "F")

    B = "Footswitch jack (3.5 mm TRS, PCB mounted)"
    b.add("J6", "Connector_Audio:AudioJack3", "FOOTSW 3.5 mm", FP_FSJ,
          {1: {"T": "FS_TIP", "R": "AGND", "S": "AGND"}}, B,
          MPN="PJ-301C", Manufacturer="XKB Connection",
          Description="vertical 3.5 mm TRS, M6 bushing, LCSC C692433. Ring tied to sleeve so a TS or TRS "
                      "footswitch cable both work; tip open or unplugged = effect ON")
    b.fixed["J6"] = K(*FS) + (0, "F")

    B = "Toggles (bat up closes 2-3, C&K 7000 convention)"
    def sw(ref, val, pins, dpdt=False):
        if dpdt:
            b.add(ref, "Switch:SW_DPDT_x2", val, FP_DPDT, pins, B, MPN=MPN_DPDT, Manufacturer="Dailywell")
        else:
            b.add(ref, "Switch:SW_SPDT", val, FP_SPDT, {1: pins}, B, MPN=MPN_SPDT, Manufacturer="Dailywell")
        x, y = K(*TOGGLES[ref])
        b.fixed[ref] = (x, y, 0, "F")
    sw("S1", "Source: up Mono>Stereo / centre Stereo / down MEGAVERB", {"1": "CTL_MEGA", "2": "+5VAUX", "3": "CTL_MONO"})
    sw("S5", "Tube: up on / centre and down off (Vol section)", {"1": None, "2": "+5VAUX", "3": "CTL_TUBE"})
    sw("S6", "Dirt: up on / centre and down off (Gain section)", {"1": None, "2": "+5VAUX", "3": "CTL_DIRT"})
    sw("S7", "Tape: up on / centre and down off (Output section)", {"1": None, "2": "+5VAUX", "3": "CTL_TAPE"})
    sw("S2", "Ext tanks: up Series / centre Off / down Parallel",
       {1: {"1": "CTL_EXT_A", "2": "+5VAUX", "3": "CTL_EXT_A"}, 2: {"4": "CTL_EXT_B", "5": "+5VAUX", "6": None}}, dpdt=True)
    sw("S3", "FB Dyn: up Comp / centre Off / down Limit", {"1": "CTL_LIMIT", "2": "+5VAUX", "3": "CTL_COMP"})
    sw("S4", "FB Phase: up normal / centre normal / down inverted", {"1": "CTL_FB_INV", "2": "+5VAUX", "3": None})

    B = "Pots (Alps RK09L dual 10k lin, CW = pins 3 / 6, centre detent)"
    pots = [("VR1", "Vol", ("VOL_L_LO", "VOL_L_W", "VOL_L_HI"), ("VOL_R_LO", "VOL_R_W", "VOL_R_HI")),
            ("VR3", "Gain", ("GAIN_L_LO", "GAIN_L_W", "GAIN_L_HI"), ("GAIN_R_LO", "GAIN_R_W", "GAIN_R_HI")),
            ("VR5", "Output", ("OUT_L_LO", "OUT_L_W", "OUT_L_HI"), ("OUT_R_LO", "OUT_R_W", "OUT_R_HI")),
            ("VR6", "Ext Mix", ("AGND", "EXM_L_W", "SEC_BUF_L"), ("AGND", "EXM_R_W", "SEC_BUF_R")),
            ("VR7", "Feedback", ("AGND", "FBP_L_W", "WET_RAW_L"), ("AGND", "FBP_R_W", "WET_RAW_R")),
            ("VR8", "Wet/Dry (CW = wet)", ("L_PROG", "WD_L_W", "WET_L"), ("R_PROG", "WD_R_W", "WET_R"))]
    for ref, label, (a1, a2, a3), (c1, c2, c3) in pots:
        b.add(ref, "Device:R_Potentiometer_Dual_Separate", label, FP_RK09,
              {1: {"1": a1, "2": a2, "3": a3}, 2: {"4": c1, "5": c2, "6": c3}}, B,
              MPN="RK09L1240015", Manufacturer="Alps Alpine",
              Description="dual 10k linear, vertical, 15 mm shaft, centre detent (marks 0 dB on Vol / Gain / Output)")
        px, py, deg, _ = rk09_place(*DUALS[ref], prefer=90 if ref in ("VR6", "VR7", "VR8") else None)
        b.fixed[ref] = (px, py, deg, "F")

    for n in ("+5VAUX", "AGND", "VIN_RAW", "PGND"):
        b.PWRFLAG(n)

    t = []
    # sgn: -1 puts the label above the part on the panel, +1 below. Outer-arc parts get their label on the
    # inboard side so no text is clipped by the board edge.
    lab = [("SRC 6.5", TOGGLES["S1"], 1), ("TUBE 6.5", TOGGLES["S5"], -1), ("DIRT 6.5", TOGGLES["S6"], -1),
           ("TAPE 6.5", TOGGLES["S7"], -1), ("EXT 6.5", TOGGLES["S2"], -1), ("FBDYN 6.5", TOGGLES["S3"], -1),
           ("PHASE 6.5", TOGGLES["S4"], 1), ("DC 8.2", DC, 1), ("FOOTSW 6.4", FS, -1),
           ("VOL 9.5", DUALS["VR1"], 1), ("GAIN 9.5", DUALS["VR3"], -1), ("OUTPUT 9.5", DUALS["VR5"], 1),
           ("EXT MIX 9.5", DUALS["VR6"], 1), ("FEEDBACK 9.5", DUALS["VR7"], 1), ("WET/DRY 9.5", DUALS["VR8"], 1),
           ("HPF 7.5", (-46.0, -30.5), 0), ("LPF 7.5", (46.0, -30.5), 0)]   # clear of the riser windows
    for txt, (X, Y), sgn in lab:
        x, y = K(X, Y)
        t.append((x, y + sgn * 9.5, txt, 1.2, "F.SilkS"))
    for (X, Y) in list(DUALS.values()) + [DC, FS] + list(QUADS.values()) + list(TOGGLES.values()):
        x, y = K(X, Y)
        t.append((x, y, "+", 3.0, "F.SilkS"))      # hole centre mark for the drilling template
    for j, (X, Y) in JACKS.items():
        x, y = K(X, Y)
        t.append((x, y - 17.5, f"{j} 24 + 2x3.2", 1.2, "F.SilkS"))
    t.append(K(0.0, -67.0) + ("GAS REV C CONTROL DECK", 1.2, "F.SilkS"))
    t.append(K(0.0, -71.0) + ("ILLICIT APOTHECARY - hole dia in mm", 1.2, "F.SilkS"))
    b.texts = t
    b.gap = 1.0
    b.passes = 150
    b.no_gap_retry = True
    b.route_tries = 3
    b.edge_band = 0.35
    b.edge_clearance = 0.3
    return b
