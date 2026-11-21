"""Respin stitch v2: goal set = ALL valid via-B sites (union of discs).

respin_stitch.py (like stitch.py) only tried the 14 nearest via-B
candidates; on 17R U_HA2 all 14 were unreachable on F.Cu while a
farther site routes at 0.30 mm width. v2 runs one A* per width with
the full candidate union as the goal geometry, then snaps the path
ends to the actual via-A / via-B candidate centres.

Usage: respin_stitch2.py <board_in> <board_out> <gate4_floor_mm>
Prints JSON {"stitches": [...]}; islands with no stitch go to stderr.
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, box
from shapely.ops import unary_union
import survey2
import respin_stitch as stitch

NM = 1e6
FCU, BCU = stitch.FCU, stitch.BCU


def add_track(board, pts, width, netcode):
    for p, q in zip(pts, pts[1:]):
        stitch.add_track(board, p, q, width, FCU, netcode)


def main():
    src, dst, floor = sys.argv[1], sys.argv[2], float(sys.argv[3])
    board = pcbnew.LoadBoard(src)
    objs, find, pad_objs = survey2.build(board)
    jw = pad_objs["J_WING.2"][0]
    jw_root = find(objs.index(jw))
    def root_geom(root, layer):
        gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == layer]
        return unary_union(gs) if gs else None
    roots = {}
    for name, olist in pad_objs.items():
        r = find(objs.index(olist[0]))
        if r != jw_root:
            roots.setdefault(r, []).append(name)
    check = stitch.ViaCheck(board, floor)
    gnd_net = board.FindNet("GND")
    netcode = gnd_net.GetNetCode()
    f_obs_all = [g for g, k in check.obs[FCU]]
    f_union = unary_union(f_obs_all)
    placed = []
    for root, names in sorted(roots.items(), key=lambda kv: sorted(kv[1])[0]):
        isl_b = root_geom(root, BCU)
        if isl_b is None or isl_b.area < 0.05:
            continue
        isl_f = root_geom(root, FCU)
        ret_b = root_geom(jw_root, BCU)
        bb = isl_b.bounds
        candA = stitch.sample_candidates(check, isl_b, box(bb[0] - 0.5, bb[1] - 0.5, bb[2] + 0.5, bb[3] + 0.5))
        cx, cy = isl_b.representative_point().x, isl_b.representative_point().y
        candA.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
        candB = stitch.sample_candidates(check, ret_b, box(bb[0] - 7, bb[1] - 7, bb[2] + 7, bb[3] + 7))
        candB.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
        done = None
        # goal type 1: island already has F.Cu copper reaching the return
        if isl_f is not None:
            ret_f = root_geom(jw_root, FCU)
            if ret_f is not None and isl_f.distance(ret_f) < 10.0:
                goals1 = ret_f.intersection(box(bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10))
                if not goals1.is_empty:
                    starts = unary_union([isl_b, isl_f] + [Point(x, y).buffer(stitch.VIA_D / 2.0, resolution=16) for (x, y) in candA[:14]])
                    for w in (0.30, 0.20, 0.10):
                        path = stitch.grid_astar(starts, goals1, f_obs_all, w)
                        if path:
                            done = ("direct", w, path, None, None)
                            break
        if done is None and candA and candB:
            starts = unary_union([Point(x, y).buffer(stitch.VIA_D / 2.0, resolution=16) for (x, y) in candA[:20]])
            goals = unary_union([Point(x, y).buffer(stitch.VIA_D / 2.0, resolution=10) for (x, y) in candB])
            for w in (0.30, 0.20, 0.10):
                path = stitch.grid_astar(starts, goals, f_obs_all, w)
                if not path:
                    continue
                p0, p1 = path[0], path[-1]
                a_near = min(candA[:40], key=lambda p: math.hypot(p[0] - p0[0], p[1] - p0[1]))
                b_near = min(candB, key=lambda p: math.hypot(p[0] - p1[0], p[1] - p1[1]))
                if math.hypot(a_near[0] - p0[0], a_near[1] - p0[1]) > stitch.VIA_D / 2.0 + 0.05:
                    continue
                if math.hypot(b_near[0] - p1[0], b_near[1] - p1[1]) > stitch.VIA_D / 2.0 + 0.05:
                    continue
                done = ("stitch", w, path, a_near, b_near)
                break
        if done is None:
            print(f"island {sorted(names)}: no stitch found", file=sys.stderr)
            continue
        kind, w, path, a_xy, b_xy = done
        if kind == "direct":
            pts = stitch.simplify(path, f_union, w)
            add_track(board, pts, w, netcode)
            placed.append({"island": sorted(names), "kind": "fcu-track", "width": w,
                           "track": [(round(x, 3), round(y, 3)) for x, y in pts]})
        else:
            full = [a_xy] + path + [b_xy]
            pts = stitch.simplify(full, f_union, w)
            stitch.add_via(board, a_xy[0], a_xy[1], netcode)
            stitch.add_via(board, b_xy[0], b_xy[1], netcode)
            add_track(board, pts, w, netcode)
            placed.append({"island": sorted(names), "kind": "stitch", "width": w,
                           "via_a": [round(a_xy[0], 3), round(a_xy[1], 3)],
                           "via_b": [round(b_xy[0], 3), round(b_xy[1], 3)],
                           "track": [(round(x, 3), round(y, 3)) for x, y in pts]})
    pcbnew.SaveBoard(dst, board)
    print(json.dumps({"stitches": placed}, indent=1))


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
