"""B1 JST drawing-bounded seated GH study; never changes B0 or production CAD."""
import os,sys,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime'; OUT=HERE/'b1'; OUT.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(RUN);sys.dont_write_bytecode=True
sys.path.insert(0,str(RUN/'caddeps'))
from build123d import Solid,Plane,Shape,Compound,Face,Wire,import_step,export_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Section
from shapely.geometry import Polygon,shape
from shapely.ops import unary_union
import sexpdata as sx

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone()
 return Shape.cast(op.Shape())
def polygons(g):return [g] if g.geom_type=='Polygon' else list(g.geoms)
def bounds(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def section(s,x):
 f=Face(Wire.make_polygon([(x,-100,-20),(x,100,-20),(x,100,40),(x,-100,40)],close=True))
 op=BRepAlgoAPI_Section(s.wrapped,f.wrapped,False);op.Build();assert op.IsDone()
 return [[[v.Y,v.Z] for v in e.positions([i/30 for i in range(31)])] for e in Shape.cast(op.Shape()).edges()]

# D1: JST eGH p3 Housing, Header/Side entry, fourteen-circuit table.
# D2: JST eGH p2 Assembly layout/Side entry. No traced/estimated details.
D=dict(header_width=20.75,header_depth=4.05,header_body_height=4.25,
       header_standoff=.1,plug_width=18.75,plug_length=5.7,
       plug_height=4.15,mated_height=4.35,mated_length=7.15,pitch=1.25,pin_span=16.25)
assert abs(D['header_standoff']+D['header_body_height']-D['mated_height'])<1e-12
# Mounting datum from Rev7 native footprint F.Fab rear edge (not a JST size).
rear=-1.6; top=8.55+D['mated_height']
header=( -D['header_width']/2,rear,.1,D['header_width']/2,rear+D['header_depth'],4.35 )
plug=( -D['plug_width']/2,rear+D['mated_length']-D['plug_length'],4.35-D['plug_height'],D['plug_width']/2,rear+D['mated_length'],4.35 )
board=ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'
S=sx.Symbol; poses={}
for f in sx.loads(board.read_text()):
 if not isinstance(f,list) or not f or f[0]!=S('footprint'):continue
 ref=next((v[2] for v in f if isinstance(v,list) and len(v)>2 and v[0]==S('property') and v[1]=='Reference'),None)
 if ref not in ('J2','J3'):continue
 at=next(v for v in f if isinstance(v,list) and v and v[0]==S('at'))
 poses[ref]=dict(side='left' if ref=='J2' else 'right',x=at[1]-100,y=at[2]-70,angle=at[3])
assert len(poses)==2
roof_path=HERE/'b0/roof-b0.step'; roof_hash=sha(roof_path);roof=import_step(roof_path)
assert len(roof.solids())==8 and all(s.is_valid for s in roof.solids())
t=json.loads((HERE/'tables-a4.json').read_text());m=11.1/(t['toe_y']-t['start_y'])
regions=[]
for f in json.loads((HERE/'raised-regions-a4.geojson').read_text())['features']:
 if f['properties']['role']!='current surface footprint':continue
 n=f['properties']['name']; a,k=(24.65+m*t['start_y']-2,m) if n=='slope' else ((11.55,0) if n=='low_south' else (22.65,0))
 regions.append((n,shape(f['geometry']),a,k))
results={};models=[];sections={};outlets=[];component_bounds=[]
for ref,p in poses.items():
 a=math.radians(p['angle'])
 def xy(u,v):return (p['x']+u*math.cos(a)+v*math.sin(a),p['y']-u*math.sin(a)+v*math.cos(a))
 def poly(b):
  u,v,z,U,V,Z=b;return Polygon([xy(u,v),xy(U,v),xy(U,V),xy(u,V)])
 def solid(b):
  u,v,z,U,V,Z=b
  return Solid.make_box(U-u,V-v,Z-z,Plane(origin=(u,v,8.55+z))).rotate(__import__('build123d').Axis.Z,-p['angle']).translate((p['x'],p['y'],0))
 h=solid(header);q=solid(plug)
 h.label=ref+"-header-DRAWING-BOUND";q.label=ref+"-plug-including-latch-DRAWING-BOUND"
 component_bounds.extend([h,q])
 # Fused occupied bound avoids counting the seated overlap twice.
 s=h.fuse(q);s.label=ref+'-'+p['side']+'-JST-DRAWING-BOUNDED-mated-GH';assert s.is_valid
 models.append(s);foot=unary_union([poly(header),poly(plug)])
 rows=[]
 for name,g,c,k in regions:
  overlap=foot.intersection(g)
  if overlap.is_empty or overlap.area<1e-12:continue
  points=[v for poly_ in polygons(overlap) for v in poly_.exterior.coords]
  x,y=min(points,key=lambda v:c-k*v[1]-top)
  rows.append(dict(region=name,vertical_gap_mm=c-k*y-top,worst_point_mm=[x,y,top],roof_underside_mm=c-k*y))
 worst=min(rows,key=lambda v:v['vertical_gap_mm']);hit=common(roof,s)
 depth=.3-worst['vertical_gap_mm']
 # Also screen header alone: does excluding every uncertain plug/latch detail
 # change the need for a closed blister? No.
 hh=common(roof,h)
 result=dict(pose=p,model_bounds_mm=bounds(s),worst=worst,regional_gaps=rows,
  intersection_mm3=abs(hit.volume),intersection_qualification='exact OCCT Common of drawing-bounded model; upper bound on physical intersection',
  header_alone_intersection_mm3=abs(hh.volume),pocket_depth_mm=depth,remaining_skin_mm=2-depth,
  closed_ceiling_z_mm=top+.3,closed_top_z_mm=top+.3+2,max_rise_above_surface_mm=depth,
  header_local_bounds_uvz_mm=header,plug_and_latch_local_bounds_uvz_mm=plug)
 results[ref]=result
 export_step(s,OUT/(ref+'-mated-gh.step'));export_step(hit,OUT/(ref+'-roof-intersection.step'))
 # Rear plug outlet is a bounded face, not an invented hole or wire axis.
 u,v,z,U,V,Z=plug
 face=Face(Wire.make_polygon([(*xy(u,V),8.55+z),(*xy(U,V),8.55+z),(*xy(U,V),8.55+Z),(*xy(u,V),8.55+Z)],close=True))
 face.label=ref+'-wire-exit-plane-DRAWING-BOUNDED';outlets.append(face)
 # Representative point within the low-south header top (minimum is a plateau).
 hp=poly(header).intersection(next(g for n,g,c,k in regions if n=='low_south'))
 point=hp.representative_point();x,y=point.x,point.y
 assert common(roof,Solid.make_box(.001,.001,2,Plane(origin=(x,y,11.55)))).volume>0
 result['section_worst_point_mm']=[x,y,top]
 sections[ref]=dict(x_mm=x,worst_point_mm=[x,y,top],roof=section(roof,x),model=section(s,x),header=section(h,x),plug_latch_bound=section(q,x))
 print(ref,json.dumps(result),flush=True)
export_step(Compound(children=models),OUT/'mated-gh-assembly-frame.step')
export_step(Compound(children=component_bounds),OUT/'mated-gh-component-bounds.step')
# Export roof read from B0 verbatim in its original frame alongside the new GHs.
export_step(Compound(children=[roof,*models,*outlets]),OUT/'roof-gh-b1.step')
sources=[roof_path,board,HERE/'tables-a4.json',HERE/'raised-regions-a4.geojson',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/connector/JST-current-eGH.pdf',ROOT/'hardware/kicad/qualification/issue-240-main-rev7/connector/eGH-distributor-copy.pdf']
save(OUT/'clearances-b1.json',dict(status='B1 dimensioned drawing-bound clearance screen complete; not production CAD',dimensions_mm=D,pcb_underside_z_mm=7.35,pcb_top_z_mm=8.55,q_provisional_mm=1.5,roof_volume_mm3=roof.volume,results=results,source_sha256={str(f.relative_to(ROOT)):sha(f) for f in sources}))
save(OUT/'sections-b1.json',sections)
assert sha(roof_path)==roof_hash
