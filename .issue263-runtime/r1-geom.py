"""R1 geometry: per-variant tab overlap + notch region in Wing board frame.
Wing->case: rotate(outline - jw_pos, deg) + env_centre. Main->case: (-100,-70).
Clearance class: 0.50 mm (case pocket rule)."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
from shapely.ops import unary_union

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
wj = json.load(open(f'{RT}/r1-wings.json'))
bj = json.load(open(f'{RT}/f2-board.json'))
CLR = 0.50

def to_case(pts):
    return [(x - 100.0, y - 70.0) for x, y in pts]

old_poly = Polygon(to_case(bj['outline_rev7']))
new_poly = Polygon(to_case(bj['outline_rev8']))
tab = new_poly.difference(old_poly)
print(f'tab area {tab.area:.1f} mm2, bounds {[round(v,2) for v in tab.bounds]}', flush=True)

result = {}
for name, env, deg in (('wing-rev5-16mm-right', (27.0, -37.5), -30.5),
                       ('wing-rev5-16mm-left', (-27.0, -37.5), 30.5),
                       ('wing-rev5-17mm-right', (27.0, -37.5), -30.5),
                       ('wing-rev5-17mm-left', (-27.0, -37.5), 30.5)):
    d = wj[name]
    jx, jy = d['jw_pos']
    base = Polygon([(x - jx, y - jy) for x, y in d['outline']])
    wing = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
    overlap = wing.intersection(tab)
    notch_case = wing.intersection(tab.buffer(CLR))
    # inverse transform to board frame
    nb = shp_translate(shp_rotate(shp_translate(notch_case, xoff=-env[0], yoff=-env[1]),
                                  -deg, origin=(0, 0)), xoff=jx, yoff=jy)
    bite = 0.0
    if not overlap.is_empty:
        wb = wing.boundary
        for i in range(401):
            pt = wb.interpolate(i / 400, normalized=True)
            if tab.contains(pt):
                bite = max(bite, pt.distance(old_poly))
    polys = [nb] if nb.geom_type == 'Polygon' else list(nb.geoms)
    result[name] = dict(overlap_area=overlap.area, notch_area=notch_case.area, max_bite=bite,
                        notch_board=[[(round(x, 3), round(y, 3)) for x, y in list(poly.exterior.coords)]
                                     for poly in polys],
                        notch_case_bounds=[round(v, 2) for v in notch_case.bounds])
    print(f"{name}: overlap {overlap.area:.1f} mm2, notch {notch_case.area:.1f} mm2, "
          f"max bite {bite:.2f} mm, notch board bounds "
          f"{[round(v,2) for v in nb.bounds]}", flush=True)
json.dump(result, open(f'{RT}/r1-notch.json', 'w'), indent=1)
print('done')
