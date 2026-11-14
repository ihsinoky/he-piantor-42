"""Independent reimport of delivered B2 STEP bounds against B0 BRep faces."""
import os,json,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];O=H/'b2';os.environ['TMPDIR']=str(R/'.issue248-runtime')
from build123d import Shape,Axis,extrude,import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone();return Shape.cast(op.Shape())
d=json.loads((O/'clearances-b2.json').read_text());roof=import_step(H/'b0/roof-b0.step');planes=[]
for f in roof.faces():
 n=f.normal_at()
 if n.Z<-.9:
  c=f.center();m=n.Y/n.Z;planes.append((c.Z+m*c.Y,m,extrude(f.translate((0,0,50)),amount=100,dir=(0,0,-1))))
rows={}
for ref,v in d['main'].items():
 s=import_step(O/(ref+'-ezmate-envelope.step'));assert s.is_valid
 assert abs(s.bounding_box().min.Z-7.9)<1e-7
 assert abs(s.bounding_box().max.Z-9.55)<1e-7
 gaps=[]
 for a,m,clip in planes:
  q=common(s,clip)
  if q.solids():gaps.append(a-q.rotate(Axis.X,math.degrees(math.atan(m))).bounding_box().max.Z*math.sqrt(1+m*m))
 g=min(gaps);vol=abs(common(s,roof).volume)
 assert abs(g-v['vertical_gap_to_B0_mm'])<2e-7
 assert abs(g-2)<2e-7 and vol<1e-8
 assert abs(s.distance_to(roof)-v['true_BRep_distance_mm'])<1e-7
 rows[ref]={'vertical_gap_mm':g,'Common_mm3':vol,'distance_mm':s.distance_to(roof)}
for side in ['left','right']:
 for idx in ['A','B']:
  s=import_step(O/f'Wing-{side}-{idx}-ezmate-envelope.step');assert s.is_valid
  assert abs(s.bounding_box().min.Z-5.05)<1e-7
  assert abs(s.bounding_box().max.Z-6.7)<1e-7
assert hashlib.sha256((H/'b0/roof-b0.step').read_bytes()).hexdigest()==d['roof_sha256']
for p in O.glob('*.step'):
 s=import_step(p);assert all(x.is_valid for x in s.solids()),p
v=dict(status='PASS',all_exported_solids_valid=True,imported_roof_underside_faces=len(planes),main=rows,wing_nominal_min_Z=5.05,wing_allowance_floor_gap_mm=2.55,qualification='Independent BRep replay of stated occupied bounds; no detailed mouldings or routing qualification')
(O/'verification-b2.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
