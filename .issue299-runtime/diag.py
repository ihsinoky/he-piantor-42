#!/usr/bin/env python3
"""Diagnose stitch feasibility for one island: candidate tallies per
rejection rule + F.Cu return geometry proximity.
Usage: diag.py <board> <pad_ref e.g. U_HA2> <floor>"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, box
from shapely.ops import unary_union
import survey2, stitch

NM = 1e6
FCU, BCU = pcbnew.F_Cu, pcbnew.B_Cu

def tally(check, target, window, floor):
    local = target.intersection(window)
    if local.is_empty:
        return {"raw": 0}
    counts = {"raw": 0, "ok": 0, "fcu_pad": 0, "fcu_other": 0, "bcu_pad": 0,
              "bcu_other": 0, "via_centre": 0, "npth": 0}
    minx, miny, maxx, maxy = local.bounds
    y = miny
    while y <= maxy + 1e-9:
        x = minx
        while x <= maxx + 1e-9:
            if local.distance(Point(x, y)) <= stitch.VIA_D / 2.0:
                disc = Point(x, y).buffer(stitch.VIA_D / 2.0, resolution=24)
                if disc.intersection(target).area >= 0.02:
                    counts["raw"] += 1
                    bad = None
                    for layer, lp, lo in ((FCU, "fcu_pad", "fcu_other"), (BCU, "bcu_pad", "bcu_other")):
                        tree = check.trees[layer]
                        if tree is None:
                            continue
                        for gi in tree.query(disc.buffer(floor), predicate="intersects"):
                            g, kind = check.obs[layer][gi]
                            req = floor if kind == "pad" else stitch.CLR
                            if disc.distance(g) < req - 1e-9:
                                bad = lp if kind == "pad" else lo
                                break
                        if bad:
                            break
                    if not bad:
                        for (vx, vy) in check.vias:
                            if math.hypot(vx - x, vy - y) < 0.55:
                                bad = "via_centre"; break
                    if not bad:
                        for (hx, hy, hr) in check.holes:
                            if math.hypot(hx - x, hy - y) < hr + stitch.VIA_DRILL / 2.0 + 0.25:
                                bad = "npth"; break
                    counts[bad or "ok"] += 1
            x += 0.05
        y += 0.05
    return counts

def main():
    path, ref, floor = sys.argv[1], sys.argv[2], float(sys.argv[3])
    board = pcbnew.LoadBoard(path)
    objs, find, pad_objs = survey2.build(board)
    jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
    target_root = None
    for name, olist in pad_objs.items():
        if name.startswith(ref + "."):
            target_root = find(objs.index(olist[0]))
    def root_geom(root, layer):
        gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == layer]
        return unary_union(gs) if gs else None
    isl_b = root_geom(target_root, BCU)
    ret_b = root_geom(jw_root, BCU)
    ret_f = root_geom(jw_root, FCU)
    isl_f = root_geom(target_root, FCU)
    print("island B.Cu area", round(isl_b.area, 2), "bounds", tuple(round(v, 2) for v in isl_b.bounds))
    print("island F.Cu:", None if isl_f is None else round(isl_f.area, 2))
    print("return F.Cu distance to island B.Cu geom:", None if ret_f is None else round(isl_b.distance(ret_f), 3))
    check = stitch.ViaCheck(board, floor)
    bb = isl_b.bounds
    print("via-A tally:", tally(check, isl_b, box(bb[0] - 0.5, bb[1] - 0.5, bb[2] + 0.5, bb[3] + 0.5), floor))
    print("via-B tally:", tally(check, ret_b, box(bb[0] - 4, bb[1] - 4, bb[2] + 4, bb[3] + 4), floor))
    # where is F.Cu HALL_3V3 fill relative to island?
    for g, kind in check.obs[FCU]:
        pass
    zones = [g for g, k in check.obs[FCU] if k == "zonefill"]
    if zones:
        z = unary_union(zones)
        print("F.Cu zone fill covers island centre?", z.contains(isl_b.representative_point()),
              "| distance to island B.Cu:", round(z.distance(isl_b), 3))

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
