"""Independent exported-STEP replay against actual B0 roof underside faces."""
import os,sys,json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; OUT=HERE/'b1'
os.environ['TMPDIR']=str(ROOT/'.issue248-runtime');sys.dont_write_bytecode=True
from build123d import Shape,Axis,extrude,import_step
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def common(a,b):
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.Build();assert op.IsDone()
 return Shape.cast(op.Shape())
d=json.loads((OUT/'clearances-b1.json').read_text());roof=import_step(HERE/'b0/roof-b0.step')
assert len(roof.solids())==8 and all(s.is_valid for s in roof.solids())
planes=[]
for f in roof.faces():
 n=f.normal_at()
 if n.Z>=-.9:continue
 c=f.center();m=n.Y/n.Z
 assert abs(n.X)<1e-10
 clip=extrude(f.translate((0,0,50)),amount=100,dir=(0,0,-1))
 planes.append((c.Z+m*c.Y,m,clip))
assert len(planes)==8,len(planes)
rows={}
for ref,r in d['results'].items():
 s=import_step(OUT/(ref+'-mated-gh.step'));assert s.is_valid
 gaps=[]
 for a,m,clip in planes:
  q=common(s,clip)
  if not q.solids():continue
  rotated=q.rotate(Axis.X,math.degrees(math.atan(m)))
  gaps.append(a-rotated.bounding_box().max.Z*math.sqrt(1+m*m))
 gap=min(gaps);hit=common(roof,s)
 assert abs(gap-r['worst']['vertical_gap_mm'])<2e-7
 assert abs(abs(hit.volume)-r['intersection_mm3'])<1e-6
 assert abs(import_step(OUT/(ref+'-roof-intersection.step')).volume-abs(hit.volume))<1e-6
 # Replay relief on a scratch copy of the whole roof (uniform lift is a
 # vertical ceiling test only; it is not an adopted local roof design).
 lifted=roof.translate((0,0,r['pocket_depth_mm']))
 gap3d=lifted.distance_to(s)
 assert abs(gap3d-.3)<2e-7,(ref,gap3d)
 assert abs(common(lifted,s).volume)<1e-8
 rows[ref]=dict(vertical_gap_mm=gap,intersection_mm3=abs(hit.volume),relieved_ceiling_gap_mm=gap3d)
assembly=import_step(OUT/'mated-gh-assembly-frame.step')
assert len(assembly.solids())==2 and all(s.is_valid for s in assembly.solids())
for p,h in d['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
result=dict(status='PASS: exported drawing bounds, exact BRep gaps/Common, relief and immutable source hashes',underside_faces_screened=len(planes),roof_volume_mm3=roof.volume,results=rows)
(OUT/'verification-b1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
