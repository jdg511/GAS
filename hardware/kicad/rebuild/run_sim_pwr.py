#!/usr/bin/env python3
"""Run the power-backplane ripple-filter AC testbench through ngspice.dll and
measure rail ripple attenuation at the DC-DC's 350 kHz switching frequency."""
import ctypes, os, sys

KICAD_BIN = r"C:\Program Files\KiCad\10.0\bin"
HERE = os.path.dirname(os.path.abspath(__file__))
os.add_dll_directory(KICAD_BIN)
ng = ctypes.CDLL(os.path.join(KICAD_BIN, "ngspice.dll"))

log = []
CB1 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
CB2 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool,
                       ctypes.c_int, ctypes.c_void_p)
send = CB1(lambda m, i, u: (log.append(m.decode(errors="replace")), 0)[1])
stat = CB1(lambda m, i, u: 0)
ex = CB2(lambda a, b, c, d, e: 0)
ng.ngSpice_Init(send, stat, ex, None, None, None, None)

def cmd(s):
    ng.ngSpice_Command(s.encode())

cmd("source " + os.path.join(HERE, "pwr-sim.cir"))
cmd("run")
cmd("meas ac atten_350k_pos find vdb(+15va) at=350k")
cmd("meas ac atten_350k_neg find vdb(-15va) at=350k")
cmd("meas ac atten_1k_pos find vdb(+15va) at=1k")

err = [l for l in log if "rror" in l and "No such" not in l]
for l in log:
    if "atten" in l and "=" in l:
        print(l.replace("stdout ", "").strip())
if err:
    print("ERRORS:")
    print("\n".join(err[:8]))
else:
    print("AC sim ran clean.")
