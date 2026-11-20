import json
from shapely.geometry import Polygon, LineString, MultiLineString
m = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/measured.json'))
wing = Polygon(m['wing_left'])
def intervals(Y):
    inter = LineString([(-200, Y), (0, Y)]).intersection(wing)
    out = []
    geoms = [inter] if inter.geom_type == 'LineString' else (list(inter.geoms) if hasattr(inter, 'geoms') else [])
    for g in geoms:
        if g.geom_type == 'LineString' and g.length > 0: out.append((round(g.bounds[0],3), round(g.bounds[2],3)))
        elif g.geom_type == 'Point': out.append((round(g.x,3), round(g.x,3)))
    return out
for Y in (44, 46, 48, 50, 52, 54, 58, 62, 66):
    print(f"Y={Y}: wing intervals {intervals(Y)}")
# wing boundary vertices within the box X[-40,-20], Y[40,70]
pts = [(round(x,3), round(y,3)) for x, y in wing.exterior.coords if -42 <= x <= -18 and 38 <= y <= 72]
print('wing boundary near dent:', pts)
