"""Independent replay of delivered STEP files; no build-script import."""
import os,sys,json,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;O=H/'b3';R=H.parents[2]/'.issue248-runtime'
os.environ['TMPDIR']=str(R);sys.path.insert(0,str(R/'caddeps'))
from build123d import Shape,Axis,extrude,import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone();return Shape.cast(op.Shape())
d=json.loads((O/'clearances-b3.json').read_text());roof=import_step(H/'b0/roof-b0.step');planes=[]
for f in roof.faces():
 n=f.normal_at()
 if n.Z<-.9:
  c=f.center();m=n.Y/n.Z;planes.append((c.Z+m*c.Y,m,extrude(f.translate((0,0,50)),amount=100,dir=(0,0,-1))))
rows={}
for key,v in d['families'].items():
 E=v['dimensions_mm']['height'];B=v['B_mm'];rows[key]={}
 for ref,target in v['main'].items():
  s=import_step(O/(key+'-'+ref+'-envelope.step'));assert s.is_valid
  assert abs(s.bounding_box().min.Z-(B+1.2))<1e-7
  assert abs(s.bounding_box().max.Z-(B+1.2+E))<1e-7
  gaps=[]
  for a,m,clip in planes:
   q=common(s,clip)
   if q.solids():gaps.append(a-q.rotate(Axis.X,math.degrees(math.atan(m))).bounding_box().max.Z*math.sqrt(1+m*m))
  g=min(gaps);vol=abs(common(s,roof).volume)
  assert abs(g-target['vertical_gap_mm'])<2e-7 and vol<1e-8
  assert g>.5
  rows[key][ref]=dict(vertical_gap_mm=g,allowance_gap_mm=g-.5,Common_mm3=vol)
 for side in ['left','right']:
  s=import_step(O/(key+'-Wing-'+side+'-envelope.step'));assert s.is_valid
  assert abs(s.bounding_box().min.Z-(B-E))<1e-7
  assert abs(s.bounding_box().max.Z-B)<1e-7
  assert B-E-.5-2>=.5
  assert not v['wing'][side]['overlaps']
for p in O.glob('*.step'):
 s=import_step(p);assert all(x.is_valid for x in s.solids()),p
assert hashlib.sha256((H/'b0/roof-b0.step').read_bytes()).hexdigest()==d['roof_sha256']
v=dict(status='PASS',all_exported_solids_valid=True,roof_sha256_unchanged=True,underside_faces=len(planes),main=rows)
(O/'verification-b3.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v,indent=2))
