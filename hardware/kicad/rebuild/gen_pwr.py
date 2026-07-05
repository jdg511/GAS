#!/usr/bin/env python3
"""Generate the GAS Rev A power-backplane schematic (production + sim variant).

Topology per hardware/rev-a-external-dc-power.md:
  +30VDC wall adapter -> board landing P500 -> SS34 reverse Schottky ->
  PTC polyfuse -> bulk cap + TVS -> URA2415YMD-10WR3 isolated +/-15V DC-DC ->
  ferrite-bead LC ripple filters -> +15VA/-15VA fanout headers.
  +5VAUX from +15VA via RECOM R-78E5.0-0.5.

IMPORTANT part correction vs old BOM: URB2415YMD-10WR3 is a SINGLE 15V output
module. The dual +/-15V part is URA2415YMD-10WR3 (+/-333mA). BOM updated.

Control landing headers P610-P614 stay off this board per the schematic-ready
definition (boards provide +5VAUX/AGND on their own control headers).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g

OUT_DIR = g.OUT_DIR
SIM_DIR = os.path.join(OUT_DIR, "sim", "power-backplane-sim")

C = g.C
res, cap = g.res, g.cap
FP_XH2 = "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
FP_VH3 = g.FP_VH3
FP_VH4 = "Connector_JST:JST_VH_B4P-VH_1x04_P3.96mm_Vertical"
FP_SMA = "Diode_SMD:D_SMA"
FP_PTC = "Fuse:Fuse_1812_4532Metric"
FP_CP10 = "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm"
FP_CP63 = "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm"
FP_R78E = "Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT"
FP_URA = "GAS:URA_YMD-10WR3"

def cpol(ref, value, netp, netn, fp=FP_CP63, simskip=False):
    val, rating = value.split("/") if "/" in value else (value, "")
    c = C(ref, "Device", "C_Polarized", val, fp, {1: {"1": netp, "2": netn}},
          sim={"Voltage": rating} if rating else None)
    c["simskip"] = simskip
    return c

def scap(ref, value, net1, net2, fp=None):
    c = cap(ref, value, net1, net2, fp=fp or g.FP_C0805)
    c["simskip"] = True
    return c

def bead(ref, net1, net2):
    return C(ref, "Device", "FerriteBead", "BLM18PG471SN1",
             "Inductor_SMD:L_0603_1608Metric", {1: {"1": net1, "2": net2}},
             sim={"Sim.Library": "gas-power-models.lib", "Sim.Name": "BEAD600",
                  "Sim.Device": "SUBCKT", "Sim.Pins": "1=a 2=b"})

def vconn(ref, n, nets, fp, nosim=True, h=30.48):
    return C(ref, "Connector_Generic", "Conn_01x0%d" % n, ref, fp,
             {1: {str(i + 1): nets[i] for i in range(n)}}, nosim=nosim, h=h)

SECTIONS = []

def _mk():
    inp = [
        vconn("P500", 2, ["+30V_RAW", "GND_IN"], FP_XH2),
        C("D500", "Device", "D_Schottky", "SS34", FP_SMA,
          {1: {"2": "+30V_RAW", "1": "+30V_D"}}, nosim=True),   # pin1=K pin2=A
        C("F500", "Device", "Polyfuse", "1.1A PTC MF-MSMF110", FP_PTC,
          {1: {"1": "+30V_D", "2": "+30V_F"}}, nosim=True),
        cpol("C500", "220u/50V", "+30V_F", "GND_IN", fp=FP_CP10, simskip=True),
        C("TVS500", "Device", "D_TVS", "SMAJ33A", FP_SMA,
          {1: {"1": "+30V_F", "2": "GND_IN"}}, nosim=True),
        cpol("C509", "100u/50V", "+30V_F", "GND_IN", fp=FP_CP10, simskip=True),
        res("R500", "0", "GND_IN", "AGND", fp=g.FP_R1206),
    ]
    inp[-1]["simskip"] = True  # star tie is meaningless in the AC testbench
    SECTIONS.append(("DC ENTRY + PROTECTION (+30VDC wall adapter)", inp))

    SECTIONS.append(("ISOLATED +/-15V CONVERSION (URA2415YMD-10WR3)", [
        C("PS500", "Connector_Generic", "Conn_01x06", "URA2415YMD-10WR3", FP_URA,
          {1: {"1": "GND_IN", "2": "+30V_F", "3": "+15VRAW",
               "4": "AGND", "5": "-15VRAW", "6": "NC"}}, nosim=True),
        cpol("C510", "10u/25V", "+15VRAW", "AGND", simskip=True),
        cpol("C511", "10u/25V", "AGND", "-15VRAW", simskip=True),
    ]))

    SECTIONS.append(("RAIL RIPPLE FILTERS (bead + 100u + 10u + 100n per rail)", [
        bead("FB500", "+15VRAW", "+15VA"),
        cpol("C501", "100u/25V", "+15VA", "AGND"),
        cap("C502", "10u", "+15VA", "AGND", fp=g.FP_C1206),
        cap("C503", "100n", "+15VA", "AGND", fp=g.FP_C1206),
        bead("FB501", "-15VRAW", "-15VA"),
        cpol("C504", "100u/25V", "AGND", "-15VA"),
        cap("C505", "10u", "-15VA", "AGND", fp=g.FP_C1206),
        cap("C506", "100n", "-15VA", "AGND", fp=g.FP_C1206),
    ]))

    SECTIONS.append(("+5VAUX (R-78E5.0-0.5 from +15VRAW, pre-bead: review F1)", [
        # Review finding F1: feed the 5V switcher from the RAW rail so its
        # input ripple current stays off the filtered analog +15VA rail.
        C("PS501", "Converter_DCDC", "R-78E5.0-0.5", "R-78E5.0-0.5", FP_R78E,
          {1: {"1": "+15VRAW", "2": "AGND", "3": "+5VAUX"}}, nosim=True),
        scap("C512", "10u", "+15VRAW", "AGND", fp=g.FP_C1206),
        cpol("C507", "47u/16V", "+5VAUX", "AGND", simskip=True),
        scap("C508", "100n", "+5VAUX", "AGND"),
    ]))

    fan = [vconn("P50%d" % i, 3, ["+15VA", "AGND", "-15VA"], FP_VH3)
           for i in range(1, 6)]
    fan.append(vconn("P506", 4, ["+15VA", "AGND", "-15VA", "+5VAUX"], FP_VH4))
    fan.append(vconn("P601", 4, ["+5VAUX", "AGND", "+15VA", "-15VA"], FP_VH4))
    SECTIONS.append(("POWER FANOUT (P501-P505 audio, P506 ext-routing, P601 control)", fan))

    flags = []
    # note: +5VAUX needs no flag; the R-78E's OUT pin is a power output
    for i, net in enumerate(["+30V_RAW", "+30V_F", "GND_IN", "AGND",
                             "+15VRAW", "-15VRAW", "+15VA", "-15VA"]):
        flags.append(C("#FLG50%d" % i, "power", "PWR_FLAG", "PWR_FLAG", "",
                       {1: {"1": net}}, nosim=True, w=15.24, h=20.32))
    SECTIONS.append(("ERC POWER FLAGS", flags))

_mk()

def vsrc(ref, symname, value, params, n1, n2):
    return C(ref, "Simulation_SPICE", symname, value, "",
             {1: {"1": n1, "2": n2}},
             sim={"Sim.Device": "V",
                  "Sim.Type": "DC" if symname == "VDC" else "SIN",
                  "Sim.Params": params}, w=20.32)

SIM_SECTIONS = [
    ("SIM: DC-DC MODULE MODELED AS 15V SOURCES WITH 1V AC RIPPLE", [
        vsrc("V1", "VDC", "15V + ripple", "dc=15 ac=1", "+15VRAW", "GND"),
        vsrc("V2", "VDC", "15V + ripple", "dc=15 ac=1", "GND", "-15VRAW"),
        vsrc("V3", "VDC", "0V AGND bond", "dc=0", "AGND", "GND"),
        res("RL1", "60", "+15VA", "AGND"),
        res("RL2", "60", "-15VA", "AGND"),
    ]),
]

DIRECTIVES = (".ac dec 50 100 10Meg\n"
              "; plots rail ripple rejection: probe v(+15va), v(-15va)\n"
              "; the bead+LC filter should be >40 dB down at the module's\n"
              "; 350 kHz switching frequency")

def main():
    prod = g.build(False, SECTIONS, SIM_SECTIONS, "power-backplane",
                   "GAS Rev A - Power Backplane", DIRECTIVES)
    with open(os.path.join(OUT_DIR, "power-backplane.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = g.build(True, SECTIONS, SIM_SECTIONS, "power-backplane",
                     "GAS Rev A - Power Backplane", DIRECTIVES)
    with open(os.path.join(SIM_DIR, "power-backplane-sim.kicad_sch"), "w",
              encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "power-backplane-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "power-backplane-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    lib = ("* GAS power board sim models\n"
           "* BLM18PG471SN1-class ferrite bead: ~0.6uH with HF damping\n"
           ".subckt BEAD600 a b\n"
           "Lb a b 0.6u\n"
           "Rb a b 470\n"
           ".ends BEAD600\n")
    with open(os.path.join(SIM_DIR, "gas-power-models.lib"), "w",
              encoding="utf-8") as f:
        f.write(lib)
    with open(os.path.join(SIM_DIR, "fp-lib-table"), "w", encoding="utf-8") as f:
        f.write('(fp_lib_table\n  (version 7)\n  (lib (name "GAS")(type "KiCad")'
                '(uri "${KIPRJMOD}/../../GAS.pretty")(options "")(descr ""))\n)\n')
    print("Wrote power-backplane production + sim schematics. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()
