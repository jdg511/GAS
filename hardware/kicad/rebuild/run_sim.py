#!/usr/bin/env python3
"""Run the tank-driver-recovery testbench through KiCad's bundled ngspice.dll
and sanity-check the results. This is the same simulator engine the KiCad GUI
uses, so if this passes, the Inspect > Simulator flow will work too."""
import ctypes, os, sys

KICAD_BIN = r"C:\Program Files\KiCad\10.0\bin"
HERE = os.path.dirname(os.path.abspath(__file__))
CIR = os.path.join(HERE, "tdr-sim.cir")

os.add_dll_directory(KICAD_BIN)
ng = ctypes.CDLL(os.path.join(KICAD_BIN, "ngspice.dll"))

log = []
CB1 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
CB2 = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool,
                       ctypes.c_int, ctypes.c_void_p)

@CB1
def send_char(msg, ident, user):
    log.append(msg.decode(errors="replace"))
    return 0

@CB1
def send_stat(msg, ident, user):
    return 0

@CB2
def ctrl_exit(status, unload, quit_, ident, user):
    return 0

ng.ngSpice_Init(send_char, send_stat, ctrl_exit, None, None, None, None)

def cmd(s):
    ng.ngSpice_Command(s.encode())

cmd("source " + CIR)
cmd("run")

# pull result vectors through the API
ng.ngGet_Vec_Info.restype = ctypes.POINTER(ctypes.c_void_p)

class VecInfo(ctypes.Structure):
    _fields_ = [("v_name", ctypes.c_char_p), ("v_type", ctypes.c_int),
                ("v_flags", ctypes.c_short), ("v_realdata", ctypes.POINTER(ctypes.c_double)),
                ("v_compdata", ctypes.c_void_p), ("v_length", ctypes.c_int)]

ng.ngGet_Vec_Info.restype = ctypes.POINTER(VecInfo)

def vec(name):
    p = ng.ngGet_Vec_Info(name.encode())
    if not p or not p.contents.v_realdata:
        return None
    v = p.contents
    return [v.v_realdata[i] for i in range(v.v_length)]

errors = [l for l in log if "rror" in l or "singular" in l or "abort" in l]
t = vec("time")
if t is None or len(t) < 100:
    print("SIM FAILED or truncated (timepoints: %s)" % (len(t) if t else 0))
    print("---- last 60 log lines ----")
    print("\n".join(log[-60:]))
    sys.exit(1)

print("SIM OK: %d timepoints, t_end=%.4f s" % (len(t), t[-1]))
# steady-state window: last 30 ms
i0 = next(i for i, x in enumerate(t) if x > t[-1] - 0.03)

def stats(name):
    d = vec(name)
    if d is None:
        return "%-18s MISSING" % name
    w = d[i0:]
    return "%-18s min=%+.4f  max=%+.4f  pk=%.4f" % (name, min(w), max(w), (max(w) - min(w)) / 2)

for n in ["v(pri_send_l)", "v(pri_drv_l)", "v(pri_out_l)", "v(pri_rec_l_in)",
          "v(pri_ret_l)", "v(sec_send_l)", "v(sec_out_l)", "v(sec_rec_l_in)",
          "v(sec_ret_l)", "v(pri_ret_r)", "v(sec_ret_r)"]:
    print(stats(n))

if errors:
    print("\nLOG ERRORS:")
    print("\n".join(errors[:10]))
else:
    print("\nNo errors in ngspice log.")
