"""Phase B millimetres, assembly frame. All outputs provisional on plateau_top_z_mm."""
import os, sys, json, math, csv, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime'/'phaseb'; RUN.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(ROOT/'.issue248-runtime')
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'.issue248-runtime/caddeps'))
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime'/'phaseb'
sys.path.insert(0,str(HERE))
from build123d import Shape, Axis
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
def volume(a,b):
 aa=a.bounding_box();bb=b.bounding_box()
 if any(min(getattr(aa.max,k),getattr(bb.max,k))-max(getattr(aa.min,k),getattr(bb.min,k))<=1e-7 for k in 'XYZ'):return 0.
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 from OCP.BRepGProp import BRepGProp
 from OCP.GProp import GProp_GProps
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
 if not op.IsDone():raise RuntimeError('OCCT Common failed')
 if op.Shape().IsNull():return 0.
 props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props,True,False,False)
 return abs(props.Mass())
P=json.loads((HERE/'parameters.json').read_text())
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for c in getattr(g,'geoms',[]) for p in polygons(c)]
PLATE=P['plate_top_z_mm']; TOP=P['plateau_top_z_mm']
START=P['slope_start_y_mm']; TOE=P['slope_toe_y_mm']; M=(TOP-PLATE)/(TOE-START)
def read(p):return json.loads(p.read_text())
def bounds(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def loadbrep(p):
 s=TopoDS_Shape();BRepTools.Read_s(s,str(p),BRep_Builder());return Shape.cast(s)
def source(pitch):
 cache=RUN/f'source{pitch}';meta=read(cache/'index.json')
 assert meta['sha256']==sha(HERE.parent/f'issue-232-final/{pitch}mm/assembly.step')
 return {r['name']:loadbrep(cache/f'{i}.brep') for i,r in enumerate(meta['parts'])}
def cleanring(ring):
 p=list(ring.coords)[:-1]
 while True:
  for i,b in enumerate(p):
   a=p[i-1];c=p[(i+1)%len(p)]
   if abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))<1e-10:p.pop(i);break
  else:return p
def clean(g):return unary_union([Polygon(cleanring(p.exterior),[cleanring(r) for r in p.interiors]) for p in polygons(g.simplify(1e-7,preserve_topology=True))])
def sloped(g,a,m,thickness=2):
 if m and thickness==2:thickness=2*math.sqrt(1+m*m)
 parts=[]
 for p in polygons(clean(g)):
  w=lambda r:Wire.make_polygon([(x,y,a-m*y-thickness) for x,y in list(r.coords)[:-1]],close=True)
  parts.append(extrude(Face(w(p.exterior),[w(r) for r in p.interiors]),amount=thickness,dir=(0,0,1)))
 return parts
def fuseall(parts):
 assert parts
 s=parts[0]
 for q in parts[1:]:s=s.fuse(q)
 return s
def save_geometry(pitch,items,meta):
 out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True)
 cache=RUN/f'geometry{pitch}';cache.mkdir(exist_ok=True);idx=[]
 for n,s in items.items():
  for k,q in enumerate(s.solids()):
   i=len(idx);BRepTools.Write_s(q.wrapped,str(cache/f'{i}.brep'))
   idx.append(dict(name=n,solid=k,bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(cache/f'{i}.brep')))
 save(cache/'index.json',idx);save(out/'assembly-index.json',idx)
 save(out/'measurements.json',dict(status=P['status'],pitch_mm=pitch,parameters=P,**meta))
def cached(pitch):
 cache=RUN/f'geometry{pitch}';idx=read(cache/'index.json');raw=[]
 for i,r in enumerate(idx):
  assert sha(cache/f'{i}.brep')==r['sha256'];raw.append((r['name'],r['solid'],loadbrep(cache/f'{i}.brep')))
 return idx,raw
