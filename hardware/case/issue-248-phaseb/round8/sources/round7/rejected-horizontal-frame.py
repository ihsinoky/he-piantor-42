"""Cheap centreline-only screen: split crossing into low/high two-row ribbons.

Round-5 reserve stays in its exact fourteen-lane envelope. Only the fixed
approaches repack around it; the turn and travel stay connected and unchanged.
"""
from derive_routes_round7 import *
def derive():
 r=read(HERE/'round5/routes-round5.json');pm=read(HERE/'round5/pinmap-round5.json');right=[w for w in pm['wires'] if w['side']=='right']
 pack=sorted([(a[-1][0]-10.85,a[-1][2]-4.1) for a in r['before']],reverse=True)
 zz0=5.805
 bb=np.array([[19,-13.5,zz0],[4.5,-22,zz0],[4.5,0,10.5],[17,8,10.5]],float)
 t=(bb[-1]-bb[-2]);t/=np.linalg.norm(t);cut=bb[-1]-6*t;bb[-1]=cut
 core=rounded_variable(bb,[0,9,9,0]);L=core.length;npts=max(1001,int(L/.05)+1);f=np.linspace(0,1,npts)
 ps=np.array([tuple(core.position_at(float(t))) for t in f]);ts=np.array([tuple(core.tangent_at(float(t))) for t in f])
 # Horizontal lateral frame avoids consuming the board-to-plate height with
 # the 7-wide dimension. This is a geometric roll, not strand permutation.
 nn=np.c_[ts[:,1],-ts[:,0],np.zeros(len(ts))];nn/=np.linalg.norm(nn,axis=1)[:,None];zz=np.cross(nn,ts)
 rows=[]
 for i,(dx,dz) in enumerate(pack):
  flat=(3-(i%7))*1.01;level=i//7;zl=2.55+level*1.01;zh=5.30+level*1.01;z=4.1+dz;ep=right[i]['main_endpoint_mm'];wx=right[i]['wing_endpoint_mm'][0]
  before=[[wx,-34.95,5.75],[wx,-31.8,5.75],[wx,-24.3,zl],[18+flat,-17,zl],[10.85+dx,-9.5,z],[10.85+dx,10.55,z]]
  wa=rounded(before,5.05);R=6.55-dx
  arc=Edge.make_three_point_arc(Vector(*before[-1]),Vector(17.4,10.55+R,z),Vector(23.95-dx,10.55,z))
  q=ps+flat*nn+(zh-zz0)*zz
  start=q[0];lead=start-4*ts[0]
  prefix=[[23.95-dx,10.55,z],[23.95-dx,-5,z],lead.tolist(),start.tolist()]
  wp=rounded(prefix,5.05)
  inds=np.unique(np.r_[np.arange(0,len(q),4),len(q)-1]);curve=Edge.make_spline([Vector(*v) for v in q[inds]],tangents=[Vector(*ts[0]),Vector(*ts[-1])])
  target=nn[-1];b4=np.array([17,8,10.5])+flat*target+(level-.5)*1.01*np.array([0,0,1]);ap=np.array(ep)+np.array([7*math.sin(math.radians(120)),7*math.cos(math.radians(120)),0])
  fan=[q[-1].tolist(),b4.tolist(),ap.tolist(),ep];wf=rounded(fan,5.05)
  path=Wire([*wa.edges(),arc,*wp.edges(),curve,*wf.edges()]);minr=curvature(curve)
  rr=dict(side='right',pin=i+1,pack_offset_mm=[dx,dz],before=before,turn_radius_mm=R,turn_z_mm=z,prefix=prefix,core_control_samples_mm=q[inds].tolist(),core_start_tangent=ts[0].tolist(),core_end_tangent=ts[-1].tolist(),fan=fan,core_length_mm=curve.length,core_minimum_sampled_curvature_radius_mm=minr,routed_length_mm=path.length,finished_length_mm=path.length+7.3,minimum_bend_radius_mm=min(5.05,R,minr),samples_mm=sample(path,step=.25).tolist())
  rows.append(rr);print(i+1,'length',path.length+7.3,'R',minr,flush=True)
 d=dict(candidate='Low/high two-row fixed crossing; immutable fourteen-lane horizontal nested reserve; horizontal lateral return frame.',round5_routes_sha256=sha(HERE/'round5/routes-round5.json'),stored_tangent_y_mm=10.55,released_tangent_y_mm=-4.55,service_translation_mm=15.1,reserve_mm=30.2,tail_mm=7.3,right=rows)
 contacts=[]
 for i in range(14):
  for j in range(i+1,14):
   a=np.array(rows[i]['samples_mm']);b=np.array(rows[j]['samples_mm']);ds,ii=cKDTree(b).query(a);k=int(ds.argmin())
   if ds[k]<1.005:contacts.append(dict(a=i+1,b=j+1,sampled_centerline_distance_mm=float(ds[k]),point_a_mm=a[k].tolist(),point_b_mm=b[ii[k]].tolist()))
 d['sampled_pairs_below_1_005_mm']=contacts;d['longest_finished_mm']=max(w['finished_length_mm'] for w in rows);d['minimum_sampled_radius_mm']=min(w['minimum_bend_radius_mm'] for w in rows)
 save(HERE/'routes-round7-stacked-prototype.json',d);print('Candidate',d['longest_finished_mm'],d['minimum_sampled_radius_mm'],'pairs',len(contacts),flush=True)
if __name__=='__main__':derive()
