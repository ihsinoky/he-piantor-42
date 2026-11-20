import pcbnew as p, json, sys
T = "/home/hatch/workspace/projects/he-piantor-wmain2/hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb"
b = p.LoadBoard(T)
def mm(v): return v/1e6
out = {}
# outline via KiCad chaining
ps = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps, None)
chains = []
for oi in range(ps.OutlineCount()):
    ch = ps.Outline(oi); pts = []
    for i in range(ch.PointCount()):
        q = ch.CPoint(i); pts.append([round(mm(q.x),4), round(mm(q.y),4)])
    chains.append(pts)
out["outline_chains"] = chains
out["thickness"] = mm(b.GetDesignSettings().GetBoardThickness()) if hasattr(b.GetDesignSettings(),'GetBoardThickness') else None
fps = []
for fp in b.GetFootprints():
    d = {"ref": fp.GetReference(), "pos": [round(mm(fp.GetPosition().x),3), round(mm(fp.GetPosition().y),3)],
         "rot": fp.GetOrientationDegrees(), "layer": fp.GetLayerName(), "pads": []}
    bb = fp.GetBoundingBox()
    d["bbox"] = [round(mm(bb.GetLeft()),2), round(mm(bb.GetTop()),2), round(mm(bb.GetRight()),2), round(mm(bb.GetBottom()),2)]
    for pad in fp.Pads():
        d["pads"].append({"n": pad.GetNumber(), "net": pad.GetNetname(),
            "pos": [round(mm(pad.GetPosition().x),3), round(mm(pad.GetPosition().y),3)],
            "size": [round(mm(pad.GetSize().x),3), round(mm(pad.GetSize().y),3)],
            "shape": str(pad.GetShape()), "layers": pad.GetLayerSet().FmtHex() if hasattr(pad.GetLayerSet(),'FmtHex') else ""})
    fps.append(d)
out["footprints"] = fps
tr = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        tr.append({"via": True, "pos": [round(mm(t.GetPosition().x),3), round(mm(t.GetPosition().y),3)],
                   "d": round(mm(t.GetDrillValue()),3), "net": t.GetNetname()})
    else:
        tr.append({"via": False, "a": [round(mm(t.GetStart().x),3), round(mm(t.GetStart().y),3)],
                   "b": [round(mm(t.GetEnd().x),3), round(mm(t.GetEnd().y),3)],
                   "w": round(mm(t.GetWidth()),3), "net": t.GetNetname(), "layer": t.GetLayerName()})
out["tracks"] = tr
zones = []
for z in b.Zones():
    zones.append({"name": z.GetZoneName(), "net": z.GetNetname(), "layer": z.GetLayerName(), "rulearea": z.GetIsRuleArea()})
out["zones"] = zones
json.dump(out, open(sys.argv[1], "w"))
print("chains:", [len(c) for c in chains], "fps:", len(fps), "tracks:", len(tr), "zones:", len(zones))
