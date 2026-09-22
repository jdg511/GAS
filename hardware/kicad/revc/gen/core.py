"""GAS Rev C board generator core.

A board is a list of parts. Each part carries:
  ref, lib (symbol lib_id), value, fp (footprint lib:name),
  units: {unit: {symbol_pin: net}}   (net None = no connect)
  pinmap: {symbol_pin: [pad, ...]}   (default: same number)
  block: functional group (schematic grouping + PCB placement cluster)
  props: extra fields (MPN, Manufacturer, Description, DNP, ...)
Connectivity is the net names only.
"""
import collections

KICAD = r"C:\Program Files\KiCad\10.0"
SYMDIR = KICAD + r"\share\kicad\symbols"
FPDIR = KICAD + r"\share\kicad\footprints"
GASFP = r"C:\Users\Jason\GAS-build\repo\hardware\kicad\GAS_Parts.pretty"

FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_R1206 = "Resistor_SMD:R_1206_3216Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_C1206 = "Capacitor_SMD:C_1206_3216Metric"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_CFILM1U = "Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"
FP_CP5 = "Capacitor_SMD:CP_Elec_5x5.8"
FP_CP63 = "Capacitor_SMD:CP_Elec_6.3x7.7"
FP_CP8 = "Capacitor_SMD:CP_Elec_8x10.5"
FP_D = "Diode_SMD:D_SOD-123"
FP_SMA = "Diode_SMD:D_SMA"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_SOT223 = "Package_TO_SOT_SMD:SOT-223-3_TabPin2"
FP_SOT89 = "Package_TO_SOT_SMD:SOT-89-3"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_SIP8 = "Package_SIP:SIP-8_19x3mm_P2.54mm"
FP_TRIM = "Potentiometer_SMD:Potentiometer_Bourns_3314J_Vertical"
FP_RELAY = "Relay_SMD:Relay_DPDT_Omron_G6K-2F-Y"
FP_XH = "Connector_JST:JST_XH_B{n}B-XH-A_1x{n:02d}_P2.50mm_Vertical"
FP_VH = "Connector_JST:JST_VH_B{n}P-VH_1x{n:02d}_P3.96mm_Vertical"
FP_HOLE = "MountingHole:MountingHole_3.2mm_M3_Pad_Via"
FP_FUSE = "Fuse:Fuse_1812_4532Metric"
FP_FB = "Inductor_SMD:L_0805_2012Metric"
FP_COMBO = "Connector_Audio:Jack_XLR-6.35mm_Neutrik_NCJ6FI-H_Horizontal"
FP_RCA = "GAS_Parts:Jack_RCA_SameSky_RCJ-041_Horizontal"
FP_TEL12 = "Converter_DCDC:Converter_DCDC_TRACO_TEL12-xxxx_THT"
FP_R78E = "Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT"

NC = None


def yageo(val, size="0603"):
    """Yageo RC series 1 % code, e.g. 30.9k -> RC0603FR-0730K9L, 100R -> RC0603FR-07100RL, 0R -> RC0603JR-070RL."""
    v = val.split()[0]
    if v in ("0R", "0"):
        return f"RC{size}JR-070RL"
    unit = v[-1].upper() if v[-1] in "RkKM" else "R"
    num = v[:-1] if v[-1] in "RkKM" else v
    if "." in num:
        num = num.rstrip("0").rstrip(".")
    if "." in num:
        a, b_ = num.split(".")
        code = f"{a}{unit}{b_}"
    else:
        code = f"{num}{unit}"
    return f"RC{size}FR-07{code}L"


