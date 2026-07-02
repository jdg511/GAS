#!/usr/bin/env python3
"""Generate the GAS Rev A crossfade/feedback/wet schematic (production + sim).

Per hardware/rev-a-crossfade-feedback-wet-schematic-ready-definition.md:
- U301 OPA1679 quad: A/B inverting crossfade summers, C/D inverting feedback drivers
- mirrored crossfade pot landing (XFD_x_HI/LO tied to TANK_MIX_L/R)
- direct wet return FILTCLIP_OUT -> R341/342 -> WET_SUM (never phase-flipped)
- feedback phase selection via K301 (Omron G5V-2 12V DPDT): coil from +15VA
  through R351, grounded by the panel SW702 line CTL_FB_INV.
  De-energized (NC) = normal phase, energized = inverted phase.
  (The old BOM had no part at all for the phase selection; this adds it.)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

OUT_DIR = g.OUT_DIR
SIM_DIR = os.path.join(OUT_DIR, "sim", "crossfade-feedback-wet-sim")
C, res, cap = g.C, g.res, g.cap

FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_G5V2 = "Relay_THT:Relay_DPDT_Omron_G5V-2"
FP_XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
FP_XH10 = "Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical"

OPA4_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1679X4",
            "Sim.Device": "SUBCKT",
            "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vp 5=in2p 6=in2n 7=out2 "
                        "8=out3 9=in3n 10=in3p 11=vn 12=in4p 13=in4n 14=out4"}

def opa4(ref, unit, pins):
    return C(ref, "Amplifier_Operational", "OPA1679", "OPA1679IDR", FP_SOIC14,
             {unit: pins}, sim=OPA4_SIM)

def xh(ref, n, nets, nosim=True, h=30.48):
    return C(ref, "Connector_Generic", "Conn_01x%02d" % n, ref,
             FP_XH3 if n == 3 else FP_XH10,
             {1: {str(i + 1): nets[i] for i in range(n)}}, nosim=nosim, h=h)

SECTIONS = [
    ("SIGNAL HEADERS", [
        xh("P301", 3, ["TANK_MIX_L", "AGND", "TANK_MIX_R"]),
        xh("P302", 3, ["XFADE_OUT_L", "AGND", "XFADE_OUT_R"]),
        xh("P303", 3, ["FILTCLIP_OUT_L", "AGND", "FILTCLIP_OUT_R"]),
        xh("P304", 3, ["WET_SUM_L", "AGND", "WET_SUM_R"]),
        xh("P305", 3, ["FB_RET_L", "AGND", "FB_RET_R"]),
        xh("P307", 10, ["TANK_MIX_L", "XFD_L_WIPER", "TANK_MIX_R",
                        "TANK_MIX_R", "XFD_R_WIPER", "TANK_MIX_L",
                        "FB_L_WIPER", "FB_R_WIPER", "CTL_FB_INV", "AGND"], h=45.72),
        C("P306", "Connector_Generic", "Conn_01x03", "JXFD-PWR B3P-VH-B", g.FP_VH3,
          {1: {"1": "+15VA", "2": "AGND", "3": "-15VA"}}, nosim=True),
    ]),
    ("CROSSFADE SUMMERS (U301A/B, inverting, unity)", [
        opa4("U301", 1, {"1": "XFADE_SUM_L", "2": "N_XF_L_M", "3": "AGND"}),
        res("R301", "20k", "XFD_L_WIPER", "N_XF_L_M"),
        res("R309", "20k", "XFADE_SUM_L", "N_XF_L_M"),
        res("R311", "100", "XFADE_SUM_L", "XFADE_OUT_L"),
        opa4("U301_B", 2, {"7": "XFADE_SUM_R", "6": "N_XF_R_M", "5": "AGND"}),
        res("R302", "20k", "XFD_R_WIPER", "N_XF_R_M"),
        res("R310", "20k", "XFADE_SUM_R", "N_XF_R_M"),
        res("R312", "100", "XFADE_SUM_R", "XFADE_OUT_R"),
    ]),
    ("FINAL WET RETURN (never phase-flipped)", [
        res("R341", "100", "FILTCLIP_OUT_L", "WET_SUM_L"),
        res("R342", "100", "FILTCLIP_OUT_R", "WET_SUM_R"),
    ]),
    ("FEEDBACK DRIVERS (U301C/D, inverting)", [
        opa4("U301_C", 3, {"8": "FB_INV_L", "9": "N_FB_L_M", "10": "AGND"}),
        res("R321", "20k", "FILTCLIP_OUT_L", "N_FB_L_M"),
        res("R323", "20k", "FB_L_WIPER", "N_FB_L_M"),
        res("R325", "10k", "FB_INV_L", "N_FB_L_M"),
        cap("C321", "47p", "FB_INV_L", "N_FB_L_M", dnp=True),
        opa4("U301_D", 4, {"14": "FB_INV_R", "13": "N_FB_R_M", "12": "AGND"}),
        res("R322", "20k", "FILTCLIP_OUT_R", "N_FB_R_M"),
        res("R324", "20k", "FB_R_WIPER", "N_FB_R_M"),
        res("R326", "10k", "FB_INV_R", "N_FB_R_M"),
        cap("C322", "47p", "FB_INV_R", "N_FB_R_M", dnp=True),
    ]),
    ("FEEDBACK PHASE SELECT (K301, de-energized = normal phase)", [
        C("K301", "Relay", "G5V-2", "G5V-2 12VDC", FP_G5V2,
          {1: {"1": "N_K301_C", "16": "CTL_FB_INV",
               "4": "FB_SEL_L", "6": "FILTCLIP_OUT_L", "8": "FB_INV_L",
               "13": "FB_SEL_R", "11": "FILTCLIP_OUT_R", "9": "FB_INV_R"}},
          nosim=True, w=33, h=27.94),
        res("R351", "240", "+15VA", "N_K301_C", fp=g.FP_R1206),
        C("D301", "Device", "D", "1N4148W", g.FP_SOD123,
          {1: {"1": "N_K301_C", "2": "CTL_FB_INV"}}, nosim=True),
    ]),
    ("POWER + DECOUPLING", [
        opa4("U301_P", 5, {"4": "+15VA", "11": "-15VA"}),
        cap("C391", "100n", "+15VA", "AGND"),
        cap("C392", "100n", "-15VA", "AGND"),
        cap("C393", "22u", "+15VA", "AGND", fp=g.FP_C1210),
        cap("C394", "22u", "-15VA", "AGND", fp=g.FP_C1210),
        C("#FLG301", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG302", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "-15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG303", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "AGND"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG304", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "CTL_FB_INV"}}, nosim=True, w=15.24, h=20.32),
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
    ("SIM: SUPPLIES + SOURCES + POT MODELS", [
        vsrc("V1", "VDC", "15V", "dc=15", "+15VA", "GND"),
        vsrc("V2", "VDC", "15V", "dc=15", "GND", "-15VA"),
        vsrc("V3", "VDC", "0V bond", "dc=0", "AGND", "GND"),
        vsrc("V4", "VSIN", "0.5Vpk 1kHz", "dc=0 ampl=0.5 f=1k ac=1",
             "TANK_MIX_L", "AGND"),
        vsrc("V5", "VSIN", "0.5Vpk 700Hz", "dc=0 ampl=0.5 f=700", "TANK_MIX_R", "AGND"),
        vsrc("V6", "VSIN", "0.5Vpk 1k3", "dc=0 ampl=0.5 f=1.3k", "FILTCLIP_OUT_L", "AGND"),
        vsrc("V7", "VSIN", "0.5Vpk 1k7", "dc=0 ampl=0.5 f=1.7k", "FILTCLIP_OUT_R", "AGND"),
        # dual crossfade pot at mid position (20k)
        res("RP1", "10k", "TANK_MIX_L", "XFD_L_WIPER"),
        res("RP2", "10k", "XFD_L_WIPER", "TANK_MIX_R"),
        res("RP3", "10k", "TANK_MIX_R", "XFD_R_WIPER"),
        res("RP4", "10k", "XFD_R_WIPER", "TANK_MIX_L"),
        # feedback pots at mid position
        res("RP5", "10k", "FILTCLIP_OUT_L", "FB_L_WIPER"),
        res("RP6", "10k", "FB_L_WIPER", "AGND"),
        res("RP7", "10k", "FILTCLIP_OUT_R", "FB_R_WIPER"),
        res("RP8", "10k", "FB_R_WIPER", "AGND"),
        # relay is excluded from sim: tie normal-phase path
        jsim("RS1", "FILTCLIP_OUT_L", "FB_SEL_L"),
        jsim("RS2", "FILTCLIP_OUT_R", "FB_SEL_R"),
        # loads
        res("RL1", "10k", "XFADE_OUT_L", "AGND"),
        res("RL2", "10k", "XFADE_OUT_R", "AGND"),
        res("RL3", "10k", "WET_SUM_L", "AGND"),
        res("RL4", "10k", "WET_SUM_R", "AGND"),
        res("RL5", "10k", "FB_RET_L", "AGND"),
        res("RL6", "10k", "FB_RET_R", "AGND"),
    ]),
]

# feedback sends need the selected-source isolators wired from FB_SEL nets
SECTIONS[4][1].extend([
    res("R331", "100", "FB_SEL_L", "FB_RET_L"),
    res("R332", "100", "FB_SEL_R", "FB_RET_R"),
])

DIRECTIVES = ".tran 10u 30m\n.options savecurrents"

OPA1679X4 = """* OPA1679 quad audio op amp, behavioral macro model
* Aol ~100 dB, GBW ~10 MHz single pole, swing to ~1 V of rails, Rout ~30
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
"""

def main():
    prod = g.build(False, SECTIONS, SIM_SECTIONS, "crossfade-feedback-wet",
                   "GAS Rev A - Crossfade Feedback Wet", DIRECTIVES)
    with open(os.path.join(OUT_DIR, "crossfade-feedback-wet.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = g.build(True, SECTIONS, SIM_SECTIONS, "crossfade-feedback-wet",
                     "GAS Rev A - Crossfade Feedback Wet", DIRECTIVES)
    with open(os.path.join(SIM_DIR, "crossfade-feedback-wet-sim.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "crossfade-feedback-wet-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "crossfade-feedback-wet-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    with open(os.path.join(SIM_DIR, "gas-models.lib"), "w", encoding="utf-8") as f:
        f.write(OPA1679X4)
    print("Wrote crossfade-feedback-wet production + sim. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()
