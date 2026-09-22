import sys, os
sys.path[:0] = [os.path.join(os.path.dirname(__file__), ".."), os.path.join(os.path.dirname(__file__), "..", "boards")]
import pcbnew, pcb, control_deck
b = control_deck.build()
print("build ok", flush=True)
sh = pcb.outline_poly(b)
print("poly outlines", sh.OutlineCount(), "holes", sh.HoleCount(0), flush=True)
u = sh.CloneDropTriangulation(); print("clone ok", flush=True)
u.Deflate(pcbnew.FromMM(3.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05)); print("deflate ok", u.OutlineCount(), flush=True)
print("contains", u.Contains(pcbnew.VECTOR2I(pcbnew.FromMM(76), pcbnew.FromMM(20))), flush=True)
ring = sh.CloneDropTriangulation(); inner = sh.CloneDropTriangulation()
inner.Deflate(pcbnew.FromMM(1.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
ring.BooleanSubtract(inner); print("ring", ring.OutlineCount(), flush=True)
brd = pcbnew.BOARD()
one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(ring.Outline(0)); print("addoutline ok", flush=True)
for hi in range(ring.HoleCount(0)): one.AddHole(ring.Hole(0, hi))
print("holes ok", flush=True)
ka = pcbnew.ZONE(brd); ka.SetIsRuleArea(True); ka.SetOutline(one); print("setoutline ok", flush=True)
