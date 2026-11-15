"""Separated north-corridor candidate; exact concentric reserve turns, R>=5."""
from common import *
def pack(i):
 p=[]
 for row,count in enumerate((4,3,4,3)):
  for col in range(count):p.append(((col-(count-1)/2)*1.01,(row-1.5)*math.sqrt(3)/2*1.01))
 return p[i]
def segments(sgn,i,south=17.1):
 if sgn<0:i=13-i
 dx,dz=pack(i);x=27+(i-6.5)*1.25;z=4.1+dz
 # Keep the 1.25 mm outlet pitch until south of the north MUX edge, below its
 # fixed Z5.95 underside. Convergence occurs at the central neck, not X27/Y-24.
 entry=[[x,-34.95,5.75],[x,-31.8,5.75],[x,-28.8,5.1],[x,-24.3,5.1],[7+dx,-13.5,z],[7+dx,south-6.55,z]]
 upper=[((j-2)*1.05,-1.05) for j in range(5)]+[((j-2)*1.05,0) for j in range(5)]+[((j-1.5)*1.05,1.05) for j in range(4)]
 off,uz=upper[i];u=(i-6.5)*1.25;a=math.radians(120)
 ep=[17.102146+u*math.cos(a)+5.55*math.sin(a),42.075001-u*math.sin(a)+5.55*math.cos(a),10.65]
 ap=[ep[0]+7*math.sin(a),ep[1]+7*math.cos(a),10.65]
 after=[[20.1-dx,south-6.55,z],[20.1-dx,-9,z],[5+off,-18,z],[5+off,-7,14.8+uz],[17+off,8,14.8+uz],ap,ep]
 entry=[[sgn*x,y,z] for x,y,z in entry];after=[[sgn*x,y,z] for x,y,z in after]
 return entry,after,6.55-dx,[sgn*13.55,south-dx,z]
def route(sgn,i,south=17.1):
 before,after,r,mid=segments(sgn,i,south)
 a=rounded(before);b=rounded(after)
 arc=Edge.make_three_point_arc(Vector(*before[-1]),Vector(*mid),Vector(*after[0]))
 return Wire([*a.edges(),arc,*b.edges()])
def points(sgn,i,south=17.1):
 a,b,r,m=segments(sgn,i,south);return a+[m]+b

def make_routes():
 parts={};rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  lengths=[];refs=[];ptsall=[];samples=[];proofs=[]
  for i in range(14):
   path=route(sgn,i);ref=route(sgn,i,2);p=points(sgn,i)
   direction=np.array(p[1])-np.array(p[0])
   q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*p[0]),z_dir=Vector(*map(float,direction))))),path=path)
   assert q.is_valid and len(q.solids())==1
   parts[f'Wire-{side}-{i+1:02d}']=q
   lengths.append(path.length);refs.append(ref.length);ptsall.append(p)
   samples.append([list(v) for v in path.positions([j/1000 for j in range(1001)])])
   before,after,r,mid=segments(sgn,i)
   proofs.append(dict(before=before,after=after,turn_radius_mm=r,turn_arc_length_mm=math.pi*r))
  rows.append(dict(side=side,conductor_lengths_mm=lengths,dressed_reference_lengths_mm=refs,conductor_waypoints_mm=ptsall,conductor_samples_mm=samples,analytic_segments=proofs,longest_conductor_mm=max(lengths),longest_dressed_reference_mm=max(refs),margin_to_200_mm=200-max(lengths),per_wire_reserve_mm=[a-b for a,b in zip(lengths,refs)],minimum_radius_mm=5,service_turn_y_mm=[17.1,2],outlet_axis_qualification='Wing dress plane Y-34.95, actual housing mouth Y-35.45: 0.50 mm lead included in length qualification; axis Z5.75. Main B1 outlet local v=5.55, axis Z10.65. Individual cavity centres remain nominal.',unmodeled_length_mm=7.3,routed_curve_only=False,terminal_internal_bound_mm_per_end=3.4,terminal_internal_length_verified=True,route_qualification='Development candidate: retained separated outlet lanes through north corridor, below MUX; fan/upper-route collision gate determines acceptance. Concentric R>=5 reserve arcs replace crossing translated equal-radius U turns.'))
 return parts,rows
if __name__=='__main__':
 parts,rows=make_routes();save(RUN/'route-candidate.json',rows)
 for r in rows:print(r['side'],r['longest_conductor_mm'],r['longest_dressed_reference_mm'],min(r['per_wire_reserve_mm']),flush=True)
