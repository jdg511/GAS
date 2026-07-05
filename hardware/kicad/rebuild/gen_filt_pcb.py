#!/usr/bin/env python3
"""Generate filter-clipper.kicad_pcb from gen_filt's circuit definition."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_tdr as g
import gen_filt
import gen_pcb_lib as lib

BOARD_W, BOARD_H = 140.0, 90.0

def layout():
    pos = {}

    def grid(refs, x0, y0, dx, dy, ncols, rot=0):
        for i, r in enumerate(refs):
            pos[r] = (x0 + (i % ncols) * dx, y0 + (i // ncols) * dy, rot)

    # headers
    grid(["P401"], 8, 20, 0, 0, 1, rot=90)
    grid(["P404"], 8, 50, 0, 0, 1, rot=90)
    grid(["P402"], 132, 72, 0, 0, 1, rot=270)
    grid(["P403"], 22, 82, 0, 0, 1)
    grid(["P405"], 78, 82, 0, 0, 1)
    # op amps central
    grid(["U401"], 38, 36, 0, 0, 1)
    grid(["U402"], 62, 36, 0, 0, 1)
    # left channel band (top)
    grid(["C401", "R401", "R402", "C403"], 18, 10, 10, 0, 4)
    grid(["R403", "R404", "C405", "R405"], 58, 10, 8, 0, 4)
    grid(["D401", "D405", "D409", "D402", "D406", "D410"], 88, 10, 8, 7, 3)
    grid(["R406", "C406", "R407", "C407"], 58, 22, 8, 0, 4)
    grid(["R408"], 126, 10, 0, 0, 1)
    # right channel band (bottom)
    grid(["C421", "R421", "R422", "C423"], 18, 62, 10, 0, 4)
    grid(["R423", "R424", "C425", "R425"], 58, 55, 8, 0, 4)
    grid(["D403", "D407", "D411", "D404", "D408", "D412"], 88, 62, 8, 7, 3)
    grid(["R426", "C426", "R427", "C427"], 58, 69, 8, 0, 4)
    grid(["R428"], 120, 76, 0, 0, 1)
    # relays rotated (long axis horizontal), drivers to their left
    grid(["K401", "K402", "K403"], 118, 26, 0, 18, 1, rot=90)
    grid(["D421", "D422", "R432"], 104, 30, 0, 7, 1)
    # decoupling near the op amps
    grid(["C591", "C592", "C593", "C594"], 20, 38, 8, 6, 2)
    grid(["C595", "C596"], 20, 28, 8, 0, 2)
    return pos

def main():
    parts = lib.merged_components(gen_filt.SECTIONS)
    lib.build_board(parts, layout(),
                    os.path.join(g.OUT_DIR, "filter-clipper.kicad_pcb"),
                    BOARD_W, BOARD_H, "GAS Rev A - Filter Clipper")

if __name__ == "__main__":
    main()
