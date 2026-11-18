"""Walk J2 pads -> first via, F.Cu tracks only, integer nm keys."""
import json, math
from collections import defaultdict, deque
from pathlib import Path
import pcbnew as p

SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))

adj = defaultdict(list)   # (x,y) nm -> [(other, uuid)]
info = {}
vias_at = {}
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    if isinstance(t, p.PCB_VIA):
        vias_at[(s.x, s.y)] = t
        info[t.m_Uuid.AsString()] = ("via", t.GetNetname(), (s.x, s.y))
    elif t.GetLayer() == p.F_Cu:
        adj[(s.x, s.y)].append(((e.x, e.y), t.m_Uuid.AsString()))
        adj[(e.x, e.y)].append(((s.x, s.y), t.m_Uuid.AsString()))
        info[t.m_Uuid.AsString()] = ("trk", t.GetNetname(), (s.x, s.y), (e.x, e.y), t.GetWidth())

def pad_hits(a):
    """track endpoints inside the pad shape (centre dist in pad frame)."""
    pp = a.GetPosition()
    ang = math.radians(a.GetParentFootprint().GetOrientationDegrees())
    # pad local offset
    off = a.GetOffset()
    hits = []
    for (x, y) in adj.keys():
        dx, dy = (x - pp.x) / 1e6, (y - pp.y) / 1e6
        # rotate into footprint frame
        lx = dx * math.cos(ang) + dy * math.sin(ang)
        ly = -dx * math.sin(ang) + dy * math.cos(ang)
        # pad centre in local frame approx (pads stored with position incl. offset already via GetPosition on pad itself)
        hits.append((x, y))
    return hits

result = {}
for ref in ("J2",):
    fp = b.FindFootprintByReference(ref)
    for a in sorted(fp.Pads(), key=lambda q: q.GetNumber()):
        ap = a.GetPosition()  # absolute pad centre (nm)
        ax, ay = ap.x, ap.y
        size = a.GetSize()
        # endpoints within pad rect (generous: half diag of pad + track half width)
        starts = [pt for pt in adj.keys() if abs(pt[0] - ax) <= size.x // 2 + 200000 and abs(pt[1] - ay) <= size.y // 2 + 200000]
        # BFS
        seen = set()
        dq = deque()
        for s0 in starts:
            dq.append((s0, []))
            seen.add(s0)
        found = None
        while dq and found is None:
            node, path = dq.popleft()
            if node in vias_at and path:
                found = (node, path)
                break
            for (other, uid) in adj.get(node, []):
                if other not in seen:
                    seen.add(other)
                    dq.append((other, path + [uid]))
        result[a.GetNumber()] = {"net": a.GetNetname(),
                                 "via_nm": list(found[0]) if found else None,
                                 "via_mm": [found[0][0] / 1e6, found[0][1] / 1e6] if found else None,
                                 "segs": len(found[1]) if found else 0,
                                 "uuids": found[1] if found else []}
        print(a.GetNumber(), a.GetNetname(), "via:", result[a.GetNumber()]["via_mm"], "segs:", result[a.GetNumber()]["segs"])
Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime/j2paths2.json").write_text(json.dumps(result, indent=1))
