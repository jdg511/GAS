"""GAS Rev B circuit-board electrical definition (netlist as data).

Every part is: ref, lib_id, value, footprint, {unit: {pin_number: net}}, extra properties.
Net names are the only connectivity. NC = deliberately unconnected pin.
"""

FP_R = "Resistor_SMD:R_0603_1608Metric"
FP_C = "Capacitor_SMD:C_0603_1608Metric"
FP_CFILM = "Capacitor_SMD:C_1206_3216Metric"          # Panasonic ECHU PPS film 1206 (47n, 15n)
FP_CFILM1210 = "Capacitor_SMD:C_1210_3225Metric"      # ECHU 68n
FP_CFILM0805 = "Capacitor_SMD:C_0805_2012Metric"      # ECHU 6.8n, 3.3n
FP_C1U = "Capacitor_THT:C_Rect_L7.2mm_W4.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2"  # WIMA MKS2 1uF/50V
FP_CP10 = "Capacitor_SMD:CP_Elec_5x5.8"
FP_CP47 = "Capacitor_SMD:CP_Elec_6.3x5.8"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_D = "Diode_SMD:D_SOD-123"
FP_TRIM = "Potentiometer_SMD:Potentiometer_Bourns_3314J_Vertical"
FP_TO92 = "Package_TO_SOT_THT:TO-92_Inline"
FP_SOT23 = "Package_TO_SOT_SMD:SOT-23"
FP_SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_SIP8 = "Package_SIP:SIP-8_19x3mm_P2.54mm"
FP_SOT89 = "Package_TO_SOT_SMD:SOT-89-3"
FP_RELAY = "GAS_Parts:Relay_DPDT_Panasonic_TQ2"
FP_VACTROL = "GAS_Parts:Vactrol_VTL5C3_Axial"
FP_XH3 = "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical"
FP_XH16 = "Connector_JST:JST_XH_B16B-XH-A_1x16_P2.50mm_Vertical"
FP_VH3 = "Connector_JST:JST_VH_B3P-VH_1x03_P3.96mm_Vertical"
FP_HOLE = "MountingHole:MountingHole_3.2mm_M3"

NC = None

parts = []      # list of dicts
blocks = []     # (title, [refs]) for schematic grouping / notes

def _add(ref, lib, value, fp, units, block, **props):
    parts.append(dict(ref=ref, lib=lib, value=value, fp=fp, units=units, block=block, props=props))

def R(ref, val, a, b, block, **p):
    _add(ref, "Device:R", val, FP_R, {1: {"1": a, "2": b}}, block, **p)

def C(ref, val, a, b, block, fp=FP_C, **p):
    _add(ref, "Device:C", val, fp, {1: {"1": a, "2": b}}, block, **p)

def CP(ref, val, plus, minus, block, fp=FP_CP10, **p):
    _add(ref, "Device:C_Polarized", val, fp, {1: {"1": plus, "2": minus}}, block, **p)

def D(ref, val, anode, cathode, block, lib="Device:D", **p):
    _add(ref, lib, val, FP_D, {1: {"1": cathode, "2": anode}}, block, **p)

def TRIM(ref, val, p1, wiper, p3, block, **p):
    _add(ref, "Device:R_Potentiometer_Trim", val, FP_TRIM, {1: {"1": p1, "2": wiper, "3": p3}}, block, **p)

def OPAMP4(ref, units, block, value="OPA1679IDR", vp="+15VA", vn="-15VA", **p):
    """units: {1:(plus,minus,out), ...4}; unit 5 = power."""
    pinmap = {1: ("3", "2", "1"), 2: ("5", "6", "7"), 3: ("10", "9", "8"), 4: ("12", "13", "14")}
    u = {}
    for k, (pl, mi, out) in units.items():
        pp, pm, po = pinmap[k]
        u[k] = {pp: pl, pm: mi, po: out}
    u[5] = {"4": vp, "11": vn}
    _add(ref, "Amplifier_Operational:OPA1679", value, FP_SOIC14, u, block,
         Datasheet="https://www.ti.com/lit/ds/symlink/opa1679.pdf", **p)

def OPAMP2(ref, units, block, value="TL072H", vp="+9VC", vn="AGND", **p):
    pinmap = {1: ("3", "2", "1"), 2: ("5", "6", "7")}
    u = {}
    for k, (pl, mi, out) in units.items():
        pp, pm, po = pinmap[k]
        u[k] = {pp: pl, pm: mi, po: out}
    u[3] = {"8": vp, "4": vn}
    _add(ref, "Amplifier_Operational:TL072", value, FP_SOIC8, u, block, MPN="TL072HIDR",
         Datasheet="https://www.ti.com/lit/ds/symlink/tl072.pdf", **p)

