"""GAS Rev C io-board (behind the jack deck; jacks moved to jack-board 2026-09-17).

jack-board buffered HOT/COLD -> differential receiver -> [INST: +12 dB] -> Mono > Stereo relay -> dry tap
2026-09-17: INST mode (jack-board TS sense) = +12 dB after the receiver and -12 dB before the output driver
(guitar in to amp out = unity); DRV135 cross-coupled balanced drivers (a TS plug on an output is safe in either
mode); footswitch trails bypass K7 mutes WET_SEND (tails and feedback ring out).

Balanced in -> Mono > Stereo relay -> dry tap
wet: Vol (+/-18 dB pot stage) -> [pull: 6GY8 section 1 emulation] -> WET_SEND (to tank board)
WET (from circuit board) + dry -> Wet/Dry pot (linear crossfade, buffered wiper)
-> Output (+/-18 dB pot stage) -> [Vol pulled: 6GY8 section 2 emulation] -> [Output pulled: tape] -> balanced out.

6GY8 section emulation (no tubes, no high voltage): MMBF5457 JFET common source with an unbypassed 2.2k source
resistor (the triode's plate feedback, 2.2k), drain current servo (Iq = 56 uA, so the curve is set by the JFET's beta,
not its Vp/Idss spread), 22 nF coupling cap + 68k grid stopper + BAT54 "grid conduction" diode referenced to the
servo-held gate bias + 1 M grid leak (blocking distortion, tau 22 ms). 0 dBFS = 0.137 V at the pad.
Fitted in ngspice against a port of the plugin's TriodeStage (dynamic, 1 kHz sine, revc/sim/fit.py): level within
0.7 dB from -18 to +18 dBFS, H2 within 2 dB and H3 within 4 dB from 0 to +12 dBFS; insensitive to Vp, beta +/-60 %
moves the level about 1.2 dB (the trim) and the curve 1 to 2 dB. One level trim per stage.
"""
from core import *
from common import *

W, H = 136.0, 180.0


def tube_stage(b, tag, ch, n, src, out, Usv, u_servo, u_mk, block):
    """src: inverted pot-stage output at 4.36 Vpk/FS. out: non-inverted, unity-clean tube output."""
    p = f"{tag}_{ch}"
    b.R(f"R{n}01", "30.9k", src, f"{p}_PAD", block, Description="pad 1/31.9: 4.36 Vpk -> 0.137 Vpk per full scale at the grid")
    b.R(f"R{n}02", "1.00k", f"{p}_PAD", "AGND", block)
    b.C(f"C{n}01", "22nF C0G", f"{p}_PAD", f"{p}_CC", block, fp=FP_C1206, MPN="GRM31C5C1H223JA01L", Manufacturer="Murata",
        Description="grid coupling cap (6GY8 model Cc 22 nF)")
    b.R(f"R{n}03", "68k", f"{p}_CC", f"{p}_G", block, Description="grid stopper")
    b.R(f"R{n}04", "1M", f"{p}_G", f"{p}_BIAS", block, Description="grid leak to the servo-held bias")
    b.SCHOTTKY_SOT23(f"D{n}01", "BAT54", f"{p}_G", f"{p}_BIAS", block, MPN="BAT54-7-F", Manufacturer="Diodes Incorporated",
                     Description="grid conduction: clamps the gate just above its bias and charges Cc (blocking)")
    b.C(f"C{n}02", "10pF C0G", f"{p}_G", "AGND", block, MPN="CL10C100JB8NNNC", Manufacturer="Samsung",
        Description="RF stopper at the gate (Miller of a real triode is bigger)")
    b.NJFET(f"Q{n}01", "MMBF5457", f"{p}_D", f"{p}_G", f"{p}_S", block)
    b.R(f"R{n}05", "2.2k", f"{p}_S", "AGND", block, Description="unbypassed source R: plate feedback of the triode")
    b.R(f"R{n}06", "47k", "+15VA", f"{p}_D", block, Description="drain load (plate resistor)")
    b.R(f"R{n}07", "470k", f"{p}_S", f"{p}_SV_N", block)
    b.C(f"C{n}03", "1uF", f"{p}_SV_N", f"{p}_BIAS", block, fp=FP_C0805, MPN="CL21B105KBFNNNE", Manufacturer="Samsung",
        Description="servo integrator, 0.47 s: holds Id at 56 uA (source at 123 mV)")
    # output
    film1u(b, f"C{n}04", f"{p}_D", f"{p}_OC", block)
    b.R(f"R{n}08", "1M", f"{p}_OC", "AGND", block)
    b.R(f"R{n}09", "10k", f"{p}_MK_N", "AGND", block)
    b.R(f"R{n}10", "18k", f"{p}_MK_N", f"{p}_MK_T", block)
    b.TRIM(f"RV{n}01", "20k", f"{p}_MK_T", out, out, block, MPN="3314J-1-203E", Manufacturer="Bourns",
           Description="tube level: pulled = pushed level at -12 dBFS (make-up x2.8 .. x4.8, nominal x3.6)")
    b.C(f"C{n}05", "22pF", f"{p}_MK_N", out, block, MPN="CL10C220JB8NNNC", Manufacturer="Samsung")
    return {u_servo: ("TUBE_REF", f"{p}_SV_N", f"{p}_BIAS"), u_mk: (f"{p}_OC", f"{p}_MK_N", out)}


