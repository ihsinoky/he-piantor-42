"""B3 survey envelopes only. Frozen XY zones; B0 BRep is imported unchanged."""
import os,sys,json,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent; ROOT=H.parents[2]; RUN=ROOT/'.issue248-runtime'; O=H/'b3'
os.environ['TMPDIR']=str(RUN);sys.dont_write_bytecode=True
sys.path.insert(0,str(RUN/'caddeps'))
from build123d import Shape,Compound,Face,Wire,Axis,extrude,import_step,export_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate
import sexpdata as sx

def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone();return Shape.cast(op.Shape())
def prism(g,z,h):
 return extrude(Face(Wire.make_polygon([(x,y,z) for x,y in list(g.exterior.coords)[:-1]],close=True)),amount=h,dir=(0,0,1))
def pose(x,y,a):
 a=math.radians(a);return dict(x=x,y=y,u=[math.cos(a),-math.sin(a)],v=[math.sin(a),math.cos(a)])
def placed(g,p):return Polygon([(p['x']+u*p['u'][0]+v*p['v'][0],p['y']+u*p['u'][1]+v*p['v'][1]) for u,v in g.exterior.coords])
def bb(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
roofpath=H/'b0/roof-b0.step';roofhash=sha(roofpath);roof=import_step(roofpath);planes=[]
for f in roof.faces():
 n=f.normal_at()
 if n.Z<-.9:
  c=f.center();m=n.Y/n.Z;planes.append((c.Z+m*c.Y,m,extrude(f.translate((0,0,50)),amount=100,dir=(0,0,-1))))
def gap(s):
 values=[]
 for a,m,clip in planes:
  q=common(s,clip)
  if q.solids():values.append(a-q.rotate(Axis.X,math.degrees(math.atan(m))).bounding_box().max.Z*math.sqrt(1+m*m))
 return min(values)
base=json.loads((ROOT/'hardware/case/issue-228-final/17mm/dimensions.json').read_text())
board=ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'
S=sx.Symbol;mainposes={}
for f in sx.loads(board.read_text()):
 if not isinstance(f,list) or not f or f[0]!=S('footprint'):continue
 ref=next((v[2] for v in f if isinstance(v,list) and len(v)>2 and v[0]==S('property') and v[1]=='Reference'),None)
 if ref in ['J2','J3']:
  at=next(v for v in f if isinstance(v,list) and v and v[0]==S('at'));mainposes[ref]=pose(at[1]-100,at[2]-70,at[3])
# Engineering datum: centre of seated occupied rectangle at old GH zone origin.
# No claim that original/new pad origins coincide. Full outlet Z retained.
families={'df52':dict(width=13.4,depth=4.1,height=1.75,pitch=.8,wire_OD=.6,contact_mohm=10,source='Hirose EDC3-356517-01 mating figure + DF52 catalogue'),
          'sh':dict(width=17.,depth=6.25,height=2.95,pitch=1.,wire_OD=.8,contact_mohm=20,source='JST eSH assembly side entry; SHR-14V-S-B protrusions included')}
results={};plots={}
for key,D in families.items():
 B=max(2+D['height']+.5+.5,5.9,3.9,3.5,6.7);E=D['height'];depth=D['depth'];rad=D['wire_OD']/2
 body=box(-D['width']/2,-depth/2,D['width']/2,depth/2)
 # All fourteen wires: 2mm straight, R5 30deg XY turn, 2mm straight.
 # Retain rectangle surrounding all swept wire cross sections, full seated Z band.
 span=13*D['pitch']/2
 turn=5*(1-math.cos(math.pi/6))+2*math.sin(math.pi/6)
 vend=depth/2+2+5*math.sin(math.pi/6)+2*math.cos(math.pi/6)+rad
 wire=box(-span-rad,depth/2-rad,span+rad+turn,vend)
 local=unary_union([body,wire]);mains=[];wings=[];mr={};wr={};plot={'main':{},'wing':{}}
 pcb=prism(Polygon(base['boards']['main']),B,1.2);pcb.label='Frozen-Main-outline-new-Z';mains.append(pcb)
 for ref,p in mainposes.items():
  g=placed(local,p);s=prism(g,B+1.2,E);s.label=key+'-'+ref+'-mated-and-XY-first-dress'
  export_step(s,O/(key+'-'+ref+'-envelope.step'));mains.append(s)
  mr[ref]=dict(pose=p,bounds_mm=bb(s),vertical_gap_mm=gap(s),allowance_gap_mm=gap(s.translate((0,0,.5))),common_mm3=abs(common(s,roof).volume),true_distance_mm=roof.distance_to(s),body_outside_board_mm2=placed(body,p).difference(Polygon(base['boards']['main'])).area,dress_outside_board_mm2=g.difference(Polygon(base['boards']['main'])).area)
  plot['main'][ref]=dict(body=list(placed(body,p).exterior.coords),dress=list(g.exterior.coords))
 export_step(Compound(children=[roof,*mains]),O/(key+'-roof-main-screen.step'))
 for side in ['left','right']:
  d=json.loads((ROOT/f'hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-{side}/definition.json').read_text())
  t=base['wing_transforms'][side];M=t['matrix'];T=t['translation']
  def tr(x,y):return [M[0][0]*x+M[0][1]*y+T[0],M[1][0]*x+M[1][1]*y+T[1]]
  c=next(c for c in d['components'] if c['reference']=='J_WING');a=math.radians(c['rotation_ccw_deg']);u=[math.cos(a),math.sin(a)];v=[-math.sin(a),math.cos(a)]
  x,y=tr(c['x_mm'],c['y_mm']);p=dict(x=x,y=y,u=[sum(M[i][j]*u[j] for j in [0,1]) for i in [0,1]],v=[sum(M[i][j]*v[j] for j in [0,1]) for i in [0,1]])
  outline=Polygon([tr(x,y) for x,y in d['outline_mm']]);pcb=prism(outline,B,1.2);pcb.label='Frozen-Wing-'+side+'-outline-new-Z';wings.append(pcb)
  g=placed(local,p);s=prism(g,B-E,E);s.label=key+'-Wing-'+side+'-mated-and-XY-first-dress';wings.append(s);export_step(s,O/(key+'-Wing-'+side+'-envelope.step'))
  other=[]
  for c2 in d['components']:
   if c2['reference']=='J_WING' or c2['kind']=='testpoint':continue
   w,h=(3.4,3.4) if c2['kind']=='hall' else (5.1,6.6) if c2['kind']=='mux' else (2.4,1.6)
   cg=translate(rotate(box(-w/2,-h/2,w/2,h/2),c2['rotation_ccw_deg']),c2['x_mm'],c2['y_mm']);cg=Polygon([tr(x,y) for x,y in cg.exterior.coords]);other.append(dict(ref=c2['reference'],gap_mm=g.distance(cg),overlap_mm2=g.intersection(cg).area))
  wr[side]=dict(pose=p,bounds_mm=bb(s),allowance_floor_gap_mm=B-E-.5-2,body_outside_board_mm2=placed(body,p).difference(outline).area,dress_outside_board_mm2=g.difference(outline).area,nearest=min(other,key=lambda v:v['gap_mm']),overlaps=[v for v in other if v['overlap_mm2']>1e-8])
  plot['wing'][side]=dict(outline=list(outline.exterior.coords),body=list(placed(body,p).exterior.coords),dress=list(g.exterior.coords))
 export_step(Compound(children=wings),O/(key+'-wing-screen.step'))
 export_step(prism(local,0,E),O/(key+'-local-envelope.step'))
 results[key]=dict(dimensions_mm=D,local_bounds=list(local.bounds),B_mm=B,connector_only_B_mm=3+E,plate_top_Z_mm=B+6.2,main=mr,wing=wr)
 plots[key]=plot
save(O/'clearances-b3.json',dict(q_mm=1.5,roof_sha256=roofhash,roof_volume_mm3=roof.volume,roof_solids=len(roof.solids()),roof_underside_faces=len(planes),families=results))
save(O/'plot-b3.json',plots)
budget=json.loads((ROOT/'hardware/kicad/qualification/issue-240-main-rev7/power-budget.json').read_text())
rows=[]
for fam,area,contact,ceiling in [('df52',.0804,.010,85),('sh',.0804,.020,85),('sur32',.032,.020,85),('sur36',.0127,.020,85),('ezmate',.0804,.020,105)]:
 for temp in [20,ceiling,125]:
  rw=1.7241e-8*.2/(area*1e-6)*(1+.00393*(temp-20))
  for cr,tag in [(contact,'initial'),(.040 if fam in ['sh','sur32','sur36','ezmate'] else .020,'environmental sensitivity')]:
   loop=(rw+2*(cr+.005))*7/6
   rows.append(dict(family=fam,T_C=temp,area_mm2=area,contact_ohm=cr,crimp_each_ohm=.005,crimp_status='B2 comparison engineering allowance; not a JST/Hirose specification',wire_ohm=rw,loop_ohm=loop,drop_mV=.127*loop*1000,Vfar_frozen=budget['six_return_worst']['farthest_V']+.127*(budget['six_return_worst']['harness_loop_ohm']-loop),model=tag))
save(O/'electrical-b3.json',dict(rows=rows,load_A=.127,length_m_each=.2,supply_contacts=1,ground_contacts=6))
assert sha(roofpath)==roofhash
print(json.dumps(results,indent=2))