def NJFET(ref, val, d, g, s, block, **p):
    _add(ref, "Device:Q_NJFET_DGS", val, FP_TO92, {1: {"1": d, "2": g, "3": s}}, block, **p)

def NPN(ref, val, b, e, c, block, **p):
    _add(ref, "Transistor_BJT:MMBT3904", val, FP_SOT23, {1: {"1": b, "2": e, "3": c}}, block, **p)

def CONN(ref, val, fp, nets, block, **p):
    n = len(nets)
    _add(ref, f"Connector_Generic:Conn_01x{n:02d}", val, fp, {1: {str(i + 1): net for i, net in enumerate(nets)}}, block, **p)

def RELAY(ref, coil_p, coil_n, com1, no1, com2, no2, block, **p):
    _add(ref, "Relay:Relay_DPDT", "TQ2-5V", FP_RELAY,
         {1: {"A1": coil_p, "A2": coil_n, "11": com1, "12": NC, "14": no1, "21": com2, "22": NC, "24": no2}},
         block, MPN="TQ2-5V", **p)

def THAT2180(ref, inp, ecp, ecn, sym, out, block, vn="-15VA"):
    _add(ref, "GAS_Parts:THAT2180", "THAT2180A", FP_SIP8,
         {1: {"1": inp, "2": ecp, "3": ecn, "4": sym, "5": vn, "6": "AGND", "7": "+15VA", "8": out}}, block,
         MPN="2180AL08-U", Datasheet="https://thatcorp.com/datashts/THAT_2180-Series_Datasheet.pdf")

def THAT2252(ref, inp, ibias, sym, cap, out, block):
    _add(ref, "GAS_Parts:THAT2252", "THAT2252", FP_SIP8,
         {1: {"1": inp, "2": ibias, "3": "AGND", "4": sym, "5": "-15VA", "6": cap, "7": out, "8": "+15VA"}}, block,
         MPN="2252L08-U", Datasheet="https://thatcorp.com/datashts/THAT_2252_Datasheet.pdf")

def VACTROL(ref, led_a, led_k, ldr1, ldr2, block):
    _add(ref, "GAS_Parts:VTL5C3", "VTL5C3", FP_VACTROL,
         {1: {"1": led_a, "2": led_k, "3": ldr1, "4": ldr2}}, block, MPN="VTL5C3",
         Datasheet="https://aionfx.com/app/files/datasheets/xvive-vtl5c3-vtl5c4.pdf")

def HOLE(ref, block):
    _add(ref, "Mechanical:MountingHole", "MountingHole", FP_HOLE, {1: {}}, block)

def PWRFLAG(ref, net, block):
    _add(ref, "power:PWR_FLAG", "PWR_FLAG", "", {1: {"1": net}}, block)

# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------
B = "Connectors"
CONN("P1", "JXF-CIR", FP_XH3, ["XFADE_OUT_L", "AGND", "XFADE_OUT_R"], B, Description="Audio in from feedback/wet board (was JXF-FILT)")
CONN("P2", "JCIR-WET", FP_XH3, ["FILTCLIP_OUT_L", "AGND", "FILTCLIP_OUT_R"], B, Description="Audio out to feedback/wet board (was JFILT-WET)")
CONN("P3", "JCIR-PWR", FP_VH3, ["+15VA", "AGND", "-15VA"], B, Description="Split-rail power from power backplane")
CONN("P4", "JCIR-CTL-A", FP_XH16,
     ["DRV_L_HI", "DRV_L_W", "DRV_L_LO", "DRV_R_HI", "DRV_R_W", "DRV_R_LO",
      "HPF_OUT_L", "HPF_L1_W", "AGND", "HPF_L2_W", "HPF_OUT_R", "HPF_R1_W", "AGND", "HPF_R2_W",
      "AGND", "AGND"], B,
     Description="Drive dual pot (10k lin) + HPF quad pot (100k lin) rheostat landings")
CONN("P5", "JCIR-CTL-B", FP_XH16,
     ["LPF_N1_L", "LPF_L1_W", "LPF_P_L", "LPF_L2_W", "LPF_N1_R", "LPF_R1_W", "LPF_P_R", "LPF_R2_W",
      "MODE1", "MODE2", "MODE3", "MODE4", "MODE5", "MODE6", "MODE7", "AGND"], B,
     Description="LPF quad pot (100k lin) rheostat landings + 7-position mode switch (+5VAUX switched)")
for i in range(1, 5):
    HOLE(f"H{i}", B)
PWRFLAG("#FLG1", "+15VA", B)
PWRFLAG("#FLG2", "-15VA", B)
PWRFLAG("#FLG3", "AGND", B)

