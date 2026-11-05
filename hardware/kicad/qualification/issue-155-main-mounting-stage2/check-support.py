"""Planar support screening, not a structural or 3D qualification."""
from common import *
from shapely.geometry import MultiPoint,Point
from shapely.ops import nearest_points
s=json.loads((E/'inspection/final/snapshot.json').read_text());index={c['ref']:c for c in s['components']}
holes=[index['H'+str(i)]['position'] for i in range(1,5)];hull=MultiPoint(holes).convex_hull
rows=[]
for ref in ['J1','J2']:
 xy=index[ref]['position'];point=Point(xy);nearest=nearest_points(hull,point)[0]
 rows.append(dict(ref=ref,position_mm=xy,inside_support_polygon=hull.covers(point),distance_outside_support_polygon_mm=point.distance(hull),nearest_support_polygon_point_mm=[nearest.x,nearest.y],meaning='Footprint origin only, not actual insertion load point or connector full volume'))
assert all(not r['inside_support_polygon'] for r in rows)
save(E/'support-screening.json',dict(utc=now(),support_polygon_absolute_xy_mm=list(map(list,hull.exterior.coords)),connector_origins=rows,board_thickness_mm=1.2,head_washer_boss_max_diameter_mm=4.5,reservation_diameter_mm=5.0,nominal_radial_tolerance_budget_mm=.25,head_to_board_minimum_edge_mm=.75,h4_nominal_head_to_assumed_gh_service_rectangle_mm=.75,h4_phi6_driver_to_assumed_service_rectangle_mm=0,qualification='Geometric screening only. No screw/head/washer/boss/driver/plug 3D models, laminate modulus, insertion force, fastener preload or bench test provided. Deflection, strength, solder strain and full tool/solder/boss clearance remain open.',required_validation=['Use insulating spacers/washer, M2 through screw, no countersink; choose screw length/torque and tolerance stack','Support USB/GH during insertion; evaluate additional insulated support that clears copper/solder and TP access','Check H4 driver with GH harness removed and actual plug/cable models','Verify underside J1 solder fillet clearance and stand-off height; no boss on POFV/pads','Confirm 1.2mm board deflection and joint strain with actual connector insertion/extraction loads']))
print('Connector origins outside support polygon:',[(r['ref'],round(r['distance_outside_support_polygon_mm'],3)) for r in rows])
