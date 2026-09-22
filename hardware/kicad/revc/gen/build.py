"""usage: build.py <board_module> [stages]  stages: sch,pcb,route,pour,drc (default all)"""
import os, sys, importlib, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "boards"))
import core, gen_sch

CLI = core.KICAD + r"\bin\kicad-cli.exe"
OUTROOT = os.path.abspath(os.path.join(HERE, ".."))


def project_files(outdir, name):
    open(os.path.join(outdir, "sym-lib-table"), "w").write(
        '(sym_lib_table\n  (version 7)\n  (lib (name "GAS_Parts")(type "KiCad")(uri "${KIPRJMOD}/GAS_Parts_RevC.kicad_sym")(options "")(descr "GAS Rev C custom symbols"))\n)\n')
    open(os.path.join(outdir, "fp-lib-table"), "w").write(
        '(fp_lib_table\n  (version 7)\n  (lib (name "GAS_Parts")(type "KiCad")(uri "${KIPRJMOD}/../../GAS_Parts.pretty")(options "")(descr "GAS custom footprints"))\n)\n')
    pro = os.path.join(outdir, name + ".kicad_pro")
    if not os.path.exists(pro):
        json.dump({"meta": {"filename": name + ".kicad_pro", "version": 3}, "board": {}, "schematic": {},
                   "net_settings": {"classes": [{"name": "Default"}]}}, open(pro, "w"), indent=2)
    gen_sch.write_symbol_lib(os.path.join(outdir, "GAS_Parts_RevC.kicad_sym"))


def main():
    mod = importlib.import_module(sys.argv[1])
    stages = sys.argv[2].split(",") if len(sys.argv) > 2 else ["sch", "pcb", "route", "pour", "drc"]
    b = mod.build()
    outdir = os.path.join(OUTROOT, b.name)
    os.makedirs(outdir, exist_ok=True)
    nets, single = b.check()
    print(f"{b.name}: {len(b.parts)} parts, {len(nets)} nets")
    if single:
        print("SINGLE-PIN NETS:", single)
    project_files(outdir, b.name)
    sch = os.path.join(outdir, b.name + ".kicad_sch")
    pcbf = os.path.join(outdir, b.name + ".kicad_pcb")
    if "sch" in stages:
        fu, s2 = gen_sch.emit(b, outdir)
        json.dump(fu, open(os.path.join(outdir, "unit_uuids.json"), "w"))
        with open(os.path.join(outdir, "netlist-report.txt"), "w") as f:
            for n in sorted(nets):
                f.write(f"{n}: {' '.join(nets[n])}\n")
        r = subprocess.run([CLI, "sch", "erc", "--severity-all", "--format", "report", "--output",
                            os.path.join(outdir, b.name + "-erc.rpt"), sch], capture_output=True, text=True)
        print("ERC:", r.stdout.strip().splitlines()[-3:])
    if "pcb" in stages:
        import pcb, route
        fu = json.load(open(os.path.join(outdir, "unit_uuids.json")))
        gaps = [getattr(b, "gap", 1.0)] + [getattr(b, "gap", 1.0) + d for d in (0.15, -0.15, 0.3, -0.3)]
        if getattr(b, "no_gap_retry", False):
            gaps = gaps[:1]
        for g in gaps:
            un = pcb.build(b, fu, pcbf, gap=g)
            print("gap", round(g, 2), "unplaced blocks:", un)
            if un:
                if g == gaps[-1]:
                    raise SystemExit("placement failed: " + str(un))
                continue
            if "route" not in stages:
                break
            route.autoroute(pcbf, passes=getattr(b, "passes", 40), tries=getattr(b, "route_tries", 1))
            u = route.unrouted(pcbf)
            print("gap", round(g, 2), "unrouted:", u)
            if u == 0:
                break
        stages = [x for x in stages if x != "route"]
    if "sync" in stages:
        import pcb
        pcb.sync_values(b, pcbf)
    if "route" in stages:
        import route
        route.autoroute(pcbf, passes=getattr(b, "passes", 40))
    if "pour" in stages:
        import route
        route.pour(pcbf)
    if "drc" in stages:
        rpt = os.path.join(outdir, b.name + "-drc.rpt")
        r = subprocess.run([CLI, "pcb", "drc", "--severity-all", "--schematic-parity", "--refill-zones", "--save-board",
                            "--format", "report", "--output", rpt, pcbf], capture_output=True, text=True)
        print("DRC:", r.stdout.strip().splitlines()[-4:])
        import collections
        cnt = collections.Counter()
        for line in open(rpt, encoding="utf8"):
            if line.startswith("["):
                cnt[line.split("]")[0][1:]] += 1
        print(dict(cnt))


if __name__ == "__main__":
    main()
