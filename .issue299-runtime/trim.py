"""South-inner-corner trim (Issue #299 respin; PO-approved via Issue #296).

Cuts a rectangular notch out of the Wing outline at the south inner
corner so the battery removal rim-roll sweep (Z-check section 6) no
longer grazes the board. The notch is defined in case-assembly (asm)
coordinates: the Z-check clip bbox (pre-shift X 6.36..12.75,
Y -6.68..-3.09) expanded by 0.25 mm on every side. For left variants
the asm box is mirrored in X.

The edit is surgical: the single Edge.Cuts segment crossing the box
is replaced by (shortened segment, notch detour chain, shortened
segment). Zone fills blanket the corner, so the caller must refill
zones afterwards (in full project context); the fills then recede
from the new edge by their clearance.

Usage: trim.py <board_in> <board_out> <transform.json> <R|L>
Prints a JSON summary (removed area, chain points in board coords).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

NM = 1e6
CLIP = (6.36, -6.68, 12.75, -3.09)   # x0, y0, x1, y1 (pre-shift asm)
MARGIN = 0.25


def chain_outline(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == pcbnew.Edge_Cuts and d.Type() == pcbnew.PCB_SHAPE_T:
            s, e = d.GetStart(), d.GetEnd()
            segs.append(((s.x / NM, s.y / NM), (e.x / NM, e.y / NM), d))
    pts = [segs[0][0], segs[0][1]]
    used = {0}
    owners = [segs[0][2]]
    for _ in range(len(segs) - 1):
        end = pts[-1]
        for i, (a, c, d) in enumerate(segs):
            if i in used:
                continue
            if abs(a[0] - end[0]) < 1e-6 and abs(a[1] - end[1]) < 1e-6:
                pts.append(c); used.add(i); owners.append(d); break
            if abs(c[0] - end[0]) < 1e-6 and abs(c[1] - end[1]) < 1e-6:
                pts.append(a); used.add(i); owners.append(d); break
        else:
            raise RuntimeError("outline chain broke")
    return pts, owners, segs


def main():
    src, dst, tfile, side = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    T = json.load(open(tfile))
    R, t = np.array(T["R"]), np.array(T["t"])
    Rinv = np.linalg.inv(R)
    def b2a(p): return tuple(R @ np.array(p) + t)
    def a2b(p): return tuple(Rinv @ (np.array(p) - t))

    x0, y0, x1, y1 = CLIP
    if side == "L":
        x0, x1 = -x1, -x0
    notch = box(x0 - MARGIN, y0 - MARGIN, x1 + MARGIN, y1 + MARGIN)
    clip = box(x0, y0, x1, y1)

    board = pcbnew.LoadBoard(src)
    pts, owners, segs = chain_outline(board)
    asm_pts = [b2a(p) for p in pts]
    poly = Polygon(asm_pts)
    removed = poly.intersection(notch)
    newpoly = poly.difference(notch)
    assert removed.area > 1.0, f"removed area too small: {removed.area}"
    assert newpoly.intersection(clip).area < 1e-9, "clip bbox not fully cleared"
    # the detour chain: newpoly boundary vertices inside the notch dilated
    probe = notch.buffer(0.01)
    coords = list(newpoly.exterior.coords)
    from shapely.geometry import Point
    # run must be a contiguous chain on the boundary; find its extent in
    # the coords list (allow wraparound)
    idx = [i for i, c in enumerate(coords) if probe.contains(Point(c))]
    assert idx, "no detour vertices found"
    # contiguity check (circular)
    n = len(coords)
    s0 = idx[0]
    chain_idx = []
    k = s0
    while probe.contains(Point(coords[k % n])) :
        chain_idx.append(k % n)
        k += 1
        if len(chain_idx) > n: break
    chain_asm = [coords[i] for i in chain_idx]
    assert len(chain_asm) == len(idx), "detour chain not contiguous"
    chain_board = [a2b(c) for c in chain_asm]
    # affected original segment: the one whose endpoints straddle the chain
    first, last = chain_board[0], chain_board[-1]
    hit = None
    for (a, c, d) in segs:
        for p, q in ((a, c), (c, a)):
            pass
        # segment intersects notch (in asm)?
        from shapely.geometry import LineString
        if LineString([b2a(a), b2a(c)]).intersects(notch):
            assert hit is None, "more than one outline segment crosses the notch"
            hit = (a, c, d)
    assert hit is not None
    a, c, d = hit
    # replace: a -> chain -> c  (chain order must run from a-side to c-side)
    if (abs(chain_board[0][0] - a[0]) + abs(chain_board[0][1] - a[1]) >
        abs(chain_board[-1][0] - a[0]) + abs(chain_board[-1][1] - a[1])):
        chain_board = chain_board[::-1]
    full = [a] + chain_board + [c]
    board.Remove(d)
    for p, q in zip(full, full[1:]):
        if abs(p[0] - q[0]) < 1e-9 and abs(p[1] - q[1]) < 1e-9:
            continue
        sh = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        sh.SetStart(pcbnew.VECTOR2I(int(round(p[0] * NM)), int(round(p[1] * NM))))
        sh.SetEnd(pcbnew.VECTOR2I(int(round(q[0] * NM)), int(round(q[1] * NM))))
        sh.SetLayer(pcbnew.Edge_Cuts)
        sh.SetWidth(0)
        board.Add(sh)
    pcbnew.SaveBoard(dst, board)
    print(json.dumps({
        "removed_area_mm2": round(removed.area, 4),
        "chain_board": [(round(x, 4), round(y, 4)) for x, y in chain_board],
        "segment_replaced": [(round(a[0], 3), round(a[1], 3)), (round(c[0], 3), round(c[1], 3))],
        "new_segments": len(full) - 1,
    }))


if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
