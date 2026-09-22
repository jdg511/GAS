"""GAS Rev C jack-board (jack deck behind the endcap, 2026-09-17).

4 x Neutrik NCJ6FI-V vertical combo jacks (IN L, IN R, OUT L, OUT R) with:
- Input per channel: XLR 2 + 1/4 tip = HOT, XLR 3 = COLD, 1/4 ring AC-coupled (10 uF) into COLD.
  1 M ohm per leg (OPA1642 JFET followers), so a guitar always sees a Hi-Z input; the buffered HOT / COLD pair
  goes to the io-board differential receiver over a short harness.
- TS / TRS sense per input: the 1/4 ring gets 0.5 V through 10k (bootstrapped from the cold follower so it does not
  load the cold leg at audio). A TS plug shorts ring to sleeve (0 V) -> INST. XLR, nothing plugged, or TRS from a
  capacitor or transformer coupled balanced output -> LINE. LMV393 with hysteresis (0.089 / 0.116 V).
  CTL_INST_L / CTL_INST_R (+5 V relay drive) go to the io-board: INST = +12 dB input gain and -12 dB output pad.
  Known limit: a DC-coupled electronically balanced TRS output reads as a short (INST). Use the XLR input for it.
- Footswitch (optional TS or TRS latching switch, tip to sleeve): open or unplugged = effect ON,
  closed = bypass with TRAILS (CTL_BYP -> io-board K7 mutes the send into the tanks; tails and feedback ring out,
  dry level unchanged). Fender style.
- K1 / K2 hard bypass at the jacks: de-energised (power off, first ~3 s after power on) the input jack is wired
  straight to the output jack (true bypass, no thump at power on). JP1 closed = the footswitch also drops K1/K2
  (true bypass footswitch, cuts tails); open (default) = trails footswitch.
"""
from core import *
from common import *
from panel_geom import *

FP_SOT363 = "Package_TO_SOT_SMD:SOT-23-6"
FP_COMBO_V = "Connector_Audio:Jack_XLR-6.35mm_Neutrik_NCJ6FI-V_Vertical"
FP_SJ = "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm"


def combo(b, ref, label, hot, cold, ring, block):
    nets = {"1": "AGND", "2": hot, "3": cold, "G": "AGND", "T": hot, "R": ring, "S": "AGND"}
    b.add(ref, "Connector_Audio:NCJ6FI-V", label, FP_COMBO_V, {1: {k: nets[k] for k in ("1", "2", "3", "G")},
                                                           2: {k: nets[k] for k in ("R", "S", "T")}}, block,
          MPN="NCJ6FI-V", Manufacturer="Neutrik")


