"""GAS Rev C power board: DC entry, protection, isolated +/-15 V, +5VAUX, distribution."""
import core
from core import *


def build():
    b = Board("power-board", "GAS Rev C - Power board (DC in, +/-15VA, +5VAUX)",
              ["24 to 30 V DC in (panel jack J5 on the endcap, flying leads to P1)",
               "TRACO TEL 12-2423 isolated +/-15 V 12 W, RECOM R-78E5.0-0.5 for +5VAUX relay/control rail",
               "Every board gets VH-4: 1 +15VA, 2 AGND, 3 -15VA, 4 +5VAUX"])
    b.outline = (120.0, 62.0)
    b.power_nets = {"AGND", "+15VA", "-15VA", "+5VAUX", "VIN_RAW", "VIN_FUSED", "VIN_PROT", "PGND", "+15V_DC", "-15V_DC"}
    B = "DC entry and protection"
    b.CONN("P1", "DC-IN (from panel jack)", FP_VH.format(n=2), ["VIN_RAW", "PGND"], B, MPN="B2P-VH(LF)(SN)", Manufacturer="JST",
           Description="1 = centre pin (+), 2 = sleeve. 24-30 V regulated adapter, 1 A or more")
    b.add("F1", "Device:Polyfuse", "MF-SM100/33", FP_FUSE, {1: {"1": "VIN_RAW", "2": "VIN_FUSED"}}, B,
          MPN="MF-SM100/33-2", Manufacturer="Bourns", Description="1.1 A hold, 33 V rated")
    b.D("D1", "SS34", "VIN_FUSED", "VIN_PROT", B, lib="Device:D_Schottky", fp=FP_SMA, MPN="SS34", Manufacturer="onsemi",
        Description="reverse polarity series diode")
    b.add("D2", "Device:D_Zener", "SMAJ33A", FP_SMA, {1: {"1": "VIN_PROT", "2": "PGND"}}, B, MPN="SMAJ33A", Manufacturer="Littelfuse",
          Description="33 V standoff TVS (unidirectional, cathode = pin 1 on VIN_PROT)")
    b.CP("C1", "100uF 50V", "VIN_PROT", "PGND", B, fp=FP_CP8, MPN="EEE-FK1H101P", Manufacturer="Panasonic",
         Description="input bulk, 50 V (Rev A used a 25 V part on a 30 V rail)")
    b.C("C2", "4.7uF 50V", "VIN_PROT", "PGND", B, fp=FP_C1210, MPN="GRM32ER71H475KA88L", Manufacturer="Murata")
    B = "Isolated +/-15 V"
    b.add("PS1", "GAS_Parts:TEL12_DUAL", "TEL 12-2423", FP_TEL12,
          {1: {"16": "VIN_PROT", "1": "PGND", "9": "+15V_DC", "8": "AGND", "10": "-15V_DC"}}, B,
          MPN="TEL 12-2423", Manufacturer="TRACO Power", Description="18-36 Vin, +/-15 V 400 mA, 12 W, isolated")
    b.R("R1", "0R", "PGND", "AGND", B, fp=FP_R1206, MPN="RC1206JR-070RL", Manufacturer="Yageo",
        Description="single-point input/output ground link, remove to float the adapter ground")
    for ch, raw, rail, n in (("+", "+15V_DC", "+15VA", 1), ("-", "-15V_DC", "-15VA", 2)):
        c_in = (raw, "AGND") if ch == "+" else ("AGND", raw)
        c_out = (rail, "AGND") if ch == "+" else ("AGND", rail)
        b.C(f"C{10 + n}", "10uF 25V", c_in[0], c_in[1], B, fp=FP_C1206, MPN="CL31B106KAHNNNE", Manufacturer="Samsung")
        b.add(f"L{n}", "Device:L", "BLM21PG221SN1", FP_FB, {1: {"1": raw, "2": rail}}, B, MPN="BLM21PG221SN1D", Manufacturer="Murata",
              Description="ferrite, 2 A")
        b.CP(f"C{20 + n}", "220uF 25V", c_out[0], c_out[1], B, fp=FP_CP8, MPN="EEE-FK1E221P", Manufacturer="Panasonic")
        b.C(f"C{30 + n}", "100nF", c_out[0], c_out[1], B, MPN="CL10B104KB8NNNC", Manufacturer="Samsung")
    B = "+5VAUX"
    b.add("PS2", "Converter_DCDC:R-78E5.0-0.5", "R-78HB5.0-0.5", FP_R78E, {1: {"1": "VIN_PROT", "2": "PGND", "3": "+5VAUX"}}, B,
          MPN="R-78HB5.0-0.5", Manufacturer="RECOM", Description="9-72 V in: relay rail runs from the adapter, not from +15VA")
    b.C("C41", "4.7uF 50V", "VIN_PROT", "PGND", B, fp=FP_C1210, MPN="GRM32ER71H475KA88L", Manufacturer="Murata")
    b.C("C42", "22uF 10V", "+5VAUX", "AGND", B, fp=FP_C1206, MPN="CL31A226KAHNNNE", Manufacturer="Samsung")
    B = "Distribution"
    names = ["io-board", "circuit-board", "tank-board", "spare"]
    for i, nm in enumerate(names):
        b.VH(f"P{2 + i}", f"PWR {nm}", ["+15VA", "AGND", "-15VA", "+5VAUX"], B)
    b.CONN("TP1", "test points", FP_XH.format(n=4), ["+15VA", "AGND", "-15VA", "+5VAUX"], B, MPN="B4B-XH-A(LF)(SN)", Manufacturer="JST",
           Description="meter / bench header")
    # mechanics: 4 x M3
    for i, (x, y) in enumerate(((4, 4), (116, 4), (4, 58), (116, 58))):
        b.HOLE(f"H{i + 1}", x, y)
    # connectors on the edges
    b.fixed["P1"] = (8.0, 20.0, 90, "F")
    for i in range(4):
        b.fixed[f"P{2 + i}"] = (20.0 + i * 22.0, 55.0, 0, "F")
    b.fixed["TP1"] = (100.0, 44.0, 0, "F")
    for n in ("VIN_PROT", "PGND", "+15VA", "-15VA"):
        b.PWRFLAG(n)
    b.passes = 30
    return b
