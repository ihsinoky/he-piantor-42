#!/usr/bin/env python3
"""Route B.Cu GND bridge tracks from each island component to the J_WING
return component (fast grid A*, >=0.100 mm to other-net copper,
>=0.25 mm to NPTH hole edges).  Widest of 0.30..0.10 first.

Usage: route.py <in.kicad_pcb> <out.kicad_pcb>
GND copper only.  Islands with no B.Cu path are left for stitch.py."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
import gndcheck as gc
import survey2
import stitch

NM = 1e6
BCU = pcbnew.B_Cu
CLR = 0.100
HOLE_CLR = 0.25

def obstacles_bcu_list(board):
    obs = []
    for t in board.GetTracks():
        if t.GetNetname() == "GND" or not t.IsOnLayer(BCU):
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            obs.append(Point(pos.x / NM, pos.y / NM).buffer(t.GetWidth(BCU) / NM / 2.0, resolution=24))
        else:
            s, e = t.GetStart(), t.GetEnd()
            obs.append(LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)]).buffer(
                t.GetWidth() / NM / 2.0, cap_style=1, resolution=8))
    for zone in board.Zones():
        if zone.GetNetname() in ("GND", "") or not zone.IsOnLayer(BCU):
            continue
        obs.extend(gc.polys_from_set(zone.GetFilledPolysList(BCU)))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                continue
            if pad.IsOnLayer(BCU):
                obs.append(gc.pad_geom(pad, BCU))
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                ds = pad.GetDrillSize()
                if ds and ds.x > 0:
                    pos = pad.GetPosition()
                    obs.append(Point(pos.x / NM, pos.y / NM).buffer(ds.x / NM / 2.0 + HOLE_CLR, resolution=24))
    return obs

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    board = pcbnew.LoadBoard(inp)
    gnd_code = None
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                gnd_code = pad.GetNetCode()
    obs = obstacles_bcu_list(board)
    obs_union = unary_union(obs) if obs else None
    bridges = []
    for attempt in range(6):
        objs, find, pad_objs = survey2.build(board)
        jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
        groups = {}
        for name, olist in pad_objs.items():
            groups.setdefault(find(objs.index(olist[0])), []).append(name)
        islands = {r: ns for r, ns in groups.items() if r != jw_root}
        if not islands:
            break
        def root_geom(root):
            gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == BCU]
            return unary_union(gs) if gs else None
        ret = root_geom(jw_root)
        progress = False
        for root, names in sorted(islands.items(), key=lambda kv: sorted(kv[1])):
            isl = root_geom(root)
            if isl is None:
                continue
            bb = isl.bounds
            placed = None
            for w in (0.30, 0.25, 0.20, 0.15, 0.10):
                for margin in (2.5, 5.0, 9.0):
                    clip = box(bb[0] - margin, bb[1] - margin, bb[2] + margin, bb[3] + margin)
                    path = stitch.grid_astar(isl, ret, obs, w, res=0.025, margin=1.0,
                                             goal_clip=clip)
                    if path:
                        break
                if path:
                    placed = (w, stitch.simplify(path, obs_union, w))
                    break
            if not placed:
                print(f"island {sorted(names)}: no B.Cu bridge", file=sys.stderr)
                continue
            w, path = placed
            for a, b in zip(path, path[1:]):
                stitch.add_track(board, a, b, w, BCU, gnd_code)
            bridges.append({"pads": sorted(names), "width": w,
                            "path": [[round(x, 3), round(y, 3)] for x, y in path]})
            progress = True
            break  # rebuild state
        if not progress:
            break
    pcbnew.SaveBoard(outp, board)
    print(json.dumps({"bridges": bridges}, indent=1))

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
