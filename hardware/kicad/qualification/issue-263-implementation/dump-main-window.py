"""Dump Main copper geometry in the J3.8 region (F/B/In2) to JSON for plotting."""
import json
import pcbnew as p
from verify import xy, polys, padgeom
from shapely.geometry import LineString, Point, mapping

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
b = p.LoadBoard(f'{E}/main-rev8/routed.kicad_pcb')
BOX = (102.0, 106.0, 129.0, 126.0)
LAYERS = ((p.F_Cu, 'F'), (p.In2_Cu, 'In2'), (p.B_Cu, 'B'))

def in_box(g):
    return g.bounds[2] >= BOX[0] and g.bounds[0] <= BOX[2] and g.bounds[3] >= BOX[1] and g.bounds[1] <= BOX[3]

out = {'tracks': [], 'pads': [], 'zones': []}
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        g = Point(xy(t.GetPosition())).buffer(0.3)
        if in_box(g):
            out['tracks'].append({'net': t.GetNetname(), 'layer': 'VIA', 'geom': mapping(g)})
    else:
        ln = {p.F_Cu: 'F', p.In1_Cu: 'In1', p.In2_Cu: 'In2', p.B_Cu: 'B'}[t.GetLayer()]
        g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth()) / 2)
        if in_box(g):
            out['tracks'].append({'net': t.GetNetname(), 'layer': ln, 'geom': mapping(g)})
for f in b.GetFootprints():
    for a in f.Pads():
        for l, ln in LAYERS + ((p.In1_Cu, 'In1'),):
            if a.IsOnLayer(l):
                g = padgeom(a, l)
                if in_box(g):
                    out['pads'].append({'net': a.GetNetname(), 'layer': ln, 'num': a.GetNumber(), 'ref': f.GetReference(), 'geom': mapping(g)})
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    for l, ln in LAYERS + ((p.In1_Cu, 'In1'),):
        if z.IsOnLayer(l):
            g = polys(z.GetFilledPolysList(l))
            if not g.is_empty and in_box(g):
                out['zones'].append({'net': z.GetNetname(), 'layer': ln, 'geom': mapping(g)})
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/main-j38-window.json', 'w'))
print('tracks', len(out['tracks']), 'pads', len(out['pads']), 'zones', len(out['zones']))