class Board:
    def __init__(self, name, title, comments=(), date="2026-09-15", rev="C"):
        self.name, self.title, self.comments, self.date, self.rev = name, title, list(comments), date, rev
        self.parts = []
        self.refs = set()
        self.power_nets = {"AGND"}
        self.wide_nets = {}          # net -> track width mm
        self.outline = (120.0, 150.0)
        self.fixed = {}              # ref -> (x, y, rot, side)
        self.regions = []            # (block-prefix, x0, y0, x1, y1)
        self.holes = []

    # ------------------------------------------------------------------ core
    def add(self, ref, lib, value, fp, units, block, pinmap=None, **props):
        assert ref not in self.refs, f"duplicate ref {ref}"
        self.refs.add(ref)
        self.parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, units=units, block=block,
                               pinmap=pinmap or {}, props=props))

    # ------------------------------------------------------------------ passives
    def R(self, ref, val, a, b, block, fp=FP_R, **p):
        if "MPN" not in p and fp in (FP_R, FP_R1206):
            p["MPN"] = yageo(val, "0603" if fp == FP_R else "1206")
            p["Manufacturer"] = "Yageo"
        self.add(ref, "Device:R", val, fp, {1: {"1": a, "2": b}}, block, **p)

    def C(self, ref, val, a, b, block, fp=FP_C, **p):
        self.add(ref, "Device:C", val, fp, {1: {"1": a, "2": b}}, block, **p)

    def CP(self, ref, val, plus, minus, block, fp=FP_CP5, **p):
        self.add(ref, "Device:C_Polarized", val, fp, {1: {"1": plus, "2": minus}}, block, **p)

    def D(self, ref, val, anode, cathode, block, lib="Device:D", fp=FP_D, **p):
        self.add(ref, lib, val, fp, {1: {"1": cathode, "2": anode}}, block, **p)

    def SCHOTTKY_SOT23(self, ref, val, anode, cathode, block, **p):
        # BAT54 single: pad 1 anode, pad 2 NC, pad 3 cathode
        self.add(ref, "GAS_Parts:BAT54_SOT23", val, FP_SOT23, {1: {"1": anode, "2": None, "3": cathode}}, block, **p)

    def TRIM(self, ref, val, p1, wiper, p3, block, **p):
        self.add(ref, "Device:R_Potentiometer_Trim", val, FP_TRIM, {1: {"1": p1, "2": wiper, "3": p3}}, block, **p)

    # ------------------------------------------------------------------ actives
    def OPA4(self, ref, units, block, value="OPA1679IDR", vp="+15VA", vn="-15VA", **p):
        pm = {1: ("3", "2", "1"), 2: ("5", "6", "7"), 3: ("10", "9", "8"), 4: ("12", "13", "14")}
        u = {}
        for k in range(1, 5):
            if k in units:
                pl, mi, out = units[k]
            else:   # unused unit: follower to AGND
                pl, mi, out = "AGND", f"SPARE_{ref}_{k}", f"SPARE_{ref}_{k}"
            a, b, c = pm[k]
            u[k] = {a: pl, b: mi, c: out}
        u[5] = {"4": vp, "11": vn}
        self.add(ref, "Amplifier_Operational:OPA1679", value, FP_SOIC14, u, block,
                 MPN=value, Manufacturer="Texas Instruments", **p)

    def OPA2(self, ref, units, block, value="OPA1656IDR", vp="+15VA", vn="-15VA", mfr="Texas Instruments", **p):
        pm = {1: ("3", "2", "1"), 2: ("5", "6", "7")}
        u = {}
        for k in (1, 2):
            if k in units:
                pl, mi, out = units[k]
            else:
                pl, mi, out = "AGND", f"SPARE_{ref}_{k}", f"SPARE_{ref}_{k}"
            a, b, c = pm[k]
            u[k] = {a: pl, b: mi, c: out}
        u[3] = {"8": vp, "4": vn}
        self.add(ref, "Amplifier_Operational:TL072", value, FP_SOIC8, u, block, MPN=value, Manufacturer=mfr, **p)

    def NJFET(self, ref, val, d, g, s, block, mpn="MMBF5457", **p):
        # onsemi MMBF5457 / MMBFJ201 SOT-23: 1 drain, 2 source, 3 gate
        self.add(ref, "Device:Q_NJFET_DSG", val, FP_SOT23, {1: {"1": d, "2": s, "3": g}}, block,
                 MPN=mpn, Manufacturer="onsemi", **p)

    def NPN(self, ref, b, e, c, block, **p):
        self.add(ref, "Transistor_BJT:MMBT3904", "MMBT3904", FP_SOT23, {1: {"1": b, "2": e, "3": c}}, block,
                 MPN="MMBT3904-7-F", Manufacturer="Diodes Incorporated", **p)

    def PNP3906(self, ref, b, e, c, block, **p):
        self.add(ref, "Transistor_BJT:MMBT3906", "MMBT3906", FP_SOT23, {1: {"1": b, "2": e, "3": c}}, block,
                 MPN="MMBT3906-7-F", Manufacturer="Diodes Incorporated", **p)

    def RELAY(self, ref, coil, com1, nc1, no1, com2, nc2, no2, block, **p):
        """Omron G6K-2F-Y DC5: 1 coil+, 8 coil-, pole A 3 COM / 2 NC / 4 NO, pole B 6 COM / 7 NC / 5 NO."""
        self.add(ref, "Relay:G6K-2", "G6K-2F-Y DC5", FP_RELAY,
                 {1: {"1": coil, "8": "AGND", "3": com1, "2": nc1, "4": no1, "6": com2, "7": nc2, "5": no2}},
                 block, MPN="G6K-2F-Y DC5", Manufacturer="Omron", **p)
        self.D(ref.replace("K", "D", 1) + "F", "1N4148W", "AGND", coil, block, MPN="1N4148W-7-F",
               Manufacturer="Diodes Incorporated", Description="relay coil flyback")

    def CONN(self, ref, val, fp, nets, block, **p):
        n = len(nets)
        self.add(ref, f"Connector_Generic:Conn_01x{n:02d}", val, fp,
                 {1: {str(i + 1): net for i, net in enumerate(nets)}}, block, **p)

    def XH(self, ref, val, nets, block, **p):
        n = len(nets)
        mpn = f"B{n}B-XH-A(LF)(SN)"
        self.CONN(ref, val, FP_XH.format(n=n), nets, block, MPN=mpn, Manufacturer="JST", **p)

    def VH(self, ref, val, nets, block, **p):
        n = len(nets)
        self.CONN(ref, val, FP_VH.format(n=n), nets, block, MPN=f"B{n}P-VH(LF)(SN)", Manufacturer="JST", **p)

    def HOLE(self, ref, x, y, net="AGND"):
        self.add(ref, "Mechanical:MountingHole_Pad", "M3", FP_HOLE, {1: {"1": net}}, "Mechanical")
        self.fixed[ref] = (x, y, 0, "F")

    def decouple(self, prefix, n, block, rails=(("+15VA", "AGND"), ("AGND", "-15VA"))):
        for i, (a, b) in enumerate(rails):
            self.C(f"{prefix}{n + i}", "100nF", a if a != "AGND" else b if False else a, b, block,
                   MPN="CL10B104KB8NNNC", Manufacturer="Samsung")

    # ------------------------------------------------------------------ report
    def nets(self):
        nets = collections.defaultdict(list)
        for p in self.parts:
            for u, pins in p["units"].items():
                for pin, net in pins.items():
                    if net is not None:
                        nets[net].append(f"{p['ref']}.{pin}")
        return nets

    def check(self):
        nets = self.nets()
        single = sorted(n for n, m in nets.items() if len(m) < 2 and not n.startswith("SPARE_"))
        return nets, single


def _pwrflag(self, net):
    n = sum(1 for p in self.parts if p["ref"].startswith("#FLG")) + 1
    self.add(f"#FLG{n:02d}", "power:PWR_FLAG", "PWR_FLAG", "", {1: {"1": net}}, "Power flags")


Board.PWRFLAG = _pwrflag
