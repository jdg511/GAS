#!/usr/bin/env python3
"""Generate crossfade-feedback-wet.kicad_pcb from gen_xfade's circuit definition."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g
import gen_xfade
import gen_pcb_lib as lib

BOARD_W, BOARD_H = 100.0, 70.0

def layout():
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            pos[r] = (x0 + (i % ncols) * dx, y0 + (i // ncols) * dy, rot)

    # headers: inputs left, outputs right, controls bottom
    grid(["P301"], 8, 20, 0, 0, 1, rot=90)
    grid(["P303"], 8, 36, 0, 0, 1, rot=90)
    grid(["P306"], 8, 52, 0, 0, 1, rot=90)
    grid(["P302"], 92, 18, 0, 0, 1, rot=270)
    grid(["P304"], 92, 34, 0, 0, 1, rot=270)
    grid(["P305"], 92, 50, 0, 0, 1, rot=270)
    grid(["P307"], 32, 64, 0, 0, 1)
    # quad op amp center
    grid(["U301"], 40, 22, 0, 0, 1)
    # crossfade passives
    grid(["R301", "R309", "R311"], 22, 10, 8, 0, 3)
    grid(["R302", "R310", "R312"], 22, 34, 8, 0, 3)
    # feedback passives
    grid(["R321", "R323", "R325", "C321"], 56, 10, 8, 0, 4)
    grid(["R322", "R324", "R326", "C322"], 56, 34, 8, 0, 4)
    # wet return isolators near P304
    grid(["R341", "R342"], 76, 22, 8, 0, 2)
    # relay + driver + send isolators
    grid(["K301"], 60, 50, 0, 0, 1)
    grid(["R351", "D301"], 42, 50, 0, 6, 1)
    grid(["R331", "R332"], 82, 52, 0, 6, 1)
    # decoupling
    grid(["C391", "C393", "C392", "C394"], 22, 44, 8, 6, 2)
    return pos

def main():
    parts = lib.merged_components(gen_xfade.SECTIONS)
    lib.build_board(parts, layout(),
                    os.path.join(g.OUT_DIR, "crossfade-feedback-wet.kicad_pcb"),
                    BOARD_W, BOARD_H, "GAS Rev A - Crossfade Feedback Wet")

if __name__ == "__main__":
    main()
