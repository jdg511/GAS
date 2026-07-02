#!/usr/bin/env python3
"""Generate the GAS Rev A tank-driver-recovery schematic (production + sim variant).

Reads symbol definitions from the installed KiCad 10 libraries, flattens any
`extends` inheritance, and emits .kicad_sch files where every pin gets a short
wire stub plus a global net label. Connectivity is therefore explicit and
auditable, and ERC can verify it.

Run on the Windows machine that has KiCad 10 installed:
    python gen_tdr.py
"""
import math, os, re, sys, uuid

KICAD_SYMS = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
OUT_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SIM_DIR = os.path.join(OUT_DIR, "sim", "tank-driver-recovery-sim")

# ---------------------------------------------------------------- s-expressions
class Sexp(list):
    pass

def tokenize(text):
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c in "()":
            yield c; i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == '\\':
                    buf.append(text[j:j+2]); j += 2
                elif text[j] == '"':
                    break
                else:
                    buf.append(text[j]); j += 1
            yield '"' + "".join(buf) + '"'
            i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()':
                j += 1
            yield text[i:j]; i = j

def parse(text):
    stack = [Sexp()]
    for tok in tokenize(text):
        if tok == '(':
            new = Sexp(); stack[-1].append(new); stack.append(new)
        elif tok == ')':
            stack.pop()
        else:
            stack[-1].append(tok)
    return stack[0]

def dump(node, indent=0):
    if not isinstance(node, Sexp):
        return str(node)
    pad = "\t" * indent
    parts = [dump(x, indent + 1) for x in node]
    flat = "(" + " ".join(parts) + ")"
    if len(flat) < 100 and "\n" not in flat:
        return flat
    head = []
    tail_start = 0
    for k, x in enumerate(node):
        if isinstance(x, Sexp):
            break
        head.append(str(x)); tail_start = k + 1
    out = "(" + " ".join(head)
    for x in node[tail_start:]:
        out += "\n" + pad + "\t" + dump(x, indent + 1)
    out += "\n" + pad + ")"
    return out

def q(s):
    return '"%s"' % s

def find(node, key):
    for x in node:
        if isinstance(x, Sexp) and x and x[0] == key:
            return x
    return None

def findall(node, key):
    return [x for x in node if isinstance(x, Sexp) and x and x[0] == key]

# ---------------------------------------------------------------- library load
_lib_cache = {}

def load_lib(libname):
    if libname not in _lib_cache:
        path = os.path.join(KICAD_SYMS, libname + ".kicad_sym")
        with open(path, encoding="utf-8") as f:
            _lib_cache[libname] = parse(f.read())[0]
    return _lib_cache[libname]

def get_symbol_raw(libname, symname):
    lib = load_lib(libname)
    for s in findall(lib, "symbol"):
        if s[1] == q(symname):
            return s
    raise KeyError("symbol %s not found in %s" % (symname, libname))

def flatten_symbol(libname, symname):
    """Resolve extends-chains, return a self-contained symbol sexp renamed to symname."""
    sym = get_symbol_raw(libname, symname)
    ext = find(sym, "extends")
    if ext is None:
        import copy
        return copy.deepcopy(sym)
    parent = flatten_symbol(libname, ext[1].strip('"'))
    # start from parent body, override with child's properties, rename
    import copy
    merged = copy.deepcopy(parent)
    child_props = {p[1]: p for p in findall(sym, "property")}
    keep = Sexp()
    for x in merged:
        if isinstance(x, Sexp) and x and x[0] == "property" and x[1] in child_props:
            keep.append(copy.deepcopy(child_props[x[1]]))
            del child_props[x[1]]
        else:
            keep.append(x)
    for p in child_props.values():
        # insert extra child-only properties after the last property
        idx = max(i for i, x in enumerate(keep) if isinstance(x, Sexp) and x and x[0] == "property")
        keep.insert(idx + 1, copy.deepcopy(p))
    # rename parent -> child everywhere (symbol name + unit sub-symbols)
    pname = parent[1].strip('"')
    def rename(node):
        for i, x in enumerate(node):
            if isinstance(x, Sexp):
                rename(x)
            elif isinstance(x, str) and x.startswith('"') and x.strip('"').startswith(pname):
                node[i] = q(symname + x.strip('"')[len(pname):])
    keep[1] = q(symname)
    for sub in findall(keep, "symbol"):
        sub[1] = q(symname + sub[1].strip('"')[len(pname):])
    return keep

