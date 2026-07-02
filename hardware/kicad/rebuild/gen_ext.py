#!/usr/bin/env python3
"""Generate the GAS Rev A ext-tank-routing schematic (production + sim).

Per hardware/rev-a-ext-routing-schematic-ready-definition.md:
- U201 OPA1679 quad: A/B final inverting summers (primary return + scaled
  secondary + feedback reinjection), C/D secondary-send buffers.
- K201/K202 source-select relays (coil = CTL_EXT_MODE_B): NC=PRI_RET (Series),
  NO=WET_SEND (Parallel).
- K203/K204 engage relays (coil = CTL_EXT_MODE_A): pole A gates SEC_SEL ->
  SEC_DRV, pole B gates SEC_RET -> EXTMIX_HI. R211/R231 100k park the buffer
  inputs in bypass.
- Relays standardized to Omron G5V-2 DC5 (KiCad-native footprint; replaces
  the old BOM's G6K-2F-Y which has no stock KiCad symbol/footprint).
- Secondary buffers built as unity followers with a DNP gain-trim slot
  (R212/R241 left, R232/R251 right) per the deferred series-makeup item.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

OUT_DIR = g.OUT_DIR
SIM_DIR = os.path.join(OUT_DIR, "sim", "ext-tank-routing-sim")
C, res, cap = g.C, g.res, g.cap

FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_G5V2 = "Relay_THT:Relay_DPDT_Omron_G5V-2"
FP_XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
FP_XH6 = "Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical"
FP_XH10 = "Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical"
FP_VH4 = "Connector_JST:JST_VH_B4P-VH_1x04_P3.96mm_Vertical"

OPA4_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1679X4",
            "Sim.Device": "SUBCKT",
            "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vp 5=in2p 6=in2n 7=out2 "
                        "8=out3 9=in3n 10=in3p 11=vn 12=in4p 13=in4n 14=out4"}

def opa4(ref, unit, pins):
    return C(ref, "Amplifier_Operational", "OPA1679", "OPA1679IDR", FP_SOIC14,
             {unit: pins}, sim=OPA4_SIM)

def relay(ref, pins):
    return C(ref, "Relay", "G5V-2", "G5V-2 DC5", FP_G5V2,
             {1: pins}, nosim=True, w=33, h=27.94)

def fly(ref, coilnet):
    return C(ref, "Device", "D", "1N4148W", g.FP_SOD123,
             {1: {"1": coilnet, "2": "AGND"}}, nosim=True)

def xh(ref, n, nets, fp, nosim=True, h=30.48):
    return C(ref, "Connector_Generic", "Conn_01x%02d" % n, ref, fp,
             {1: {str(i + 1): nets[i] for i in range(n)}}, nosim=nosim, h=h)

SECTIONS = [
    ("HEADERS", [
        xh("P201", 3, ["WET_SEND_L", "AGND", "WET_SEND_R"], FP_XH3),
        xh("P202", 6, ["PRI_SEND_L", "PRI_RET_L", "AGND",
                       "PRI_SEND_R", "PRI_RET_R", "AGND"], FP_XH6, h=35.56),
        xh("P203", 6, ["SEC_SEND_L", "SEC_RET_L", "AGND",
                       "SEC_SEND_R", "SEC_RET_R", "AGND"], FP_XH6, h=35.56),
        xh("P204", 3, ["TANK_MIX_L", "AGND", "TANK_MIX_R"], FP_XH3),
        xh("P205", 3, ["FB_RET_L", "AGND", "FB_RET_R"], FP_XH3),
        xh("P206", 10, ["EXTMIX_L_HI", "EXTMIX_L_WIPER", "AGND",
                        "EXTMIX_R_HI", "EXTMIX_R_WIPER", "AGND",
                        "+5VAUX", "AGND", "CTL_EXT_MODE_A", "CTL_EXT_MODE_B"],
           FP_XH10, h=45.72),
        xh("P207", 4, ["+15VA", "AGND", "-15VA", "+5VAUX"], FP_VH4),
    ]),
    ("PRIMARY SEND PASS-THROUGH", [
        res("R201", "100", "WET_SEND_L", "PRI_SEND_L"),
        res("R221", "100", "WET_SEND_R", "PRI_SEND_R"),
    ]),
    ("MODE RELAYS (A=engage, B=series/parallel)", [
        relay("K201", {"1": "CTL_EXT_MODE_B", "16": "AGND",
                       "4": "SEC_SEL_L", "6": "PRI_RET_L", "8": "WET_SEND_L",
                       "13": "NC", "11": "NC", "9": "NC"}),
        relay("K202", {"1": "CTL_EXT_MODE_B", "16": "AGND",
                       "4": "SEC_SEL_R", "6": "PRI_RET_R", "8": "WET_SEND_R",
                       "13": "NC", "11": "NC", "9": "NC"}),
        relay("K203", {"1": "CTL_EXT_MODE_A", "16": "AGND",
                       "4": "SEC_DRV_L", "6": "NC", "8": "SEC_SEL_L",
                       "13": "SEC_RET_L", "11": "NC", "9": "EXTMIX_L_HI"}),
        relay("K204", {"1": "CTL_EXT_MODE_A", "16": "AGND",
                       "4": "SEC_DRV_R", "6": "NC", "8": "SEC_SEL_R",
                       "13": "SEC_RET_R", "11": "NC", "9": "EXTMIX_R_HI"}),
        fly("D261", "CTL_EXT_MODE_B"),
        fly("D262", "CTL_EXT_MODE_A"),
    ]),
    ("SECONDARY SEND BUFFERS", [
        opa4("U201_C", 3, {"8": "N_SECBUF_L", "9": "N_SECFB_L", "10": "SEC_DRV_L"}),
        res("R211", "100k", "SEC_DRV_L", "AGND"),
        res("R212", "0", "N_SECBUF_L", "N_SECFB_L"),
        res("R241", "20k", "N_SECFB_L", "AGND", dnp=True),
        res("R206", "100", "N_SECBUF_L", "SEC_SEND_L"),
        opa4("U201_D", 4, {"14": "N_SECBUF_R", "13": "N_SECFB_R", "12": "SEC_DRV_R"}),
        res("R231", "100k", "SEC_DRV_R", "AGND"),
        res("R232", "0", "N_SECBUF_R", "N_SECFB_R"),
        res("R251", "20k", "N_SECFB_R", "AGND", dnp=True),
        res("R226", "100", "N_SECBUF_R", "SEC_SEND_R"),
    ]),
    ("FINAL SUMMERS", [
        opa4("U201", 1, {"1": "N_TMIX_L", "2": "N_SUM_L_M", "3": "AGND"}),
        res("R202", "20k", "PRI_RET_L", "N_SUM_L_M"),
        res("R203", "20k", "EXTMIX_L_WIPER", "N_SUM_L_M"),
        res("R204", "20k", "FB_RET_L", "N_SUM_L_M"),
        res("R209", "20k", "N_TMIX_L", "N_SUM_L_M"),
        res("R205", "100", "N_TMIX_L", "TANK_MIX_L"),
        opa4("U201_B", 2, {"7": "N_TMIX_R", "6": "N_SUM_R_M", "5": "AGND"}),
        res("R222", "20k", "PRI_RET_R", "N_SUM_R_M"),
        res("R223", "20k", "EXTMIX_R_WIPER", "N_SUM_R_M"),
        res("R224", "20k", "FB_RET_R", "N_SUM_R_M"),
        res("R229", "20k", "N_TMIX_R", "N_SUM_R_M"),
        res("R225", "100", "N_TMIX_R", "TANK_MIX_R"),
    ]),
    ("POWER + DECOUPLING", [
        opa4("U201_P", 5, {"4": "+15VA", "11": "-15VA"}),
        cap("C291", "100n", "+15VA", "AGND"),
        cap("C292", "100n", "-15VA", "AGND"),
        cap("C293", "22u", "+15VA", "AGND", fp=g.FP_C1210),
        cap("C294", "22u", "-15VA", "AGND", fp=g.FP_C1210),
        cap("C295", "100n", "+5VAUX", "AGND"),
        C("#FLG201", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG202", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "-15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG203", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "AGND"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG204", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+5VAUX"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG205", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "CTL_EXT_MODE_A"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG206", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "CTL_EXT_MODE_B"}}, nosim=True, w=15.24, h=20.32),
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
    ("SIM: LEFT=SERIES MODE (relay ties), RIGHT=OFF", [
        vsrc("V1", "VDC", "15V", "dc=15", "+15VA", "GND"),
        vsrc("V2", "VDC", "15V", "dc=15", "GND", "-15VA"),
        vsrc("V3", "VDC", "0V bond", "dc=0", "AGND", "GND"),
        vsrc("V4", "VSIN", "0.3Vpk 600Hz", "dc=0 ampl=0.3 f=600", "PRI_RET_L", "AGND"),
        vsrc("V5", "VSIN", "0.3Vpk 600Hz", "dc=0 ampl=0.3 f=600", "PRI_RET_R", "AGND"),
        vsrc("V6", "VSIN", "0.2Vpk 1k5", "dc=0 ampl=0.2 f=1.5k", "FB_RET_L", "AGND"),
        vsrc("V7", "VSIN", "0.2Vpk 1k5", "dc=0 ampl=0.2 f=1.5k", "FB_RET_R", "AGND"),
        vsrc("V8", "VSIN", "0.25Vpk 2k", "dc=0 ampl=0.25 f=2k", "SEC_RET_L", "AGND"),
        vsrc("V9", "VSIN", "0.4Vpk 1k", "dc=0 ampl=0.4 f=1k", "WET_SEND_L", "AGND"),
        vsrc("V10", "VSIN", "0.4Vpk 1k", "dc=0 ampl=0.4 f=1k", "WET_SEND_R", "AGND"),
        # relay states, LEFT engaged in Series: NC path PRI_RET->SEC_SEL,
        # engage SEC_SEL->SEC_DRV, SEC_RET->EXTMIX_HI
        jsim("RS1", "PRI_RET_L", "SEC_SEL_L"),
        jsim("RS2", "SEC_SEL_L", "SEC_DRV_L"),
        jsim("RS3", "SEC_RET_L", "EXTMIX_L_HI"),
        # amount pots mid position
        res("RP1", "10k", "EXTMIX_L_HI", "EXTMIX_L_WIPER"),
        res("RP2", "10k", "EXTMIX_L_WIPER", "AGND"),
        res("RP3", "10k", "EXTMIX_R_HI", "EXTMIX_R_WIPER"),
        res("RP4", "10k", "EXTMIX_R_WIPER", "AGND"),
        # loads
        res("RL1", "10k", "TANK_MIX_L", "AGND"),
        res("RL2", "10k", "TANK_MIX_R", "AGND"),
        res("RL3", "10k", "SEC_SEND_L", "AGND"),
        res("RL4", "10k", "SEC_SEND_R", "AGND"),
        res("RL5", "10k", "PRI_SEND_L", "AGND"),
    ]),
]

DIRECTIVES = ".tran 10u 30m\n.options savecurrents"

MODELS = """* OPA1679 quad audio op amp, behavioral macro model
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
    prod = g.build(False, SECTIONS, SIM_SECTIONS, "ext-tank-routing",
                   "GAS Rev A - Ext Tank Routing", DIRECTIVES)
    with open(os.path.join(OUT_DIR, "ext-tank-routing.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = g.build(True, SECTIONS, SIM_SECTIONS, "ext-tank-routing",
                     "GAS Rev A - Ext Tank Routing", DIRECTIVES)
    with open(os.path.join(SIM_DIR, "ext-tank-routing-sim.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "ext-tank-routing-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "ext-tank-routing-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    with open(os.path.join(SIM_DIR, "gas-models.lib"), "w", encoding="utf-8") as f:
        f.write(MODELS)
    print("Wrote ext-tank-routing production + sim. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()
