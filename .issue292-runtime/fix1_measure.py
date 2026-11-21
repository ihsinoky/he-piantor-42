#!/usr/bin/env python3
"""F1 measurement: annulus coverage of named vias by In1.Cu GND zone fill,
plus a full snapshot of every zone fill (per layer: polygon count, area,
geometry hash). Runs on the board file AS SAVED - no refill, no save.

Usage: fix1_measure.py <board.kicad_pcb> <out.json>
"""
import sys, json, hashlib, math
import pcbnew
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

NM = 1e6  # pcbnew internal units per mm

def polys_from_set(ps):
    """Convert a pcbnew SHAPE_POLY_SET to a list of shapely polygons (mm)."""
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

def geom_hash(polys):
    h = hashlib.sha256()
    for p in polys:
        h.update(p.wkb)
    return h.hexdigest()

def main():
    board_path, out_path = sys.argv[1], sys.argv[2]
    board = pcbnew.LoadBoard(board_path)
    layer_ids = {}
    for lid in range(pcbnew.PCB_LAYER_ID_COUNT):
        name = board.GetLayerName(lid)
        if name:
            layer_ids[name] = lid
    cu_layers = [n for n in ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu") if n in layer_ids]

    # --- zone fill snapshot (all zones, all copper layers) ---
    snapshot = []
    gnd_in1 = None
    for zone in board.Zones():
        ref = zone.GetZoneName() or ""
        net = zone.GetNetname()
        for lname in cu_layers:
            lid = layer_ids[lname]
            if not zone.IsOnLayer(lid):
                continue
            try:
                ps = zone.GetFilledPolysList(lid)
            except Exception:
                continue
            if ps is None or ps.OutlineCount() == 0:
                continue
            polys = polys_from_set(ps)
            if not polys:
                continue
            area = sum(p.area for p in polys)
            snapshot.append({
                "zone": ref, "net": net, "layer": lname,
                "polygons": len(polys), "area_mm2": round(area, 6),
                "geom_sha256": geom_hash(polys),
            })
            if net == "GND" and lname == "In1.Cu":
                gnd_in1 = unary_union(polys)

    # --- target vias ---
    targets = [
        ("RESET_N", 112.9, 133.75),
        ("RESET_N", 108.3, 133.975),
        ("SYS_3V3", 100.5, 134.95),
    ]
    # JSWD guide holes (NPTH) from the review finding 2 - locate JSWD footprint holes
    results = []
    vias = {}
    for track in board.GetTracks():
        if isinstance(track, pcbnew.PCB_VIA):
            pos = track.GetPosition()
            key = (track.GetNetname(), round(pos.x / NM, 3), round(pos.y / NM, 3))
            vias[key] = track
    for net, x, y in targets:
        via = vias.get((net, x, y))
        if via is None:
            # fuzzy match
            for (n, vx, vy), v in vias.items():
                if n == net and abs(vx - x) < 0.01 and abs(vy - y) < 0.01:
                    via = v
                    break
        if via is None:
            results.append({"net": net, "x": x, "y": y, "error": "via not found"})
            continue
        dia = via.GetWidth() / NM
        drill = via.GetDrillValue() / NM
        outer = Point(x, y).buffer(dia / 2.0, resolution=256)
        inner = Point(x, y).buffer(drill / 2.0, resolution=256)
        annulus = outer.difference(inner)
        overlap = annulus.intersection(gnd_in1).area if gnd_in1 is not None else None
        results.append({
            "net": net, "x": x, "y": y,
            "via_dia_mm": dia, "drill_mm": drill,
            "annulus_area_mm2": round(annulus.area, 6),
            "gnd_fill_overlap_mm2": None if overlap is None else round(overlap, 6),
        })

    # --- JSWD guide-hole drill disks vs In1.Cu GND fill ---
    holes = []
    for fp in board.GetFootprints():
        if fp.GetReference() == "JSWD":
            for pad in fp.Pads():
                d = pad.GetDrillSize()
                if d.x > 0:
                    pos = pad.GetPosition()
                    holes.append({
                        "pad": pad.GetNumber(),
                        "x": pos.x / NM, "y": pos.y / NM,
                        "drill_mm": d.x / NM,
                    })
    for h in holes:
        disk = Point(h["x"], h["y"]).buffer(h["drill_mm"] / 2.0, resolution=256)
        h["gnd_fill_overlap_mm2"] = (
            round(disk.intersection(gnd_in1).area, 6) if gnd_in1 is not None else None)

    out = {
        "board": board_path,
        "annulus_coverage": results,
        "jswd_guide_holes": holes,
        "zone_snapshot": snapshot,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({"annulus_coverage": results, "jswd_guide_holes": holes}, indent=1))
    print(f"zones snapshotted: {len(snapshot)}")

if __name__ == "__main__":
    main()