def embed_symbol(libname, symname):
    sym = flatten_symbol(libname, symname)
    sym[1] = q(libname + ":" + symname)
    return sym

def symbol_pins(libname, symname):
    """{unit: [(number, name, x, y, angle)]} - unit 0 pins are common to all."""
    sym = flatten_symbol(libname, symname)
    pins = {}
    for sub in findall(sym, "symbol"):
        m = re.match(r'^"?%s_(\d+)_(\d+)"?$' % re.escape(symname), sub[1])
        if not m:
            continue
        unit = int(m.group(1))
        for p in findall(sub, "pin"):
            at = find(p, "at")
            num = find(p, "number")[1].strip('"')
            name = find(p, "name")[1].strip('"')
            pins.setdefault(unit, []).append((num, name, float(at[1]), float(at[2]), float(at[3])))
    return pins

# ---------------------------------------------------------------- id helpers
_uuid_n = 0

def uid():
    global _uuid_n
    _uuid_n += 1
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "gas-tdr-%d" % _uuid_n))

# ---------------------------------------------------------------- circuit data
GRID = 2.54
STUB = 5.08

def C(ref, lib, name, value, fp, unitpins, dnp=False, nosim=False, sim=None, w=25.4, h=30.48):
    return dict(ref=ref, lib=lib, name=name, value=value, fp=fp,
                units=unitpins, dnp=dnp, nosim=nosim, sim=sim or {}, w=w, h=h)

FP_R0805 = "Resistor_SMD:R_0805_2012Metric"
FP_R1206 = "Resistor_SMD:R_1206_3216Metric"
FP_R2512 = "Resistor_SMD:R_2512_6332Metric"
FP_C0805 = "Capacitor_SMD:C_0805_2012Metric"
FP_C1206 = "Capacitor_SMD:C_1206_3216Metric"
FP_C1210 = "Capacitor_SMD:C_1210_3225Metric"
FP_SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
FP_TO126 = "Package_TO_SOT_THT:TO-126-3_Vertical"
FP_SOD123 = "Diode_SMD:D_SOD-123"
FP_XH2 = "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
FP_XH6 = "Connector_JST:JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical"
FP_VH3 = "Connector_JST:JST_VH_B3P-VH_1x03_P3.96mm_Vertical"

OPA = "OPA1656ID"
OPA_SIM = {"Sim.Library": "gas-models.lib", "Sim.Name": "OPA1656X2",
           "Sim.Device": "SUBCKT",
           "Sim.Pins": "1=out1 2=in1n 3=in1p 4=vn 5=in2p 6=in2n 7=out2 8=vp"}

def res(ref, value, net1, net2, fp=FP_R0805, dnp=False):
    return C(ref, "Device", "R", value, fp, {1: {"1": net1, "2": net2}}, dnp=dnp)

def cap(ref, value, net1, net2, fp=FP_C0805, dnp=False):
    return C(ref, "Device", "C", value, fp, {1: {"1": net1, "2": net2}}, dnp=dnp)

def diode(ref, netA, netK, dnp=True):
    # Device:D pin 1 = K (cathode), pin 2 = A (anode)
    return C(ref, "Device", "D", "1N4148W", FP_SOD123,
             {1: {"1": netK, "2": netA}}, dnp=dnp,
             sim={"Sim.Library": "gas-models.lib", "Sim.Name": "D1N4148",
                  "Sim.Device": "D", "Sim.Pins": "1=K 2=A"})

def npn(ref, part, nB, nC, nE):
    return C(ref, "Transistor_BJT", part, part + "-16", FP_TO126,
             {1: {"B": nB, "C": nC, "E": nE}},
             sim={"Sim.Library": "gas-models.lib",
                  "Sim.Name": part + "_16",
                  "Sim.Device": "NPN" if part == "BD139" else "PNP",
                  # symbol pins: 1=E 2=C 3=B ; model nodes: 1=C 2=B 3=E
                  "Sim.Pins": "1=3 2=1 3=2"})

