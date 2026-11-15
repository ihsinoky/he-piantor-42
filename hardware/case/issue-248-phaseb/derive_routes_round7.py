"""Stage-0 centreline prototype for the nested-U / Z-spread fallback.

No strand solids. Full-width twist rejected by fixed envelope. A compact
parallel ribbon follows the reserve and the return hairpin; its fixed fan
frame is aligned by a sub-90-degree roll, not a second strand permutation.
"""
from ribbon_geometry_round7 import *
from scipy.spatial import cKDTree
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.gp import gp_Pnt,gp_Vec
from metrology import analytic

def sample(w,step=.22):
 return np.array([tuple(v) for v in w.positions(np.linspace(0,1,max(3,int(w.length/step)+1)).tolist())])
def curvature(e,n=1001):
 c=BRepAdaptor_Curve(e.wrapped);rs=[]
 for u in np.linspace(c.FirstParameter(),c.LastParameter(),n):
  p=gp_Pnt();v=gp_Vec();a=gp_Vec();c.D2(float(u),p,v,a)
  v=np.array([v.X(),v.Y(),v.Z()]);a=np.array([a.X(),a.Y(),a.Z()]);den=np.linalg.norm(np.cross(v,a))
  if den>1e-9:rs.append(np.linalg.norm(v)**3/den)
 return min(rs) if rs else 1e9

def derive():
 r=read(HERE/'round5/routes-round5.json');pm=read(HERE/'round5/pinmap-round5.json');right=[w for w in pm['wires'] if w['side']=='right']
 # Reuse the same fourteen reserve lanes, within the frozen channel envelope.
 pack=[(a[-1][0]-10.85,a[-1][2]-4.1) for a in r['before']]
 pack=sorted(pack);pack=list(reversed(pack))
 a=np.array(r['before']).mean(axis=0);b=np.array(r['after']).mean(axis=0);z0=4.1
 b[:3,2]=z0;b[1,1]=-11;b[2,1]=-20.5;b[3,1]=-3
 # Central return geometry enlarged only enough to retain R>=5 at the edge
 # of a true parallel bundle. Fixed bodies are never relieved to fit it.
 cut=b[4]-8*(b[4]-b[3])/np.linalg.norm(b[4]-b[3]);bb=np.vstack([b[:4],cut])
 core=rounded_variable(bb,[0,8.5,8.5,8.5,0]);L=core.length
 npts=max(1001,int(L/.05)+1);f=np.linspace(0,1,npts);ps=np.array([tuple(core.position_at(float(t))) for t in f]);ts=np.array([tuple(core.tangent_at(float(t))) for t in f]);ns=[np.array([-1.,0,0])]
 for v,w in zip(ts[:-1],ts[1:]):
  axis=np.cross(v,w);sin=np.linalg.norm(axis);cos=np.dot(v,w)
  ns.append(ns[-1] if sin<1e-10 else Rotation.from_rotvec(axis/sin*math.atan2(sin,cos)).apply(ns[-1]))
 ns=np.array(ns);bs=np.cross(ns,ts);target=np.array([ts[-1,1],-ts[-1,0],0]);angle=math.atan2(np.dot(np.cross(ns[-1],target),ts[-1]),np.dot(ns[-1],target))
 s=f*L;phase=np.clip((s-23)/(L-23),0,1);phase=phase**3*(10-15*phase+6*phase**2);roll=angle*phase
 nn=np.cos(roll)[:,None]*ns+np.sin(roll)[:,None]*np.cross(ts,ns);zz=np.cross(nn,ts)
 rows=[];parts=[]
 for i,(dx,dz) in enumerate(pack):
  ep=right[i]['main_endpoint_mm'];wx=right[i]['wing_endpoint_mm'][0];z=z0+dz
  before=[[wx,-34.95,5.75],[wx,-31.8,5.75],[wx,-24.3,z],[10.85+dx,-13.5,z],[10.85+dx,10.55,z]]
  wa=rounded(before,5.05);R=6.55-dx
  arc=Edge.make_three_point_arc(Vector(*before[-1]),Vector(17.4,10.55+R,z),Vector(23.95-dx,10.55,z))
  q=ps+dx*nn+dz*zz
  # Sample the parallel arcs plus smooth fixed roll, then interpolate at a
  # bounded 0.20 mm pitch; endpoint tangents are explicitly constrained.
  inds=np.unique(np.r_[np.arange(0,len(q),4),len(q)-1]);curve=Edge.make_spline([Vector(*v) for v in q[inds]],tangents=[Vector(*ts[0]),Vector(*ts[-1])])
  start=q[-1];b4=b[4]+dx*target+np.array([0,0,dz]);ap=np.array(ep)+np.array([7*math.sin(math.radians(120)),7*math.cos(math.radians(120)),0])
  fan=[start.tolist(),b4.tolist(),ap.tolist(),ep];wf=rounded(fan,5.05)
  path=Wire([*wa.edges(),arc,curve,*wf.edges()]);minr=curvature(curve)
  rr=dict(side='right',pin=i+1,pack_offset_mm=[dx,dz],before=before,turn_radius_mm=R,turn_z_mm=z,core_control_samples_mm=q[inds].tolist(),core_start_tangent=ts[0].tolist(),core_end_tangent=ts[-1].tolist(),fan=fan,core_length_mm=curve.length,core_minimum_sampled_curvature_radius_mm=minr,routed_length_mm=path.length,finished_length_mm=path.length+7.3,minimum_bend_radius_mm=min(5.05,R,minr),samples_mm=sample(path).tolist())
  rows.append(rr);parts.append(path)
  print(i+1,'length',path.length+7.3,'R',minr,flush=True)
 d=dict(candidate='Nested horizontal U with Z-spread in the existing round-5 fourteen-lane reserve; order-preserving transported return ribbon and corrected Main fan.',round5_routes_sha256=sha(HERE/'round5/routes-round5.json'),stored_tangent_y_mm=10.55,released_tangent_y_mm=-4.55,service_translation_mm=15.1,reserve_mm=30.2,fixed_roll_degrees=angle*180/math.pi,roll_start_after_reserve_mm=23,roll_end_after_reserve_mm=L,core_centerline_waypoints_mm=bb.tolist(),core_centerline_radii_mm=[0,8.5,8.5,8.5,0],tail_mm=7.3,right=rows)
 # Dense sample screen is a cheap rejection test; solids decide acceptance.
 contacts=[]
 for i in range(14):
  for j in range(i+1,14):
   a=np.array(rows[i]['samples_mm']);b=np.array(rows[j]['samples_mm']);ds,ii=cKDTree(b).query(a);k=int(ds.argmin())
   if ds[k]<1.01:contacts.append(dict(a=i+1,b=j+1,sampled_centerline_distance_mm=float(ds[k]),point_a_mm=a[k].tolist(),point_b_mm=b[ii[k]].tolist()))
 d['sampled_pairs_below_1_01_mm']=contacts;d['longest_finished_mm']=max(w['finished_length_mm'] for w in rows);d['minimum_sampled_radius_mm']=min(w['minimum_bend_radius_mm'] for w in rows)
 save(HERE/'routes-round7-prototype.json',d)
 print('Candidate',d['longest_finished_mm'],d['minimum_sampled_radius_mm'],'pairs',len(contacts),'roll',d['fixed_roll_degrees'],flush=True)
if __name__=='__main__':derive()