# ---------------------------------------------------------------------------
# Power and bias (1xx)
# ---------------------------------------------------------------------------
B = "Power / +9VC / VBIAS"
CP("C101", "10uF", "+15VA", "AGND", B)
CP("C102", "10uF", "AGND", "-15VA", B)
_add("U101", "Regulator_Linear:L78L09_SOT89", "L78L09", FP_SOT89, {1: {"3": "+15VA", "2": "AGND", "1": "+9VC"}}, B,
     MPN="L78L09ACUTR", Datasheet="https://www.st.com/resource/en/datasheet/l78l.pdf")
C("C103", "100nF", "+15VA", "AGND", B)
CP("C104", "10uF", "+9VC", "AGND", B)
C("C105", "100nF", "+9VC", "AGND", B)
R("R101", "10k", "+9VC", "VB_RAW", B)
R("R102", "10k", "VB_RAW", "AGND", B)
CP("C106", "47uF", "VB_RAW", "AGND", B, fp=FP_CP47)
OPAMP2("U102", {1: ("VB_RAW", "VBIAS", "VBIAS"), 2: ("VBIAS", "SPARE_U102B", "SPARE_U102B")}, B)
C("C107", "100nF", "+9VC", "AGND", B)

# ---------------------------------------------------------------------------
# Main path, per channel (L = 2xx/U201/U202, R = 3xx/U301/U302)
# ---------------------------------------------------------------------------
def main_path(ch, n, U, UM):
    B = f"Main path {ch}: Drive, HPF, pad, LPF, output"
    # Drive: symmetric +/-24 dB inverting gain pot
    R(f"R{n}01", "680R", f"XFADE_OUT_{ch}", f"DRV_{ch}_HI", B)
    R(f"R{n}02", "680R", f"DRV_{ch}_LO", f"DRV_OUT_{ch}", B)
    R(f"R{n}03", "1M", f"DRV_{ch}_W", f"DRV_OUT_{ch}", B, Description="safety feedback if pot unplugged")
    C(f"C{n}01", "22pF", f"DRV_{ch}_W", f"DRV_OUT_{ch}", B)
    # HPF: Sallen-Key equal R/C, K = 1.59 -> Q = 0.71, fc = 1/(2*pi*R*68n), R = 1k + rheostat
    C(f"C{n}02", "68nF film", f"DRV_OUT_{ch}", f"HPF_N1_{ch}", B, fp=FP_CFILM1210)
    C(f"C{n}03", "68nF film", f"HPF_N1_{ch}", f"HPF_P_{ch}", B, fp=FP_CFILM1210)
    R(f"R{n}04", "1k", f"HPF_N1_{ch}", f"HPF_{ch}1_W", B)
    R(f"R{n}05", "1k", f"HPF_P_{ch}", f"HPF_{ch}2_W", B)
    R(f"R{n}06", "5.9k", f"HPF_OUT_{ch}", f"HPF_FB_{ch}", B)
    R(f"R{n}07", "10k", f"HPF_FB_{ch}", "AGND", B)
    R(f"R{n}08", "1M", f"HPF_P_{ch}", "AGND", B, Description="bias safety if pot unplugged")
    # Pad to pedal-level circuits: 0 dBFS (6.93 Vpk at bus scale) -> 0.1 Vpk
    R(f"R{n}15", "47k", f"HPF_OUT_{ch}", f"PAD_{ch}", B)
    R(f"R{n}16", "680R", f"PAD_{ch}", "AGND", B, Description="pad 680/47680 = 0.01426 (-36.9 dB): 6.93 Vpk -> 0.1 Vpk")
    # Mode bus pulldown
    R(f"R{n}11", "100k", f"BUS_{ch}", "AGND", B)
    # LPF: Sallen-Key unity gain, C1 = 15n / C2 = 6.8n -> Q = 0.74, R = 1k + rheostat
    R(f"R{n}09", "1k", f"BUS_{ch}", f"LPF_{ch}1_W", B)
    R(f"R{n}10", "1k", f"LPF_N1_{ch}", f"LPF_{ch}2_W", B)
    C(f"C{n}04", "15nF film", f"LPF_N1_{ch}", f"LPF_OUT_{ch}", B, fp=FP_CFILM)
    C(f"C{n}05", "6.8nF film", f"LPF_P_{ch}", "AGND", B, fp=FP_CFILM0805)
    # Output buffer: inverting, gain -1/1.59 (undoes HPF K and the drive inversion)
    R(f"R{n}12", "15.8k", f"LPF_OUT_{ch}", f"OB_N_{ch}", B)
    R(f"R{n}13", "10k", f"OB_N_{ch}", f"OUT_RAW_{ch}", B)
    C(f"C{n}06", "22pF", f"OB_N_{ch}", f"OUT_RAW_{ch}", B)
    R(f"R{n}14", "100R", f"OUT_RAW_{ch}", f"FILTCLIP_OUT_{ch}", B)
    OPAMP4(U, {1: ("AGND", f"DRV_{ch}_W", f"DRV_OUT_{ch}"),
               2: (f"HPF_P_{ch}", f"HPF_FB_{ch}", f"HPF_OUT_{ch}"),
               3: (f"LPF_P_{ch}", f"LPF_OUT_{ch}", f"LPF_OUT_{ch}"),
               4: ("AGND", f"OB_N_{ch}", f"OUT_RAW_{ch}")}, B)
    C(f"C{n}07", "100nF", "+15VA", "AGND", B)
    C(f"C{n}08", "100nF", "-15VA", "AGND", B)
    # Make-up quad for the pedal-level modes + opto buffer
    OPAMP4(UM, {1: ("AGND", f"TUBE_MK_{ch}", f"TUBE_OUT_{ch}"),
                2: (f"TAPE_DIV_{ch}", f"TAPE_FB2_{ch}", f"TAPE_OUT_{ch}"),
                3: (f"TS_DIV_{ch}", f"TS_FB2_{ch}", f"TS_OUT_{ch}"),
                4: (f"OPTO_N_{ch}", f"OPTO_OUT_{ch}", f"OPTO_OUT_{ch}")}, B)
    C(f"C{n}09", "100nF", "+15VA", "AGND", B)
    C(f"C{n}10", "100nF", "-15VA", "AGND", B)