def conn2(ref, value, n1, n2, nosim=True):
    return C(ref, "Connector", "Conn_Coaxial", value, FP_XH2,
             {1: {"1": n1, "2": n2}}, nosim=nosim)

SECTIONS = []

def section(title, comps):
    SECTIONS.append((title, comps))

# --- Primary send L -----------------------------------------------------------
section("PRIMARY SEND LEFT  (4AB1C1B, 8R)", [
    C("U101", "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
      {1: {"1": "PRI_DRV_L", "2": "N_PRI_L_M", "3": "N_PRI_L_P"}}, sim=OPA_SIM),
    res("R107", "10k", "PRI_SEND_L", "N_PRI_L_P"),
    res("R106", "1k", "PRI_SEND_L", "N_PRI_L_M"),
    res("R108", "10k", "PRI_OUT_L", "N_PRI_L_M"),
    res("R101", "68", "PRI_DRV_L", "N_Q101_B"),
    res("R102", "68", "PRI_DRV_L", "N_Q102_B"),
    diode("D101", "N_Q101_B", "PRI_DRV_L"),
    diode("D102", "PRI_DRV_L", "N_Q102_B"),
    npn("Q101", "BD139", "N_Q101_B", "+15VA", "N_Q101_E"),
    npn("Q102", "BD140", "N_Q102_B", "-15VA", "N_Q102_E"),
    res("R103", "0.33", "N_Q101_E", "PRI_OUT_L", fp=FP_R2512),
    res("R104", "0.33", "N_Q102_E", "PRI_OUT_L", fp=FP_R2512),
    res("R105", "10", "PRI_OUT_L", "N_ZOB_L", fp=FP_R1206),
    cap("C101", "47n", "N_ZOB_L", "AGND", fp=FP_C1210),
    conn2("J101", "PRI L SEND", "PRI_OUT_L", "TANK_SHIELD_SEND"),
])

# --- Primary send R -----------------------------------------------------------
section("PRIMARY SEND RIGHT  (4AB1C1B, 8R)", [
    C("U101_B", "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
      {2: {"5": "N_PRI_R_P", "6": "N_PRI_R_M", "7": "PRI_DRV_R"}}, sim=OPA_SIM),
    res("R127", "10k", "PRI_SEND_R", "N_PRI_R_P"),
    res("R126", "1k", "PRI_SEND_R", "N_PRI_R_M"),
    res("R128", "10k", "PRI_OUT_R", "N_PRI_R_M"),
    res("R121", "68", "PRI_DRV_R", "N_Q103_B"),
    res("R122", "68", "PRI_DRV_R", "N_Q104_B"),
    diode("D121", "N_Q103_B", "PRI_DRV_R"),
    diode("D122", "PRI_DRV_R", "N_Q104_B"),
    npn("Q103", "BD139", "N_Q103_B", "+15VA", "N_Q103_E"),
    npn("Q104", "BD140", "N_Q104_B", "-15VA", "N_Q104_E"),
    res("R123", "0.33", "N_Q103_E", "PRI_OUT_R", fp=FP_R2512),
    res("R124", "0.33", "N_Q104_E", "PRI_OUT_R", fp=FP_R2512),
    res("R125", "10", "PRI_OUT_R", "N_ZOB_R", fp=FP_R1206),
    cap("C121", "47n", "N_ZOB_R", "AGND", fp=FP_C1210),
    conn2("J103", "PRI R SEND", "PRI_OUT_R", "TANK_SHIELD_SEND"),
])

