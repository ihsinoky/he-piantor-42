"""Stage 2b gates for Main Rev.9 + Wing Rev.6 x4, using the #263 yardsticks:
kicad-cli DRC (material filter), copper-graph connectivity / wrong-net
contacts (verify.py method), via-pad nearest gaps (floor 0.10).
Writes gates-2b.json + drc.json into each board dir and prints a summary.
Usage: gates-2b.py [board ...]  (default: all five)"""
import collections, json, subprocess, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from shapely.strtree import STRtree

MM = 1e6
ROOT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification")
CLI = "/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli"
sys.path.insert(0, str(ROOT / "issue-263-implementation"))
from verify import polys, padgeom, xy  # #263 helpers (read-only import)

EXCLUDE = {"silk_overlap", "silk_over_copper", "text_height",
           "lib_footprint_mismatch", "lib_footprint_issues"}

def gates(w: Path):
    subprocess.run([CLI, "pcb", "drc", "--format", "json", "--severity-all",
                    "-o", str(w / "drc.json"), str(w / "main.kicad_pcb")], check=True,
                   capture_output=True)
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
    out = dict(board=w.name,
               drc_violations_total=len(drc["violations"]),
               drc_types=dict(collections.Counter(x["type"] for x in drc["violations"])),
               material_violations=len(material),
               drc_unconnected=len(drc["unconnected_items"]),
               graph_unconnected=unconnected,
               wrong_net_contacts=len(shorts),
               vias=len(vias), via_pad_min_mm=round(min(gaps), 4) if gaps else None,
               via_pad_below_0p10=sum(g < 0.1 - 1e-9 for g in gaps))
    out["pass"] = (out["material_violations"] == 0 and out["drc_unconnected"] == 0
                   and out["graph_unconnected"] == 0 and out["wrong_net_contacts"] == 0
                   and out["via_pad_below_0p10"] == 0)
    (w / "gates-2b.json").write_text(json.dumps(out, indent=2) + "\n")
    print(w.name, {k: out[k] for k in ("material_violations", "drc_unconnected", "graph_unconnected",
                                       "wrong_net_contacts", "via_pad_min_mm", "via_pad_below_0p10", "pass")}, flush=True)
    return out

if __name__ == "__main__":
    dirs = [ROOT / "issue-270-main-rev9" / "main-rev9"] + sorted((ROOT / "issue-270-wing-rev6").glob("wing-rev6-*"))
    if len(sys.argv) > 1:
        dirs = [d for d in dirs if d.name in sys.argv[1:]]
    res = [gates(d) for d in dirs]
    print("ALL PASS" if all(r["pass"] for r in res) else "SOME FAILED")