main_path("L", 2, "U201", "U202")
main_path("R", 3, "U301", "U302")

# ---------------------------------------------------------------------------
# Mode 2: Tube = TL072 x11 boost + J201 stage (9 V), per channel (L 4xx, R 5xx)
# Mode 3: Tape = record EQ + 2N3904 diff pair + repro EQ (L 6xx, R 7xx)
# ---------------------------------------------------------------------------
def tube_tape(ch, nt, ntp, U):
    B = f"Tube {ch} (J201 stage) + Tape {ch} (record EQ, diff pair, repro EQ) on +9VC"
    # Tube
    C(f"C{nt}01", "1uF film", f"PAD_{ch}", f"TUBE_IN_{ch}", B, fp=FP_C1U)
    R(f"R{nt}01", "100k", f"TUBE_IN_{ch}", "VBIAS", B)
    R(f"R{nt}02", "100k", f"TUBE_BOOST_{ch}", f"TUBE_FB_{ch}", B)
    R(f"R{nt}03", "10k", f"TUBE_FB_{ch}", "VBIAS", B)
    C(f"C{nt}02", "47nF film", f"TUBE_BOOST_{ch}", f"TUBE_G_{ch}", B, fp=FP_CFILM)
    R(f"R{nt}04", "1M", f"TUBE_G_{ch}", "AGND", B)
    NJFET(f"Q{nt}01", "J201", f"TUBE_D_{ch}", f"TUBE_G_{ch}", f"TUBE_S_{ch}", B, MPN="J201")
    R(f"R{nt}05", "470R", f"TUBE_S_{ch}", "AGND", B)
    CP(f"C{nt}03", "10uF", f"TUBE_S_{ch}", "AGND", B)
    R(f"R{nt}06", "4.7k", "+9VC", f"TUBE_RD_{ch}", B)
    TRIM(f"RV{nt}01", "50k", f"TUBE_RD_{ch}", f"TUBE_D_{ch}", f"TUBE_D_{ch}", B, Description="set drain to 4.9 V (covers J201 Idss spread)")
    C(f"C{nt}04", "1uF film", f"TUBE_D_{ch}", f"TUBE_C_{ch}", B, fp=FP_C1U)
    R(f"R{nt}07", "100k", f"TUBE_C_{ch}", f"TUBE_MK_{ch}", B)
    R(f"R{nt}08", "43.2k", f"TUBE_MK_{ch}", f"TUBE_OUT_{ch}", B, Description="inverting make-up 69.3/159.5 = 0.434, restores polarity")
    # Tape
    C(f"C{ntp}01", "1uF film", f"PAD_{ch}", f"TAPE_IN_{ch}", B, fp=FP_C1U)
    R(f"R{ntp}01", "100k", f"TAPE_IN_{ch}", "VBIAS", B)
    R(f"R{ntp}02", "10k", f"TAPE_FB_{ch}", "VBIAS", B)
    R(f"R{ntp}03", "4.7k", f"TAPE_FB_{ch}", f"TAPE_Z_{ch}", B)
    C(f"C{ntp}02", "6.8nF film", f"TAPE_Z_{ch}", "VBIAS", B, fp=FP_CFILM0805)
    R(f"R{ntp}04", "82k", f"TAPE_REC_{ch}", f"TAPE_FB_{ch}", B)
    C(f"C{ntp}03", "1uF film", f"TAPE_REC_{ch}", f"TAPE_B1_{ch}", B, fp=FP_C1U)
    R(f"R{ntp}05", "47k", "+9VC", f"TAPE_B1_{ch}", B)
    R(f"R{ntp}06", "22k", f"TAPE_B1_{ch}", "AGND", B)
    R(f"R{ntp}07", "47k", "+9VC", f"TAPE_B2_{ch}", B)
    R(f"R{ntp}08", "22k", f"TAPE_B2_{ch}", "AGND", B)
    CP(f"C{ntp}04", "10uF", f"TAPE_B2_{ch}", "AGND", B)
    NPN(f"Q{ntp}01", "MMBT3904", f"TAPE_B1_{ch}", f"TAPE_E1_{ch}", f"TAPE_C1_{ch}", B, MPN="MMBT3904-7-F")
    NPN(f"Q{ntp}02", "MMBT3904", f"TAPE_B2_{ch}", f"TAPE_E2_{ch}", f"TAPE_C2_{ch}", B, MPN="MMBT3904-7-F")
    R(f"R{ntp}09", "470R", f"TAPE_E1_{ch}", f"TAPE_T_{ch}", B)
    R(f"R{ntp}10", "470R", f"TAPE_E2_{ch}", f"TAPE_T_{ch}", B)
    R(f"R{ntp}11", "2.2k", f"TAPE_T_{ch}", "AGND", B)
    R(f"R{ntp}12", "4.7k", "+9VC", f"TAPE_C1_{ch}", B)
    R(f"R{ntp}13", "4.7k", "+9VC", f"TAPE_C2_{ch}", B)
    R(f"R{ntp}14", "15k", f"TAPE_C2_{ch}", f"TAPE_REP_{ch}", B)
    R(f"R{ntp}15", "10k", f"TAPE_REP_{ch}", f"TAPE_REP2_{ch}", B)
    C(f"C{ntp}05", "3.3nF film", f"TAPE_REP2_{ch}", "AGND", B, fp=FP_CFILM0805)
    C(f"C{ntp}06", "1uF film", f"TAPE_REP_{ch}", f"TAPE_DIV_{ch}", B, fp=FP_C1U)
    R(f"R{ntp}16", "100k", f"TAPE_DIV_{ch}", "AGND", B, Description="bias return, loads repro EQ x0.835")
    R(f"R{ntp}17", "100k", f"TAPE_OUT_{ch}", f"TAPE_FB2_{ch}", B, Description="non-inverting x2: 0.835 x 2 = 1.67 = 69.3/(9.2 x 4.53)")
    R(f"R{ntp}18", "100k", f"TAPE_FB2_{ch}", "AGND", B)
    OPAMP2(U, {1: (f"TUBE_IN_{ch}", f"TUBE_FB_{ch}", f"TUBE_BOOST_{ch}"),
               2: (f"TAPE_IN_{ch}", f"TAPE_FB_{ch}", f"TAPE_REC_{ch}")}, B)
    C(f"C{nt}05", "100nF", "+9VC", "AGND", B)