# --- Secondary sends ----------------------------------------------------------
section("SECONDARY SENDS  (9EB2C1B L / 9EB3C1B R, 800R)", [
    C("U102", "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
      {1: {"1": "SEC_DRV_L", "2": "N_SEC_L_M", "3": "N_SEC_L_P"}}, sim=OPA_SIM),
    res("R157", "10k", "SEC_SEND_L", "N_SEC_L_P"),
    res("R153", "10k", "N_SEC_L_M", "AGND"),
    res("R151", "12k", "SEC_DRV_L", "N_SEC_L_M"),
    res("R155", "220", "SEC_DRV_L", "SEC_OUT_L"),
    conn2("J105", "SEC L SEND", "SEC_OUT_L", "TANK_SHIELD_SEND"),
    C("U102_B", "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
      {2: {"5": "N_SEC_R_P", "6": "N_SEC_R_M", "7": "SEC_DRV_R"}}, sim=OPA_SIM),
    res("R158", "10k", "SEC_SEND_R", "N_SEC_R_P"),
    res("R154", "10k", "N_SEC_R_M", "AGND"),
    res("R152", "12k", "SEC_DRV_R", "N_SEC_R_M"),
    res("R156", "220", "SEC_DRV_R", "SEC_OUT_R"),
    conn2("J107", "SEC R SEND", "SEC_OUT_R", "TANK_SHIELD_SEND"),
])

# --- Recovery -----------------------------------------------------------------
def recovery(uref, unit, pins, jref, jname, n_in, n_in2, rb, rj, rg, rf, cf, cs, out):
    pmap = dict(zip(("out", "inm", "inp"), pins))
    comps = [
        C(uref, "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
          {unit: {pmap["out"]: out, pmap["inm"]: "N_%s_M" % out, pmap["inp"]: n_in2}},
          sim=OPA_SIM),
        conn2(jref, jname, n_in, "TANK_SHIELD_RET"),
        res(rb, "2.2Meg", n_in, "AGND"),
        # 0R jumper on the board; simulated as 10 mOhm so the matrix stays well-conditioned
        C(rj, "Device", "R", "0", FP_R0805, {1: {"1": n_in, "2": n_in2}},
          sim={"Sim.Device": "R", "Sim.Params": "r=10m"}),
        cap(cs, "22n", n_in, n_in2, fp=FP_C1206, dnp=True),
        res(rg, "1k", "N_%s_M" % out, "AGND"),
        res(rf, "33k", out, "N_%s_M" % out),
        cap(cf, "68p", out, "N_%s_M" % out),
    ]
    return comps

section("RECOVERY  PRIMARY L", recovery("U103", 1, ("1", "2", "3"), "J102", "PRI L RET",
        "PRI_REC_L_IN", "N_REC_PL_IN", "R171", "R183", "R175", "R179", "C171", "C175", "PRI_RET_L"))
section("RECOVERY  PRIMARY R", recovery("U103_B", 2, ("7", "6", "5"), "J104", "PRI R RET",
        "PRI_REC_R_IN", "N_REC_PR_IN", "R172", "R184", "R176", "R180", "C172", "C176", "PRI_RET_R"))
section("RECOVERY  SECONDARY L", recovery("U104", 1, ("1", "2", "3"), "J106", "SEC L RET",
        "SEC_REC_L_IN", "N_REC_SL_IN", "R173", "R185", "R177", "R181", "C173", "C177", "SEC_RET_L"))
section("RECOVERY  SECONDARY R", recovery("U104_B", 2, ("7", "6", "5"), "J108", "SEC R RET",
        "SEC_REC_R_IN", "N_REC_SR_IN", "R174", "R186", "R178", "R182", "C174", "C178", "SEC_RET_R"))

# --- Power, decoupling, harness, shield ----------------------------------------
pwr_comps = []
for i, u in enumerate(["U101", "U102", "U103", "U104"]):
    pwr_comps.append(C(u + "_P", "Amplifier_Operational", OPA, "OPA1656IDR", FP_SOIC8,
                       {3: {"8": "+15VA", "4": "-15VA"}}, sim=OPA_SIM))
for i in range(4):
    pwr_comps.append(cap("C29%d" % (i + 1), "100n", "+15VA", "AGND"))
for i in range(4):
    pwr_comps.append(cap("C29%d" % (i + 5), "100n", "-15VA", "AGND"))
pwr_comps.append(cap("C299", "22u", "+15VA", "AGND", fp=FP_C1210))
pwr_comps.append(cap("C300", "22u", "-15VA", "AGND", fp=FP_C1210))
pwr_comps.append(C("P103", "Connector_Generic", "Conn_01x03", "JTR-PWR B3P-VH-B", FP_VH3,
                   {1: {"1": "+15VA", "2": "AGND", "3": "-15VA"}}, nosim=True))
