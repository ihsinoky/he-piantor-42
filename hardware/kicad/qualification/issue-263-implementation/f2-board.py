"""F2 step A: board-frame anchors (H1/H2/H3) + Rev.7/Rev.8 outlines to JSON."""
import json
import pcbnew as p
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
from verify import xy

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
out = {}
b = p.LoadBoard(f'{E}/main-rev8/input.kicad_pcb')
anchors = {}
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref in ('H1', 'H2', 'H3'):
        anchors[ref] = xy(f.GetPosition())
out['anchors_rev8'] = anchors

from shapely.ops import unary_union, polygonize

def outline_of(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            segs.append(LineString([xy(d.GetStart()), xy(d.GetEnd())]))
    polys = list(polygonize(unary_union(segs)))
    polys.sort(key=lambda q: -q.area)
    return [list(c) for c in polys[0].exterior.coords]

out['outline_rev8'] = outline_of(b)
b7 = p.LoadBoard(f'{E}/../issue-240-main-rev7/inspection/final/main.kicad_pcb')
out['outline_rev7'] = outline_of(b7)
anchors7 = {}
for f in b7.GetFootprints():
    if f.GetReference() in ('H1', 'H2', 'H3'):
        anchors7[f.GetReference()] = xy(f.GetPosition())
out['anchors_rev7'] = anchors7
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime/f2-board.json', 'w'))
print('anchors', anchors)
print('rev8 outline pts', len(out['outline_rev8']))
