#!/usr/bin/env python3
"""F1 fix: refill ALL zones on the tree board and save in place.
Keeps a pristine copy of the pre-fix file in the runtime dir first."""
import shutil, sys
import pcbnew

TREE = "hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb"
shutil.copyfile(TREE, ".issue292-runtime/fix1-board-before.kicad_pcb")
b = pcbnew.LoadBoard(TREE)
filler = pcbnew.ZONE_FILLER(b)
ok = filler.Fill(b.Zones())
print("fill ok:", ok)
pcbnew.SaveBoard(TREE, b)
print("saved")
