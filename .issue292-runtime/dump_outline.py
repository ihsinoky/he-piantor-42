import pcbnew as p, json, sys
b = p.LoadBoard(sys.argv[1])
def mm(v): return v/1e6
ps = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps, None)
chains = []
for oi in range(ps.OutlineCount()):
    ch = ps.Outline(oi); pts = []
    for i in range(ch.PointCount()):
        q = ch.CPoint(i); pts.append([round(mm(q.x),3), round(mm(q.y),3)])
    chains.append(pts)
fps = {}
for fp in b.GetFootprints():
    fps[fp.GetReference()] = [round(mm(fp.GetPosition().x),3), round(mm(fp.GetPosition().y),3), fp.GetOrientationDegrees()]
json.dump({"chains": chains, "fps": fps}, open(sys.argv[2], "w"))
print(sys.argv[1].split("/")[-2], "chains:", [len(c) for c in chains], "J_WING:", fps.get("J_WING"), "refs:", len(fps))
