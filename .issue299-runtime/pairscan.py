#!/usr/bin/env python3
"""Exact different-net copper pair scan: every pair of copper objects
(pads, tracks, vias, zone fills as saved) on the same layer belonging
to different nets whose edge distance is below a threshold.
Usage: pairscan.py <board.kicad_pcb> [threshold_mm]
Prints JSON: count + the 25 smallest pairs."""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree

NM = 1e6

def layer_objs(board, layer):
    objs = []  # (net, geom, label)
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            if not pad.GetNetname():
                continue
            g = gc.pad_geom(pad, layer)
            if g is not None:
                objs.append((pad.GetNetname(), g, f"{ref}.{pad.GetNumber()}"))
    for t in board.GetTracks():
        net = t.GetNetname()
        if not net:
            continue
        if type(t).__name__ == "PCB_VIA":
            for lay in (pcbnew.F_Cu, pcbnew.B_Cu):
                if lay == layer:
                    c = t.GetPosition()
                    objs.append((net, Point(c.x / NM, c.y / NM).buffer(
                        t.GetWidth() / NM / 2.0, resolution=16), "via"))
        elif t.GetLayer() == layer:
            s, e = t.GetStart(), t.GetEnd()
            ls = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)])
            objs.append((net, ls.buffer(t.GetWidth() / NM / 2.0,
                                         cap_style=1, resolution=8), "track"))
    for zone in board.Zones():
        if zone.GetNetname() and zone.GetLayerSet().Contains(layer):
            for p in gc.polys_from_set(zone.GetFilledPolysList(layer)):
                objs.append((zone.GetNetname(), p, "fill"))
    return objs

def main():
    path = sys.argv[1]
    thr = float(sys.argv[2]) if len(sys.argv) > 2 else 0.13
    board = pcbnew.LoadBoard(path)
    out = {}
    for layer, lname in ((pcbnew.F_Cu, "F.Cu"), (pcbnew.B_Cu, "B.Cu")):
        objs = layer_objs(board, layer)
        geoms = [o[1] for o in objs]
        tree = STRtree(geoms)
        pairs = []
        for i, (net, g, label) in enumerate(objs):
            for j in tree.query(g.buffer(thr)):
                if j <= i:
                    continue
                net2, g2, label2 = objs[j]
                if net2 == net:
                    continue
                d = g.distance(g2)
                if d < thr:
                    pairs.append((round(d, 6), net, label, net2, label2))
        pairs.sort()
        out[lname] = {"n_below_thr": len(pairs), "smallest": pairs[:25]}
    print(json.dumps({"board": os.path.basename(path), "thr": thr,
                      "layers": out}, indent=1))

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