tube_tape("L", 4, 6, "U401")
tube_tape("R", 5, 7, "U501")

# ---------------------------------------------------------------------------
# Mode 4: Tube Screamer feedback clipper (L 8xx, R 9xx), U402 = TL072 shared
# ---------------------------------------------------------------------------
def ts(ch, n):
    B = f"Tube Screamer {ch}: Rf 51k / Rg 4.7k, 1N4148 pair, +9VC"
    C(f"C{n}01", "1uF film", f"PAD_{ch}", f"TS_IN_{ch}", B, fp=FP_C1U)
    R(f"R{n}01", "100k", f"TS_IN_{ch}", "VBIAS", B)
    R(f"R{n}02", "4.7k", f"TS_FB_{ch}", "VBIAS", B)
    R(f"R{n}03", "51k", f"TS_CLIP_{ch}", f"TS_FB_{ch}", B)
    D(f"D{n}01", "1N4148W", f"TS_FB_{ch}", f"TS_CLIP_{ch}", B, MPN="1N4148W-7-F")
    D(f"D{n}02", "1N4148W", f"TS_CLIP_{ch}", f"TS_FB_{ch}", B, MPN="1N4148W-7-F")
    C(f"C{n}03", "51pF", f"TS_CLIP_{ch}", f"TS_FB_{ch}", B)
    C(f"C{n}04", "1uF film", f"TS_CLIP_{ch}", f"TS_DIV_{ch}", B, fp=FP_C1U)
    R(f"R{n}04", "100k", f"TS_DIV_{ch}", "AGND", B, Description="bias return")
    R(f"R{n}05", "59k", f"TS_OUT_{ch}", f"TS_FB2_{ch}", B, Description="non-inverting x6.9 = 69.3 x 1.185/11.85 (+1.4 dB clean, as plugin)")
    R(f"R{n}06", "10k", f"TS_FB2_{ch}", "AGND", B)

