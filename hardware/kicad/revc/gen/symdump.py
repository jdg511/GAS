import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, find, find_all
SYM = r"C:\Program Files\KiCad\10.0\share\kicad\symbols"
for arg in sys.argv[1:]:
    lib, name = arg.split(":")
    t = parse(open(os.path.join(SYM, lib + ".kicad_sym"), encoding="utf8").read())[0]
    for s in find_all(t, "symbol"):
        if s[1] == name:
            ext = find(s, "extends")
            print(arg, "extends", ext[1] if ext else None)
            for p in find_all(s, "property"):
                if p[1] in ("Footprint", "ki_fp_filters", "Description"): print("  ", p[1], p[2][:90])
            for sub in find_all(s, "symbol"):
                for pin in find_all(sub, "pin"):
                    at = find(pin, "at")
                    print("  ", sub[1], pin[1], "num", find(pin, "number")[1], "name", find(pin, "name")[1], "at", at[1:])
