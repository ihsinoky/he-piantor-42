"""Round 3 candidate: ordered inlet fan, low concentric reserve, raised return fan.

Frozen analytic waypoints are reviewable inputs, not a runtime optimizer dependency.
Fitted contact and continuous service gates determine acceptance.
"""
from common import *
DESIGN=read(HERE/'routes-round3.json')
STORED=DESIGN['turn_centre_y_mm'];RELEASED=STORED-DESIGN['service_travel_mm']
def segments(sgn,i,south=STORED):
 j=13-i if sgn<0 else i
 before=[p[:] for p in DESIGN['before'][j]];after=[p[:] for p in DESIGN['after'][j]]
 before[-1][1]=south;after[0][1]=south
 radius=DESIGN['centre_x_mm']-before[-1][0]
 mid=[sgn*DESIGN['centre_x_mm'],south+radius,before[-1][2]]
 return [[sgn*x,y,z] for x,y,z in before],[[sgn*x,y,z] for x,y,z in after],radius,mid

def route(sgn,i,south=STORED):
 before,after,r,mid=segments(sgn,i,south)
 assert r>=5
 a=rounded(before);b=rounded(after)
 arc=Edge.make_three_point_arc(Vector(*before[-1]),Vector(*mid),Vector(*after[0]))
 return Wire([*a.edges(),arc,*b.edges()])

def points(sgn,i,south=STORED):
 a,b,r,m=segments(sgn,i,south);return a+[m]+b

def make_routes():
 parts={};rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  lengths=[];refs=[];ptsall=[];samples=[];proofs=[];releasedproofs=[]
  for i in range(14):
   path=route(sgn,i);ref=route(sgn,i,RELEASED);p=points(sgn,i)
   direction=np.array(p[1])-np.array(p[0])
   q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*p[0]),z_dir=Vector(*map(float,direction))))),path=path)
   assert q.is_valid and len(q.solids())==1,(side,i,q.is_valid,len(q.solids()))
   assert abs(path.length-ref.length-30.2)<1e-6
   assert path.length+7.3<=200
   parts[f'Wire-{side}-{i+1:02d}']=q
   lengths.append(path.length);refs.append(ref.length);ptsall.append(p)
   samples.append([list(v) for v in path.positions([j/1000 for j in range(1001)])])
   for south,target in [(STORED,proofs),(RELEASED,releasedproofs)]:
    before,after,r,mid=segments(sgn,i,south)
    target.append(dict(before=before,after=after,turn_radius_mm=r,turn_arc_length_mm=math.pi*r))
  rows.append(dict(side=side,conductor_lengths_mm=lengths,dressed_reference_lengths_mm=refs,conductor_waypoints_mm=ptsall,conductor_samples_mm=samples,analytic_segments=proofs,released_analytic_segments=releasedproofs,longest_conductor_mm=max(lengths),longest_dressed_reference_mm=max(refs),margin_to_200_mm=200-max(lengths),per_wire_reserve_mm=[a-b for a,b in zip(lengths,refs)],minimum_radius_mm=min(5,min(r['turn_radius_mm'] for r in proofs)),service_turn_y_mm=[STORED,RELEASED],outlet_axis_qualification=read(HERE/'tail-source.json')['dress_plane_definition'],unmodeled_length_mm=7.3,routed_curve_only=False,terminal_internal_bound_mm_per_end=3.4,terminal_internal_length_verified=True,wing_tail_plus_dress_lead_bound_mm=3.9,main_tail_bound_mm=3.4,route_qualification='Round 3 development candidate: ordered inlet fan, lower concentric connected reserve, independently positioned return fan. Exact all-pair and service audits decide acceptance; search clearance is not certification.'))
 return parts,rows
if __name__=='__main__':
 parts,rows=make_routes();save(RUN/'route-candidate.json',rows)
 for r in rows:print(r['side'],r['longest_conductor_mm'],r['longest_dressed_reference_mm'],min(r['per_wire_reserve_mm']),flush=True)