ts("L", 8)
ts("R", 9)
OPAMP2("U402", {1: ("TS_IN_L", "TS_FB_L", "TS_CLIP_L"), 2: ("TS_IN_R", "TS_FB_R", "TS_CLIP_R")},
       "Tube Screamer L: Rf 51k / Rg 4.7k, 1N4148 pair, +9VC")
C("C805", "100nF", "+9VC", "AGND", "Tube Screamer L: Rf 51k / Rg 4.7k, 1N4148 pair, +9VC")

# ---------------------------------------------------------------------------
# Mode 5: Opto compressor (11xx). Shunt LDR divider per channel, linked sidechain.
# ---------------------------------------------------------------------------
B = "Opto compressor: VTL5C3 shunt divider per channel, linked feed-forward sidechain"
R("R1101", "22k", "HPF_OUT_L", "OPTO_N_L", B)
VACTROL("VT1101", "OPTO_LED_A", "OPTO_LED_MID", "OPTO_N_L", "AGND", B)
R("R1121", "22k", "HPF_OUT_R", "OPTO_N_R", B)
VACTROL("VT1121", "OPTO_LED_MID", "AGND", "OPTO_N_R", "AGND", B)
# sidechain: sum -> precision half-wave -> 10 ms average -> LED driver
R("R1141", "100k", "HPF_OUT_L", "SC1_N", B)
R("R1142", "100k", "HPF_OUT_R", "SC1_N", B)
R("R1143", "47k", "SC1_N", "SC1_SUM", B)
R("R1144", "10k", "SC1_SUM", "SC1_RN", B)
D("D1141", "1N4148W", "SC1_RN", "SC1_OP", B, MPN="1N4148W-7-F")
D("D1142", "1N4148W", "SC1_OP", "SC1_X", B, MPN="1N4148W-7-F")
R("R1145", "10k", "SC1_X", "SC1_RN", B)
R("R1146", "10k", "SC1_X", "SC1_ENV", B, Description="10 ms average with C1141")
C("C1141", "1uF film", "SC1_ENV", "AGND", B, fp=FP_C1U)
R("R1148", "120k", "SC1_DRV", "SC1_DFB", B, Description="LED driver gain 13: two LEDs (3.4 V) light at -18 dBFS")
R("R1149", "10k", "SC1_DFB", "AGND", B)
R("R1150", "2.2k", "SC1_DRV", "SC1_LEDR", B)
TRIM("RV1101", "10k", "SC1_LEDR", "OPTO_LED_A", "OPTO_LED_A", B, Description="compression depth: 7 dB GR at +12 dB over threshold")
OPAMP4("U1101", {1: ("SC2_ENV", "FET_SC", "FET_SC"),
                 2: ("AGND", "SC1_N", "SC1_SUM"),
                 3: ("AGND", "SC1_RN", "SC1_OP"),
                 4: ("SC1_ENV", "SC1_DFB", "SC1_DRV")}, B)
C("C1101", "100nF", "+15VA", "AGND", B)
C("C1102", "100nF", "-15VA", "AGND", B)

# ---------------------------------------------------------------------------
# Mode 6: FET compressor (12xx). 2N5457 shunt VCR after -20.8 dB pad, x11 make-up, linked feedback sidechain.
# ---------------------------------------------------------------------------
B = "FET compressor: 2N5457 shunt divider per channel, x11 make-up, linked feedback sidechain"
def fet_ch(ch, n, unit):
    R(f"R{n}1", "22k", f"HPF_OUT_{ch}", f"FET_DIV_{ch}", B)
    R(f"R{n}2", "2.2k", f"FET_DIV_{ch}", "AGND", B)
    NJFET(f"Q{n}1", "2N5457", f"FET_DIV_{ch}", f"FET_G_{ch}", "AGND", B, MPN="2N5457")
    R(f"R{n}3", "1M", f"FET_G_{ch}", f"FET_CV_{ch}", B)
    R(f"R{n}4", "1M", f"FET_G_{ch}", f"FET_DIV_{ch}", B, Description="drain/2 to gate: distortion cancellation")
    R(f"R{n}5", "47k", f"FET_CV_{ch}", f"FET_BIAS_{ch}", B, Description="gate reaches -5.1 V at full trim")
    R(f"R{n}6", "100k", f"FET_CV_{ch}", "FET_SC", B)
    TRIM(f"RV{n}1", "10k", "-15VA", f"FET_BIAS_{ch}", "AGND", B, Description="Q bias: set gate at Vgs(off), threshold trim")
    R(f"R{n}7", "100k", f"FET_OUT_{ch}", f"FET_MK_{ch}", B)
    R(f"R{n}8", "10k", f"FET_MK_{ch}", "AGND", B)
    return (f"FET_DIV_{ch}", f"FET_MK_{ch}", f"FET_OUT_{ch}")
