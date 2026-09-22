import sys, os, json
H = os.path.join(os.path.dirname(__file__), "..")
sys.path[:0] = [H, os.path.join(H, "boards")]
import importlib, pcb
mod = importlib.import_module(sys.argv[1]); gap = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
b = mod.build()
out = os.path.join(H, "..", b.name)
fu = json.load(open(os.path.join(out, "unit_uuids.json")))
un = pcb.build(b, fu, os.path.join(out, b.name + "-dbg.kicad_pcb"), gap=gap)
print("unplaced", un)
