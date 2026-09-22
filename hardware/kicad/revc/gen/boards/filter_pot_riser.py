"""GAS Rev C filter-pot riser (2026-09-21b): the carrier board for one Bourns PTD904 4-gang filter pot.

Why it exists. The PTD904's PC pins leave the body at 90 degrees to the shaft ("side adjust"), and the Bourns
PTD90 recommended PCB layout puts the mounting surface perpendicular to the board. The pin columns sit 5.0, 7.5,
12.5 and 15.0 mm behind the mounting shoulder, which with the shoulder on the endcap counterbore floor puts the
four gangs at 8.0, 10.5, 15.5 and 18.0 mm behind the cap's outer face. The control deck is at 15.0 to 16.6 mm, so
the pin field straddles it: no board lying in the deck's plane, and no card standing on the deck, can reach all
four gangs. This riser is therefore a pot CARRIER, not a daughtercard on the deck: the pot solders flat to it,
the assembly passes through the control deck's filter-pot window and nut-mounts to the cap exactly as a bare pot
would, and a single JST XH-8 goes to the circuit board.

One design serves both filters. HPF (circuit P5) and LPF (circuit P6) take the same 8 lines in the same order,
(HI, wiper) x 4, so the riser carries generic G1..G4 nets and the cable decides which filter it is. Build two.

Wiring per gang: pad g1 (CCW end) = HI, pads g2 (wiper) and g3 (CW end) tied = W. That makes each gang a rheostat
whose resistance RISES as the knob turns clockwise, so CW lowers both corner frequencies: CW = less bass cut on the
HPF and darker on the LPF. Jason picked this direction on 2026-09-21 after the first cut felt backwards; the
earlier wiring (g3 = HI) gave the opposite sweep. Flipping it is a one-line change here and a riser respin, and it
flips BOTH filters together because one board design serves both.

Geometry: 46 x 15 mm, all parts on F. The pot's shoulder is at local x = 1.0 (the board's panel-end edge), so the
board spans 1.0 to 47.0 mm behind the shoulder in the tube. The front 18 mm is what passes through the control
deck window, so nothing there may be wider than the board.
"""
from core import *
from common import *

FP_POT = "GAS_Parts:Pot_Bourns_PTD904_SideAdjust"
W, H = 46.0, 15.0
POT_X, POT_Y = 2.0, 7.5          # footprint origin: shaft axis at the mounting shoulder, 2 mm in from the edge
HDR_X, HDR_Y = 23.0, 7.5         # XH-8 pin 1, clear of the pot body (17.2 mm deep)


def build():
    b = Board("filter-pot-riser", "GAS Rev C - filter-pot riser (carries one PTD904 4-gang pot, HPF or LPF)",
              ["Stands perpendicular to the control deck; the pot's own M7 bushing nut holds the assembly to the cap",
               "Per gang: CCW end = HI, wiper and CW end tied = W. CW lowers both filter corners",
               "Same board for HPF (circuit P5) and LPF (circuit P6): build 2"], date="2026-09-21")
    b.outline = (W, H)

    B = "Pot and harness"
    nets = {}
    for g in range(1, 5):
        nets[f"{g}1"] = f"G{g}_HI"     # CCW end drives the filter node
        nets[f"{g}2"] = f"G{g}_W"      # wiper
        nets[f"{g}3"] = f"G{g}_W"      # CW end tied to the wiper: resistance rises clockwise
    b.add("VR1", "GAS_Parts:PTD904", "50k lin x4", FP_POT, {1: nets}, B,
          MPN="PTD904-2015K-B503", Manufacturer="Bourns",
          Description="4-gang 50k linear, M7x0.75, 15 mm shaft, side adjust. Gang 1 is nearest the panel")
    b.fixed["VR1"] = (POT_X, POT_Y, 0, "F")

    b.XH("P1", "to circuit-board P5 (HPF) or P6 (LPF)",
         ["G1_HI", "G1_W", "G2_HI", "G2_W", "G3_HI", "G3_W", "G4_HI", "G4_W"], B,
         Description="1:1 with circuit P5 / P6: (HI, wiper) per gang, gang 1 nearest the panel")
    b.fixed["P1"] = (HDR_X, HDR_Y, 0, "F")

    # the front is wall-to-wall pads, so the legend goes on the back
    b.texts = [(W / 2, 5.5, "GAS REV C FILTER POT RISER - HPF or LPF", 1.0, "B.SilkS"),
               (W / 2, 9.5, "ILLICIT APOTHECARY - gang 1 at the panel end", 1.0, "B.SilkS")]
    b.gap = 1.2
    b.passes = 40
    b.edge_clearance = 0.3
    return b