for i, net in enumerate(["+15VA", "-15VA", "AGND"]):
    pwr_comps.append(C("#FLG10%d" % (i + 1), "power", "PWR_FLAG", "PWR_FLAG", "",
                       {1: {"1": net}}, nosim=True, w=15.24, h=20.32))
section("POWER ENTRY + DECOUPLING", pwr_comps)

section("BOARD HARNESS", [
    C("P101", "Connector_Generic", "Conn_01x06", "JTR-PRI B6B-XH-A", FP_XH6,
      {1: {"1": "PRI_SEND_L", "2": "PRI_RET_L", "3": "AGND",
           "4": "PRI_SEND_R", "5": "PRI_RET_R", "6": "AGND"}}, nosim=True, h=35.56),
    C("P102", "Connector_Generic", "Conn_01x06", "JTR-SEC B6B-XH-A", FP_XH6,
      {1: {"1": "SEC_SEND_L", "2": "SEC_RET_L", "3": "AGND",
           "4": "SEC_SEND_R", "5": "SEC_RET_R", "6": "AGND"}}, nosim=True, h=35.56),
])

_shield = [
    res("R205", "100", "TANK_SHIELD_RET", "AGND", fp=FP_R1206),
    cap("C191", "1n", "TANK_SHIELD_RET", "AGND"),
    res("R206", "0", "TANK_SHIELD_SEND", "TANK_SHIELD_RET", fp=FP_R1206),
]
for _c in _shield:
    _c["simskip"] = True
section("TANK SHIELD STRATEGY", _shield)

# --- sim-only additions ---------------------------------------------------------
def vsrc(ref, symname, value, params, n1, n2):
    return C(ref, "Simulation_SPICE", symname, value, "",
             {1: {"1": n1, "2": n2}},
             sim={"Sim.Device": "V",
                  "Sim.Type": "DC" if symname == "VDC" else "SIN",
                  "Sim.Params": params}, w=20.32)

def tank(ref, model, nin, nret):
    return C(ref, "Device", "Transformer_1P_1S", model, "",
             {1: {"1": nin, "2": "GND", "3": nret, "4": "GND"}},
             sim={"Sim.Library": "tanks.lib", "Sim.Name": model,
                  "Sim.Device": "SUBCKT", "Sim.Pins": "1=ip 2=iret 3=op 4=oret"},
             w=25.4, h=27.94)

SIM_SECTIONS = [
    ("SIM: SUPPLIES + SOURCES", [
        vsrc("V1", "VDC", "15V", "dc=15", "+15VA", "GND"),
        vsrc("V2", "VDC", "15V", "dc=15", "GND", "-15VA"),
        vsrc("V3", "VDC", "0V AGND bond", "dc=0", "AGND", "GND"),
        vsrc("V4", "VSIN", "0.5Vpk 1kHz", "dc=0 ampl=0.5 f=1k ac=1", "PRI_SEND_L", "AGND"),
        vsrc("V5", "VSIN", "0.5Vpk 1kHz", "dc=0 ampl=0.5 f=1k ac=1", "PRI_SEND_R", "AGND"),
        vsrc("V6", "VSIN", "0.5Vpk 1kHz", "dc=0 ampl=0.5 f=1k ac=1", "SEC_SEND_L", "AGND"),
        vsrc("V7", "VSIN", "0.5Vpk 1kHz", "dc=0 ampl=0.5 f=1k ac=1", "SEC_SEND_R", "AGND"),
    ]),
    ("SIM: SPRING TANK ELECTRICAL MODELS", [
        tank("TK1", "TANK_4AB1C1B", "PRI_OUT_L", "PRI_REC_L_IN"),
        tank("TK2", "TANK_4AB1C1B", "PRI_OUT_R", "PRI_REC_R_IN"),
        tank("TK3", "TANK_9EB2C1B", "SEC_OUT_L", "SEC_REC_L_IN"),
        tank("TK4", "TANK_9EB3C1B", "SEC_OUT_R", "SEC_REC_R_IN"),
    ]),
]