uL = fet_ch("L", 120, 1)
uR = fet_ch("R", 122, 2)
R("R1241", "100k", "FET_OUT_L", "SC2_N", B)
R("R1242", "100k", "FET_OUT_R", "SC2_N", B)
R("R1243", "47k", "SC2_N", "SC2_SUM", B)
R("R1244", "10k", "SC2_SUM", "SC2_RN", B)
D("D1241", "1N4148W", "SC2_RN", "SC2_OP", B, MPN="1N4148W-7-F")
D("D1242", "1N4148W", "SC2_OP", "SC2_X", B, MPN="1N4148W-7-F")
R("R1245", "10k", "SC2_X", "SC2_RN", B)
D("D1243", "1N5819HW", "SC2_X", "SC2_PK", B, lib="Device:D_Schottky", MPN="1N5819HW-7-F")
R("R1246", "1.5k", "SC2_PK", "SC2_ENV", B, Description="150 us attack with C1241")
C("C1241", "100nF", "SC2_ENV", "AGND", B, Description="detector hold cap, X7R is fine here")
R("R1247", "2.2M", "SC2_ENV", "AGND", B, Description="220 ms release")
OPAMP4("U1201", {1: uL, 2: uR, 3: ("AGND", "SC2_N", "SC2_SUM"), 4: ("AGND", "SC2_RN", "SC2_OP")}, B)
C("C1201", "100nF", "+15VA", "AGND", B)
C("C1202", "100nF", "-15VA", "AGND", B)

# ---------------------------------------------------------------------------
# Mode 7: VCA limiter (13xx). THAT2180 per channel, THAT2252 RMS detector on the summed output, 10:1.
# ---------------------------------------------------------------------------
B = "VCA limiter: THAT2180 x2, THAT2252 RMS detector (feedback), ratio 10:1"
def vca_ch(ch, n, Uvca):
    R(f"R{n}1", "20k", f"HPF_OUT_{ch}", f"VCA_IN_N_{ch}", B)
    R(f"R{n}2", "20k", f"VCA_IN_N_{ch}", f"VCA_INV_{ch}", B)
    C(f"C{n}1", "1uF film", f"VCA_INV_{ch}", f"VCA_C_{ch}", B, fp=FP_C1U, Description="keeps op-amp offset out of the log core")
    R(f"R{n}3", "20k", f"VCA_C_{ch}", f"VCA_IN_{ch}", B)
    THAT2180(Uvca, f"VCA_IN_{ch}", "AGND", "VCA_EC", f"VCA_SYM_{ch}", f"VCA_O_{ch}", B, vn=f"VCA_VN_{ch}")
    R(f"R{n}6", "5.1k", f"VCA_VN_{ch}", "-15VA", B, Description="ISET 2.4 mA, THAT2180 pin 5 must not go straight to V-")
    R(f"R{n}4", "20k", f"VCA_O_{ch}", f"VCA_OUT_{ch}", B)
    C(f"C{n}2", "22pF", f"VCA_O_{ch}", f"VCA_OUT_{ch}", B)
    TRIM(f"RV{n}1", "50k", "+15VA", f"VCA_SYMW_{ch}", "-15VA", B, DNP="yes", Description="DNP: 2180A is factory trimmed, fit only if using 2181")
    R(f"R{n}5", "510k", f"VCA_SYMW_{ch}", f"VCA_SYM_{ch}", B, DNP="yes", Description="DNP with RV")
    C(f"C{n}3", "100nF", "+15VA", "AGND", B)
    C(f"C{n}4", "100nF", "-15VA", "AGND", B)
vca_ch("L", 130, "U1303")
vca_ch("R", 132, "U1304")
OPAMP4("U1301", {1: ("AGND", "VCA_IN_N_L", "VCA_INV_L"), 2: ("AGND", "VCA_O_L", "VCA_OUT_L"),
                 3: ("AGND", "VCA_IN_N_R", "VCA_INV_R"), 4: ("AGND", "VCA_O_R", "VCA_OUT_R")}, B)
