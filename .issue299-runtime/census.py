#!/usr/bin/env python3
"""Diff census between two board files (base vs fixed).

Reports, per file: object counts by class; and the multiset difference
of NON-GND copper geometry (tracks, vias, pads, zone outlines/fills,
footprints, Edge.Cuts) which must be empty, plus a summary of GND-only
differences (added/removed tracks and vias).

Usage: census.py <base.kicad_pcb> <fixed.kicad_pcb>
Exit 0 iff non-GND geometry multisets are identical."""
import sys, os
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew

NM = 1e6

def census(path):
    b = pcbnew.LoadBoard(path)
    c = Counter()
    nongnd = Counter()
    gnd = Counter()
    def key_track(t):
        s, e = t.GetStart(), t.GetEnd()
        return ("trk", t.GetNetname(), t.GetLayer(),
                round(s.x / NM, 4), round(s.y / NM, 4),
                round(e.x / NM, 4), round(e.y / NM, 4), round(t.GetWidth() / NM, 4))
    def key_via(t):
        p = t.GetPosition()
        return ("via", t.GetNetname(), round(p.x / NM, 4), round(p.y / NM, 4),
                round(t.GetWidth(pcbnew.F_Cu) / NM, 4), round(t.GetDrillValue() / NM, 4))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            k = key_via(t); c["via"] += 1
        else:
            k = key_track(t); c["track"] += 1
        (gnd if t.GetNetname() == "GND" else nongnd)[k] += 1
    for fp in b.GetFootprints():
        c["footprint"] += 1
        pos = fp.GetPosition()
        fk = ("fp", str(fp.GetReference()), round(pos.x / NM, 4), round(pos.y / NM, 4),
              round(fp.GetOrientationDegrees(), 4), str(fp.GetFPID().GetLibItemName()))
        nongnd[fk] += 1
        for pad in fp.Pads():
            c["pad"] += 1
            pp = pad.GetPosition()
            pk = ("pad", str(fp.GetReference()), str(pad.GetNumber()), str(pad.GetNetname()),
                  round(pp.x / NM, 4), round(pp.y / NM, 4),
                  round(pad.GetSize().x / NM, 4), round(pad.GetSize().y / NM, 4))
            (gnd if pad.GetNetname() == "GND" else nongnd)[pk] += 1
    for z in b.Zones():
        c["zone"] += 1
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if z.IsOnLayer(layer):
                ps = z.GetFilledPolysList(layer)
                pts = []
                for i in range(ps.OutlineCount()):
                    ch = ps.Outline(i)
                    pts.append(tuple((round(ch.CPoint(j).x / NM, 3), round(ch.CPoint(j).y / NM, 3))
                                     for j in range(ch.PointCount())))
                zk = ("zonefill", z.GetNetname(), layer, tuple(sorted(pts)))
                (gnd if z.GetNetname() == "GND" else nongnd)[zk] += 1
    for d in b.GetDrawings():
        c["drawing"] += 1
        if d.GetLayer() == pcbnew.Edge_Cuts:
            try:
                s, e = d.GetStart(), d.GetEnd()
                dk = ("edge", round(s.x / NM, 4), round(s.y / NM, 4),
                      round(e.x / NM, 4), round(e.y / NM, 4))
            except Exception:
                dk = ("edge", d.GetClass(), d.GetLength())
            nongnd[dk] += 1
    return c, nongnd, gnd

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    cb, nb, gb = census(sys.argv[1])
    cf, nf, gf = census(sys.argv[2])
    print("counts base :", dict(cb))
    print("counts fixed:", dict(cf))
    only_b = nb - nf
    only_f = nf - nb
    print("non-GND only-in-base :", sum(only_b.values()), dict(list(only_b.items())[:5]))
    print("non-GND only-in-fixed:", sum(only_f.values()), dict(list(only_f.items())[:5]))
    g_only_b = gb - gf
    g_only_f = gf - gb
    print("GND removed:", sum(g_only_b.values()), dict(list(g_only_b.items())[:5]))
    print("GND added  :", sum(g_only_f.values()))
    for k, v in g_only_f.items():
        print("   +", k, "x", v)
    sys.exit(0 if not only_b and not only_f else 1)