def clamp(b, n, node, block):
    b.D(f"D{n}", "1N4148W", node, "+15VA", block, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")
    b.D(f"D{n + 1}", "1N4148W", "-15VA", node, block, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")


def pfet(b, ref, gate, drain, block, **p):
    b.add(ref, "Transistor_FET:AO3401A", "AO3401A", FP_SOT23, {1: {"1": gate, "2": "+5VAUX", "3": drain}}, block,
          MPN="AO3401A", Manufacturer="Alpha & Omega Semiconductor", **p)


def build():
    b = Board("jack-board", "GAS Rev C - jack-board (combo jacks, Hi-Z buffers, TS/TRS sense, footswitch, hard bypass)",
              ["IN: 1M per leg JFET followers; 1/4 ring sense: TS = instrument (+12 dB in, -12 dB out), else line",
               "3.5 mm footswitch tip-sleeve: open/unplugged = ON, closed = bypass with trails (JP1 closed = true bypass)",
               "K1/K2: power off or first 3 s = input jack hard-wired to output jack"], date="2026-09-17")
    b.outline = (2 * R, 2 * R)
    # jack deck: 6 in circle below the control-deck header rows
    # 2026-09-21b: the footswitch jack is now PCB mounted on the control deck, so its 21 mm window is gone;
    # the only cut-outs left are the two plug windows for the control-deck pot headers P1 / P2.
    b.shape = dict(circle=(R, R, R), clip=(0, K(0, JACK_DECK_TOP_Y)[1], 2 * R, K(0, JACK_DECK_BOTTOM_Y)[1]),
                   cutouts=[cut_rect(X, Y, 34.0, 10.0) for (X, Y) in POT_HEADERS.values()])   # control-deck plugs
    b.power_nets = {"+15VA", "-15VA", "+5VAUX"}   # AGND by pour
    B = "Jacks and connectors"
    combo(b, "J1", "IN L", "INL_HOT_J", "INL_XC", "INL_RING", B)
    combo(b, "J2", "IN R", "INR_HOT_J", "INR_XC", "INR_RING", B)
    combo(b, "J3", "OUT L", "OUTL_HOT_J", "OUTL_COLD_J", "OUTL_COLD_J", B)
    combo(b, "J4", "OUT R", "OUTR_HOT_J", "OUTR_COLD_J", "OUTR_COLD_J", B)
    for j, (X, Y) in JACKS.items():
        x, y = K(X, Y)
        b.fixed[j] = (x + 6.15, y, 0, "F")      # NCJ6FI-V footprint axis is at (-6.15, 0)
    for ref, (X, Y) in (("H1", (-68.0, 5.0)), ("H2", (68.0, 5.0))):
        b.add(ref, "Mechanical:MountingHole", "M3 sled bracket", "MountingHole:MountingHole_3.2mm_M3", {1: {}}, "Mechanical",
              Description="M3 to the aluminium angle on the front of the sled plate (nylon washers, no ground)")
        x, y = K(X, Y)
        b.fixed[ref] = (x, y, 0, "F")
    for ref, (X, Y) in (("P1", (48.0, 38.0)), ("P2", (14.0, 38.0)), ("P3", (-20.0, 38.0)), ("P4", (-34.0, 38.0))):
        x, y = K(X, Y)
        b.fixed[ref] = (x, y, 0, "B")
    power_in(b, "P1", B)
    b.XH("P2", "AUDIO (to io-board P6)", ["IN_L_HOT", "IN_L_COLD", "AGND", "IN_R_HOT", "IN_R_COLD", "AGND",
                                          "OUT_L_HOT", "OUT_L_COLD", "AGND", "OUT_R_HOT", "OUT_R_COLD", "AGND"], B)
    b.XH("P3", "MODE (to io-board P7)", ["CTL_INST_L", "CTL_INST_R", "CTL_BYP", "AGND"], B,
         Description="+5 V relay coil drive lines")
    b.XH("P4", "FOOTSWITCH (from control-deck P8, the 3.5 mm jack: tip, sleeve)", ["FS_TIP", "AGND"], B)

    for ch, n, U in (("L", 10, "U1"), ("R", 30, "U2")):
        B = f"Input {ch}: Hi-Z followers"
        c = f"IN{ch}"
        b.R(f"R{n}1", "1k", f"{c}_HOT_J", f"{c}_HS", B)
        b.R(f"R{n}2", "1k", f"{c}_XC", f"{c}_CS", B)
        b.C(f"C{n}1", "47pF", f"{c}_HS", "AGND", B, MPN="CL10C470JB8NNNC", Manufacturer="Samsung")
        b.C(f"C{n}2", "47pF", f"{c}_CS", "AGND", B, MPN="CL10C470JB8NNNC", Manufacturer="Samsung")
        clamp(b, n + 1, f"{c}_HS", B)
        clamp(b, n + 3, f"{c}_CS", B)
        b.C(f"C{n}3", "1uF C0G 50V", f"{c}_HS", f"{c}_HG", B, fp=FP_C1210, MPN="C3225C0G1H105J250AA", Manufacturer="TDK",
            Description="C0G: no microphonics or distortion at the 1 M ohm node")
        b.C(f"C{n}4", "1uF C0G 50V", f"{c}_CS", f"{c}_CG", B, fp=FP_C1210, MPN="C3225C0G1H105J250AA", Manufacturer="TDK")
        b.R(f"R{n}3", "1M", f"{c}_HG", "AGND", B, Description="1 M ohm input impedance (guitar)")
        b.R(f"R{n}4", "1M", f"{c}_CG", "AGND", B)
        b.OPA2(U, {1: (f"{c}_HG", f"{c}_HB", f"{c}_HB"), 2: (f"{c}_CG", f"{c}_CB", f"{c}_CB")}, B, value="OPA1642AIDR")
        dec(b, f"C{n}8", "+15VA", B); dec(b, f"C{n}9", "-15VA", B)
        b.R(f"R{n}5", "100R", f"{c}_HB", f"IN_{ch}_HOT", B)
        b.R(f"R{n}6", "100R", f"{c}_CB", f"IN_{ch}_COLD", B)
        B = f"Input {ch}: TS/TRS sense"
        b.C(f"C{n}5", "10uF 50V", f"{c}_RING", f"{c}_XC", B, fp=FP_C1206, MPN="CL31A106KBHNNNE", Manufacturer="Samsung",
            Description="1/4 ring into COLD; blocks the sense DC from the XLR 3 source")
        # bootstrapped 0.5 V / 10k pull-up on the ring
        b.R(f"R{n}7", "49.9k", "+5VAUX", f"{c}_PU", B)
        b.R(f"R{n}8", "5.49k", f"{c}_PU", "AGND", B, Description="0.496 V, 4.95k Thevenin")
        b.R(f"R{n}9", "4.99k", f"{c}_PU", f"{c}_RING", B)
        b.C(f"C{n}6", "10uF", f"{c}_PU", f"{c}_CB", B, fp=FP_C0805, MPN="CL21A106KAYNNNE", Manufacturer="Samsung",
            Description="bootstrap: pull-up follows the cold leg, no audio load")
        b.R(f"R{n}10", "470k", f"{c}_RING", f"{c}_SNS", B)
        b.C(f"C{n}7", "2.2uF", f"{c}_SNS", "AGND", B, fp=FP_C0805, MPN="CL21A225KAFNNNE", Manufacturer="Samsung",
            Description="1 s filter, rejects audio on the ring")
        b.R(f"R{n}11", "1M", "+5VAUX", f"{c}_TH", B)
        b.R(f"R{n}12", "18.2k", f"{c}_TH", "AGND", B)
        b.R(f"R{n}13", "3.3M", f"INST_{ch}", f"{c}_TH", B, Description="hysteresis: INST below 0.089 V, LINE above 0.116 V")
        b.C(f"C{n}10", "10nF", f"{c}_TH", "AGND", B, MPN="CL10B103KB8NNNC", Manufacturer="Samsung")
        b.R(f"R{n}14", "10k", "+5VAUX", f"INST_{ch}", B)

    B = "Mode logic and relay drivers"
    b.add("U3", "Comparator:LM393", "LMV393IDR", FP_SOIC8,
          {1: {"3": "INL_TH", "2": "INL_SNS", "1": "INST_L"}, 2: {"5": "INR_TH", "6": "INR_SNS", "7": "INST_R"},
           3: {"8": "+5VAUX", "4": "AGND"}}, B, MPN="LMV393IDR", Manufacturer="Texas Instruments")
    dec(b, "C51", "+5VAUX", B)
    b.add("U4", "74xGxx:74LVC2G04", "74LVC2G04", FP_SOT363,
          {1: {"1": "INST_L", "6": "NINST_L"}, 2: {"3": "INST_R", "4": "NINST_R"}, 3: {"5": "+5VAUX", "2": "AGND"}}, B,
          MPN="74LVC2G04GV,125", Manufacturer="Nexperia")
    dec(b, "C52", "+5VAUX", B)
    pfet(b, "Q1", "NINST_L", "CTL_INST_L", B, Description="INST L relay drive (io-board K5)")
    pfet(b, "Q2", "NINST_R", "CTL_INST_R", B, Description="INST R relay drive (io-board K6 via Mono relay K1)")

    B = "Footswitch and power-on delay"
    b.R("R51", "10k", "+5VAUX", "FS_TIP", B, Description="open or unplugged = high = effect ON")
    b.D("D51", "1N4148W", "FS_TIP", "+5VAUX", B, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")
    b.D("D52", "1N4148W", "AGND", "FS_TIP", B, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")
    b.R("R52", "10k", "FS_TIP", "FS_FILT", B)
    b.C("C53", "100nF", "FS_FILT", "AGND", B, MPN="CL10B104KB8NNNC", Manufacturer="Samsung", Description="1 ms debounce")
    b.R("R53", "10k", "FS_FILT", "FS_IN", B)
    b.R("R54", "1M", "FS_OK", "FS_IN", B)
    b.R("R55", "100k", "+5VAUX", "HALF5", B)
    b.R("R56", "100k", "HALF5", "AGND", B)
    b.R("R57", "10k", "+5VAUX", "FS_OK", B)
    B = "Power-on delay and hard bypass drive"
    b.R("R58", "3.3M", "+5VAUX", "DLY", B)
    b.C("C54", "1uF", "DLY", "AGND", B, fp=FP_C0805, MPN="CL21B105KBFNNNE", Manufacturer="Samsung", Description="about 3.4 s")
    b.D("D53", "1N4148W", "DLY", "+5VAUX", B, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated", Description="fast reset at power off")
    b.R("R59", "100k", "+5VAUX", "DLYREF", B)
    b.R("R60", "180k", "DLYREF", "AGND", B)
    b.R("R61", "10k", "+5VAUX", "HARD_EN", B)
    b.add("U5", "Comparator:LM393", "LMV393IDR", FP_SOIC8,
          {1: {"3": "DLY", "2": "DLYREF", "1": "HARD_EN"}, 2: {"5": "FS_IN", "6": "HALF5", "7": "FS_OK"},
           3: {"8": "+5VAUX", "4": "AGND"}}, B, MPN="LMV393IDR", Manufacturer="Texas Instruments")
    dec(b, "C55", "+5VAUX", B)
    b.add("JP1", "Jumper:SolderJumper_2_Open", "TRUE BYP", FP_SJ, {1: {"1": "FS_OK", "2": "HARD_EN"}}, B,
          Description="open (default): footswitch = trails bypass. Closed: footswitch = true bypass (K1/K2)")
    pfet(b, "Q3", "FS_OK", "CTL_BYP", B, Description="trails bypass relay drive (io-board K7 mutes the tank send)")
    b.add("Q4", "Transistor_FET:2N7002", "2N7002", FP_SOT23, {1: {"1": "HARD_EN", "2": "AGND", "3": "HARD_G"}}, B,
          MPN="2N7002-7-F", Manufacturer="Diodes Incorporated")
    b.R("R62", "10k", "+5VAUX", "HARD_G", B)
    pfet(b, "Q5", "HARD_G", "CTL_HARD", B, Description="K1/K2 coils: on = normal, off = hard bypass")
    b.R("R63", "10k", "CTL_HARD", "AGND", B)

    B = "Hard bypass relay L"
    b.RELAY("K1", "CTL_HARD", "OUTL_HOT_J", "INL_HOT_J", "OUT_L_HOT", "OUTL_COLD_J", "INL_XC", "OUT_L_COLD", B,
            Description="L: NC = IN L jack to OUT L jack, NO = io-board driver")
    B = "Hard bypass relay R"
    b.RELAY("K2", "CTL_HARD", "OUTR_HOT_J", "INR_HOT_J", "OUT_R_HOT", "OUTR_COLD_J", "INR_XC", "OUT_R_COLD", B,
            Description="R: NC = IN R jack to OUT R jack, NO = io-board driver")
    B = "Bulk decoupling"
    b.C("C56", "10uF 25V", "+15VA", "AGND", B, fp=FP_C0805, MPN="CL21A106KAYNNNE", Manufacturer="Samsung")
    b.C("C57", "10uF 25V", "AGND", "-15VA", B, fp=FP_C0805, MPN="CL21A106KAYNNNE", Manufacturer="Samsung")
    b.C("C58", "10uF 25V", "+5VAUX", "AGND", B, fp=FP_C0805, MPN="CL21A106KAYNNNE", Manufacturer="Samsung")
    for n in ("+15VA", "-15VA", "+5VAUX", "AGND"):
        b.PWRFLAG(n)
    b.texts = [(R, K(0, -5.5)[1], "GAS REV C JACK DECK - ILLICIT APOTHECARY", 1.2, "F.SilkS")]
    b.block_pref = {"Hard bypass relay L": (24.0, 100.0), "Hard bypass relay R": (108.0, 100.0),
                    "Bulk decoupling": (66.0, 108.0)}
    b.place_margin = 1.6
    b.gap = 0.9
    b.passes = 100
    b.route_tries = 3
    b.edge_band = 0.35
    b.edge_clearance = 0.3
    return b
