#!/usr/bin/env python3
"""Test: refill the GND zone with reduced clearance / min_thickness and
see if the islands connect, and how wide the connecting necks are.
Usage: refill_test.py <in> <out> <clearance> <min_thickness>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.geometry import Point
from shapely.ops import unary_union

NM = 1e6

def main():
    inp, outp, clr, mt = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
    board = pcbnew.LoadBoard(inp)
    for zone in board.Zones():
        if zone.GetNetname() == "GND":
            zone.SetLocalClearance(int(clr * NM))
            zone.SetMinThickness(int(mt * NM))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(outp, board)
    res = gc.board_gnd(outp)
    print("after refill clr=%.2f mt=%.2f: %d/%d off=%s" % (
        clr, mt, res["on_return"], res["total_gnd_pads"],
        [o["pad"] for o in res["off_return"]]))
    # neck width probe: for each newly connected pad, find min width of
    # GND copper along the way is hard; instead report the smallest
    # "waist": erode the B.Cu GND union by r and see when the pad
    # disconnects from J_WING (binary search on r) -> neck ~ 2r.
    board2 = pcbnew.LoadBoard(outp)
    import survey2
    objs, find, pad_objs = survey2.build(board2)
    jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
    def root_geom(root, layer):
        gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == layer]
        return unary_union(gs) if gs else None
    # component of each pad in the FIXED board is now one; waist test:
    # take full B.Cu GND union, erode progressively
    allb = root_geom(jw_root, pcbnew.B_Cu)
    for name in sys.argv[5:] if len(sys.argv) > 5 else ("U_HA2.2", "C_HC2.2", "C_HB3.2"):
        if name not in pad_objs:
            continue
        pad_geom = pad_objs[name][0]["geom"] if pad_objs[name][0]["layer"] == pcbnew.B_Cu else pad_objs[name][-1]["geom"]
        pt = pad_geom.representative_point()
        lo, hi = 0.0, 0.30
        for _ in range(12):
            mid = (lo + hi) / 2
            er = allb.buffer(-mid)
            if er.is_empty or not er.contains(pt):
                hi = mid
            else:
                # is the eroded component containing pt the same as one
                # containing a J_WING pad? approx: check J_WING pt too
                jw_pt = pad_objs["J_WING.2"][0]["geom"].representative_point()
                polys = list(er.geoms) if er.geom_type == "MultiPolygon" else [er]
                same = any(p.contains(pt) and p.contains(jw_pt) for p in polys)
                if same:
                    lo = mid
                else:
                    hi = mid
        print(f"  waist at {name}: neck width ~= {2*lo:.3f} mm")

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
