import pcbnew as p, math
MM = 1e6
b = p.LoadBoard("hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
for d in b.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts: continue
    s, e = d.GetStart(), d.GetEnd()
    cx, cy = (s.x+e.x)/2/MM, (s.y+e.y)/2/MM
    if 60 < cx < 90 and 95 < cy < 125:
        info = f"shape={d.GetShape()} start=({s.x/MM:.4f},{s.y/MM:.4f}) end=({e.x/MM:.4f},{e.y/MM:.4f})"
        if d.GetShape() == p.SHAPE_T_ARC:
            m = d.GetArcMid(); c = d.GetCenter()
            info += f" mid=({m.x/MM:.4f},{m.y/MM:.4f}) centre=({c.x/MM:.4f},{c.y/MM:.4f}) r={d.GetRadius()/MM:.4f}"
        print(info)
