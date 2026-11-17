"""Stage B extract: Rev.9 J2/J3 footprints, pads, fanout tracks, outline."""
import json, math
from pathlib import Path
import pcbnew as p

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))

out = {}
for ref in ("J2", "J3"):
    fp = b.FindFootprintByReference(ref)
    pos = fp.GetPosition()
    pads = []
    for a in fp.Pads():
        pp = a.GetPosition()
        pads.append({"num": a.GetNumber(), "net": a.GetNetname(),
                     "x": pp.x / MM, "y": pp.y / MM,
                     "sx": a.GetSize().x / MM, "sy": a.GetSize().y / MM,
                     "layer": "B" if a.IsOnLayer(p.B_Cu) and not a.IsOnLayer(p.F_Cu) else "F"})
    out[ref] = {"x": pos.x / MM, "y": pos.y / MM, "rot": fp.GetOrientationDegrees(),
                "layer": fp.GetLayer(), "pads": sorted(pads, key=lambda q: int(q["num"]) if q["num"].isdigit() else 99)}
    print(ref, out[ref]["x"], out[ref]["y"], out[ref]["rot"], "pads:", len(pads))

# tracks/vias on J2/J3 nets, near sites
def near(x, y, cx, cy, r=14.0):
    return abs(x - cx) < r and abs(y - cy) < r

tr = []
for t in b.GetTracks():
    net = t.GetNetname()
    if net in {q["net"] for q in out["J2"]["pads"]} | {q["net"] for q in out["J3"]["pads"]}:
        s, e = t.GetStart(), t.GetEnd()
        tr.append({"kind": "via" if isinstance(t, p.PCB_VIA) else "trk",
                   "uuid": t.m_Uuid.AsString(), "net": net, "layer": t.GetLayer(),
                   "x1": s.x / MM, "y1": s.y / MM, "x2": e.x / MM, "y2": e.y / MM,
                   "w": (t.GetWidth() / MM) if not isinstance(t, p.PCB_VIA) else (t.GetWidth() / MM)})
out["tracks_jnets"] = tr
print("tracks on J nets:", len(tr))

edges = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        rec = {"kind": str(d.GetShape()), "x1": s.x / MM, "y1": s.y / MM, "x2": e.x / MM, "y2": e.y / MM}
        if d.GetShape() == p.SHAPE_T_ARC:
            m = d.GetArcMid if hasattr(d, "GetArcMid") else None
        edges.append(rec)
out["edges"] = edges
for i, e in enumerate(edges):
    print(i, e)
(RT / "extractB.json").write_text(json.dumps(out, indent=1))
print("written extractB.json")
