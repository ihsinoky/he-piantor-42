"""Dump Edge.Cuts items of a board (type, start, end, mid for arcs)."""
import sys, json
import pcbnew as p

MM = 1e6

def xy(v):
    return [round(v.x / MM, 4), round(v.y / MM, 4)]

board = p.LoadBoard(sys.argv[1])
out = []
for d in board.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        item = {"shape": str(d.GetShape()), "start": xy(d.GetStart()), "end": xy(d.GetEnd())}
        if d.GetShape() == p.SHAPE_T_ARC:
            item["mid"] = xy(d.GetArcMid())
        out.append(item)
print(json.dumps(out, indent=1))
print("count:", len(out), file=sys.stderr)
