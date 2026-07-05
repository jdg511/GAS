#!/usr/bin/env python3
"""Generate the GAS Rev A filter/clipper schematic (production + sim).

Per hardware/rev-a-filter-clipper-schematic-ready-definition.md, with these
first-pass engineering decisions (final values are bench-tunable per spec §9):
- HPF: 1st-order variable (47n film + off-board pot rheostat, ~33Hz..3.3kHz)
  buffered by U401A/B, with a mild resonance-injection path through the
  compressed Q-wiper landing (inert until the control-backplane pass wires
  the pot ends; documented).
- Drive: U401C/D non-inverting, fixed 4.9x (1+39k/10k).
- Clip: shunt networks after a 4k7 series resistor. Relay decode tree
  (K401=bit A, K402/K403=bit B, G5V-2 DC5) implements the frozen truth table:
  00 clean (no diodes), 01 silicon (1N4148W), 10 LED, 11 Schottky
  (germanium-adapter, 1N5819HW). Diode returns go through the shared
  drive-pot landing (DRV_HI) as a clip-floor control.
- LPF: 1st-order variable (pot series + 10n film shunt, ~160Hz..16kHz)
  buffered by U402A/B, same Q-injection reserve.
- Output buffers U402C/D + 100R isolators.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

OUT_DIR = g.OUT_DIR
SIM_DIR = os.path.join(OUT_DIR, "sim", "filter-clipper-sim")
C, res, cap = g.C, g.res, g.cap

FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_G5V2 = "Relay_THT:Relay_DPDT_Omron_G5V-2"
FP_XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
FP_XH12 = "Connector_JST:JST_XH_B12B-XH-A_1x12_P2.50mm_Vertical"
FP_C_FILM = "Capacitor_SMD:C_1210_3225Metric"
FP_LED = "LED_SMD:LED_0805_2012Metric"

OPA4_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1679X4",
            "Sim.Device": "SUBCKT",
            "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vp 5=in2p 6=in2n 7=out2 "
                        "8=out3 9=in3n 10=in3p 11=vn 12=in4p 13=in4n 14=out4"}

def opa4(ref, unit, pins):
    return C(ref, "Amplifier_Operational", "OPA1679", "OPA1679IDR", FP_SOIC14,
             {unit: pins}, sim=OPA4_SIM)

def diode(ref, netA, netK, val="1N4148W", fp=None, lib="Device", name="D"):
    return C(ref, lib, name, val, fp or g.FP_SOD123,
             {1: {"1": netK, "2": netA}},
             sim={"Sim.Library": "gas-models.lib",
                  "Sim.Name": {"1N4148W": "D1N4148", "LED red": "DLED",
                               "1N5819HW": "DSCHOTTKY"}[val],
                  "Sim.Device": "D", "Sim.Pins": "1=K 2=A"})

def relay(ref, pins):
    return C(ref, "Relay", "G5V-2", "G5V-2 DC5", FP_G5V2,
             {1: pins}, nosim=True, w=33, h=27.94)

def chan(sfx, inp, out, hf_hi, hf_w, hq_w, lf_hi, lf_w, lq_w,
         rc, rd, dsi, dled, dge, u1a, u1c, u2a, u2c, ka, kb):
    """One audio channel. sfx = 'L' or 'R'; rc/rd = ref prefixes."""
    n = lambda s: "N_%s_%s" % (s, sfx)
    comps = [
        # HPF: in-cap to node A (= pot HI landing), pot wiper leg to ground
        cap(rc[0], "47n", inp, hf_hi, fp=FP_C_FILM),
        res(rd[0], "1k", hf_w, "AGND"),
        opa4(u1a[0], u1a[1], {u1a[2]: n("HPF_OUT"), u1a[3]: n("HPF_OUT"),
                              u1a[4]: hf_hi}),
        # Q reserve: series R+C injection via the compressed wiper landing
        res(rd[1], "47k", n("HPF_OUT"), hq_w),
        cap(rc[1], "10n", hq_w, hf_hi, fp=FP_C_FILM),
        # drive stage, fixed 4.9x
        opa4(u1c[0], u1c[1], {u1c[2]: n("DRV_OUT"), u1c[3]: n("DRV_M"),
                              u1c[4]: n("HPF_OUT")}),
        res(rd[2], "39k", n("DRV_OUT"), n("DRV_M")),
        res(rd[3], "10k", n("DRV_M"), "AGND"),
        cap(rc[2], "47p", n("DRV_OUT"), n("DRV_M"), dnp=True),
        # series into the clip node
        res(rd[4], "4.7k", n("DRV_OUT"), n("CLIP")),
        # clip diode families (shunt, return via shared DRV_HI clip floor)
        diode(dsi[0], n("SI"), "DRV_HI"),
        diode(dsi[1], "DRV_HI", n("SI")),
        diode(dled[0], n("LED"), "DRV_HI", val="LED red", fp=FP_LED,
              lib="Device", name="LED"),
        diode(dled[1], "DRV_HI", n("LED"), val="LED red", fp=FP_LED,
              lib="Device", name="LED"),
        diode(dge[0], n("GE"), "DRV_HI", val="1N5819HW"),
        diode(dge[1], "DRV_HI", n("GE"), val="1N5819HW"),
        # LPF: series R + pot, shunt film cap, buffer
        res(rd[5], "1k", n("CLIP"), lf_hi),
        cap(rc[3], "10n", lf_w, "AGND", fp=FP_C_FILM),
        opa4(u2a[0], u2a[1], {u2a[2]: n("LPF_OUT"), u2a[3]: n("LPF_OUT"),
                              u2a[4]: lf_w}),
        res(rd[6], "47k", n("LPF_OUT"), lq_w),
        cap(rc[4], "10n", lq_w, lf_w, fp=FP_C_FILM),
        # output buffer + isolator
        opa4(u2c[0], u2c[1], {u2c[2]: n("BUF_OUT"), u2c[3]: n("BUF_OUT"),
                              u2c[4]: n("LPF_OUT")}),
        res(rd[7], "100", n("BUF_OUT"), out),
    ]
    return comps

SECTIONS = [
    ("HEADERS", [
        C("P401", "Connector_Generic", "Conn_01x03", "JXF-FILT B3B-XH-A", FP_XH3,
          {1: {"1": "XFADE_OUT_L", "2": "AGND", "3": "XFADE_OUT_R"}}, nosim=True),
        C("P402", "Connector_Generic", "Conn_01x03", "JFILT-WET B3B-XH-A", FP_XH3,
          {1: {"1": "FILTCLIP_OUT_L", "2": "AGND", "3": "FILTCLIP_OUT_R"}}, nosim=True),
        C("P403", "Connector_Generic", "Conn_01x12", "JFILT-CTL-A B12B-XH-A", FP_XH12,
          {1: {"1": "DRV_HI", "2": "DRV_WIPER", "3": "AGND",
               "4": "HPF_F_L_HI", "5": "HPF_F_L_WIPER", "6": "AGND",
               "7": "HPF_F_R_HI", "8": "HPF_F_R_WIPER", "9": "AGND",
               "10": "HPF_Q_L_WIPER", "11": "HPF_Q_R_WIPER", "12": "AGND"}},
          nosim=True, h=50.8),
        C("P405", "Connector_Generic", "Conn_01x12", "JFILT-CTL-B B12B-XH-A", FP_XH12,
          {1: {"1": "LPF_F_L_HI", "2": "LPF_F_L_WIPER", "3": "AGND",
               "4": "LPF_F_R_HI", "5": "LPF_F_R_WIPER", "6": "AGND",
               "7": "LPF_Q_L_WIPER", "8": "LPF_Q_R_WIPER", "9": "+5VAUX",
               "10": "CTL_CLIP_MODE_A", "11": "CTL_CLIP_MODE_B", "12": "AGND"}},
          nosim=True, h=50.8),
        C("P404", "Connector_Generic", "Conn_01x03", "JFILT-PWR B3P-VH-B", g.FP_VH3,
          {1: {"1": "+15VA", "2": "AGND", "3": "-15VA"}}, nosim=True),
    ]),
    ("LEFT CHANNEL", chan("L", "XFADE_OUT_L", "FILTCLIP_OUT_L",
        "HPF_F_L_HI", "HPF_F_L_WIPER", "HPF_Q_L_WIPER",
        "LPF_F_L_HI", "LPF_F_L_WIPER", "LPF_Q_L_WIPER",
        ["C401", "C403", "C405", "C406", "C407"],
        ["R401", "R402", "R403", "R404", "R405", "R406", "R407", "R408"],
        ["D401", "D402"], ["D405", "D406"], ["D409", "D410"],
        ("U401", 1, "1", "2", "3"), ("U401_C", 3, "8", "9", "10"),
        ("U402", 1, "1", "2", "3"), ("U402_C", 3, "8", "9", "10"),
        None, None)),
    ("RIGHT CHANNEL", chan("R", "XFADE_OUT_R", "FILTCLIP_OUT_R",
        "HPF_F_R_HI", "HPF_F_R_WIPER", "HPF_Q_R_WIPER",
        "LPF_F_R_HI", "LPF_F_R_WIPER", "LPF_Q_R_WIPER",
        ["C421", "C423", "C425", "C426", "C427"],
        ["R421", "R422", "R423", "R424", "R425", "R426", "R427", "R428"],
        ["D403", "D404"], ["D407", "D408"], ["D411", "D412"],
        ("U401_B", 2, "7", "6", "5"), ("U401_D", 4, "14", "13", "12"),
        ("U402_B", 2, "7", "6", "5"), ("U402_D", 4, "14", "13", "12"),
        None, None)),
    ("CLIP MODE DECODE (00 clean, 01 Si, 10 LED, 11 Schottky)", [
        relay("K401", {"1": "CTL_CLIP_MODE_A", "16": "AGND",
                       "4": "N_CLIP_L", "6": "N_KA_L_NC", "8": "N_KA_L_NO",
                       "13": "N_CLIP_R", "11": "N_KA_R_NC", "9": "N_KA_R_NO"}),
        relay("K402", {"1": "CTL_CLIP_MODE_B", "16": "AGND",
                       "4": "N_KA_L_NC", "6": "NC", "8": "N_SI_L",
                       "13": "N_KA_L_NO", "11": "N_LED_L", "9": "N_GE_L"}),
        relay("K403", {"1": "CTL_CLIP_MODE_B", "16": "AGND",
                       "4": "N_KA_R_NC", "6": "NC", "8": "N_SI_R",
                       "13": "N_KA_R_NO", "11": "N_LED_R", "9": "N_GE_R"}),
        res("R432", "100", "DRV_WIPER", "AGND"),
        C("D421", "Device", "D", "1N4148W", g.FP_SOD123,
          {1: {"1": "CTL_CLIP_MODE_A", "2": "AGND"}}, nosim=True),
        C("D422", "Device", "D", "1N4148W", g.FP_SOD123,
          {1: {"1": "CTL_CLIP_MODE_B", "2": "AGND"}}, nosim=True),
    ]),
    ("POWER + DECOUPLING", [
        opa4("U401_P", 5, {"4": "+15VA", "11": "-15VA"}),
        opa4("U402_P", 5, {"4": "+15VA", "11": "-15VA"}),
        cap("C591", "100n", "+15VA", "AGND"),
        cap("C592", "100n", "-15VA", "AGND"),
        cap("C593", "100n", "+15VA", "AGND"),
        cap("C594", "100n", "-15VA", "AGND"),
        cap("C595", "22u", "+15VA", "AGND", fp=g.FP_C1210),
        cap("C596", "22u", "-15VA", "AGND", fp=g.FP_C1210),
        C("#FLG401", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG402", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "-15VA"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG403", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "AGND"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG404", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "+5VAUX"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG405", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "CTL_CLIP_MODE_A"}}, nosim=True, w=15.24, h=20.32),
        C("#FLG406", "power", "PWR_FLAG", "PWR_FLAG", "",
          {1: {"1": "CTL_CLIP_MODE_B"}}, nosim=True, w=15.24, h=20.32),
    ]),
]

# relay COM nets N_CLIP_L/R equal chan()'s clip nodes by construction

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
    ("SIM: SUPPLIES, SOURCES, POT MODELS, CLIP ENGAGE (L=silicon, R=clean)", [
        vsrc("V1", "VDC", "15V", "dc=15", "+15VA", "GND"),
        vsrc("V2", "VDC", "15V", "dc=15", "GND", "-15VA"),
        vsrc("V3", "VDC", "0V bond", "dc=0", "AGND", "GND"),
        vsrc("V4", "VSIN", "0.3Vpk 1kHz", "dc=0 ampl=0.3 f=1k ac=1",
             "XFADE_OUT_L", "AGND"),
        vsrc("V5", "VSIN", "0.3Vpk 1kHz", "dc=0 ampl=0.3 f=1k",
             "XFADE_OUT_R", "AGND"),
        # HPF pots mid (100k): 50k HI->WIPER
        res("RP1", "50k", "HPF_F_L_HI", "HPF_F_L_WIPER"),
        res("RP2", "50k", "HPF_F_R_HI", "HPF_F_R_WIPER"),
        # LPF pots near min: 5k
        res("RP3", "5k", "LPF_F_L_HI", "LPF_F_L_WIPER"),
        res("RP4", "5k", "LPF_F_R_HI", "LPF_F_R_WIPER"),
        # clip floor pot low (hard clip)
        res("RP5", "100", "DRV_HI", "DRV_WIPER"),
        # engage silicon on LEFT only (emulates relay state A=0,B=1)
        jsim("RS1", "N_CLIP_L", "N_SI_L"),
        res("RL1", "10k", "FILTCLIP_OUT_L", "AGND"),
        res("RL2", "10k", "FILTCLIP_OUT_R", "AGND"),
    ]),
]

DIRECTIVES = ".tran 5u 20m\n.options savecurrents"

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

.model D1N4148 D(IS=4.352n N=1.906 RS=0.6458 CJO=4p TT=11.5n BV=100 IBV=100u)
.model DLED D(IS=1e-16 N=3.5 RS=2 CJO=30p)
.model DSCHOTTKY D(IS=1u N=1.1 RS=0.3 CJO=80p BV=40)
"""

def main():
    prod = g.build(False, SECTIONS, SIM_SECTIONS, "filter-clipper",
                   "GAS Rev A - Filter Clipper", DIRECTIVES)
    with open(os.path.join(OUT_DIR, "filter-clipper.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = g.build(True, SECTIONS, SIM_SECTIONS, "filter-clipper",
                     "GAS Rev A - Filter Clipper", DIRECTIVES)
    with open(os.path.join(SIM_DIR, "filter-clipper-sim.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "filter-clipper-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "filter-clipper-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    with open(os.path.join(SIM_DIR, "gas-models.lib"), "w", encoding="utf-8") as f:
        f.write(MODELS)
    print("Wrote filter-clipper production + sim. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()
