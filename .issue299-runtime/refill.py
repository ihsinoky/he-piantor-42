#!/usr/bin/env python3
"""Refill ONLY the HALL_3V3 zone of a board (in its project dir) and
report fill areas before/after for HALL_3V3 and GND.

Usage: refill.py <board.kicad_pcb>
The board MUST be loaded from its full project directory (the saved
fill only reproduces with the .kicad_pro present)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.ops import unary_union

def areas(board):
    out = {}
    for z in board.Zones():
        net = z.GetNetname()
        if net in ("GND", "HALL_3V3"):
            layer = pcbnew.B_Cu if net == "GND" else pcbnew.F_Cu
            ps = gc.polys_from_set(z.GetFilledPolysList(layer))
            u = unary_union(ps) if ps else None
            out[net] = round(u.area, 4) if u else 0.0
    return out

def main():
    path = sys.argv[1]
    board = pcbnew.LoadBoard(path)
    before = areas(board)
    hz = [z for z in board.Zones() if z.GetNetname() == "HALL_3V3"]
    assert len(hz) == 1
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(hz)
    after = areas(board)
    pcbnew.SaveBoard(path, board)
    print(f"HALL_3V3 fill: {before['HALL_3V3']:.4f} -> {after['HALL_3V3']:.4f} (delta {after['HALL_3V3']-before['HALL_3V3']:+.4f})")
    print(f"GND fill     : {before['GND']:.4f} -> {after['GND']:.4f} (delta {after['GND']-before['GND']:+.4f})")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
