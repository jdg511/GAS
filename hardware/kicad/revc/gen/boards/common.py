"""Shared Rev C building blocks."""
from core import *

MPN_R = "Yageo RC0603FR-07 series"


def dec(b, ref, rail, block, value="100nF"):
    """Decoupling cap from rail to AGND (positive or negative rail)."""
    if rail.startswith("-"):
        b.C(ref, value, "AGND", rail, block, MPN="CL10B104KB8NNNC", Manufacturer="Samsung")
    else:
        b.C(ref, value, rail, "AGND", block, MPN="CL10B104KB8NNNC", Manufacturer="Samsung")


def bulk(b, ref, rail, block, value="10uF 25V"):
    if rail.startswith("-"):
        b.CP(ref, value, "AGND", rail, block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    else:
        b.CP(ref, value, rail, "AGND", block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")


def power_in(b, ref, block):
    b.VH(ref, "PWR (from power board)", ["+15VA", "AGND", "-15VA", "+5VAUX"], block,
         Description="1 +15VA, 2 AGND, 3 -15VA, 4 +5VAUX")


def film1u(b, ref, a, c, block, **p):
    b.C(ref, "1uF film", a, c, block, fp=FP_CFILM1U, MPN="MKS2C041001F00KSSD", Manufacturer="WIMA", **p)


def pot_stage(b, prefix, inp, hi, wiper, lo, out, U, unit, block):
    """Symmetric-in-dB inverting pot stage, +/-18 dB with a 10k linear dual gang and 1.43k end resistors.
    Gain = -(1.43k + R_lower) / (1.43k + R_upper): -18.0 dB .. 0 dB (centre) .. +18.0 dB."""
    b.R(f"R{prefix}1", "1.43k", inp, hi, block)
    b.R(f"R{prefix}2", "1.43k", lo, out, block)
    b.R(f"R{prefix}3", "1M", wiper, out, block, Description="keeps the loop closed if the pot is unplugged")
    b.C(f"C{prefix}1", "22pF", wiper, out, block, MPN="CL10C220JB8NNNC", Manufacturer="Samsung")
    return ("AGND", wiper, out)


def tl_vbias(b, prefix, block, u_ref, spare_unit=None):
    """+9VC from +15VA (L78L09) and a buffered 4.5 V VBIAS (TL072H unit A)."""
    b.add(f"U{prefix}1", "Regulator_Linear:L78L09_SOT89", "L78L09", FP_SOT89, {1: {"3": "+15VA", "2": "AGND", "1": "+9VC"}}, block,
          MPN="L78L09ACUTR", Manufacturer="STMicroelectronics")
    dec(b, f"C{prefix}1", "+15VA", block)
    b.CP(f"C{prefix}2", "10uF 25V", "+9VC", "AGND", block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    dec(b, f"C{prefix}3", "+9VC", block)
    b.R(f"R{prefix}1", "10k", "+9VC", "VB_RAW", block)
    b.R(f"R{prefix}2", "10k", "VB_RAW", "AGND", block)
    b.CP(f"C{prefix}4", "47uF 16V", "VB_RAW", "AGND", block, fp=FP_CP63, MPN="EEE-FK1C470P", Manufacturer="Panasonic")


def tape_stage(b, ch, n, inp, out_div, U, unit, block):
    """Rev B tape stage (record EQ -> MMBT3904 long-tailed pair -> repro EQ) at pedal level on +9VC.
    inp: 0.1 Vpk per full scale AC source. out_div: node after the output coupling cap + 100k bias return."""
    film1u(b, f"C{n}01", inp, f"TAPE_IN_{ch}", block)
    b.R(f"R{n}01", "100k", f"TAPE_IN_{ch}", "VBIAS", block)
    b.R(f"R{n}02", "10k", f"TAPE_FB_{ch}", "VBIAS", block)
    b.R(f"R{n}03", "4.7k", f"TAPE_FB_{ch}", f"TAPE_Z_{ch}", block)
    b.C(f"C{n}02", "6.8nF C0G", f"TAPE_Z_{ch}", "VBIAS", block, fp=FP_C0805, MPN="C0805C682J5GACTU", Manufacturer="KEMET")
    b.R(f"R{n}04", "82k", f"TAPE_REC_{ch}", f"TAPE_FB_{ch}", block)
    film1u(b, f"C{n}03", f"TAPE_REC_{ch}", f"TAPE_B1_{ch}", block)
    b.R(f"R{n}05", "47k", "+9VC", f"TAPE_B1_{ch}", block)
    b.R(f"R{n}06", "22k", f"TAPE_B1_{ch}", "AGND", block)
    b.R(f"R{n}07", "47k", "+9VC", f"TAPE_B2_{ch}", block)
    b.R(f"R{n}08", "22k", f"TAPE_B2_{ch}", "AGND", block)
    b.CP(f"C{n}04", "10uF 25V", f"TAPE_B2_{ch}", "AGND", block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    b.NPN(f"Q{n}01", f"TAPE_B1_{ch}", f"TAPE_E1_{ch}", f"TAPE_C1_{ch}", block)
    b.NPN(f"Q{n}02", f"TAPE_B2_{ch}", f"TAPE_E2_{ch}", f"TAPE_C2_{ch}", block)
    b.R(f"R{n}09", "470R", f"TAPE_E1_{ch}", f"TAPE_T_{ch}", block)
    b.R(f"R{n}10", "470R", f"TAPE_E2_{ch}", f"TAPE_T_{ch}", block)
    b.R(f"R{n}11", "2.2k", f"TAPE_T_{ch}", "AGND", block)
    b.R(f"R{n}12", "4.7k", "+9VC", f"TAPE_C1_{ch}", block)
    b.R(f"R{n}13", "4.7k", "+9VC", f"TAPE_C2_{ch}", block)
    b.R(f"R{n}14", "15k", f"TAPE_C2_{ch}", f"TAPE_REP_{ch}", block)
    b.R(f"R{n}15", "10k", f"TAPE_REP_{ch}", f"TAPE_REP2_{ch}", block)
    b.C(f"C{n}05", "3.3nF C0G", f"TAPE_REP2_{ch}", "AGND", block, fp=FP_C0805, MPN="C0805C332J5GACTU", Manufacturer="KEMET")
    film1u(b, f"C{n}06", f"TAPE_REP_{ch}", out_div, block)
    b.R(f"R{n}16", "100k", out_div, "AGND", block, Description="bias return, loads the repro EQ x0.835")
    return (f"TAPE_IN_{ch}", f"TAPE_FB_{ch}", f"TAPE_REC_{ch}")
