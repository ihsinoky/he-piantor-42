"""B2 feasibility envelopes, not footprints or production CAD. Run in CAD venv."""
import os,sys,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime';OUT=HERE/'b2';OUT.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(RUN);sys.dont_write_bytecode=True
sys.path.insert(0,str(RUN/'caddeps'))
from build123d import Solid,Plane,Shape,Compound,Face,Wire,Axis,extrude,import_step,export_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
import sexpdata as sx

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone();return Shape.cast(op.Shape())
def prism(g,z,h):
 # Geometry is a deliberate occupied envelope; round bend outlines are sampled
 # at <=0.25 degree for illustration; analytical rectangle bounds drive STEP. Height support is exact.
 w=Wire.make_polygon([(x,y,z) for x,y in list(g.exterior.coords)[:-1]],close=True)
 return extrude(Face(w),amount=h,dir=(0,0,1))
def bb(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def xy(p,u,v):return [p['x']+u*p['u'][0]+v*p['v'][0],p['y']+u*p['u'][1]+v*p['v'][1]]
def pose(x,y,a):
 a=math.radians(a);return dict(x=x,y=y,u=[math.cos(a),-math.sin(a)],v=[math.sin(a),math.cos(a)])
def moved(p,du):
 x,y=xy(p,du,0);return dict(p,x=x,y=y)
def placed(g,p):return Polygon([xy(p,u,v) for u,v in g.exterior.coords])
D=dict(pitch=1.2,header_width=10.2,header_depth=4.5,housing_width=8.54,housing_depth=3.97,housing_height=1.4,mated_depth=4.83,mated_height=1.65,wire_max_OD=.7,first_straight=2.,first_bend_radius=5.,first_bend_angle_deg=30.,after_bend_straight=2.,body_pair_gap=2.,allowance=.5)
# Keep Phase A floor, free gap, Hall envelope, screw/root and stack.
B=max(2+1.65+.5+.5,5.9,6.7);plate=B+6.2
roofpath=HERE/'b0/roof-b0.step';roofhash=sha(roofpath);roof=import_step(roofpath)
assert len(roof.solids())==8
# Actual imported underside-face clipping, same signed vertical definition as B1.
planes=[]
for f in roof.faces():
 n=f.normal_at()
 if n.Z>=-.9:continue
 c=f.center();m=n.Y/n.Z
 planes.append((c.Z+m*c.Y,m,extrude(f.translate((0,0,50)),amount=100,dir=(0,0,-1))))
def gap(s):
 values=[]
 for a,m,clip in planes:
  q=common(s,clip)
  if q.solids():values.append(a-q.rotate(Axis.X,math.degrees(math.atan(m))).bounding_box().max.Z*math.sqrt(1+m*m))
 return min(values)
# Full-height bound for wire exit: axis height is not dimensioned in Molex SD.
# Therefore wire dress is bounded over entire mated Z0..1.65, rather than inventing outlet Z.
def envelope(p,sign,z,bottom=False):
 body=box(-5.1,-1.6,5.1,3.23)
 paths=[]
 for i in range(7):
  u=(i-3)*1.2;v=3.23
  pts=[(u,v),(u,v+2)]
  for j in range(1,121):
   t=math.radians(30*j/120);pts.append((u+sign*5*(1-math.cos(t)),v+2+5*math.sin(t)))
  q=pts[-1];pts.append((q[0]+sign*2*math.sin(math.pi/6),q[1]+2*math.cos(math.pi/6)))
  paths.append(LineString(pts).buffer(.35,resolution=32))
 turn=5*(1-math.cos(math.pi/6))+2*math.sin(math.pi/6)
 wire_rect=box(-3.95+(0 if sign==1 else -turn),2.88,3.95+(turn if sign==1 else 0),5.23+5*math.sin(math.pi/6)+2*math.cos(math.pi/6)+.35)
 local=unary_union([body,wire_rect]);world=placed(local,p)
 s=prism(world,z-1.65 if bottom else z,1.65)
 return s,world,body,paths
# Frozen Main placements supply zone centers and rotation; pair centers +/-6.1 along pin row.
board=ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'
S=sx.Symbol;poses={};old_courts={}
for f in sx.loads(board.read_text()):
 if not isinstance(f,list) or not f or f[0]!=S('footprint'):continue
 ref=next((v[2] for v in f if isinstance(v,list) and len(v)>2 and v[0]==S('property') and v[1]=='Reference'),None)
 if ref not in ('J2','J3'):continue
 at=next(v for v in f if isinstance(v,list) and v and v[0]==S('at'));poses[ref]=pose(at[1]-100,at[2]-70,at[3])
 pts=[]
 for v in f:
  if isinstance(v,list) and v and v[0]==S('fp_line') and [S('layer'),'F.CrtYd'] in v:
   pts += [q[1:] for q in v if isinstance(q,list) and q and q[0] in (S('start'),S('end'))]
 old_courts[ref]=[min(x[0] for x in pts),min(x[1] for x in pts),max(x[0] for x in pts),max(x[1] for x in pts)]
base=json.loads((ROOT/'hardware/case/issue-228-final/17mm/dimensions.json').read_text())
mainboard=prism(Polygon(base['boards']['main']),B,1.2);mainboard.label='Main-Rev7-outline-reference-new-Z'
main=[mainboard];nominal=[];results={};plot={};placement={}
for ref,p in poses.items():
 for idx,sign in [('A',-1),('B',1)]:
  name=ref+'-'+idx;p1=moved(p,sign*6.1)
  s,g,body,paths=envelope(p1,sign,B+1.2);s.label=name+'-10.2x4.83x1.65-wire-exit-band-R5-30deg'
  export_step(s,OUT/(name+'-ezmate-envelope.step'));main.append(s);nominal.append(s)
  results[name]=dict(pose=p1,mount_z=B+1.2,bounds_mm=bb(s),vertical_gap_to_B0_mm=gap(s),Common_mm3=abs(common(roof,s).volume),true_BRep_distance_mm=roof.distance_to(s),gap_at_B1_board_Z_mm=gap(s.translate((0,0,.65))),gap_with_half_mm_allowance_mm=gap(s.translate((0,0,.5))),gap_if_roof_follows_deck_down_mm=gap(s.translate((0,0,.65))))
  plot[name]=dict(body=list(placed(body,p1).exterior.coords),dress=list(g.exterior.coords))
 # pair body vs board outline only; copper and neighbors are future route work.
 g=unary_union([placed(box(-5.1,-1.6,5.1,3.23),moved(p,k*6.1)) for k in [-1,1]])
 placement[ref]=dict(body_outside_board_mm2=g.difference(Polygon(base['boards']['main'])).area,old_courtyard_uv=old_courts[ref])
export_step(Compound(children=main),OUT/'main-ezmate-screen.step')
export_step(Compound(children=[roof,*main]),OUT/'roof-main-ezmate-screen.step')
# Wing local coordinate frame and actual Rev4 J_WING zone; bottom-facing +depth -> -Z.
wing=[];wingposes={};wingplot={}
for side in ['left','right']:
 path=ROOT/f'hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-{side}/definition.json'
 d=json.loads(path.read_text());t=base['wing_transforms'][side];M=t['matrix'];T=t['translation']
 def tr(x,y):return [M[0][0]*x+M[0][1]*y+T[0],M[1][0]*x+M[1][1]*y+T[1]]
 c=next(c for c in d['components'] if c['reference']=='J_WING');a=math.radians(c['rotation_ccw_deg']);u=[math.cos(a),math.sin(a)];v=[-math.sin(a),math.cos(a)]
 x,y=tr(c['x_mm'],c['y_mm']);p=dict(x=x,y=y,u=[sum(M[i][j]*u[j] for j in [0,1]) for i in [0,1]],v=[sum(M[i][j]*v[j] for j in [0,1]) for i in [0,1]])
 outline=Polygon([tr(x,y) for x,y in d['outline_mm']]);pcb=prism(outline,B,1.2);pcb.label='Wing-Rev4-'+side+'-outline-reference';wing.append(pcb)
 wingplot[side]=dict(outline=list(outline.exterior.coords));wingposes[side]={}
 for idx,sign in [('A',-1),('B',1)]:
  name='Wing-'+side+'-'+idx;p1=moved(p,sign*6.1);s,g,body,paths=envelope(p1,sign,B,True);s.label=name+'-mated-and-first-bend-FULL-Z-BOUND';wing.append(s);export_step(s,OUT/(name+'-ezmate-envelope.step'))
  wingposes[side][idx]=dict(pose=p1,bounds_mm=bb(s),nominal_floor_gap_mm=B-1.65-2,allowance_floor_gap_mm=B-1.65-.5-2,body_outside_board_mm2=placed(body,p1).difference(outline).area,full_dress_outside_board_mm2=g.difference(outline).area)
  wingplot[side][idx]=dict(body=list(placed(body,p1).exterior.coords),dress=list(g.exterior.coords))
  from shapely.affinity import rotate,translate
  other=[]
  for c2 in d['components']:
   if c2['reference']=='J_WING' or c2['kind']=='testpoint':continue
   w,h,depth=(3.4,3.4,3.4) if c2['kind']=='hall' else (5.1,6.6,1.4) if c2['kind']=='mux' else (2.4,1.6,1.)
   cg=translate(rotate(box(-w/2,-h/2,w/2,h/2),c2['rotation_ccw_deg']),c2['x_mm'],c2['y_mm'])
   cg=Polygon([tr(x,y) for x,y in cg.exterior.coords]);other.append(dict(ref=c2['reference'],XY_gap_mm=g.distance(cg),overlap_mm2=g.intersection(cg).area))
  wingposes[side][idx]['nearest_component_reservation']=min(other,key=lambda v:v['XY_gap_mm'])
  wingposes[side][idx]['component_reservation_overlaps']=[v for v in other if v['overlap_mm2']>1e-8]
export_step(Compound(children=wing),OUT/'wing-ezmate-screen.step')
# Dimensioned local section assembly: PCB and floor + bound; exported same screen equations.
p=pose(0,0,0);env,_,_,_=envelope(p,1,B,True)
local=[Solid.make_box(30,20,2,Plane(origin=(-15,-5,0))),Solid.make_box(30,20,1.2,Plane(origin=(-15,-5,B))),env]
for s,n in zip(local,['Floor-Z0-to-2','Wing-PCB-B6.70-to-7.90','Mated1.65-wire-band-first-bend']):s.label=n
export_step(Compound(children=local),OUT/'wing-underside-section-context.step')
# Electrical recomputation: use project AWG28 minimum area rather than nominal AWG table.
rows=[];rho=1.7241e-8;area=.0804e-6
for temp in [20,105,125]:
 rw=rho*.2/area*(1+.00393*(temp-20))
 for contact,crimp,label in [(.02,0,'datasheet contact only'),(.02,.005,'contact plus separate crimp allowance'),(.04,.005,'40mOhm environmental sensitivity')]:
  loop=(rw+2*(contact+crimp))*7/6
  # Use Rev7 worst power budget frozen copper and conservative legacy Wing drop.
  budget=json.loads((ROOT/'hardware/kicad/qualification/issue-240-main-rev7/power-budget.json').read_text())
  v=budget['six_return_worst']['farthest_V']+.127*(budget['six_return_worst']['harness_loop_ohm']-loop)
  rows.append(dict(temperature_C=temp,wire_ohm=rw,contact_ohm=contact,crimp_each_ohm=crimp,model=label,loop_ohm=loop,drop_V=.127*loop,Vfar_conservative_frozen_copper=v))
save(OUT/'electrical-b2.json',dict(rows=rows,load_A=.127,length_m_each=.2,supply_parallel=1,return_parallel=6,MP_is_not_circuit=True))
save(OUT/'clearances-b2.json',dict(status='B2 bounded nominal feasibility screen; not board redesign',q_mm=1.5,dimensions_mm=D,PCB_underside_B_mm=B,plate_top_Z_mm=plate,deck_saving_mm=13.55-plate,roof_sha256=roofhash,roof_volume_mm3=roof.volume,main=results,wing=wingposes,placement=placement))
save(OUT/'plot-b2.json',dict(main=plot,wing=wingplot,boards=base['boards']))
assert sha(roofpath)==roofhash
print(json.dumps(dict(B=B,plate=plate,main=results,wing=wingposes,placement=placement),indent=2))
