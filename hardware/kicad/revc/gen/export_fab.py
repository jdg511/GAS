"""usage: export_fab.py <board-name>  -> revc/fab/<board>/ gerbers zip, drill, centroid, BOM, schematic PDF, assembly PDF, renders."""
import os, sys, subprocess, shutil, zipfile, csv
HERE = os.path.dirname(os.path.abspath(__file__))
CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
name = sys.argv[1]
src = os.path.abspath(os.path.join(HERE, "..", name))
out = os.path.abspath(os.path.join(HERE, "..", "fab", name))
g = os.path.join(out, "gerbers")
shutil.rmtree(out, ignore_errors=True)
os.makedirs(g)
pcb = os.path.join(src, name + ".kicad_pcb")
sch = os.path.join(src, name + ".kicad_sch")
def run(*a):
    r = subprocess.run([CLI, *a], capture_output=True, text=True)
    print(" ".join(a[:3]), "->", (r.stdout.strip().splitlines() or [""])[-1], r.stderr.strip()[-200:] if r.returncode else "")
run("pcb", "export", "gerbers", "--output", g + "\\", "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
    "--subtract-soldermask", "--no-protel-ext", pcb)
run("pcb", "export", "drill", "--output", g + "\\", "--format", "excellon", "--excellon-units", "mm", "--excellon-zeros-format", "decimal",
    "--excellon-separate-th", "--generate-map", "--map-format", "pdf", "--drill-origin", "absolute", pcb)
tag = f"{name}-RevC"
zp = os.path.join(out, f"{tag}-gerbers.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for f in os.listdir(g):
        z.write(os.path.join(g, f), f)
run("pcb", "export", "pos", "--output", os.path.join(out, f"{tag}-centroid.csv"), "--format", "csv", "--units", "mm", "--side", "both",
    "--exclude-dnp", pcb)
run("pcb", "export", "pdf", "--output", os.path.join(out, f"{tag}-assembly-top.pdf"), "--layers", "F.Fab,F.Silkscreen,Edge.Cuts", "--mode-single", pcb)
run("sch", "export", "pdf", "--output", os.path.join(out, f"{tag}-schematic.pdf"), sch)
raw = os.path.join(out, "bom-raw.csv")
run("sch", "export", "bom", "--output", raw, "--fields", "Reference,Value,Footprint,${QUANTITY},MPN,Manufacturer,Description,${DNP}",
    "--labels", "Designator,Value,Footprint,Qty,MPN,Manufacturer,Description,DNP", "--group-by", "Value,Footprint,MPN,${DNP}",
    "--exclude-dnp" if False else "--ref-range-delimiter", "", sch)
rows = list(csv.DictReader(open(raw, encoding="utf8")))
with open(os.path.join(out, f"{tag}-BOM.csv"), "w", newline="", encoding="utf8") as f:
    w = csv.writer(f)
    w.writerow(["Item", "Designator", "Qty", "Value", "Package", "MPN", "Manufacturer", "Description", "DNP"])
    i = 0
    for r in rows:
        if r["Designator"].startswith("#") or r["Footprint"].startswith("MountingHole"):
            continue
        i += 1
        pkg = r["Footprint"].split(":")[-1]
        w.writerow([i, r["Designator"], r["Qty"], r["Value"], pkg, r["MPN"], r["Manufacturer"], r["Description"], "DNP" if r["DNP"] else ""])
os.remove(raw)
run("pcb", "render", "--output", os.path.join(out, f"{tag}-top.png"), "--side", "top", "--width", "1800", "--height", "1800", "--quality", "high", pcb)
shutil.copy(os.path.join(src, name + "-drc.rpt"), os.path.join(out, f"{tag}-DRC.rpt"))
shutil.copy(os.path.join(src, name + "-erc.rpt"), os.path.join(out, f"{tag}-ERC.rpt"))
print("done", out)
