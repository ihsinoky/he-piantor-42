"""Physically disconnected pad groups on the Main routed board (per net)."""
import collections, sys
import pcbnew as p
import shapely
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from verify import xy, polys, padgeom

path = sys.argv[1]
b = p.LoadBoard(path)
mgr = p.GetSettingsManager(); mgr.LoadProject('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/main-rev8/input.kicad_pro'); b.SetProject(mgr.Prj())
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()

def components(net):
    es = []
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetAttribute() == p.PAD_ATTRIB_NPTH or a.GetNetname() != net:
                continue
            ALL = (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu)
            g = unary_union([padgeom(a, l) for l in ALL if a.IsOnLayer(l)])
            es.append((g, {l for l in ALL if a.IsOnLayer(l)}, f'{f.GetReference()}.{a.GetNumber()}'))
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        if isinstance(t, p.PCB_VIA):
            g = Point(xy(t.GetPosition())).buffer(0.3); ls = {p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu}
        else:
            g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth()) / 2); ls = {t.GetLayer()}
        es.append((g, ls, None))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net:
            continue
        for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu):
            if z.IsOnLayer(l):
                g = polys(z.GetFilledPolysList(l))
                for part in (g.geoms if hasattr(g, 'geoms') else [g]):
                    if not part.is_empty:
                        es.append((part, {l}, None))
    tree = shapely.STRtree([e[0] for e in es]); parent = list(range(len(es)))
    def find(i):
        while i != parent[i]:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i, (g, ls, _) in enumerate(es):
        for jj in tree.query(g, predicate='intersects'):
            j = int(jj)
            if j < i and ls & es[j][1]:
                parent[find(i)] = find(j)
    groups = collections.defaultdict(list)
    for i, e in enumerate(es):
        groups[find(i)].append(e)
    return [g for g in groups.values() if any(e[2] for e in g)]

for net in sorted({a.GetNetname() for f in b.GetFootprints() for a in f.Pads() if a.GetNetname()}):
    gs = components(net)
    if len(gs) > 1:
        gs.sort(key=lambda g: -sum(e[0].area for e in g))
        main_g = unary_union([e[0] for e in gs[0]])
        for g in gs[1:]:
            pads = sorted({e[2] for e in g if e[2]})
            gg = unary_union([e[0] for e in g])
            print(f'{net}: island pads {pads} area {gg.area:.3f} dist_to_main {gg.distance(main_g):.3f}')
print('scan done')
