#!/usr/bin/env python3
"""Exact free-space connectivity test: can a B.Cu track of width w
(centreline must stay >= 0.10 + w/2 from other-net copper) connect the
island to the return component within island-bbox + MARGIN?
Usage: freetest.py <board> [width] [margin]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, box
from shapely.ops import unary_union
import survey2, route as rt

BCU = pcbnew.B_Cu

def test(path, width=0.10, margin=12.0):
    board = pcbnew.LoadBoard(path)
    objs, find, pad_objs = survey2.build(board)
    jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
    groups = {}
    for name, olist in pad_objs.items():
        groups.setdefault(find(objs.index(olist[0])), []).append(name)
    obs_union = unary_union(rt.obstacles_bcu(board))
    blocked = obs_union.buffer(rt.CLR + width / 2.0 + rt.EPS)
    def root_geom(root):
        gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == BCU]
        return unary_union(gs) if gs else None
    ret = root_geom(jw_root)
    print(f"{os.path.basename(path)} w={width} margin={margin}")
    for root, names in groups.items():
        if root == jw_root:
            continue
        isl = root_geom(root)
        win = box(isl.bounds[0] - margin, isl.bounds[1] - margin,
                  isl.bounds[2] + margin, isl.bounds[3] + margin)
        free = win.difference(blocked)
        u = unary_union([free, isl, ret.intersection(win)])
        polys = list(u.geoms) if u.geom_type == "MultiPolygon" else [u]
        pi = Point(isl.representative_point())
        ok = False
        for p in polys:
            if p.contains(pi):
                ok = p.intersects(ret)
                break
        print(f"  island {sorted(names)}: {'PATH EXISTS' if ok else 'SEALED'}")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    w = float(sys.argv[2]) if len(sys.argv) > 2 else 0.10
    m = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0
    test(sys.argv[1], w, m)
