#!/usr/bin/env python3
"""Generate the GAS Rev A input/output board schematic (production + sim).

Per hardware/rev-a-io-schematic-ready-definition.md:
- U1 OPA1644 quad (TL074 symbol, identical pinout): A/B unity diff receivers,
  C/D post-mono buffers. Mono switch landing P6: A=L_RX, B=R_RX, C -> U1D+.
- Dry + wet-send fanout from L_PROG/R_PROG through 100R isolators.
- P5 raw 6-wire wet/dry landing: HI=program, LO=wet return, wiper buffered
  by U2A/U2B (inverting unity per spec).
- Fully active balanced outputs: follower hot leg + inverting cold leg
  (U3/U4 OPA1656), 49.9R build-outs, 600R-capable.
- Panel combo jacks (NCJ6FI-S) are hand-wired panel parts; the board carries
  3-pin XH landings J1-J4 (P, N, AGND) per the Panel-DNP assembly scope.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

OUT_DIR = g.OUT_DIR
SIM_DIR = os.path.join(OUT_DIR, "sim", "io-board-sim")
C, res, cap = g.C, g.res, g.cap

FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
FP_XH6 = "Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical"

QUAD_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1679X4",
            "Sim.Device": "SUBCKT",
            "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vp 5=in2p 6=in2n 7=out2 "
                        "8=out3 9=in3n 10=in3p 11=vn 12=in4p 13=in4n 14=out4"}
DUAL_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1656X2",
            "Sim.Device": "SUBCKT",
            "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vn 5=in2p 6=in2n 7=out2 8=vp"}

def quad(ref, unit, pins):
    return C(ref, "Amplifier_Operational", "TL074", "OPA1644AIDR", FP_SOIC14,
             {unit: pins}, sim=QUAD_SIM)

def dual(ref, unit, pins):
    return C(ref, "Amplifier_Operational", "OPA1656ID", "OPA1656IDR", g.FP_SOIC8,
             {unit: pins}, sim=DUAL_SIM)

def xh(ref, n, nets, fp=FP_XH3, nosim=True, h=30.48, val=None):
    return C(ref, "Connector_Generic", "Conn_01x%02d" % n, val or ref, fp,
             {1: {str(i + 1): nets[i] for i in range(n)}}, nosim=nosim, h=h)

def prec(ref, net1, net2):
    """10k 0.1% receiver resistor."""
    c = res(ref, "10k", net1, net2)
    c["sim"]["Tolerance"] = "0.1%"
    return c

SECTIONS = [
    ("PANEL JACK LANDINGS (NCJ6FI-S combo jacks, hand-wired)", [
        xh("J1", 3, ["IN_BAL_L_P", "IN_BAL_L_N", "AGND"], val="to L IN combo jack"),
        xh("J2", 3, ["IN_BAL_R_P", "IN_BAL_R_N", "AGND"], val="to R IN combo jack"),
        xh("J3", 3, ["OUT_BAL_L_P", "OUT_BAL_L_N", "AGND"], val="to L OUT combo jack"),
        xh("J4", 3, ["OUT_BAL_R_P", "OUT_BAL_R_N", "AGND"], val="to R OUT combo jack"),
    ]),
    ("HEADERS", [
        C("P1", "Connector_Generic", "Conn_01x03", "JIO-PWR B3P-VH-B", g.FP_VH3,
          {1: {"1": "+15VA", "2": "AGND", "3": "-15VA"}}, nosim=True),
        xh("P2", 3, ["WET_SEND_L", "AGND", "WET_SEND_R"]),
        xh("P3", 3, ["WET_SUM_L", "AGND", "WET_SUM_R"]),
        xh("P4", 3, ["DRY_L", "AGND", "DRY_R"]),
        xh("P5", 6, ["L_PROG", "WD_L_WIPER", "WET_SUM_L",
                     "R_PROG", "WD_R_WIPER", "WET_SUM_R"], fp=FP_XH6, h=35.56),
        xh("P6", 3, ["L_RX", "MONO_C", "R_RX"]),
    ]),
    ("BALANCED RECEIVERS (unity differential)", [
        res("R1", "100", "IN_BAL_L_P", "N_INL_P"),
        res("R2", "100", "IN_BAL_L_N", "N_INL_N"),
        cap("C1", "220p", "IN_BAL_L_P", "AGND", dnp=True),
        cap("C2", "220p", "IN_BAL_L_N", "AGND", dnp=True),
        prec("R11", "N_INL_N", "N_U1A_M"),
        prec("R12", "L_RX", "N_U1A_M"),
        prec("R13", "N_INL_P", "N_U1A_P"),
        prec("R14", "N_U1A_P", "AGND"),
        quad("U1", 1, {"1": "L_RX", "2": "N_U1A_M", "3": "N_U1A_P"}),
        res("R3", "100", "IN_BAL_R_P", "N_INR_P"),
        res("R4", "100", "IN_BAL_R_N", "N_INR_N"),
        cap("C3", "220p", "IN_BAL_R_P", "AGND", dnp=True),
        cap("C4", "220p", "IN_BAL_R_N", "AGND", dnp=True),
        prec("R15", "N_INR_N", "N_U1B_M"),
        prec("R16", "R_RX", "N_U1B_M"),
        prec("R17", "N_INR_P", "N_U1B_P"),
        prec("R18", "N_U1B_P", "AGND"),
        quad("U1_B", 2, {"7": "R_RX", "6": "N_U1B_M", "5": "N_U1B_P"}),
    ]),
    ("MONO ROUTING + PROGRAM BUFFERS + FANOUT", [
        quad("U1_C", 3, {"8": "L_PROG", "9": "L_PROG", "10": "L_RX"}),
        quad("U1_D", 4, {"14": "R_PROG", "13": "R_PROG", "12": "MONO_C"}),
        # Review finding F2: default the right channel to stereo if the mono
        # switch has a center-off position or the harness is unplugged;
        # otherwise U1D+ floats.
        res("R25", "1Meg", "MONO_C", "R_RX"),
        res("R21", "100", "L_PROG", "DRY_L"),
        res("R22", "100", "L_PROG", "WET_SEND_L"),
        res("R23", "100", "R_PROG", "DRY_R"),
        res("R24", "100", "R_PROG", "WET_SEND_R"),
    ]),
    ("WET/DRY BLEND BUFFERS", [
        dual("U2", 1, {"1": "L_BLEND", "2": "N_U2A_M", "3": "AGND"}),
        res("R31", "20k", "WD_L_WIPER", "N_U2A_M"),
        res("R35", "20k", "L_BLEND", "N_U2A_M"),
        dual("U2_B", 2, {"7": "R_BLEND", "6": "N_U2B_M", "5": "AGND"}),
        res("R32", "20k", "WD_R_WIPER", "N_U2B_M"),
        res("R36", "20k", "R_BLEND", "N_U2B_M"),
    ]),
    ("BALANCED OUTPUT DRIVERS (+4dBu, 600R-capable)", [
        dual("U3", 1, {"1": "N_HOT_L", "2": "N_HOT_L", "3": "L_BLEND"}),
        res("R49", "49.9", "N_HOT_L", "OUT_BAL_L_P"),
        dual("U3_B", 2, {"7": "N_COLD_L", "6": "N_U3B_M", "5": "AGND"}),
        res("R43", "10k", "L_BLEND", "N_U3B_M"),
        res("R44", "10k", "N_COLD_L", "N_U3B_M"),
        res("R50", "49.9", "N_COLD_L", "OUT_BAL_L_N"),
        dual("U4", 1, {"1": "N_HOT_R", "2": "N_HOT_R", "3": "R_BLEND"}),
        res("R59", "49.9", "N_HOT_R", "OUT_BAL_R_P"),
        dual("U4_B", 2, {"7": "N_COLD_R", "6": "N_U4B_M", "5": "AGND"}),
        res("R53", "10k", "R_BLEND", "N_U4B_M"),
        res("R54", "10k", "N_COLD_R", "N_U4B_M"),
        res("R60", "49.9", "N_COLD_R", "OUT_BAL_R_N"),
    ]),
    ("POWER + DECOUPLING", [
        quad("U1_P", 5, {"4": "+15VA", "11": "-15VA"}),
        dual("U2_P", 3, {"8": "+15VA", "4": "-15VA"}),
        dual("U3_P", 3, {"8": "+15VA", "4": "-15VA"}),
        dual("U4_P", 3, {"8": "+15VA", "4": "-15VA"}),
        cap("C91", "100n", "+15VA", "AGND"),
        cap("C92", "100n", "-15VA", "AGND"),
        cap("C93", "100n", "+15VA", "AGND"),
        cap("C94", "100n", "-15VA", "AGND"),
        cap("C95", "100n", "+15VA", "AGND"),
        cap("C96", "100n", "-15VA", "AGND"),
        cap("C97", "100n", "+15VA", "AGND"),
        cap("C98", "100n", "-15VA", "AGND"),
        cap("C99", "22u", "+15VA", "AGND", fp=g.FP_C1210),
        cap("C100", "22u", "-15VA", "AGND", fp=g.FP_C1210),
        C("#FLG1", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG2", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "-15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG3", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "AGND"}}, nosim=True, w=15.24, h=20.32),
    ]),
]

def vsrc(ref, symname, value, params, n1, n2):
    return C(ref, "Simulation_SPICE", symname, value, "",
             {1: {"1": n1, "2": n2}},
             sim={"Sim.Device": "V",
                  "Sim.Type": "DC" if symname == "VDC" else "SIN",
                  "Sim.Params": params}, w=20.32)

def jsim(ref, n1, n2):
    c = res(ref, "0", n1, n2)
    c["sim"] = {"Sim.Device": "R", "Sim.Params": "r=10m"}
    return c

SIM_SECTIONS = [
    ("SIM: BALANCED DRIVE, STEREO MODE, POTS MID, 600R LOADS", [
        vsrc("V1", "VDC", "15V", "dc=15", "+15VA", "GND"),
        vsrc("V2", "VDC", "15V", "dc=15", "GND", "-15VA"),
        vsrc("V3", "VDC", "0V bond", "dc=0", "AGND", "GND"),
        vsrc("V4", "VSIN", "+0.5 1kHz", "dc=0 ampl=0.5 f=1k", "IN_BAL_L_P", "AGND"),
        vsrc("V5", "VSIN", "-0.5 1kHz", "dc=0 ampl=-0.5 f=1k", "IN_BAL_L_N", "AGND"),
        vsrc("V6", "VSIN", "+0.5 1kHz", "dc=0 ampl=0.5 f=1k", "IN_BAL_R_P", "AGND"),
        vsrc("V7", "VSIN", "-0.5 1kHz", "dc=0 ampl=-0.5 f=1k", "IN_BAL_R_N", "AGND"),
        vsrc("V8", "VSIN", "0.3 500Hz", "dc=0 ampl=0.3 f=500", "WET_SUM_L", "AGND"),
        vsrc("V9", "VSIN", "0.3 500Hz", "dc=0 ampl=0.3 f=500", "WET_SUM_R", "AGND"),
        jsim("RS1", "R_RX", "MONO_C"),
        res("RP1", "10k", "L_PROG", "WD_L_WIPER"),
        res("RP2", "10k", "WD_L_WIPER", "WET_SUM_L"),
        res("RP3", "10k", "R_PROG", "WD_R_WIPER"),
        res("RP4", "10k", "WD_R_WIPER", "WET_SUM_R"),
        res("RL1", "600", "OUT_BAL_L_P", "OUT_BAL_L_N"),
        res("RL2", "600", "OUT_BAL_R_P", "OUT_BAL_R_N"),
        res("RL3", "10k", "WET_SEND_L", "AGND"),
        res("RL4", "10k", "DRY_L", "AGND"),
    ]),
]

DIRECTIVES = ".tran 10u 30m\n.options savecurrents"

MODELS = """* Behavioral op amp macro models (see board-1 notes)
.subckt OPA1679_1CH inp inn vp vn out
Rin  inp inn 1e12
Gd   0 x inp inn 1m
Rp   x 0 1e8
Cp   x 0 16p
Bout xo 0 V = min(max(V(x), V(vn)+1.0), V(vp)-1.0)
Ro   xo out 30
.ends OPA1679_1CH

