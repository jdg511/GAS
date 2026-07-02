#!/usr/bin/env python3
"""Generate ext-tank-routing.kicad_pcb from gen_ext's circuit definition."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g
import gen_ext
import gen_pcb_lib as lib

BOARD_W, BOARD_H = 120.0, 80.0

def layout():
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            pos[r] = (x0 + (i % ncols) * dx, y0 + (i // ncols) * dy, rot)

    # headers: signal in/fb left, tank bundles right, controls bottom
    grid(["P201"], 8, 20, 0, 0, 1, rot=90)
    grid(["P205"], 8, 36, 0, 0, 1, rot=90)
    grid(["P207"], 8, 54, 0, 0, 1, rot=90)
    grid(["P202"], 112, 14, 0, 0, 1, rot=270)
    grid(["P203"], 112, 40, 0, 0, 1, rot=270)
    grid(["P204"], 62, 72, 0, 0, 1)
    grid(["P206"], 26, 72, 0, 0, 1)
    # op amp central-left
    grid(["U201"], 36, 30, 0, 0, 1)
    # summers
    grid(["R202", "R203", "R204", "R209", "R205"], 20, 10, 8, 0, 5)
    grid(["R222", "R223", "R224", "R229", "R225"], 20, 60, 8, 0, 5)
    grid(["R201"], 64, 10, 0, 0, 1)
    grid(["R221"], 64, 60, 0, 0, 1)
    # secondary buffers
    grid(["R211", "R212", "R241", "R206"], 48, 22, 7, 0, 4)
    grid(["R231", "R232", "R251", "R226"], 48, 40, 7, 0, 4)
    # relays (rotated: long axis horizontal), flybacks beside
    grid(["K201", "K203"], 86, 16, 0, 16, 1, rot=90)
    grid(["K202", "K204"], 86, 48, 0, 16, 1, rot=90)
    grid(["D261", "D262"], 74, 34, 8, 0, 2)
    # decoupling
    grid(["C291", "C292", "C293", "C294", "C295"], 20, 38, 7, 0, 5)
    return pos

def main():
    parts = lib.merged_components(gen_ext.SECTIONS)
    lib.build_board(parts, layout(),
                    os.path.join(g.OUT_DIR, "ext-tank-routing.kicad_pcb"),
                    BOARD_W, BOARD_H, "GAS Rev A - Ext Tank Routing")

if __name__ == "__main__":
    main()
