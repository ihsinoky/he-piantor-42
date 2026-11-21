#!/usr/bin/env python3
"""F1 change enumeration: 
(a) symmetric difference of the In1.Cu GND fill before/after refill,
    reported as connected regions with bbox, area, and nearby board features;
(b) object census comparison (tracks, vias, pads, footprints) proving the
    refill changed nothing but zone fill geometry.
Usage: fix1_diff.py <before.kicad_pcb> <after.kicad_pcb> <out.json>
"""
import sys, json, math
import pcbnew
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

NM = 1e6

def polys_from_set(ps):
    out = []
    for i in range(ps.OutlineCount()):
        chain = ps.Outline(i)
        pts = [(chain.CPoint(j).x / NM, chain.CPoint(j).y / NM)
               for j in range(chain.PointCount())]
        if len(pts) < 3:
            continue
        holes = []
        for j in range(ps.HoleCount(i)):
            h = ps.Hole(i, j)
            hpts = [(h.CPoint(k).x / NM, h.CPoint(k).y / NM)
                    for k in range(h.PointCount())]
            if len(hpts) >= 3:
                holes.append(hpts)
        try:
            p = Polygon(pts, holes)
            if not p.is_valid:
                p = p.buffer(0)
            if not p.is_empty:
                out.append(p)
        except Exception:
            pass
    return out

def gnd_fill(board):
    for zone in board.Zones():
        if zone.GetNetname() == "GND":
            for lid_name in ("In1.Cu",):
                lid = None
                for cand in range(pcbnew.PCB_LAYER_ID_COUNT):
                    if board.GetLayerName(cand) == lid_name:
                        lid = cand
                if lid is not None and zone.IsOnLayer(lid):
                    return unary_union(polys_from_set(zone.GetFilledPolysList(lid)))
    return None

def census(board):
    items = []
    for t in board.GetTracks():
        pos = t.GetPosition()
        if isinstance(t, pcbnew.PCB_VIA):
            items.append(("via", t.GetNetname(), round(pos.x / NM, 4), round(pos.y / NM, 4),
                          round(t.GetWidth() / NM, 4), round(t.GetDrillValue() / NM, 4)))
        else:
            end = t.GetEnd()
            items.append(("track", t.GetNetname(), round(pos.x / NM, 4), round(pos.y / NM, 4),
                          round(end.x / NM, 4), round(end.y / NM, 4), t.GetLayer()))
    for fp in board.GetFootprints():
        pos = fp.GetPosition()
        items.append(("fp", fp.GetReference(), round(pos.x / NM, 4), round(pos.y / NM, 4),
                      round(fp.GetOrientationDegrees(), 4)))
        for pad in fp.Pads():
            ppos = pad.GetPosition()
            items.append(("pad", fp.GetReference(), pad.GetNumber(), pad.GetNetname(),
                          round(ppos.x / NM, 4), round(ppos.y / NM, 4)))
    return sorted(str(i) for i in items)

def main():
    before = pcbnew.LoadBoard(sys.argv[1])
    after = pcbnew.LoadBoard(sys.argv[2])
    fb, fa = gnd_fill(before), gnd_fill(after)
    removed = fb.difference(fa)   # copper the refill took away
    added = fa.difference(fb)     # copper the refill put back

    def regions(geom):
        if geom.is_empty:
            return []
        geoms = list(geom.geoms) if hasattr(geom, "geoms") else [geom]
        out = []
        for g in geoms:
            if g.area <= 0:
                continue
            out.append({"area_mm2": round(g.area, 6),
                        "bbox": [round(v, 3) for v in g.bounds]})
        return sorted(out, key=lambda r: -r["area_mm2"])

    cb, ca = census(before), census(after)
    out = {
        "fill_area_before_mm2": round(fb.area, 6),
        "fill_area_after_mm2": round(fa.area, 6),
        "removed_regions": regions(removed),
        "added_regions": regions(added),
        "removed_total_mm2": round(removed.area, 6),
        "added_total_mm2": round(added.area, 6),
        "census_before": len(cb), "census_after": len(ca),
        "census_identical": cb == ca,
    }
    with open(sys.argv[3], "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
