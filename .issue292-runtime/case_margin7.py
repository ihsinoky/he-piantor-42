import json
from shapely.geometry import Polygon
w = json.load(open('.issue292-runtime/wing6-assembly.json'))
wing6 = Polygon(w['wing6_assembly'])
r10 = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/rev10-assembly.json'))
main = Polygon(r10['rev10_assembly'])
inter = main.intersection(wing6)
print('intersection type:', inter.geom_type, 'area:', round(inter.area, 3))
geoms = list(inter.geoms) if hasattr(inter, 'geoms') else [inter]
for g in geoms:
    print(' piece bounds:', [round(v, 2) for v in g.bounds], 'area', round(g.area, 3))
    print('  coords:', [(round(x, 2), round(y, 2)) for x, y in g.exterior.coords])
