"""B0 study only. Exact OCCT solids; no production files. Run with CAD Python.
Scratch/dependencies: .issue248-runtime; see REPORT-B0.md for model limitations.
"""
import os, sys, json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
RUN=ROOT/'.issue248-runtime'
OUT=HERE/'b0'; OUT.mkdir(exist_ok=True)
os.environ['TMPDIR']=str(RUN)
sys.dont_write_bytecode=True
sys.path.insert(0,str(RUN/'caddeps'))
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
HERE=Path(__file__).resolve().parent
from build123d import Shape, Axis
from OCP.BRepTools import BRepTools
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Shape
T=json.loads((HERE/'tables-a4.json').read_text())
START,TOE=T['start_y'],T['toe_y']; M=11.1/(TOE-START)
SRC=HERE.parent/'issue-246-delta6-tuning/packed/delta-6/17mm'
def read(p):return json.loads(p.read_text())
def bounds(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def cleanring(ring):
 p=list(ring.coords)[:-1]
 while True:
  for i,b in enumerate(p):
   a=p[i-1];c=p[(i+1)%len(p)]
   cross=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))
   if cross<1e-10:
    p.pop(i);break
  else:return p
def cleanpoly(p):return Polygon(cleanring(p.exterior),[cleanring(r) for r in p.interiors])
def flatprism(g,z,h):
 parts=[]
 for p in polygons(g):
  w=lambda ring:Wire.make_polygon([(x,y,z) for x,y in list(ring.coords)[:-1]],close=True)
  parts.append(extrude(Face(w(p.exterior),[w(r) for r in p.interiors]),amount=h,dir=(0,0,1)))
 return parts[0] if len(parts)==1 else Compound(children=parts)
def roofpiece(g,slope):
 parts=[]
 for p in polygons(g):
  w=lambda ring:Wire.make_polygon([(x,y,slope[0]-slope[1]*y-2) for x,y in list(ring.coords)[:-1]],close=True)
  parts.append(extrude(Face(w(p.exterior),[w(r) for r in p.interiors]),amount=2,dir=(0,0,1)))
 return parts
regions={f['properties']['name']:shape(f['geometry']) for f in read(HERE/'raised-regions-a4.geojson')['features'] if f['properties']['role']=='current surface footprint'}
pieces=[]; screens=[]
for n,g in regions.items():
 original=g
 g=g.simplify(1e-7,preserve_topology=True)
 assert abs(g.area-original.area)<1e-5 and g.hausdorff_distance(original)<1.01e-7
 g=unary_union([cleanpoly(p) for p in polygons(g)])
 assert original.symmetric_difference(g).area<1e-6
 a,m=(24.65+M*START,M) if n=='slope' else ((13.55,0) if n=='low_south' else (24.65,0))
 ps=roofpiece(g,(a,m));print('region',n,[(p.is_valid,p.volume) for p in ps],flush=True);pieces+=ps
 screens.append((n,g,a-2,m,flatprism(g,-50,100)))
roof=Compound(children=pieces);roof.label='A4-roof-study-2mm-vertical-skin'
assert all(s.is_valid for s in pieces)
print('roof built',len(pieces),roof.volume,flush=True)
cache=RUN/'b0-source';cache.mkdir(exist_ok=True)
assembly=SRC/'assembly-with-cover.step'
if not (cache/'index.json').exists():
 print('Importing #246 assembly',flush=True)
 items=dict(leaves(import_step(assembly)))
 selected={n:s for n,s in items.items() if n in ['main','Main-GH-left','Main-GH-right','cover-screw-2','cover-screw-3','cover-Main-spacer-2','cover-Main-spacer-3']}
 for i,(n,s) in enumerate(selected.items()):BRepTools.Write_s(s.wrapped,str(cache/f'{i}.brep'))
 save(cache/'index.json',dict(source_sha256=sha(assembly),names=list(selected)))
else: selected={}
meta=read(cache/'index.json');assert meta['source_sha256']==sha(assembly)
for i,n in enumerate(meta['names']):
 s=TopoDS_Shape();BRepTools.Read_s(s,str(cache/f'{i}.brep'),BRep_Builder());selected[n]=Shape.cast(s)
