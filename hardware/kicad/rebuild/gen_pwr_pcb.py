#!/usr/bin/env python3
"""Generate power-backplane.kicad_pcb from gen_pwr's circuit definition."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g
import gen_pwr
import gen_pcb_lib as lib

BOARD_W, BOARD_H = 120.0, 80.0

def layout():
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            pos[r] = (x0 + (i % ncols) * dx, y0 + (i // ncols) * dy, rot)

    # DC entry chain along the top
    grid(["P500"], 8, 16, 0, 0, 1, rot=90)
    grid(["D500", "F500"], 22, 16, 10, 0, 2)
    grid(["C500", "TVS500"], 40, 16, 14, 0, 2)
    grid(["C509"], 62, 34, 0, 0, 1)
    # DC-DC module
    grid(["PS500"], 86, 20, 0, 0, 1)
    grid(["C510", "C511"], 72, 40, 10, 0, 2)
    # ripple filters
    grid(["FB500", "C501", "C502", "C503"], 20, 52, 9, 0, 4)
    grid(["FB501", "C504", "C505", "C506"], 58, 52, 9, 0, 4)
    # +5VAUX
    grid(["PS501"], 16, 36, 0, 0, 1)
    grid(["C507", "C508"], 30, 36, 8, 0, 2)
    # star tie
    grid(["R500"], 96, 44, 0, 0, 1)
    # fanout headers: five VH3 along the bottom, two VH4 on the right edge
    grid(["P501", "P502", "P503", "P504", "P505"], 32, 70, 16, 0, 5)
    grid(["P506", "P601"], 108, 28, 0, 20, 1, rot=270)
    return pos

def main():
    parts = lib.merged_components(gen_pwr.SECTIONS)
    lib.build_board(parts, layout(),
                    os.path.join(g.OUT_DIR, "power-backplane.kicad_pcb"),
                    BOARD_W, BOARD_H, "GAS Rev A - Power Backplane")

if __name__ == "__main__":
    main()
