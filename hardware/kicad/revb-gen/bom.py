"""Build the PCBWay BOM (grouped) and an MPN map for the Rev B circuit board from design.py."""
import sys, os, csv, collections, re
sys.path.insert(0, os.path.dirname(__file__))
import design

OUT = "/home/claude/gas-revb/out"

def rcode(val):
    """Yageo RC0603FR-07 value code."""
    v = val.replace("R", "").replace("k", "K").replace("M", "M")
    m = re.match(r"^([\d.]+)([KM]?)$", v)
    num, suf = m.group(1), m.group(2)
    if suf == "":
        suf = "R"
    if "." in num:
        a, b = num.split(".")
        code = f"{a}{suf}{b}"
    else:
        code = f"{num}{suf}"
    return f"RC0603FR-07{code}L"

MPN = {  # (value, footprint-key) -> (MPN, Manufacturer, Alt, note)
    ("22pF", "0603"): ("CL10C220JB8NNNC", "Samsung", "", "C0G 50V"),
    ("51pF", "0603"): ("CL10C510JB8NNNC", "Samsung", "", "C0G 50V"),
    ("100pF", "0603"): ("CL10C101JB8NNNC", "Samsung", "", "C0G 50V"),
    ("100nF", "0603"): ("CL10B104KB8NNNC", "Samsung", "", "X7R 50V"),
    ("1uF", "0603"): ("CL10A105KA8NNNC", "Samsung", "", "X5R 25V, bias filter only"),
    ("68nF film", "1210"): ("ECH-U1C683JX5", "Panasonic", "", "PPS film 16V 5%"),
    ("47nF film", "1206"): ("ECH-U1C473JX5", "Panasonic", "", "PPS film 16V 5%"),
    ("15nF film", "1206"): ("ECH-U1C153JX5", "Panasonic", "", "PPS film 16V 5%"),
    ("6.8nF film", "0805"): ("ECH-U1C682JX5", "Panasonic", "", "PPS film 16V 5%"),
    ("3.3nF film", "0805"): ("ECH-U1C332JX5", "Panasonic", "", "PPS film 16V 5%"),
    ("1uF film", "THT"): ("MKS2C041001F00KSSD", "WIMA", "R82EC4100AA50K (Kemet)", "polyester box 63V, 5 mm pitch"),
    ("10uF", "CP5"): ("UWT1H100MCL1GB", "Nichicon", "", "50V SMD electrolytic 5x5.8"),
    ("47uF", "CP6"): ("UWT1E470MCL1GS", "Nichicon", "UWT1C470MCL1GS", "25V SMD electrolytic 6.3x5.8"),
    ("1N4148W", "D"): ("1N4148W-7-F", "Diodes Inc", "", "SOD-123"),
    ("1N5819HW", "D"): ("1N5819HW-7-F", "Diodes Inc", "", "Schottky SOD-123, detector diode"),
    ("TQ2-5V", "K"): ("TQ2-5V", "Panasonic", "", "DPDT 5V signal relay, no substitutes"),
    ("VTL5C3", "VT"): ("VTL5C3", "Xvive", "", "vactrol, sold by pedal-parts distributors (Small Bear, Tayda, Stompbox Parts); consign if PCBWay cannot source"),
    ("J201", "Q"): ("J201", "InterFET", "MMBFJ201 on SOT-23 adapter", "TO-92 JFET, InterFET is the only active TO-92 source"),
    ("2N5457", "Q"): ("2N5457", "InterFET", "", "TO-92 JFET, InterFET; screen for |Vgs(off)| < 5 V"),
    ("MMBT3904", "Q"): ("MMBT3904-7-F", "Diodes Inc", "", "SOT-23"),
    ("MMBT3906", "Q"): ("MMBT3906-7-F", "Diodes Inc", "", "SOT-23"),
    ("OPA1679IDR", "U"): ("OPA1679IDR", "Texas Instruments", "", "SOIC-14 quad"),
    ("TL072H", "U"): ("TL072HIDR", "Texas Instruments", "", "SOIC-8 dual, rated to 4.5 V supply"),
    ("THAT2180A", "U"): ("2180AL08-U", "THAT", "2180CL08-U", "SIP-8 VCA. EOL: Mouser had 1226 pcs on 2026-09-13, buy for all boards now"),
    ("L78L09", "U"): ("L78L09ACUTR", "STMicroelectronics", "", "SOT-89"),
    ("10k", "RV"): ("3314J-1-103E", "Bourns", "", "4 mm SMD trimmer"),
    ("50k", "RV"): ("3314J-1-503E", "Bourns", "", "4 mm SMD trimmer"),
    ("JXF-CIR", "P"): ("B3B-XH-A(LF)(SN)", "JST", "", ""),
    ("JCIR-WET", "P"): ("B3B-XH-A(LF)(SN)", "JST", "", ""),
    ("JCIR-PWR", "P"): ("B3P-VH(LF)(SN)", "JST", "", ""),
    ("JCIR-CTL-A", "P"): ("B16B-XH-A(LF)(SN)", "JST", "", ""),
    ("JCIR-CTL-B", "P"): ("B16B-XH-A(LF)(SN)", "JST", "", ""),
}

def key_for(p):
    ref, val, fp = p["ref"], p["value"], p["fp"]
    if ref.startswith("R") and not ref.startswith("RV"):
        return None
    if ref.startswith("RV"):
        return (val, "RV")
    if ref.startswith("C"):
        if "1210" in fp: return (val, "1210")
        if "1206" in fp: return (val, "1206")
        if "0805" in fp: return (val, "0805")
        if "6.3x5.8" in fp: return (val, "CP6")
        if "CP_Elec" in fp: return (val, "CP5")
        if "THT" in fp: return (val, "THT")
        return (val, "0603")
    if ref.startswith("D"): return (val, "D")
    if ref.startswith("K"): return (val, "K")
    if ref.startswith("VT"): return (val, "VT")
    if ref.startswith("Q"): return (val, "Q")
    if ref.startswith("U"): return (val, "U")
    if ref.startswith("P"): return (val, "P")
    return None

groups = collections.OrderedDict()
mpn_map = {}
for p in design.parts:
    ref = p["ref"]
    if ref.startswith("#") or ref.startswith("H"):
        continue
    dnp = p["props"].get("DNP") == "yes"
    if ref.startswith("R") and not ref.startswith("RV"):
        mpn, mfr, alt, note = rcode(p["value"]), "Yageo", "", "0603 1% thick film"
    else:
        k = key_for(p)
        if k not in MPN:
            raise SystemExit(f"no MPN for {ref} {k}")
        mpn, mfr, alt, note = MPN[k]
    mpn_map[ref] = (mpn, mfr)
    g = (p["value"], p["fp"], mpn, mfr, alt, "DNP" if dnp else "", note)
    groups.setdefault(g, []).append(ref)

def pkg(fp):
    return fp.split(":")[1] if ":" in fp else fp

def compress(refs):
    return ",".join(refs)

with open(f"{OUT}/circuit-board-BOM-RevB.csv", "w", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(["Refs", "Value", "Footprint", "Package", "MPN", "Manufacturer", "Alt_MPN", "DNP", "Qty", "Notes"])
    for (val, fp, mpn, mfr, alt, dnp, note), refs in groups.items():
        w.writerow([compress(refs), val, fp, pkg(fp), mpn, mfr, alt, dnp, len(refs), note])
print("BOM lines:", len(groups), "parts:", sum(len(v) for v in groups.values()))
import json
json.dump(mpn_map, open(f"{OUT}/mpn_map.json", "w"), indent=1)