C("C1305", "100nF", "+15VA", "AGND", B)
C("C1306", "100nF", "-15VA", "AGND", B)
# detector: THAT2252 is discontinued (no stock anywhere, 2026-09), so the RMS detector is built from
# a precision full-wave rectifier, a 10 ms average and a transistor log converter (mean-absolute, log-domain).
# Log slope 3.0 mV/dB (Vt ln10 / 20) tracks the 2180's 6.1 mV/dB with temperature, so the ratio is stable.
C("C1341", "1uF film", "VCA_OUT_L", "DET_C_L", B, fp=FP_C1U)
R("R1341", "20k", "DET_C_L", "DET_SUM_N", B)
C("C1342", "1uF film", "VCA_OUT_R", "DET_C_R", B, fp=FP_C1U)
R("R1342", "20k", "DET_C_R", "DET_SUM_N", B)
R("R1343", "10k", "DET_SUM_N", "DET_SUM", B, Description="SUM = -(L+R)/2")
R("R1344", "10k", "DET_SUM", "HW_N", B)
D("D1342", "1N4148W", "HW_N", "HW_OP", B, MPN="1N4148W-7-F")
D("D1343", "1N4148W", "HW_OP", "HW_X", B, MPN="1N4148W-7-F")
R("R1345", "10k", "HW_X", "HW_N", B, Description="precision half-wave, positive output")
R("R1347", "20k", "DET_SUM", "FW_N", B)
R("R1348", "10k", "HW_X", "FW_N", B)
R("R1349", "20k", "FW_N", "FW_OUT", B, Description="full-wave: FW = -|L+R|/2")
R("R1346", "10k", "FW_OUT", "DET_AVG", B, Description="10 ms average with C1344")
C("C1344", "1uF film", "DET_AVG", "AGND", B, fp=FP_C1U)
R("R1350", "100k", "DET_AVG", "LOG_N", B, Description="5.5 uA into the log transistor at -18 dBFS")
_add("Q1341", "Transistor_BJT:MMBT3906", "MMBT3906", FP_SOT23, {1: {"1": "AGND", "2": "DET_OUT", "3": "LOG_N"}}, B,
     MPN="MMBT3906-7-F", Description="transdiode log converter: DET_OUT = +Vt ln(I/Is), about 3 mV/dB")
C("C1343", "100pF", "LOG_N", "DET_OUT", B)
OPAMP4("U1305", {1: ("AGND", "DET_SUM_N", "DET_SUM"), 2: ("AGND", "HW_N", "HW_OP"),
                 3: ("AGND", "FW_N", "FW_OUT"), 4: ("AGND", "LOG_N", "DET_OUT")}, B)
C("C1345", "100nF", "+15VA", "AGND", B)
C("C1346", "100nF", "-15VA", "AGND", B)
# threshold / ratio / clamp
R("R1351", "10k", "DET_OUT", "TH_P", B)
R("R1352", "182k", "TH_P", "AGND", B)
R("R1353", "100k", "TH_REF", "TH_N", B, Description="high value so the trimmer wiper impedance does not unbalance the difference amp")
R("R1354", "1.82M", "TH_N", "TH_OUT", B, Description="difference gain 18.2 x 3.0 mV/dB = 54 mV/dB = 8.9 dB/dB at Ec-: ratio 10:1 in feedback topology")
R("R1355", "100k", "+15VA", "TH_TOP", B)
TRIM("RV1342", "10k", "TH_TOP", "TH_REF", "TH_BOT", B, Description="threshold: +/-0.71 V range, set for -18 dBFS")
R("R1356", "100k", "TH_BOT", "-15VA", B)
D("D1341", "1N4148W", "CL_OP", "VCA_EC_RAW", B, MPN="1N4148W-7-F")
R("R1357", "10k", "VCA_EC_RAW", "AGND", B)
OPAMP4("U1302", {1: ("TH_P", "TH_N", "TH_OUT"), 2: ("TH_OUT", "VCA_EC_RAW", "CL_OP"),
                 3: ("AGND", "SPARE_U1302C", "SPARE_U1302C"), 4: ("VCA_EC_RAW", "VCA_EC", "VCA_EC")}, B)
C("C1307", "100nF", "+15VA", "AGND", B)
C("C1308", "100nF", "-15VA", "AGND", B)

# ---------------------------------------------------------------------------
# Mode relays K1..K7 (TQ2-5V), coil driven straight from the panel rotary switch (+5VAUX)
# ---------------------------------------------------------------------------
B = "Mode select: 7 x TQ2-5V relays, one energised per rotary position"
mode_out = {1: "HPF_OUT", 2: "TUBE_OUT", 3: "TAPE_OUT", 4: "TS_OUT", 5: "OPTO_OUT", 6: "FET_OUT", 7: "VCA_OUT"}
for i in range(1, 8):
    RELAY(f"K{i}", f"MODE{i}", "AGND", "BUS_L", f"{mode_out[i]}_L", "BUS_R", f"{mode_out[i]}_R", B)
    D(f"D{i}", "1N4148W", "AGND", f"MODE{i}", B, MPN="1N4148W-7-F", Description="coil flyback")

MODE_NAMES = {1: "Clean", 2: "Tube", 3: "Tape", 4: "Tube Screamer", 5: "Opto Comp", 6: "FET Comp", 7: "VCA Limiter"}
