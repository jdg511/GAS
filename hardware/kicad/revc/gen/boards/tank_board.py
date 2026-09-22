"""GAS Rev C tank board: feedback injection, 4 tank drivers, 4 recovery amps, Ext tank routing (Off / Series / Parallel).

Replaces the Rev A tank-driver-recovery and ext-tank-routing boards.
Plugin: wet in (after Vol/tube) + feedback return -> main tank; Parallel: same sum -> 2nd tank;
Series: main tank return x2 (+6 dB) -> 2nd tank. Ext Mix happens on the circuit board.
Driver: Rev A topology (op-amp + complementary emitter follower inside the loop, diode bias, 10R emitters, 47R to the tank).
Recovery: Rev A (2.2k across the coil, x48, 220p, 10 uF out + 100k).
"""
from core import *
from common import *


def driver(b, pre, n, inp, jack_send, jack_ret, ret_out, U, block):
    """n: 1..4 index; resistor numbering n01.. like Rev A (R101 ...)."""
    b.CP(f"C{n}01", "10uF 25V", inp, f"{pre}_DRV_IN", block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    b.R(f"R{n}01", "10k", f"{pre}_DRV_IN", "AGND", block)
    b.R(f"R{n}02", "100R", f"{pre}_DRV_OUT", f"{pre}_BIAS_MID", block)
    b.R(f"R{n}03", "2.2k", "+15VA", f"{pre}_BIAS_A", block)
    b.R(f"R{n}04", "2.2k", f"{pre}_BIAS_B", "-15VA", block)
    b.D(f"D{n}01", "1N4148W", f"{pre}_BIAS_A", f"{pre}_BIAS_MID", block, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")
    b.D(f"D{n}02", "1N4148W", f"{pre}_BIAS_MID", f"{pre}_BIAS_B", block, MPN="1N4148W-7-F", Manufacturer="Diodes Incorporated")
    b.R(f"R{n}05", "100R", f"{pre}_BIAS_A", f"{pre}_QN_B", block)
    b.R(f"R{n}06", "100R", f"{pre}_BIAS_B", f"{pre}_QP_B", block)
    # BCP56 NPN / BCP53 PNP, SOT-223: symbol 1 B, 2 C, 3 E, 4 C(tab) -> pads 1 B, 2 C, 3 E
    b.add(f"Q{n}01", "GAS_Parts:BCP56", "BCP56-16", FP_SOT223, {1: {"1": f"{pre}_QN_B", "2": "+15VA", "3": f"{pre}_QN_E"}},
          block, MPN="BCP56-16T1G", Manufacturer="onsemi", Description="replaces BD139-16 (TO-126)")
    b.add(f"Q{n}02", "GAS_Parts:BCP53", "BCP53-16", FP_SOT223, {1: {"1": f"{pre}_QP_B", "2": "-15VA", "3": f"{pre}_QP_E"}},
          block, MPN="BCP53-16T1G", Manufacturer="onsemi", Description="replaces BD140-16 (TO-126)")
    b.R(f"R{n}07", "10R 1W", f"{pre}_QN_E", f"{pre}_TANK", block, fp="Resistor_SMD:R_2512_6332Metric", MPN="RC2512FK-0710RL", Manufacturer="Yageo")
    b.R(f"R{n}08", "10R 1W", f"{pre}_QP_E", f"{pre}_TANK", block, fp="Resistor_SMD:R_2512_6332Metric", MPN="RC2512FK-0710RL", Manufacturer="Yageo")
    b.R(f"R{n}09", "1k", f"{pre}_TANK", f"{pre}_DRV_FB", block)
    b.R(f"R{n}10", "47R", f"{pre}_TANK", f"{pre}_SEND", block, fp=FP_R1206, MPN="RC1206FR-0747RL", Manufacturer="Yageo")
    b.add(jack_send[0], "Connector:Conn_Coaxial", jack_send[1], FP_RCA, {1: {"1": f"{pre}_SEND", "2": "AGND"}}, block,
          MPN="RCJ-041", Manufacturer="Same Sky")
    # recovery
    b.add(jack_ret[0], "Connector:Conn_Coaxial", jack_ret[1], FP_RCA, {1: {"1": f"{pre}_COIL", "2": "AGND"}}, block,
          MPN="RCJ-041", Manufacturer="Same Sky")
    b.CP(f"C{n}02", "10uF 25V", f"{pre}_COIL", f"{pre}_REC_IN", block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    b.R(f"R{n}12", "2.2k", f"{pre}_COIL", "AGND", block, Description="coil damping, tune by ear")
    b.R(f"R{n}11", "100k", f"{pre}_REC_IN", "AGND", block)
    b.R(f"R{n}13", "1k", f"{pre}_REC_FB", "AGND", block)
    b.R(f"R{n}14", "47k", f"{pre}_REC_OUT", f"{pre}_REC_FB", block, Description="recovery gain x48")
    b.C(f"C{n}03", "220pF C0G", f"{pre}_REC_OUT", f"{pre}_REC_FB", block, MPN="CL10C221JB8NNNC", Manufacturer="Samsung")
    b.CP(f"C{n}04", "10uF 25V", f"{pre}_REC_OUT", ret_out, block, MPN="UWT1E100MCL1GB", Manufacturer="Nichicon")
    b.R(f"R{n}15", "100k", ret_out, "AGND", block)
    b.OPA2(U, {1: (f"{pre}_DRV_IN", f"{pre}_DRV_FB", f"{pre}_DRV_OUT"), 2: (f"{pre}_REC_IN", f"{pre}_REC_FB", f"{pre}_REC_OUT")}, block,
           value="OPA1656IDR")
    dec(b, f"C{n}05", "+15VA", block); dec(b, f"C{n}06", "-15VA", block)
    bulk(b, f"C{n}07", "+15VA", block); bulk(b, f"C{n}08", "-15VA", block)


def build():
    b = Board("tank-board", "GAS Rev C - Tank board (feedback injection, 4 tank drivers + recovery, Ext tank routing)",
              ["Rev C: replaces Rev A tank-driver-recovery and ext-tank-routing",
               "Main tanks 4AB1C1B (8 R input), 2nd tanks 9EB2C1B L / 9EB3C1B R (600 R input), all RCA",
               "Ext tanks toggle: A = engage (K2 sends, K3 returns), B = Parallel (K1), Series adds +6 dB (x2)",
               "Feedback return is summed with the wet send BEFORE the main tank, as the plugin"])
    b.outline = (120.0, 150.0)
    b.power_nets = {"AGND", "+15VA", "-15VA", "+5VAUX"}
    B = "Connectors"
    b.XH("P1", "WET-SEND (from io-board)", ["WET_SEND_L", "AGND", "WET_SEND_R"], B)
    b.XH("P2", "FB-RET (from circuit board)", ["FB_RET_L", "AGND", "FB_RET_R"], B)
    b.XH("P3", "TANK-RET (to circuit board)", ["PRI_RET_L", "AGND", "PRI_RET_R", "SEC_RET_L", "AGND", "SEC_RET_R"], B)
    power_in(b, "P4", B)
    b.XH("P5", "CTL (Ext tanks toggle)", ["CTL_EXT_A", "CTL_EXT_B", "+5VAUX", "AGND"], B,
         Description="S2 up = Series (A), centre = Off, down = Parallel (A + B)")
    for i, (x, y) in enumerate(((4, 4), (116, 4), (4, 132), (116, 132))):
        b.HOLE(f"H{i + 1}", x, y)

    B = "Send sum and series gain"
    for ch, k in (("L", 1), ("R", 5)):
        b.R(f"R{50 + k}", "20k", f"WET_SEND_{ch}", f"SUM_N_{ch}", B)
        b.R(f"R{51 + k}", "20k", f"FB_RET_{ch}", f"SUM_N_{ch}", B)
        b.R(f"R{52 + k}", "20k", f"SUM_N_{ch}", f"SUM_{ch}", B, Description="-(wet + feedback), unity")
        b.C(f"C{50 + k}", "22pF", f"SUM_N_{ch}", f"SUM_{ch}", B, MPN="CL10C220JB8NNNC", Manufacturer="Samsung")
        b.R(f"R{60 + k}", "10k", f"SER_FB_{ch}", "AGND", B)
        b.R(f"R{61 + k}", "10k", f"SER_{ch}", f"SER_FB_{ch}", B, Description="Series inter-tank gain x2 (+6 dB), as the plugin")
        b.R(f"R{70 + k}", "100k", f"WET_SEND_{ch}", "AGND", B)
        b.R(f"R{71 + k}", "100k", f"FB_RET_{ch}", "AGND", B)
    b.OPA4("U5", {1: ("AGND", "SUM_N_L", "SUM_L"), 2: ("PRI_RET_L", "SER_FB_L", "SER_L"),
                  3: ("AGND", "SUM_N_R", "SUM_R"), 4: ("PRI_RET_R", "SER_FB_R", "SER_R")}, B)
    dec(b, "C58", "+15VA", B); dec(b, "C59", "-15VA", B)

    driver(b, "PL", 1, "SUM_L", ("J1", "Main L send"), ("J2", "Main L return"), "PRI_RET_L", "U1", "Main tank L (4AB1C1B)")
    driver(b, "PR", 2, "SUM_R", ("J3", "Main R send"), ("J4", "Main R return"), "PRI_RET_R", "U2", "Main tank R (4AB1C1B)")
    driver(b, "SL", 3, "SEC_DRV_L", ("J5", "2nd L send"), ("J6", "2nd L return"), "SEC_REC_L", "U3", "2nd tank L (9EB2C1B)")
    driver(b, "SR", 4, "SEC_DRV_R", ("J7", "2nd R send"), ("J8", "2nd R return"), "SEC_REC_R", "U4", "2nd tank R (9EB3C1B)")

    B = "Ext tank relays (Omron G6K-2F-Y 5 V)"
    b.RELAY("K1", "CTL_EXT_B", "SEC_SRC_L", "SER_L", "SUM_L", "SEC_SRC_R", "SER_R", "SUM_R", B, Description="Parallel: 2nd tank fed from the wet+FB sum")
    b.RELAY("K2", "CTL_EXT_A", "SEC_DRV_L", "AGND", "SEC_SRC_L", "SEC_DRV_R", "AGND", "SEC_SRC_R", B, Description="engage: 2nd tank sends")
    b.RELAY("K3", "CTL_EXT_A", "SEC_RET_L", "AGND", "SEC_REC_L", "SEC_RET_R", "AGND", "SEC_REC_R", B, Description="engage: 2nd tank returns (Off = muted)")
    b.R("R81", "10k", "CTL_EXT_A", "AGND", B)
    b.R("R82", "10k", "CTL_EXT_B", "AGND", B)
    b.R("R83", "100k", "SEC_DRV_L", "AGND", B)
    b.R("R84", "100k", "SEC_DRV_R", "AGND", B)
    for n in ("+15VA", "-15VA", "+5VAUX", "AGND"):
        b.PWRFLAG(n)
    # RCA jacks on the rear edge (y = 150), connectors on the front edge
    xs = [13 + i * 13.1 for i in range(8)]
    for i, x in enumerate(xs):
        b.fixed[f"J{i + 1}"] = (x, 144.5, 270, "F")   # barrels point off the rear edge
    b.fixed.update({"P1": (14.0, 5.0, 0, "F"), "P2": (34.0, 5.0, 0, "F"), "P3": (56.0, 5.0, 0, "F"),
                    "P4": (86.0, 6.0, 0, "F"), "P5": (108.0, 12.0, 90, "F")})
    b.gap = 1.6
    b.passes = 100
    return b