assert abs(bounds(selected['main'])[0][2]-16)<1e-5
obstacles={n:s.translate((0,0,-8.65)) for n,s in selected.items() if n!='main'}
fly=import_step(SRC/'fly-170mm.step').translate((0,0,-8.65));obstacles['Fly-170mm']=fly
meas=read(SRC/'measurements.json')
assert abs(bounds(fly)[1][2]-12.95)<1e-5
assert max(z for x,y,z in meas['fly']['path_samples_mm'])==14.6
# Reconstruct only the terminal straight / first R5 bend / approach from each
# authoritative complete #246 conductor waypoint list. No new wire route.
def corner(a,b,c):
 a,b,c=[np.array(p,float) for p in (a,b,c)]
 u=a-b;u/=np.linalg.norm(u);v=c-b;v/=np.linalg.norm(v)
 theta=math.acos(float(np.dot(u,v)));d=5/math.tan(theta/2)
 center=b+(u+v)/np.linalg.norm(u+v)*5/math.sin(theta/2)
 return b+u*d,center+(b-center)/np.linalg.norm(b-center)*5,b+v*d
for wing in meas['wings']:
 wires=[]
 for pts in wing['conductor_waypoints_mm']:
  _,_,tail=corner(*pts[-4:-1]);a,mid,b=corner(*pts[-3:])
  path=Wire([Edge.make_line(Vector(*tail),Vector(*a)),Edge.make_three_point_arc(Vector(*a),Vector(*mid),Vector(*b)),Edge.make_line(Vector(*b),Vector(*pts[-1]))])
  s=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*tail),z_dir=Vector(*(a-tail))))),path=path).translate((0,0,-2.65))
  assert s.is_valid;wires.append(s)
 obstacles['Main-first-wire-bends-'+wing['side']]=Compound(children=wires)
def common(a,b):
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone()
 return Shape.cast(op.Shape())
def screen(s):
 # Exact support of each clipped obstacle against the affine underside.
 # Rotate so z'=(z+m*y)/sqrt(1+m*m); OCCT optimal BRep bounding box.
 rows=[]
 for n,g,a,m,clip in screens:
  q=common(s,clip)
  if not q.solids():continue
  rot=q.rotate(Axis.X,math.degrees(math.atan(m))) if m else q
  top=bounds(rot)[1][2]*math.sqrt(1+m*m)
  gap=a-top
  # Closest point to a parallel plane above its support gives a witness.
  z=a+50
  f=Face(Wire.make_polygon([(-400,-400,z+400*m),(400,-400,z+400*m),(400,400,z-400*m),(-400,400,z-400*m)],close=True))
  dist,p1,p2=q.distance_to_with_closest_points(f)
  rows.append(dict(region=n,vertical_raw_gap_mm=gap,normal_plane_gap_mm=gap/math.sqrt(1+m*m),witness_mm=list(p1)))
 worst=min(rows,key=lambda r:r['vertical_raw_gap_mm'])
 hit=common(roof,s)
 return dict(worst=worst,regions=rows,intersection_mm3=abs(hit.volume),solid_distance_mm=roof.distance_to(s),outer_surface_vertical_gap_mm=worst['vertical_raw_gap_mm']+2,
             pocket_depth_for_vertical_030_mm=max(0,.3-worst['vertical_raw_gap_mm']),
             pocket_remaining_skin_mm=2-max(0,.3-worst['vertical_raw_gap_mm']))
results={}
for n,s in obstacles.items():
 print('screen',n,flush=True)
 if n.startswith('Main-first-wire'):
  ds=[roof.distance_to_with_closest_points(w) for w in s.solids()]
  dist,pr,pw=min(ds,key=lambda r:r[0])
  results[n]=dict(solid_distance_mm=dist,intersection_mm3=0,worst=dict(witness_mm=list(pw),roof_witness_mm=list(pr)),method='exact BRep minimum Euclidean distance, constituent by constituent')
  assert dist>.3
 else:results[n]=screen(s)
 print(results[n],flush=True)
 for v in s.solids():assert v.is_valid
 s.label=n+('-RESERVATION-NOT-EXACT-HOUSING' if n.startswith('Main-GH') else '')
 # Exact intersections are included separately as reviewable BReps.
 hit=common(roof,s) if not n.startswith('Main-first-wire') else Compound(children=[])
 if hit.solids():export_step(hit,OUT/(n+'-intersection.step'))
