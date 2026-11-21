#!/usr/bin/env python3
"""Locate copper added by a refill: diff B.Cu GND fill(base) vs fill(new),
report each added region's bounds/area, and identify which added region
bridges the island component to the return component.
Usage: neckfind.py <base> <new>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.ops import unary_union

def fills(path):
    board = pcbnew.LoadBoard(path)
    gs = []
    for zone in board.Zones():
        if zone.GetNetname() == "GND":
            gs.extend(gc.polys_from_set(zone.GetFilledPolysList(pcbnew.B_Cu)))
    return unary_union(gs) if gs else None

def polys(g):
    if g is None or g.is_empty:
        return []
    return list(g.geoms) if g.geom_type == "MultiPolygon" else [g]

def main():
    base_f = fills(sys.argv[1])
    new_f = fills(sys.argv[2])
    added = new_f.difference(base_f)
    removed = base_f.difference(new_f)
    print(f"base fill area {base_f.area:.2f}  new {new_f.area:.2f}  "
          f"added {added.area:.3f}  removed {removed.area:.4f}")
    for p in sorted((q for q in polys(added) if q.area >= 0.02), key=lambda q: -q.area):
        b = p.bounds
        print(f"  added region area {p.area:8.3f} bounds "
              f"({b[0]:.2f},{b[1]:.2f})-({b[2]:.2f},{b[3]:.2f}) "
              f"w {b[2]-b[0]:.2f} h {b[3]-b[1]:.2f}")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
