"""16L: MUX_A1/A2 components using verify.py's own copper assembly."""
import pcbnew as p, sys, collections
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
from verify import xy, polys, padgeom
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-16mm-left')
b = p.LoadBoard(str(w / 'main.kicad_pcb'))
p.ZONE_FILLER(b).Fill(b.Zones())
for net in ('MUX_A1', 'MUX_A2'):
    copper = []
    def add(g, layers, identity, pad=False):
        if g.is_valid and not g.is_empty:
            copper.append(dict(geom=g, layers=set(layers), id=identity, pad=pad))
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() != net or a.GetAttribute() == p.PAD_ATTRIB_NPTH:
                continue
            for l in (p.F_Cu, p.B_Cu):
                if a.IsOnLayer(l):
                    add(padgeom(a, l), [l], f'{f.GetReference()}.{a.GetNumber()}', True)
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        if isinstance(t, p.PCB_VIA):
            g = Point(xy(t.GetPosition())).buffer(.3, quad_segs=32)
            add(g, [p.F_Cu, p.B_Cu], 'via@' + str([round(v, 1) for v in xy(t.GetPosition())]))
        else:
            width = p.ToMM(t.GetWidth())
            g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(width / 2, quad_segs=16)
            add(g, [t.GetLayer()], 'trk')
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net:
            continue
        for l in (p.F_Cu, p.B_Cu):
            if z.IsOnLayer(l):
                g = polys(z.GetFilledPolysList(l))
                for part in (g.geoms if hasattr(g, 'geoms') else [g]):
                    add(part, [l], 'zone')
    geoms = [c['geom'] for c in copper]
    tree = STRtree(geoms)
    parent = list(range(len(copper)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i, a in enumerate(copper):
        for j0 in tree.query(a['geom'], predicate='intersects'):
            j = int(j0)
            if j < i and a['layers'] & copper[j]['layers']:
                parent[find(i)] = find(j)
    comps = collections.defaultdict(list)
    for i, c in enumerate(copper):
        comps[find(i)].append(c)
    print(net, len(comps), 'components')
    for root, members in comps.items():
        pads = sorted({m['id'] for m in members if m['pad']})
        allg = [m['geom'] for m in members]
        from shapely.ops import unary_union
        u = unary_union(allg)
        print('   pads:', pads, '| centroid:', [round(v, 1) for v in (u.centroid.x, u.centroid.y)], '| items:', len(members))
print('done')
