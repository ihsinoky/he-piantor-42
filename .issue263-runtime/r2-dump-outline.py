"""Dump board outline points (mm) to JSON. Arg: board path, out path."""
import pcbnew as p, json, sys
b = p.LoadBoard(sys.argv[1])
poly = p.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(poly)
o = poly.Outline(0)
pts = [[p.ToMM(o.GetPoint(i).x), p.ToMM(o.GetPoint(i).y)] for i in range(o.PointCount())]
json.dump(pts, open(sys.argv[2], 'w'))
print('pts', len(pts))
