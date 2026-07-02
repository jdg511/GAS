#!/usr/bin/env python3
"""Generate io-board.kicad_pcb from gen_io's circuit definition."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g
import gen_io
import gen_pcb_lib as lib

BOARD_W, BOARD_H = 160.0, 75.0

def layout():
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            pos[r] = (x0 + (i % ncols) * dx, y0 + (i // ncols) * dy, rot)

    # jack landings along the top: inputs left, outputs right
    grid(["J1", "J2"], 20, 8, 22, 0, 2)
    grid(["J3", "J4"], 112, 8, 22, 0, 2)
    # power left edge, signal headers along the bottom
    grid(["P1"], 8, 34, 0, 0, 1, rot=90)
    grid(["P2", "P3", "P4"], 34, 67, 20, 0, 3)
    grid(["P5"], 94, 67, 0, 0, 1)
    grid(["P6"], 128, 67, 0, 0, 1)
    # op amps
    grid(["U1"], 36, 30, 0, 0, 1)
    grid(["U2"], 70, 42, 0, 0, 1)
    grid(["U3"], 104, 28, 0, 0, 1)
    grid(["U4"], 132, 28, 0, 0, 1)
    # input boundary parts
    grid(["R1", "R2", "C1", "C2"], 16, 16, 7, 0, 4)
    grid(["R3", "R4", "C3", "C4"], 46, 16, 7, 0, 4)
    grid(["R11", "R12", "R13", "R14"], 16, 24, 7, 0, 4)
    grid(["R15", "R16", "R17", "R18"], 46, 24, 7, 0, 4)
    # fanout isolators
    grid(["R21", "R22", "R23", "R24"], 16, 42, 7, 0, 4)
    # blend buffers
    grid(["R31", "R35", "R32", "R36"], 58, 52, 7, 0, 4)
    # balanced output legs
    grid(["R43", "R44", "R49", "R50"], 92, 16, 7, 0, 4)
    grid(["R53", "R54", "R59", "R60"], 122, 16, 7, 0, 4)
    # decoupling row
    grid(["C91", "C92", "C93", "C94", "C95", "C96", "C97", "C98"], 16, 56, 7, 0, 8)
    grid(["C99", "C100"], 84, 42, 8, 0, 2)
    return pos

def main():
    parts = lib.merged_components(gen_io.SECTIONS)
    lib.build_board(parts, layout(),
                    os.path.join(g.OUT_DIR, "io-board.kicad_pcb"),
                    BOARD_W, BOARD_H, "GAS Rev A - Input Output Board")

if __name__ == "__main__":
    main()
