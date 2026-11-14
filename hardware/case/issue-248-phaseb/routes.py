"""Dedicated horizontal GH exits, north rise and southern connected R5 reserve."""
from common import *
def points(sgn,i,south):
 # Flatten the low south storage to a single OD1 layer: no OD5 under-Wing pack.
 off=(i-6.5)*.55
 a=math.radians(sgn*120);u=(i-6.5)*1.25
 ep=[sgn*17.102146+u*math.cos(a)+5.55*math.sin(a),42.075001-u*math.sin(a)+5.55*math.cos(a),10.65]
 ap=[ep[0]+11*math.sin(a),ep[1]+11*math.cos(a),10.65]
 return [[sgn*27+u,-35.45,5.75],[sgn*27+u,-29,5.75],[sgn*(7+off),-21,5.75],[sgn*(7+off),-8,17.0],[sgn*(12+off),13,17.0],[sgn*(12+off),31,9.7],[sgn*(12+off),south,9.7],[sgn*(24+off),south,9.7],[sgn*(24+off),27,9.7],ap,ep]
def make_routes():
 parts={};rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  lengths=[];refs=[];ptsall=[];samples=[];slacks=[]
  for i in range(14):
   pts=points(sgn,i,61);q,path=tube(pts,.5);ref=rounded(points(sgn,i,45.9))
   assert q.is_valid and len(q.solids())==1
   parts[f'Wire-{side}-{i+1:02d}']=q
   lengths.append(path.length);refs.append(ref.length);ptsall.append(pts)
   samples.append([[v.X,v.Y,v.Z] for v in path.positions([j/600 for j in range(601)])])
  rows.append(dict(side=side,conductor_lengths_mm=lengths,dressed_reference_lengths_mm=refs,conductor_waypoints_mm=ptsall,conductor_samples_mm=samples,longest_conductor_mm=max(lengths),longest_dressed_reference_mm=max(refs),margin_to_200_mm=200-max(lengths),per_wire_reserve_mm=[a-b for a,b in zip(lengths,refs)],minimum_radius_mm=5,service_turn_y_mm=[61,45.9],outlet_axis_qualification='Wing Z5.75 and Main Z10.65 are nominal dress axes inside drawing-bounded outlets, not dimensioned cavity centres',unmodeled_length_mm=0))
 return parts,rows
if __name__=='__main__':
 parts,rows=make_routes();save(RUN/'route-candidate.json',rows)
 for r in rows:print(r['side'],r['longest_conductor_mm'],r['longest_dressed_reference_mm'],min(r['per_wire_reserve_mm']))
