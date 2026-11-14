"""Cancel coincident, oppositely oriented planar boundary sheets; preserve volume."""
from common import *
from collections import defaultdict
from build123d import GeomType, Solid
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS

def rebuild(q):
 groups=defaultdict(list);other=[]
 for f in q.faces():
  if f.geom_type!=GeomType.PLANE:other.append(f);continue
  n=np.array(tuple(f.normal_at()),float);n/=np.linalg.norm(n)
  sign=1
  for x in n:
   if abs(x)>1e-8:
    if x<0:n=-n;sign=-1
    break
  d=float(np.dot(n,np.array(tuple(f.center()))));key=tuple(np.round(n,7))+(round(d,6),)
  groups[key].append((sign,f,n,d))
 faces=other[:];cancelled=0;changed=0
 for key,rows in groups.items():
  if len(rows)==1 or len(set(r[0] for r in rows))==1 or any(e.geom_type!=GeomType.LINE for r in rows for e in r[1].edges()):faces.extend(r[1] for r in rows);continue
  n=rows[0][2];d=rows[0][3];origin=n*d
  ref=np.array([1.,0,0]) if abs(n[0])<.9 else np.array([0.,1,0])
  u=np.cross(ref,n);u/=np.linalg.norm(u);v=np.cross(n,u)
  def xy(w):return [(float(np.dot(np.array(tuple(p))-origin,u)),float(np.dot(np.array(tuple(p))-origin,v))) for p in [e.position_at(0) for e in w.order_edges()]]
  plus=[];minus=[]
  for sign,f,nn,dd in rows:
   outer=xy(f.outer_wire());holes=[xy(w) for w in f.inner_wires()]
   g=Polygon(outer,holes)
   assert g.is_valid, (key, g.wkt)
   (plus if sign>0 else minus).append(g)
  a=unary_union(plus);b=unary_union(minus);overlap=a.intersection(b)
  if overlap.area<1e-8:
   faces.extend(r[1] for r in rows);continue
  cancelled+=overlap.area;changed+=1
  for sign,g in [(1,a.difference(b)),(-1,b.difference(a))]:
   for p in polygons(g):
    def w(r):return Wire.make_polygon([Vector(*(origin+u*x+v*y)) for x,y in list(r.coords)[:-1]],close=True)
    f=Face(w(p.exterior),[w(r) for r in p.interiors])
    if np.dot(np.array(tuple(f.normal_at())),n)*sign<0:f.wrapped.Reverse()
    faces.append(f)
 sewing=BRepBuilderAPI_Sewing(1e-7)
 for f in faces:sewing.Add(f.wrapped)
 sewing.Perform();sewn=Shape.cast(sewing.SewedShape());solids=[]
 for sh in sewn.shells():
  op=BRepBuilderAPI_MakeSolid(sh.wrapped);solid=Solid(op.Solid());solids.append(solid)
 result=solids[0] if len(solids)==1 else Compound(children=solids)
 return result,dict(cancelled_opposing_sheet_area_mm2=cancelled,changed_plane_groups=changed,before_faces=len(q.faces()),after_faces=len(result.faces()),before_volume_mm3=q.volume,after_volume_mm3=result.volume,volume_delta_mm3=result.volume-q.volume,valid=result.is_valid,solids=len(result.solids()))

def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);groups={}
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 old=Compound(children=groups['shell-central']);q,record=rebuild(old)
 print(pitch,record,flush=True)
 assert q.is_valid and abs(q.volume-old.volume)<1e-6
 groups['shell-central']=list(q.solids())
 items={n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()}
 meta=read(out/'measurements.json')
 for k in ('status','pitch_mm','parameters'):meta.pop(k,None)
 meta['shell_boundary_regularization']=record
 save_geometry(pitch,items,meta);save(out/'shell-regularization.json',record)
if __name__=='__main__':run(int(sys.argv[1]))
