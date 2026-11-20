import json
from shapely.geometry import Polygon, LineString
from shapely.ops import nearest_points
r10 = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/rev10-assembly.json'))
print('rev10-assembly keys:', list(r10.keys())[:10] if isinstance(r10, dict) else type(r10))
