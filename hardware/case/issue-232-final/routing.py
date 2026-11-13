"""Rev.4 route integrated around the unchanged D-037 rack.
Fourteen individual OD<=1 wires can be dressed in 3/4/4/3 rows at
Y=-1.5,-.5,.5,1.5, X=-1,0,1 (outer rows), X=-1.5,-.5,.5,1.5
(inner rows). Every wire lies inside both a diameter5 circle and a Y±2 strip.
This is a controlled flat pack, not a round jacket forced through a narrow gap.
"""
from geometry import *

def wing_points(sgn,width):
 return [[sgn*27,-24,5],[sgn*7,-16,5],[sgn*7,-19,14],[sgn*7,-19,28.5],[sgn*width,-19,28.5],[sgn*width,10,28.5],[sgn*(7+29*8.5/62),10,28.5],[sgn*15.5,43,28.5],[sgn*15.5,43,18.5]]

def flat_bundle(points):
 s,path=tube(points,2.5)
 # Locally tighten the conservative round envelope to the proven 14-wire pack.
 # Expanding outside this band is an envelope allowance, not wire movement.
 x=points[1][0]
 for north in (True,False):
  wires=[]
  for z,half in [(16,2.5),(18,2),(24.5,2),(26.5,2.5)]:
   ys=(-25,-19-half) if north else (-19+half,-13)
   g=box(x-3,ys[0],x+3,ys[1]);wires.append(Wire.make_polygon([Vector(a,b,z) for a,b in list(g.exterior.coords)[:-1]],close=True))
  s=s.cut(Solid.make_loft(wires,ruled=True))
 assert s.is_valid and len(s.solids())==1
 return s,path

def route(side,sgn,target=160):
 exits=[];fan_lengths=[]
 for i in range(14):
  wp=[[sgn*27+(i-6.5)*1.25,-35.45,8.4],[sgn*27+(i-6.5)*1.25,-31.5,8.4],[sgn*27,-24,5],[sgn*14,-18.8,5]]
  wire,path=tube(wp,.5);exits.append(wire);fan_lengths.append(path.length)
 common=math.dist([sgn*27,-24,5],[sgn*14,-18.8,5])
 def length(width):return rounded(wing_points(sgn,width)).length+max(fan_lengths)-common
 lo,hi=24.,60.
 assert length(lo)<target<length(hi)
 for i in range(45):
  mid=(lo+hi)/2
  if length(mid)<target:lo=mid
  else:hi=mid
 width=(lo+hi)/2;pts=wing_points(sgn,width);bundle,path=flat_bundle(pts);cutter,_=tube(pts,3.)
 reference=[[sgn*27,-24,5],[sgn*7,-16,5],[sgn*7,-19,14],[sgn*7,-19,28.5],[sgn*15.5,43,28.5],[sgn*15.5,43,18.5]]
 ref=rounded(reference).length+max(fan_lengths)-common
 data=dict(side=side,planning_length_mm=target,longest_connected_conductor_mm=length(width),study_reference_longest_mm=123.395,integrated_reference_longest_mm=ref,service_stored_mm=target-ref,waypoints_mm=pts,detour_width_mm=width,bundle_diameter_mm=5,rack_flat_pack_xy_mm=[5,4],rack_passage_center_y_mm=-19,rack_edge_clearance_mm=.5,minimum_bend_radius_mm=5,compatible_planning_range_mm=[153.4,170],length_definition='Longest conductor at #235 exit-to-Main datums. All14 wires connected; shared fanout/bundle geometry is not added twice.',route_delta='Floor point (±7,−16,5) retained; rise leans to (±7,−19,14), vertical through the existing rack slot, then cruises atZ28.5. Main approach points unchanged. Flat4mm Y wire pack clears the unmodified5mm rack gap by0.5 each side.')
 return bundle,Compound(children=exits),cutter,data
