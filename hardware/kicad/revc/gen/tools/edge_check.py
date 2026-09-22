"""Edge check: every footprint courtyard and every board-edge feature must sit inside the board outline.

usage:  python tools\edge_check.py control-deck jack-board ...
Only for the two round 6 in decks; a rectangular board has no disc to measure against and is skipped.
Prints, per board, the worst radius reached by each footprint courtyard measured from the disc centre,
and flags anything that gets within MARGIN mm of the 76.2 mm edge (or crosses it).
"""
import sys, os, math, pcbnew

R = 76.2
MARGIN = 1.0          # required board material beyond every courtyard
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ROUND = ("control-deck", "jack-board")

for name in sys.argv[1:]:
    if name not in ROUND:
        print(f"== {name}: not a round deck, skipped")
        continue
    path = os.path.join(OUT, name, name + ".kicad_pcb")
    brd = pcbnew.LoadBoard(path)
    cx = cy = pcbnew.FromMM(R)
    rows, worst = [], 0.0
    for fp in brd.Footprints():
        far = 0.0
        for g in fp.GraphicalItems():
            if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
                bb = g.GetBoundingBox()
                for x in (bb.GetX(), bb.GetRight()):
                    for y in (bb.GetY(), bb.GetBottom()):
                        far = max(far, math.hypot(x - cx, y - cy))
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            for x in (bb.GetX(), bb.GetRight()):
                for y in (bb.GetY(), bb.GetBottom()):
                    far = max(far, math.hypot(x - cx, y - cy))
        far = pcbnew.ToMM(far)
        rows.append((far, fp.GetReference(), str(fp.GetFPID().GetLibItemName())))
        worst = max(worst, far)
    rows.sort(reverse=True)
    print(f"== {name}: {len(rows)} footprints, worst radius {worst:.2f} mm (edge {R} mm)")
    for far, ref, fpn in rows[:12]:
        flag = "  *** OUTSIDE ***" if far > R else ("  *** < MARGIN ***" if far > R - MARGIN else "")
        print(f"   {ref:<6} {far:7.2f}  {fpn[:52]}{flag}")
    bad = [r for r in rows if r[0] > R - MARGIN]
    print("   RESULT:", "FAIL" if bad else f"OK - {R - worst:.2f} mm of board beyond the outermost courtyard")
