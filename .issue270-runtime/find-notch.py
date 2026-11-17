"""Identify Wing notch-floor Edge.Cuts items: those near the Main outline
in the fitted case frame (stage-1/2a transform conventions)."""
import json, sys
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate as shp_rotate

MM = 1e6
HERE = "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime"
g = json.loads(open(f"{HERE}/geometry.json").read())
main_poly = Polygon(g["main_rev8_outline"])  # case frame

board_path, side = sys.argv[1], sys.argv[2]
deg, env = (30.5, (-27.0, -37.5)) if side == "left" else (-30.5, (27.0, -37.5))
board = p.LoadBoard(board_path)
jf = [x for x in board.GetFootprints() if x.GetReference() == "J_WING"][0]
jx, jy = jf.GetPosition().x / MM, jf.GetPosition().y / MM
print("J_WING board origin:", jx, jy, file=sys.stderr)

def xf(pt):
    q = shp_rotate(Point(pt[0] - jx, pt[1] - jy), deg, origin=(0, 0))
    return (q.x + env[0], q.y + env[1])

for i, d in enumerate(board.GetDrawings()):
    if d.GetLayer() != p.Edge_Cuts:
        continue
    s = (d.GetStart().x / MM, d.GetStart().y / MM)
    e = (d.GetEnd().x / MM, d.GetEnd().y / MM)
    seg = LineString([xf(s), xf(e)])
    dist = seg.distance(main_poly)
    if dist < 2.5:
        print(i, "dist=%.3f" % dist, "board", [round(v, 3) for v in s], "->", [round(v, 3) for v in e])
