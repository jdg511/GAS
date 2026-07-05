#!/usr/bin/env python3
"""Generic transient-sim verifier: run_tran.py <netlist.cir> <node1,node2,...>
Runs the netlist through KiCad's ngspice.dll and prints steady-state stats."""
import ctypes, os, sys

KICAD_BIN = r"C:\Program Files\KiCad\10.0\bin"
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

class VecInfo(ctypes.Structure):
    _fields_ = [("v_name", ctypes.c_char_p), ("v_type", ctypes.c_int),
                ("v_flags", ctypes.c_short),
                ("v_realdata", ctypes.POINTER(ctypes.c_double)),
                ("v_compdata", ctypes.c_void_p), ("v_length", ctypes.c_int)]

ng.ngGet_Vec_Info.restype = ctypes.POINTER(VecInfo)

def vec(name):
    p = ng.ngGet_Vec_Info(name.encode())
    if not p or not p.contents.v_realdata:
        return None
    v = p.contents
    return [v.v_realdata[i] for i in range(v.v_length)]

ng.ngSpice_Command(("source " + os.path.abspath(sys.argv[1])).encode())
ng.ngSpice_Command(b"run")

t = vec("time")
if t is None or len(t) < 100:
    print("SIM FAILED (timepoints: %s)" % (len(t) if t else 0))
    print("\n".join(log[-40:]))
    sys.exit(1)
print("SIM OK: %d timepoints, t_end=%.4f s" % (len(t), t[-1]))
i0 = next(i for i, x in enumerate(t) if x > t[-1] * 0.5)
for name in sys.argv[2].split(","):
    d = vec("v(%s)" % name)
    if d is None:
        print("%-18s MISSING" % name)
        continue
    w = d[i0:]
    print("%-18s min=%+.4f  max=%+.4f  pk=%.4f"
          % (name, min(w), max(w), (max(w) - min(w)) / 2))
err = [l for l in log if "rror" in l and "No such" not in l]
print("ERRORS:" if err else "No errors in ngspice log.")
if err:
    print("\n".join(err[:8]))
    sys.exit(1)