.subckt OPA1679X4 out1 in1n in1p vp in2p in2n out2 out3 in3n in3p vn in4p in4n out4
XA in1p in1n vp vn out1 OPA1679_1CH
XB in2p in2n vp vn out2 OPA1679_1CH
XC in3p in3n vp vn out3 OPA1679_1CH
XD in4p in4n vp vn out4 OPA1679_1CH
Rq vp vn 7.5k
.ends OPA1679X4

.subckt OPA1656_1CH inp inn vp vn out
Rin  inp inn 1e12
Gd   0 x inp inn 1m
Rp   x 0 1e8
Cp   x 0 3p
Bout xo 0 V = min(max(V(x), V(vn)+1.2), V(vp)-1.2)
Ro   xo out 20
.ends OPA1656_1CH

.subckt OPA1656X2 out1 in1n in1p vn in2p in2n out2 vp
XA in1p in1n vp vn out1 OPA1656_1CH
XB in2p in2n vp vn out2 OPA1656_1CH
Rq vp vn 3.75k
.ends OPA1656X2
"""

def main():
    prod = g.build(False, SECTIONS, SIM_SECTIONS, "io-board",
                   "GAS Rev A - Input Output Board", DIRECTIVES)
    with open(os.path.join(OUT_DIR, "io-board.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = g.build(True, SECTIONS, SIM_SECTIONS, "io-board",
                     "GAS Rev A - Input Output Board", DIRECTIVES)
    with open(os.path.join(SIM_DIR, "io-board-sim.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "io-board-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "io-board-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    with open(os.path.join(SIM_DIR, "gas-models.lib"), "w", encoding="utf-8") as f:
        f.write(MODELS)
    print("Wrote io-board production + sim. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()
