"""Connectivity walk: from each J2 pad along tracks to the first via(s)."""
import json, math
from collections import defaultdict, deque
from pathlib import Path
import pcbnew as p

MM = 1e6
SRC = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
b = p.LoadBoard(str(SRC))

def key(x, y, layer):
    return (round(x, 3), round(y, 3), layer)

# adjacency: node -> list of (other node, uuid, kind)
adj = defaultdict(list)
items = {}
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    x1, y1, x2, y2 = s.x / MM, s.y / MM, e.x / MM, e.y / MM
    if isinstance(t, p.PCB_VIA):
        # via connects all layers at its point: model as node per point, linked across layers implicitly by same xy in lookups
        for L in (0, 2, 4, 6, 31):  # placeholder; use xy-only node for vias
            pass
        n1 = (round(x1, 3), round(y1, 3), "VIA")
        adj[n1].append((n1, t.m_Uuid.AsString(), "via-self"))
        items[t.m_Uuid.AsString()] = ("via", t.GetNetname(), (x1, y1))
    else:
        L = t.GetLayer()
        n1, n2 = key(x1, y1, L), key(x2, y2, L)
        adj[n1].append((n2, t.m_Uuid.AsString(), "trk"))
        adj[n2].append((n1, t.m_Uuid.AsString(), "trk"))
        items[t.m_Uuid.AsString()] = ("trk", t.GetNetname(), (x1, y1), (x2, y2), L)

# link track endpoints to vias at same xy (any layer)
pts = defaultdict(list)
for n in list(adj.keys()):
    pts[(n[0], n[1])].append(n)
for xy, ns in pts.items():
    vias = [n for n in ns if n[2] == "VIA"]
    for v in vias:
        for n in ns:
            if n != v:
                adj[v].append((n, "vialink", "vialink"))
                adj[n].append((v, "vialink", "vialink"))

fp = b.FindFootprintByReference("J2")
result = {}
for a in sorted(fp.Pads(), key=lambda q: q.GetNumber()):
    pp = a.GetPosition()
    px, py = pp.x / MM, pp.y / MM
    layer = 0  # F_Cu
    start = key(px, py, layer)
    # BFS along same net until a VIA node
    net = a.GetNetname()
    seen = {start}
    dq = deque([(start, [])])
    found = []
    while dq and not found:
        node, path = dq.popleft()
        for (other, uid, kind) in adj.get(node, []):
            if other in seen:
                continue
            if kind == "trk":
                it = items[uid]
                if it[1] != net:
                    continue
            seen.add(other)
            if other[2] == "VIA":
                found.append((other, path + [uid]))
            else:
                dq.append((other, path + [uid]))
    result[a.GetNumber()] = {"net": net, "pad": [round(px, 4), round(py, 4)],
                             "via": [found[0][0][0], found[0][0][1]] if found else None,
                             "path_uuids": found[0][1] if found else [],
                             "path_len": len(found[0][1]) if found else 0}
    print(a.GetNumber(), net, "via:", result[a.GetNumber()]["via"], "segs:", result[a.GetNumber()]["path_len"])
Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime/j2paths.json").write_text(json.dumps(result, indent=1))
