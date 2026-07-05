#!/usr/bin/env python3
"""Refill zones on a .kicad_pcb and save (run with KiCad's bundled python).

Usage: python refill_zones.py <board.kicad_pcb>
Added 2026-07-04: used to refill io-board after removing the orphan AGND
stitching via at (117.102, 96.479) so the filler drops the dead islands.
"""
import sys
import pcbnew

path = sys.argv[1]
board = pcbnew.LoadBoard(path)
zones = board.Zones()
print("zones:", len(zones))
for z in zones:
    print("zone", z.GetNetname(), "island mode was:", z.GetIslandRemovalMode())
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
filler = pcbnew.ZONE_FILLER(board)
ok = filler.Fill(zones)
print("fill ok:", ok)
pcbnew.SaveBoard(path, board)
print("saved:", path)
