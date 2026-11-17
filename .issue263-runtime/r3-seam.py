"""R3 seam verification: FINAL notched Wing outlines vs AS-BUILT Main Rev.8
outline at the fitted poses (F2 transforms): overlap must be 0 and the
board-to-board distance >= 0.50 mm."""
import pcbnew as p, json
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union, polygonize
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
from pathlib import Path
E = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation')
RT = Path('/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime')

def xy(v):
    return [p.ToMM(v.x), p.ToMM(v.y)]

def outline_of(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            segs.append(LineString([xy(d.GetStart()), xy(d.GetEnd())]))
    polys = list(polygonize(unary_union(segs)))
    polys.sort(key=lambda q: -q.area)
    return [list(c) for c in polys[0].exterior.coords]

def jw_of(board):
    for f in board.GetFootprints():
        if f.GetReference() == 'J_WING':
            return xy(f.GetPosition())
    raise KeyError('J_WING')

mb = p.LoadBoard(str(E / 'main-rev8' / 'main.kicad_pcb'))
main_poly = Polygon([(x - 100.0, y - 70.0) for x, y in outline_of(mb)])
out = {}
for pitch in (17, 16):
    for side, deg, env in (('right', -30.5, (27.0, -37.5)), ('left', 30.5, (-27.0, -37.5))):
        name = f'wing-rev5-{pitch}mm-{side}'
        b = p.LoadBoard(str(E / name / 'main.kicad_pcb'))
        jx, jy = jw_of(b)
        base = Polygon([(x - jx, y - jy) for x, y in outline_of(b)])
        wing = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
        ov = wing.intersection(main_poly).area
        dist = wing.distance(main_poly)
        out[f'{pitch}{side[0].upper()}'] = dict(overlap_mm2=round(ov, 6), distance_mm=round(dist, 4))
        print(f'{name}: overlap {ov:.6f} mm2, distance {dist:.4f} mm', flush=True)
json.dump(out, open(RT / 'r3-seam.json', 'w'), indent=2)
print('done')
