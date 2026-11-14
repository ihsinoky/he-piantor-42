"""Dedicated horizontal GH exits, north rise and southern connected R5 reserve."""
from common import *
def points(sgn,i,south):
 # Four-row pack stays below Main; only the separated entry crosses Wing corridor.
 pack=[]
 for row,count in enumerate((4,3,4,3)):
  for col in range(count):pack.append(((col-(count-1)/2)*1.01,(row-1.5)*math.sqrt(3)/2*1.01))
 dx,dz=pack[i]
 upper=[((j-2)*1.05,-1.05) for j in range(5)]+[((j-2)*1.05,0) for j in range(5)]+[((j-1.5)*1.05,1.05) for j in range(4)]
 off,uz=upper[i]
 a=math.radians(sgn*120);u=(i-6.5)*1.25
 ep=[sgn*17.102146+u*math.cos(a)+5.55*math.sin(a),42.075001-u*math.sin(a)+5.55*math.cos(a),10.65]
 ap=[ep[0]+7*math.sin(a),ep[1]+7*math.cos(a),10.65]
 return [[sgn*27+u,-35.45,5.75],[sgn*27+u,-31.5,5.75],[sgn*(27+dx),-24,4.9+dz],[sgn*(7+dx),-16,4.9+dz],[sgn*(7+dx),south,4.9+dz],[sgn*(19+dx),south,4.9+dz],[sgn*(19+dx),0,4.9+dz],[sgn*(5+off),-18,4.9+dz],[sgn*(5+off),-7,14.8+uz],[sgn*(17+off),8,14.8+uz],ap,ep]
def make_routes():
 parts={};rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  lengths=[];refs=[];ptsall=[];samples=[];slacks=[]
  for i in range(14):
   pts=points(sgn,i,22.1);q,path=tube(pts,.5);ref=rounded(points(sgn,i,7))
   assert q.is_valid and len(q.solids())==1
   parts[f'Wire-{side}-{i+1:02d}']=q
   lengths.append(path.length);refs.append(ref.length);ptsall.append(pts)
   samples.append([[v.X,v.Y,v.Z] for v in path.positions([j/600 for j in range(601)])])
  rows.append(dict(side=side,conductor_lengths_mm=lengths,dressed_reference_lengths_mm=refs,conductor_waypoints_mm=ptsall,conductor_samples_mm=samples,longest_conductor_mm=max(lengths),longest_dressed_reference_mm=max(refs),margin_to_200_mm=200-max(lengths),per_wire_reserve_mm=[a-b for a,b in zip(lengths,refs)],minimum_radius_mm=5,service_turn_y_mm=[22.1,7],outlet_axis_qualification='Wing Z5.75 and Main Z10.65 are nominal dress axes inside drawing-bounded outlets, not dimensioned cavity centres',unmodeled_length_mm=None,routed_curve_only=True,terminal_internal_bound_mm_per_end=5.7,terminal_internal_length_verified=False))
 return parts,rows
if __name__=='__main__':
 parts,rows=make_routes();save(RUN/'route-candidate.json',rows)
 for r in rows:print(r['side'],r['longest_conductor_mm'],r['longest_dressed_reference_mm'],min(r['per_wire_reserve_mm']))