export_step(Compound(children=[roof,*obstacles.values()]),OUT/'roof-obstacles-b0.step')
roof.parent=None
export_step(roof,OUT/'roof-b0.step')
save(OUT/'clearances-b0.json',dict(status='PARTIAL B0: GH housing and plug exact source unavailable',units='mm',roof_skin='2 mm vertical per A4',roof_volume_mm3=roof.volume,roof_piece_count=len(pieces),results=results,frames=dict(main_source_underside_z=16,lowered_underside_z=7.35,assembly_step_translation_z=-8.65,fly_samples_translation_z=-2.65),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [assembly,SRC/'fly-170mm.step',SRC/'measurements.json',HERE/'raised-regions-a4.geojson',HERE/'tables-a4.json']}))

# One minimal redress family: northward south-U turn, compensate length by
# widening its west leg. All other #246 waypoints and endpoints stay fixed.
pts=meas['fly']['waypoints_mm']; south0=pts[5][1]
def redress(south,west):
 p=[list(v) for v in pts];p[5][1]=p[6][1]=south;p[6][0]=p[7][0]=-west
 return rounded(p),p
def analytic(south,west):
 p=[np.array(v,float) for v in pts];p[5][1]=p[6][1]=south;p[6][0]=p[7][0]=-west
 ds=[0.];arcs=[]
 for i in range(1,len(p)-1):
  u=p[i-1]-p[i];v=p[i+1]-p[i];u/=np.linalg.norm(u);v/=np.linalg.norm(v)
  theta=math.acos(float(np.dot(u,v)));ds.append(5/math.tan(theta/2));arcs.append(5*(math.pi-theta))
 ds.append(0.)
 slack=[float(np.linalg.norm(p[i+1]-p[i]))-ds[i]-ds[i+1] for i in range(len(p)-1)]
 return sum(slack)+sum(arcs),min(slack),slack
def west_for_length(south):
 lo,hi=14.6,40.
 for _ in range(50):
  mid=(lo+hi)/2
  if analytic(south,mid)[0]<170:lo=mid
  else:hi=mid
 return (lo+hi)/2
# Move the U as far north as this one-parameter compensated family permits.
# Analytic tangent consumption governs R5; preserve 0.0001 mm straight slack.
lo,hi=56.01,south0
for _ in range(45):
 mid=(lo+hi)/2;west=west_for_length(mid)
 if analytic(mid,west)[1]<.0001:lo=mid
 else:hi=mid
south=hi;west=west_for_length(south)
path,p=redress(south,west)
assert abs(path.length-170)<1e-7
variant=sweep(Face(Wire.make_circle(1,Plane(origin=Vector(*p[0]),z_dir=(0,1,0)))),path=path).translate((0,0,-2.65))
assert variant.is_valid and len(variant.solids())==1
export_step(variant,OUT/'fly-redress-b0.step')
red=screen(variant)
save(OUT/'fly-redress-b0.json',dict(family='northward south U; widen west leg to preserve length; every other waypoint fixed',south_original_mm=south0,south_variant_mm=south,shift_north_mm=south0-south,west_variant_mm=west,length_mm=path.length,radius_mm=5,straight_slacks_mm=analytic(south,west)[2],volume_mm3=variant.volume,waypoints_pre_delta_mm=p,screen=red,verdict='FAIL for this redress family: R5 tangent consumption on west leg against fixed Y51 return limits northward travel; low-roof interference remains'))

# Actual X-constant OCCT sections for PNG plotting in a separate system Python.
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
def section(s,x):
 plane=Face(Wire.make_polygon([(x,-100,-20),(x,100,-20),(x,100,40),(x,-100,40)],close=True))
 op=BRepAlgoAPI_Section(s.wrapped,plane.wrapped,False);op.ComputePCurveOn1(True);op.Approximation(True);op.Build();assert op.IsDone()
 q=Shape.cast(op.Shape());return [[[v.Y,v.Z] for v in e.positions([i/100 for i in range(101)])] for e in q.edges()]
sec={}
for title,n in [('gh','Main-first-wire-bends-left'),('fly','Fly-170mm')]:
 x=results[n]['worst']['witness_mm'][0]
 if title=='fly':x=-14.6
 sec[title]=dict(x_mm=x,roof=section(roof,x),obstacle=section(obstacles[n],x),reservation=section(obstacles['Main-GH-left'],x) if title=='gh' else [],result=results[n],label=n+('; detailed housing/plug unavailable' if title=='gh' else ' exact #246 OD2 R5 solid'))
save(OUT/'sections-b0.json',sec)
print('B0 outputs complete',flush=True)
