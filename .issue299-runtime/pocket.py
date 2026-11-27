#!/usr/bin/env python3
"""Dump all copper near a point, both layers, with distances to a
reference island polygon.  Usage: pocket.py <board> <x> <y> <radius>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, LineString
import gndcheck as gc

NM = 1e6

def main():
    path, cx, cy, rad = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    board = pcbnew.LoadBoard(path)
    centre = Point(cx, cy)
    for layer, lname in ((pcbnew.F_Cu, "F.Cu"), (pcbnew.B_Cu, "B.Cu")):
        print(f"--- {lname} ---")
        rows = []
        for t in board.GetTracks():
            if not t.IsOnLayer(layer):
                continue
            if t.Type() == pcbnew.PCB_VIA_T:
                pos = t.GetPosition()
                g = Point(pos.x / NM, pos.y / NM).buffer(t.GetWidth(layer) / NM / 2.0, resolution=16)
                d = g.distance(centre)
                if d < rad:
                    rows.append((d, f"via [{t.GetNetname()}] @({pos.x/NM:.3f},{pos.y/NM:.3f}) d={t.GetWidth(layer)/NM:.2f} drill={t.GetDrillValue()/NM:.2f}"))
            else:
                s, e = t.GetStart(), t.GetEnd()
                g = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)]).buffer(t.GetWidth() / NM / 2.0, cap_style=1, resolution=4)
                d = g.distance(centre)
                if d < rad:
                    rows.append((d, f"track [{t.GetNetname()}] ({s.x/NM:.2f},{s.y/NM:.2f})->({e.x/NM:.2f},{e.y/NM:.2f}) w={t.GetWidth()/NM:.2f}"))
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if not pad.IsOnLayer(layer):
                    continue
                g = gc.pad_geom(pad, layer)
                d = g.distance(centre)
                if d < rad:
                    pos = pad.GetPosition()
                    rows.append((d, f"pad [{pad.GetNetname()}] {fp.GetReference()}.{pad.GetNumber()} @({pos.x/NM:.3f},{pos.y/NM:.3f})"))
        for zone in board.Zones():
            if not zone.IsOnLayer(layer):
                continue
            for i, p in enumerate(gc.polys_from_set(zone.GetFilledPolysList(layer))):
                d = p.distance(centre)
                if d < rad:
                    rows.append((d, f"zonefill [{zone.GetNetname()}] #{i} area={p.area:.2f} bounds={tuple(round(v,2) for v in p.bounds)}"))
        for d, s in sorted(rows):
            print(f"  {d:6.3f}  {s}")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
