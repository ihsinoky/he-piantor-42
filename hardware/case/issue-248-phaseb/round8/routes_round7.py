"""Round-7 diagnostic Z-spread fallback on the frozen round-5 reserve.

The all-contact audit remains binding; this module makes no success claim.
"""
from common import *
DESIGN=read(HERE/'routes-round7-prototype.json')
STORED=17.1;RELEASED=2.0

def row_for(sgn,i):return DESIGN['right'][13-i if sgn<0 else i]
def components(row,travel=0):
 before=[p[:] for p in row['before']];before[-1][1]-=travel
 wa=rounded(before,5.05);R=row['turn_radius_mm'];z=row['turn_z_mm'];y=10.55-travel
 arc=Edge.make_three_point_arc(Vector(*before[-1]),Vector(17.4,y+R,z),Vector(23.95-row['pack_offset_mm'][0],y,z))
 curve=Edge.make_spline([Vector(*v) for v in row['core_control_samples_mm']],tangents=[Vector(*row['core_start_tangent']),Vector(*row['core_end_tangent'])])
 if travel:curve=curve.trim(travel/curve.length,1)
 fan=rounded(row['fan'],5.05)
 return wa,arc,curve,fan

def path_for_row(row,travel=0):
 wa,arc,curve,fan=components(row,travel)
 return Wire([*wa.edges(),arc,curve,*fan.edges()])
def mirror(q,sgn):return q.mirror(Plane.YZ) if sgn<0 else q

def segments(sgn,i,south=STORED):
 row=row_for(sgn,i);a=[v[:] for v in row['before']];travel=STORED-south;a[-1][1]-=travel
 b=[[23.95-row['pack_offset_mm'][0],10.55-travel,row['turn_z_mm']]]+row['fan'];r=row['turn_radius_mm'];mid=[sgn*17.4,10.55-travel+r,row['turn_z_mm']]
 return [[sgn*x,y,z] for x,y,z in a],[[sgn*x,y,z] for x,y,z in b],r,mid

def route(sgn,i,south=STORED):return mirror(path_for_row(row_for(sgn,i),STORED-south),sgn)
def fixed_parts(sgn,i):
 row=row_for(sgn,i);wa,arc,curve,fan=components(row)
 # Preserve every fixed inlet edge except its final straight reserve leg.
 # The returned initial 15.70 mm is straight (roll begins at23 mm) and exceeds
 # moving travel15.10 plus the0.52 mm continuous-envelope endpoint allowance.
 inlet=Wire(list(wa.edges())[:-1]);returnfan=Wire([curve.trim(15.7/curve.length,1),*fan.edges()]);solids=[]
 for path in (inlet,returnfan):
  q=sweep(Face(Wire.make_circle(.5,Plane(origin=path.position_at(0),z_dir=path.tangent_at(0)))),path=path)
  assert q.is_valid and len(q.solids())==1
  solids.append(mirror(q,sgn))
 return solids

def make_routes():
 cert=read(HERE/'curve-certificates-round7.json');assert cert['prototype_sha256']==sha(HERE/'routes-round7-prototype.json') and cert['passed']
 proofs={r['pin']:r for r in cert['strands']};parts={};rows=[]
 center=DESIGN['core_centerline_waypoints_mm'];p0,p1,p2=map(np.array,center[:3]);u=(p0-p1)/np.linalg.norm(p0-p1);v=(p2-p1)/np.linalg.norm(p2-p1);theta=math.acos(float(np.clip(np.dot(u,v),-1,1)))
 straight_lower=np.linalg.norm(p1-p0)-DESIGN['core_centerline_radii_mm'][1]/math.tan(theta/2)-.4
 assert straight_lower>15.7
 for side,sgn in [('left',-1),('right',1)]:
  lengths=[];refs=[];samples=[];analytic=[];released=[];waypoints=[]
  for i in range(14):
   row=row_for(sgn,i);path=route(sgn,i);ref=route(sgn,i,RELEASED)
   assert abs(path.length-row['routed_length_mm'])<1e-6
   assert abs(path.length-ref.length-30.2)<1e-6
   assert path.length+7.3<=200
   q=sweep(Face(Wire.make_circle(.5,Plane(origin=path.position_at(0),z_dir=path.tangent_at(0)))),path=path)
   assert q.is_valid and len(q.solids())==1,(side,i,q.is_valid,len(q.solids()))
   parts[f'Wire-{side}-{i+1:02d}']=q;lengths.append(path.length);refs.append(ref.length)
   samples.append([[sgn*x,y,z] for x,y,z in row['samples_mm']])
   proof=proofs[row['pin']]
   for travel,target in [(0,analytic),(15.1,released)]:
    a=[v[:] for v in row['before']];a[-1][1]-=travel
    target.append(dict(before=[[sgn*x,y,z] for x,y,z in a],after=[[sgn*x,y,z] for x,y,z in row['fan']],corner_radius_mm=5.05,turn_radius_mm=row['turn_radius_mm'],turn_arc_length_mm=math.pi*row['turn_radius_mm'],round7_curve_certificate=proof,curve_trimmed_length_mm=travel,return_initial_straight_lower_bound_mm=float(straight_lower)))
   aa,bb,r,mid=segments(sgn,i);waypoints.append(aa+[mid]+bb)
   print(side,i+1,path.length+7.3,'valid volume error',abs(q.volume-path.length*math.pi*.25),flush=True)
  rows.append(dict(side=side,conductor_lengths_mm=lengths,dressed_reference_lengths_mm=refs,conductor_waypoints_mm=waypoints,conductor_samples_mm=samples,analytic_segments=analytic,released_analytic_segments=released,longest_conductor_mm=max(lengths),longest_dressed_reference_mm=max(refs),margin_to_200_mm=200-max(lengths),per_wire_reserve_mm=[a-b for a,b in zip(lengths,refs)],minimum_radius_mm=min(5.035,min(p['minimum_radius_lower_bound_mm'] for p in proofs.values())),service_turn_y_mm=[STORED,RELEASED],outlet_axis_qualification=read(HERE/'tail-source.json')['dress_plane_definition'],unmodeled_length_mm=7.3,routed_curve_only=False,terminal_internal_bound_mm_per_end=3.4,terminal_internal_length_verified=True,wing_tail_plus_dress_lead_bound_mm=3.9,main_tail_bound_mm=3.4,route_qualification='Round7 Z-spread nested-reserve diagnostic fallback. Existing round5 reserve lanes and connected30.20 mm travel; ordered inlet rank and transported return frame. Exact fitted/service gates decide acceptance.'))
 return parts,rows