def build():
    b = Board("io-board", "GAS Rev C - io-board (receivers + INST gain, Vol + tube 1, Wet/Dry, Output + tube 2 + tape, balanced out)",
              ["Jacks on jack-board (P6 audio, P7 mode); INST = +12 dB in / -12 dB out; footswitch trails = K7",
               "Vol pull (CTL_TUBE) = K2 + K3: 6GY8 section emulation after Vol and after Output",
               "Output pull (CTL_TAPE) = K4 tape stage; Source toggle Mono > Stereo = K1",
               "No tubes and no high voltage: JFET triode emulation (see definition doc)"])
    b.outline = (W, H)
    b.power_nets = {"AGND", "+15VA", "-15VA", "+5VAUX", "+9VC"}
    cx = W / 2
    B = "Jacks and connectors"
    b.XH("P6", "AUDIO (from jack-board P2)", ["IN_L_HOT", "IN_L_COLD", "AGND", "IN_R_HOT", "IN_R_COLD", "AGND",
                                              "OUT_L_HOT", "OUT_L_COLD", "AGND", "OUT_R_HOT", "OUT_R_COLD", "AGND"], B)
    b.XH("P7", "MODE (from jack-board P3)", ["CTL_INST_L", "CTL_INST_R", "CTL_BYP", "AGND"], B)
    power_in(b, "P1", B)
    b.XH("P2", "WET-SEND (to tank board)", ["WET_SEND_L", "AGND", "WET_SEND_R"], B)
    b.XH("P3", "WET (from circuit board)", ["WET_L", "AGND", "WET_R"], B)
    b.XH("P4", "CTL-A: Vol dual 10k lin push-pull, Output dual 10k lin push-pull",
         ["VOL_L_HI", "VOL_L_W", "VOL_L_LO", "VOL_R_HI", "VOL_R_W", "VOL_R_LO",
          "OUT_L_HI", "OUT_L_W", "OUT_L_LO", "OUT_R_HI", "OUT_R_W", "OUT_R_LO"], B)
    b.XH("P5", "CTL-B: Wet/Dry dual 10k lin (control deck P3)",
         ["L_PROG", "WD_L_W", "WET_L", "R_PROG", "WD_R_W", "WET_R"], B,
         Description="Wet/Dry pot: HI (pin 3 / 6, CW) = wet, LO = dry tap")
    b.XH("P8", "CTL-D: switch lines (control deck P5)", ["CTL_MONO", "CTL_TUBE", "CTL_TAPE", "+5VAUX", "AGND"], B,
         Description="1 Source toggle Mono throw, 2 Tube toggle, 3 Tape toggle, 4 +5VAUX to the switch commons")
    for i, (x, y) in enumerate(((4, 34), (W - 4, 34), (4, H - 4), (W - 4, H - 4))):
        b.HOLE(f"H{i + 1}", x, y)

    B = "Balanced receivers, INST gain, Mono > Stereo, dry"
    for ch, k in (("L", 1), ("R", 3)):
        b.R(f"R{k}", "100R", f"IN_{ch}_HOT", f"INB_{ch}_P", B)
        b.R(f"R{k + 1}", "100R", f"IN_{ch}_COLD", f"INB_{ch}_N", B)
    for ch, k in (("L", 11), ("R", 15)):
        b.R(f"R{k}", "10k 0.1%", f"INB_{ch}_N", f"RX_{ch}_M", B, MPN="ERA-3AEB103V", Manufacturer="Panasonic")
        b.R(f"R{k + 1}", "10k 0.1%", f"{ch}_RX", f"RX_{ch}_M", B, MPN="ERA-3AEB103V", Manufacturer="Panasonic")
        b.R(f"R{k + 2}", "10k 0.1%", f"INB_{ch}_P", f"RX_{ch}_P", B, MPN="ERA-3AEB103V", Manufacturer="Panasonic")
        b.R(f"R{k + 3}", "10k 0.1%", f"RX_{ch}_P", "AGND", B, MPN="ERA-3AEB103V", Manufacturer="Panasonic")
    for ch, k, K, ctl in (("L", 10, "K5", "CTL_INST_L"), ("R", 12, "K6", "CTL_INST_R_K")):
        b.R(f"R{k}1", "30.1k", f"GN_{ch}", f"{ch}_RXG", B, Description="INST: x4.01 (+12.06 dB)")
        b.C(f"C{k}1", "22pF", f"GN_{ch}", f"{ch}_RXG", B, MPN="CL10C220JB8NNNC", Manufacturer="Samsung")
        b.R(f"R{k}2", "10k", f"GN_{ch}", f"GRG_{ch}", B)
        b.R(f"R{k}3", "10k", f"OFIN_{ch}", f"PADN_{ch}", B, Description="LINE: x0.5 (DRV135 x2 = unity balanced out)")
        b.R(f"R{k}4", "10k", f"PADN_{ch}", "AGND", B)
        b.R(f"R{k}5", "1.65k", f"PADN_{ch}", f"PSH_{ch}", B, Description="INST: x0.1241 (-12.07 dB more)")
        b.RELAY(K, ctl, f"GRG_{ch}", None, "AGND", f"PSH_{ch}", None, "AGND", B,
                Description=f"INST {ch}: input +12 dB and output -12 dB")
        b.R(f"R{k}6", "10k", ctl, "AGND", B)
    b.OPA4("U11", {1: ("L_RX", "GN_L", "L_RXG"), 2: ("R_RX", "GN_R", "R_RXG"),
                   3: ("PADN_L", "DRVIN_L", "DRVIN_L"), 4: ("PADN_R", "DRVIN_R", "DRVIN_R")}, B, value="OPA1644AIDR")
    dec(b, "C111", "+15VA", B); dec(b, "C112", "-15VA", B)
    b.RELAY("K1", "CTL_MONO", "R_SRC", "R_RXG", "L_RXG", "CTL_INST_R_K", "CTL_INST_R", "CTL_INST_L", B,
            Description="Source toggle Mono > Stereo: right program = left input, right INST mode = left INST mode")
    b.R("R9", "10k", "CTL_INST_R", "AGND", B)
    b.R("R19", "100k", "R_SRC", "AGND", B)
    b.R("R20", "10k", "CTL_MONO", "AGND", B)
    b.OPA4("U1", {1: ("RX_L_P", "RX_L_M", "L_RX"), 2: ("RX_R_P", "RX_R_M", "R_RX"),
                  3: ("L_RXG", "L_PROG", "L_PROG"), 4: ("R_SRC", "R_PROG", "R_PROG")}, B, value="OPA1644AIDR")
    dec(b, "C91", "+15VA", B); dec(b, "C92", "-15VA", B)
    bulk(b, "C93", "+15VA", B); bulk(b, "C94", "-15VA", B)

    B = "Tube reference and +9VC / VBIAS"
    b.R("R95", "100k", "+15VA", "TUBE_REF", B)
    b.R("R96", "825R", "TUBE_REF", "AGND", B, Description="123 mV source set point for all four JFET servos (Iq = 56 uA)")
    b.C("C95", "10uF", "TUBE_REF", "AGND", B, fp=FP_C0805, MPN="CL21A106KAYNNNE", Manufacturer="Samsung")
    tl_vbias(b, "8", B, "U8")
    b.OPA2("U8", {1: ("VB_RAW", "VBIAS", "VBIAS")}, B, value="TL072HIDR", vp="+9VC", vn="AGND")
    dec(b, "C85", "+9VC", B)

    # ---------------------------------------------------------------- Vol and tube 1
    B = "Vol (+/-18 dB) and clean inverters"
    uv = {}
    for ch, n, unit in (("L", 2, 1), ("R", 3, 2)):
        uv[unit] = pot_stage(b, f"{n}0", f"{ch}_PROG", f"VOL_{ch}_HI", f"VOL_{ch}_W", f"VOL_{ch}_LO", f"VOL_OUT_{ch}", None, None, B)
        b.R(f"R{n}11", "20k", f"VOL_OUT_{ch}", f"VCL_N_{ch}", B)
        b.R(f"R{n}12", "20k", f"VCL_N_{ch}", f"VCLEAN_{ch}", B)
        uv[unit + 2] = ("AGND", f"VCL_N_{ch}", f"VCLEAN_{ch}")
    b.OPA4("U2", uv, B)
    dec(b, "C21", "+15VA", B); dec(b, "C22", "-15VA", B)

    B = "Tube 1: 6GY8 section emulation after Vol"
    ut = {}
    ut.update(tube_stage(b, "TA", "L", 40, "VOL_OUT_L", "TA_OUT_L", "U3", 1, 2, B))
    ut.update(tube_stage(b, "TA", "R", 41, "VOL_OUT_R", "TA_OUT_R", "U3", 3, 4, B))
    b.OPA4("U3", ut, B)
    dec(b, "C31", "+15VA", B); dec(b, "C32", "-15VA", B)
    B = "Wet send select"
    b.RELAY("K2", "CTL_TUBE", "WSEND_RAW_L", "VCLEAN_L", "TA_OUT_L", "WSEND_RAW_R", "VCLEAN_R", "TA_OUT_R", B, Description="Vol pull: tube after Vol")
    b.RELAY("K7", "CTL_BYP", "WSEND_SW_L", "WSEND_RAW_L", "AGND", "WSEND_SW_R", "WSEND_RAW_R", "AGND", B,
            Description="footswitch bypass with trails: tank send muted, tails + feedback ring out")
    b.R("R59", "10k", "CTL_BYP", "AGND", B)
    b.R("R51", "100R", "WSEND_SW_L", "WET_SEND_L", B)
    b.R("R52", "100R", "WSEND_SW_R", "WET_SEND_R", B)
    b.R("R53", "10k", "CTL_TUBE", "AGND", B)

    # ---------------------------------------------------------------- Wet/Dry and Output
    B = "Wet/Dry buffers and Output (+/-18 dB)"
    b.R("R54", "1M", "WD_L_W", "AGND", B)
    b.R("R55", "1M", "WD_R_W", "AGND", B)
    b.R("R56", "100k", "WET_L", "AGND", B)
    b.R("R57", "100k", "WET_R", "AGND", B)
    uo = {1: ("WD_L_W", "BLEND_L", "BLEND_L"), 2: ("WD_R_W", "BLEND_R", "BLEND_R")}
    uo[3] = pot_stage(b, "60", "BLEND_L", "OUT_L_HI", "OUT_L_W", "OUT_L_LO", "OUT_POT_L", None, None, B)
    uo[4] = pot_stage(b, "61", "BLEND_R", "OUT_R_HI", "OUT_R_W", "OUT_R_LO", "OUT_POT_R", None, None, B)
    b.OPA4("U4", uo, B)
    dec(b, "C41", "+15VA", B); dec(b, "C42", "-15VA", B)

    B = "Tube 2: 6GY8 section emulation after Output"
    ut = {}
    ut.update(tube_stage(b, "TB", "L", 70, "OUT_POT_L", "TB_OUT_L", "U6", 1, 2, B))
    ut.update(tube_stage(b, "TB", "R", 71, "OUT_POT_R", "TB_OUT_R", "U6", 3, 4, B))
    b.OPA4("U6", ut, B)
    dec(b, "C61", "+15VA", B); dec(b, "C62", "-15VA", B)

    B = "Output clean inverters, tube select, tape make-ups"
    for ch, n in (("L", 62), ("R", 63)):
        b.R(f"R{n}1", "20k", f"OUT_POT_{ch}", f"OCL_N_{ch}", B)
        b.R(f"R{n}2", "20k", f"OCL_N_{ch}", f"OCLEAN_{ch}", B)
        b.R(f"R{n}3", "47k", f"OTS_{ch}", f"TP_PAD_{ch}", B)
        b.R(f"R{n}4", "1.1k", f"TP_PAD_{ch}", "AGND", B, Description="tape pad 0.02287: 4.36 Vpk -> 0.1 Vpk")
        b.R(f"R{n}5", "10k", f"TPM_N_{ch}", "AGND", B)
        b.R(f"R{n}6", "2.55k", f"TPM_N_{ch}", f"TAPE_OUT_{ch}", B, Description="x1.255: 0.02287 x 9.2 x 4.53 x 0.835 x 1.255 = 1")
    b.OPA4("U5", {1: ("AGND", "OCL_N_L", "OCLEAN_L"), 2: ("AGND", "OCL_N_R", "OCLEAN_R"),
                  3: ("TAPE_DIV_L", "TPM_N_L", "TAPE_OUT_L"), 4: ("TAPE_DIV_R", "TPM_N_R", "TAPE_OUT_R")}, B)
    dec(b, "C51", "+15VA", B); dec(b, "C52", "-15VA", B)
    b.RELAY("K3", "CTL_TUBE", "OTS_L", "OCLEAN_L", "TB_OUT_L", "OTS_R", "OCLEAN_R", "TB_OUT_R", B, Description="Vol pull: tube after Output")

    B = "Tape (Output pull): record EQ, MMBT3904 pair, repro EQ, +9VC"
    ua = tape_stage(b, "L", 80, "TP_PAD_L", "TAPE_DIV_L", "U7", 1, B)
    ub = tape_stage(b, "R", 81, "TP_PAD_R", "TAPE_DIV_R", "U7", 2, B)
    b.OPA2("U7", {1: ua, 2: ub}, B, value="TL072HIDR", vp="+9VC", vn="AGND")
    dec(b, "C71", "+9VC", B)
    b.RELAY("K4", "CTL_TAPE", "OFIN_L", "OTS_L", "TAPE_OUT_L", "OFIN_R", "OTS_R", "TAPE_OUT_R", B, Description="Output pull: tape")
    b.R("R58", "10k", "CTL_TAPE", "AGND", B)

    B = "Balanced line drivers (DRV135, cross-coupled: TS plug safe)"
    for ch, U, n in (("L", "U9", 90), ("R", "U10", 92)):
        b.add(U, "GAS_Parts:DRV135", "DRV135UA", FP_SOIC8,
              {1: {"4": f"DRVIN_{ch}", "3": "AGND", "6": "+15VA", "5": "-15VA",
                   "8": f"OUT_{ch}_HOT", "7": f"OUT_{ch}_HOT", "1": f"OUT_{ch}_COLD", "2": f"OUT_{ch}_COLD"}}, B,
              MPN="DRV135UA", Manufacturer="Texas Instruments")
        dec(b, f"C{n}1", "+15VA", B); dec(b, f"C{n}2", "-15VA", B)
    for n in ("+15VA", "-15VA", "+5VAUX", "AGND"):
        b.PWRFLAG(n)
    b.fixed.update({"P6": (30.0, 5.0, 0, "F"), "P7": (80.0, 5.0, 0, "F"), "P1": (112.0, 172.0, 0, "F"), "P2": (96.0, 174.0, 0, "F"), "P3": (82.0, 174.0, 0, "F"),
                    "P4": (13.0, 174.0, 0, "F"), "P5": (47.0, 174.0, 0, "F"), "P8": (66.0, 174.0, 0, "F")})
    b.gap = 1.8
    b.passes = 60
    return b
