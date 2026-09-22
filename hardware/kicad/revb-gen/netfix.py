"""Assign every pad net in a .kicad_pcb from design.py (ref + pin number). Also drops stray nets."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, dump, find, find_all, Sym
import design

SRC, DST = sys.argv[1], sys.argv[2]
t = parse(open(SRC).read())[0]
want = {}
for p in design.parts:
    for unit, pins in p["units"].items():
        for num, net in pins.items():
            want[(p["ref"], num)] = net
changed = 0
missing = []
for f in find_all(t, "footprint"):
    ref = [q[2] for q in find_all(f, "property") if q[1] == "Reference"][0]
    for pad in find_all(f, "pad"):
        num = pad[1]
        key = (ref, num)
        cur = find(pad, "net")
        if key in want and want[key] is not None:
            netname = want[key]
            if cur is None:
                pad.append([Sym("net"), netname]); changed += 1
            elif cur[1] != netname:
                cur[1] = netname; changed += 1
        else:
            # unconnected pad (NC, mounting pads): remove any net
            if (ref, num) in want:
                # deliberately unconnected pin: KiCad names these unconnected-(REF-PadN)
                nm = f"unconnected-({ref}-Pad{num})"
                if cur is None:
                    pad.append([Sym("net"), nm]); changed += 1
                elif cur[1] != nm:
                    cur[1] = nm; changed += 1
            elif cur is not None and ref.startswith("K") and num in ("MP1", "MP2"):
                pad.remove(cur); changed += 1
            elif cur is not None:
                missing.append((ref, num, cur[1]))
# DNP / exclude-from-BOM attributes
dnp_refs = {p["ref"] for p in design.parts if p["props"].get("DNP") == "yes"}
for f in find_all(t, "footprint"):
    ref = [q[2] for q in find_all(f, "property") if q[1] == "Reference"][0]
    if ref in dnp_refs:
        attr = find(f, "attr")
        for flag in ("dnp",):
            if Sym(flag) not in attr:
                attr.append(Sym(flag))
# tracks/vias: keep only those whose net exists in design
valid = set(v for v in want.values() if v)
for kind in ("segment", "via", "zone"):
    for it in find_all(t, kind):
        n = find(it, "net")
        if n and n[1] not in valid:
            print("stray", kind, n[1])
open(DST, "w").write(dump(t) + "\n")
print("pads changed:", changed, "unexpected netted pads:", missing[:10])
