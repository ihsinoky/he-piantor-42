"""Dump copper geometry in a window to JSON for plotting (16L MUX_OUT_C)."""
import json, sys
import pcbnew as p
from verify import xy, polys, padgeom
from shapely.geometry import LineString, Point, mapping

W = 'wing-rev5-16mm-left'
b = p.LoadBoard(f'{W}/routed.kicad_pcb')
BOX = (104.0, 24.0, 126.0, 44.0)

def in_box(g):
    return g.bounds[2] >= BOX[0] and g.bounds[0] <= BOX[2] and g.bounds[3] >= BOX[1] and g.bounds[1] <= BOX[3]

out = {'tracks': [], 'pads': [], 'zones': []}
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        g = Point(xy(t.GetPosition())).buffer(0.3)
        if in_box(g):
            out['tracks'].append({'net': t.GetNetname(), 'layer': 'VIA', 'geom': mapping(g)})
    else:
        g = LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth()) / 2)
        if in_box(g):
            out['tracks'].append({'net': t.GetNetname(), 'layer': 'F' if t.GetLayer() == p.F_Cu else 'B', 'geom': mapping(g)})
for f in b.GetFootprints():
    for a in f.Pads():
        for l, ln in ((p.F_Cu, 'F'), (p.B_Cu, 'B')):
            if a.IsOnLayer(l):
                g = padgeom(a, l)
                if in_box(g):
                    out['pads'].append({'net': a.GetNetname(), 'layer': ln, 'num': a.GetNumber(), 'fp': str(f.GetFPID().GetLibItemName()), 'geom': mapping(g)})
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    for l, ln in ((p.F_Cu, 'F'), (p.B_Cu, 'B')):
        if z.IsOnLayer(l):
            g = polys(z.GetFilledPolysList(l))
            if not g.is_empty and in_box(g):
                out['zones'].append({'net': z.GetNetname(), 'layer': ln, 'geom': mapping(g)})
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/wing16l-window.json', 'w'))
print('tracks', len(out['tracks']), 'pads', len(out['pads']), 'zones', len(out['zones']))