# ---------------------------------------------------------------- emit schematic
def build(sim):
    root_uuid = uid()
    project = "tank-driver-recovery-sim" if sim else "tank-driver-recovery"
    body = []
    body.append('(kicad_sch')
    body.append('\t(version 20250114)')
    body.append('\t(generator "eeschema")')
    body.append('\t(generator_version "10.0")')
    body.append('\t(uuid "%s")' % root_uuid)
    body.append('\t(paper "A2")')
    title = "GAS Rev A - Tank Driver Recovery" + (" - SIMULATION TESTBENCH" if sim else " Board")
    body.append('\t(title_block\n\t\t(title "%s")\n\t\t(company "Illicit Apothecary")'
                '\n\t\t(comment 1 "Netlist-style capture: every pin carries a stub and a global net label")'
                '\n\t\t(comment 2 "Generated by hardware/kicad/rebuild/gen_tdr.py - edit the generator, not this file")\n\t)' % title)

    # collect needed lib symbols
    sections = SECTIONS + (SIM_SECTIONS if sim else [])
    needed, comps = {}, []
    def skip_in_sim(c):
        return sim and (c.get("simskip") or (c["nosim"] and c["lib"] == "Connector"))

    for _, cs in sections:
        for c in cs:
            if skip_in_sim(c):
                continue  # tank jacks / shield bond replaced by tank models in the sim sheet
            needed[(c["lib"], c["name"])] = True
            comps.append(c)
    if sim:
        needed[("power", "GND")] = True

    libsyms = []
    pincache = {}
    for lib, name in needed:
        libsyms.append(dump(embed_symbol(lib, name), 2))
        pincache[(lib, name)] = symbol_pins(lib, name)
    body.append('\t(lib_symbols\n\t\t' + "\n\t\t".join(libsyms) + '\n\t)')

    texts, wires, labels, symbols = [], [], [], []

    def add_label(net, x, y, ang, just):
        labels.append(
            '\t(global_label "%s"\n\t\t(shape passive)\n\t\t(at %.2f %.2f %d)\n\t\t(fields_autoplaced yes)'
            '\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)'
            '\n\t\t(uuid "%s")\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n\t\t\t(at %.2f %.2f 0)'
            '\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)\n\t)'
            % (net, x, y, ang, just, uid(), x, y))

    def add_wire(x1, y1, x2, y2):
        wires.append('\t(wire\n\t\t(pts\n\t\t\t(xy %.2f %.2f) (xy %.2f %.2f)\n\t\t)'
                     '\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                     % (x1, y1, x2, y2, uid()))

    def place(c, X, Y):
        lib, name = c["lib"], c["name"]
        allpins = pincache[(lib, name)]
        ref = c["ref"].split("_")[0] if not c["ref"].startswith("#") else c["ref"]
        for unit, netmap in c["units"].items():
            upins = allpins.get(unit, []) + allpins.get(0, [])
            sy = ('\t(symbol\n\t\t(lib_id "%s:%s")\n\t\t(at %.2f %.2f 0)\n\t\t(unit %d)'
                  '\n\t\t(exclude_from_sim %s)\n\t\t(in_bom %s)\n\t\t(on_board %s)\n\t\t(dnp %s)'
                  '\n\t\t(fields_autoplaced yes)\n\t\t(uuid "%s")'
                  % (lib, name, X, Y, unit,
                     "yes" if (c["nosim"] or c["dnp"]) else "no",
                     "no" if c["ref"].startswith("#") else "yes",
                     "no" if c["ref"].startswith("#") else "yes",
                     "yes" if c["dnp"] else "no", uid()))
            props = [("Reference", ref, False), ("Value", c["value"], False),
                     ("Footprint", c["fp"], True), ("Datasheet", "", True)]
            for k, v in c["sim"].items():
                props.append((k, v, True))
            py_off = -c["h"] / 2 - 1.27
            for j, (k, v, hide) in enumerate(props):
                sy += ('\n\t\t(property "%s" "%s"\n\t\t\t(at %.2f %.2f 0)'
                       '\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)%s\n\t\t\t)\n\t\t)'
                       % (k, v.replace('"', ''), X, Y + py_off - 2.54 * j,
                          "\n\t\t\t\t(hide yes)" if hide else ""))
            for num, pname, px, py, pang in upins:
                sy += '\n\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (num, uid())
            sy += ('\n\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s"\n\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit %d)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
                   % (project, root_uuid, ref, unit))
            symbols.append(sy)
            # stubs + labels
            for num, pname, px, py, pang in upins:
                key = num
                net = netmap.get(num) or netmap.get(pname)
                if net is None:
                    continue
                ex, ey = X + px, Y - py
                dx, dy = -math.cos(math.radians(pang)), math.sin(math.radians(pang))
                lx, ly = ex + dx * STUB, ey + dy * STUB
                add_wire(ex, ey, lx, ly)
                if abs(dx) > 0.5:
                    ang = 0 if dx > 0 else 180
                    just = "left" if dx > 0 else "right"
                else:
                    ang = 90 if dy < 0 else 270
                    just = "left" if dy < 0 else "right"
                add_label(net, lx, ly, ang, just)

    # layout: sections stacked, components in rows
    Y0 = 40.64
    PERROW = 7
    for title_txt, cs in sections:
        cs = [c for c in cs if not skip_in_sim(c)]
        if not cs:
            continue
        texts.append('\t(text "%s"\n\t\t(exclude_from_sim yes)\n\t\t(at 25.4 %.2f 0)'
                     '\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 2.54 2.54) (bold yes)\n\t\t\t)\n\t\t\t(justify left)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                     % (title_txt, Y0 - 10.16, uid()))
        maxh = 0
        for i, c in enumerate(cs):
            col, row = i % PERROW, i // PERROW
            X = 50.8 + col * 38.1
            Y = Y0 + row * 45.72
            X = round(X / GRID) * GRID
            Y = round(Y / GRID) * GRID
            place(c, X, Y)
            maxh = max(maxh, (row + 1) * 45.72)
        Y0 += maxh + 25.4

    if sim:
        # power:GND symbol on the GND net
        gnd_pins = pincache[("power", "GND")]
        place(C("#PWR01", "power", "GND", "GND", "", {1: {"1": "GND"}}, nosim=False, w=10, h=10),
              50.8, round((Y0) / GRID) * GRID)
        place(C("#FLG201", "power", "PWR_FLAG", "PWR_FLAG", "", {1: {"1": "GND"}}, nosim=True, w=10, h=10),
              76.2, round((Y0) / GRID) * GRID)
        directives = (".tran 20u 60m\n"
                      "\n; switch to AC analysis by commenting .tran and uncommenting:\n"
                      "; .ac dec 50 10 100k\n"
                      ".options savecurrents")
        texts.append('\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at 25.4 %.2f 0)'
                     '\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 2.0 2.0)\n\t\t\t)\n\t\t\t(justify left)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                     % (directives.replace("\n", "\\n"), Y0 + 30.48, uid()))

    body.extend(texts)
    body.extend(wires)
    body.extend(labels)
    body.extend(symbols)
    body.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)')
    body.append('\t(embedded_fonts no)')
    body.append(')')
    return "\n".join(body) + "\n"

# ---------------------------------------------------------------- write outputs
def main():
    prod = build(sim=False)
    with open(os.path.join(OUT_DIR, "tank-driver-recovery.kicad_sch"), "w", encoding="utf-8") as f:
        f.write(prod)
    os.makedirs(SIM_DIR, exist_ok=True)
    simsch = build(sim=True)
    with open(os.path.join(SIM_DIR, "tank-driver-recovery-sim.kicad_sch"), "w", encoding="utf-8") as f:
        f.write(simsch)
    pro = ('{\n  "board": { "design_settings": {}, "layer_presets": [], "viewports": [] },\n'
           '  "libraries": { "pinned_footprint_libs": [], "pinned_symbol_libs": [] },\n'
           '  "meta": { "filename": "tank-driver-recovery-sim.kicad_pro", "version": 3 },\n'
           '  "schematic": { "legacy_lib_dir": "", "legacy_lib_list": [] },\n'
           '  "sheets": [],\n  "text_variables": {}\n}\n')
    propath = os.path.join(SIM_DIR, "tank-driver-recovery-sim.kicad_pro")
    if not os.path.exists(propath):
        with open(propath, "w", encoding="utf-8") as f:
            f.write(pro)
    print("Wrote production + sim schematics. Components:",
          sum(len(cs) for _, cs in SECTIONS))

if __name__ == "__main__":
    main()