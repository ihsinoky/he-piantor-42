"""Stage B2 comparative gates for Main Rev.9 vs Rev.10 (gates-2d method):
kicad-cli DRC (material filter), copper-graph connectivity / wrong-net,
via-pad gaps; plus ZIF pad-to-outline and copper-to-outline minima.
Usage: gates-main.py <boarddir> <label>  (boarddir contains main.kicad_pcb)"""
import collections, json, subprocess, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree

MM = 1e6
CLI = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli"
IMPL = Path("/home/hatch/workspace/projects/he-piantor-mainsym/hardware/kicad/qualification/issue-263-implementation")
sys.path.insert(0, str(IMPL))
from verify import polys, padgeom, xy

EXCLUDE = {"silk_overlap", "silk_over_copper", "text_height",
           "lib_footprint_mismatch", "lib_footprint_issues"}

w, label = Path(sys.argv[1]), sys.argv[2]
subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all",
                "-o", str(w / "drc.json"), str(w / "main.kicad_pcb")], check=True, capture_output=True)
drc = json.loads((w / "drc.json").read_text())
material = [x for x in drc["violations"] if x["type"] not in EXCLUDE]
b = p.LoadBoard(str(w / "main.kicad_pcb"))
copper, padshapes, vias = [], [], []
def add(g, layers, net, identity, pad=False):
    copper.append(dict(geom=g, layers=set(layers), net=net, id=identity, pad=pad))
for f in b.GetFootprints():
    for a in f.Pads():
        layers = [l for l in (p.F_Cu, p.B_Cu) if a.IsOnLayer(l)]
        padshapes.append((f.GetReference() + "." + a.GetNumber(), a,
                          {l: a.GetEffectiveShape(l) for l in layers}))
        if a.GetAttribute() == p.PAD_ATTRIB_NPTH:
            continue
        for l in layers:
            add(padgeom(a, l), [l], a.GetNetname(), f.GetReference() + "." + a.GetNumber(), True)
n_layers = b.GetCopperLayerCount()
layer_ids = [p.F_Cu] + ([p.In1_Cu, p.In2_Cu] if n_layers == 4 else []) + [p.B_Cu]
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        vias.append(t)
        g = Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2, quad_segs=64).difference(
            Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetDrillValue()) / 2, quad_segs=64))
        add(g, layer_ids, t.GetNetname(), t.m_Uuid.AsString())
    else:
        width = p.ToMM(t.GetWidth())
        g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(width / 2, quad_segs=64)
        add(g, [t.GetLayer()], t.GetNetname(), t.m_Uuid.AsString())
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    for l in layer_ids:
        if not z.IsOnLayer(l):
            continue
        g = polys(z.GetFilledPolysList(l))
        for i, part in enumerate(g.geoms if hasattr(g, "geoms") else [g]):
            add(part, [l], z.GetNetname(), z.m_Uuid.AsString() + f".{i}")
geoms = [x["geom"] for x in copper]
tree = STRtree(geoms)
parent = list(range(len(copper)))
def find(i):
    while i != parent[i]:
        parent[i] = parent[parent[i]]; i = parent[i]
    return i
shorts = []
for i, a in enumerate(copper):
    for j0 in tree.query(a["geom"], predicate="intersects"):
        j = int(j0)
        if j >= i:
            continue
        o = copper[j]
        if not a["layers"] & o["layers"]:
            continue
        if a["net"] != o["net"] or not a["net"]:
            shorts.append([a["id"], o["id"], a["net"], o["net"]])
        parent[find(i)] = find(j)
required = collections.defaultdict(set)
for i, a in enumerate(copper):
    if a["pad"] and a["net"]:
        required[a["net"]].add(find(i))
unconnected = sum(len(v) - 1 for v in required.values() if len(v) > 1)
gaps = []
for v in vias:
    best = 1e9
    for identity, a, shapes in padshapes:
        common = [l for l in shapes if v.IsOnLayer(l)]
        if not common:
            continue
        gap = min(shapes[l].Distance(v.GetPosition()) / MM for l in common) - p.ToMM(v.GetWidth(p.F_Cu)) / 2
        best = min(best, gap)
    gaps.append(best)

# outline geometry: pad-angle clearance at J2/J3 + min copper-to-edge
chain = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        chain.append(((s.x / MM, s.y / MM), (e.x / MM, e.y / MM)))
pts = [chain[0][0]]
cur = chain[0][1]
pts.append(cur)
used = [False] * len(chain); used[0] = True
for _ in range(len(chain) - 1):
    for i, (a2, b2) in enumerate(chain):
        if used[i]:
            continue
        if abs(a2[0] - cur[0]) < 2e-3 and abs(a2[1] - cur[1]) < 2e-3:
            cur = b2
        elif abs(b2[0] - cur[0]) < 2e-3 and abs(b2[1] - cur[1]) < 2e-3:
            cur = a2
        else:
            continue
        used[i] = True; pts.append(cur); break
outline = Polygon(pts)
zif = {}
for ref in ("J2", "J3"):
    fp = b.FindFootprintByReference(ref)
    dmin = 1e9
    for a in fp.Pads():
        if a.GetNumber() == "MP":
            continue
        g = padgeom(a, p.F_Cu)
        dmin = min(dmin, g.distance(outline.exterior))
    zif[ref] = round(dmin, 4)
allcopper = unary_union([x["geom"] for x in copper if p.F_Cu in x["layers"]])
edge_cu = round(allcopper.distance(outline.exterior), 4) if outline.exterior else None

out = dict(board=label,
           drc_violations_total=len(drc["violations"]),
           drc_types=dict(collections.Counter(x["type"] for x in drc["violations"])),
           material_violations=len(material),
           material_types=dict(collections.Counter(x["type"] for x in material)),
           drc_unconnected=len(drc["unconnected_items"]),
           graph_unconnected=unconnected,
           wrong_net_contacts=len(shorts),
           vias=len(vias), via_pad_min_mm=round(min(gaps), 4) if gaps else None,
           via_pad_below_0p10=sum(g < 0.1 - 1e-9 for g in gaps),
           zif_pad_to_outline_mm=zif,
           fcu_copper_to_outline_min_mm=edge_cu)
print(json.dumps(out, indent=1))
Path(f"/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime/gates-{label}.json").write_text(json.dumps(out, indent=1) + "\n")
