"""Independent STEP replay and analytic cross-checks; CAD Python, no rebuild."""
import os,sys,json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];OUT=HERE/'b0';RUN=ROOT/'.issue248-runtime'
os.environ['TMPDIR']=str(RUN);sys.dont_write_bytecode=True
from build123d import import_step,Solid,Plane
d=json.loads((OUT/'clearances-b0.json').read_text());r=d['results']
roof=import_step(OUT/'roof-b0.step')
assert len(roof.solids())==8 and all(s.is_valid for s in roof.solids())
assert abs(roof.volume-d['roof_volume_mm3'])<1e-5
assembly=import_step(OUT/'roof-obstacles-b0.step')
assert all(s.is_valid for s in assembly.solids())
for name,expected in [('cover-screw-2',2.72*math.pi),('cover-screw-3',2.72*math.pi),('cover-Main-spacer-2',1.92625*math.pi),('cover-Main-spacer-3',1.92625*math.pi)]:
 # Screw: 1 mm of r0.8 shaft plus 1 mm r0.8->r2 cone.
 # Spacer: 0.5 mm of exact annulus r2.25 / r1.1.
 q=import_step(OUT/(name+'-intersection.step'))
 assert abs(q.volume-expected)<1e-7 and abs(q.volume-r[name]['intersection_mm3'])<1e-7
assert abs(r['Fly-170mm']['worst']['vertical_raw_gap_mm']+1.4)<2e-7
src=ROOT/'hardware/case/issue-246-delta6-tuning/packed/delta-6/17mm'
fly=import_step(src/'fly-170mm.step')
assert abs(fly.volume-170*math.pi)<.001
assert abs(fly.bounding_box().max.Z-21.6)<1e-6
variant=import_step(OUT/'fly-redress-b0.step')
assert len(variant.solids())==1 and variant.is_valid
assert abs(variant.volume-170*math.pi)<.001
rd=json.loads((OUT/'fly-redress-b0.json').read_text())
assert abs(rd['length_mm']-170)<1e-7 and rd['radius_mm']==5 and min(rd['straight_slacks_mm'])>0
assert abs(rd['screen']['worst']['vertical_raw_gap_mm']+1.4)<2e-7
# Replay minimum circular holes for both exact hardware stacks.
def leaves(q):
 if q.children:return [x for c in q.children for x in leaves(c)]
 return [q]
items={q.label:q for q in leaves(assembly)}
modified=roof
centers=[(-31.892683,64.4),(31.892682,64.4)]
for x,y in centers:modified=modified.cut(Solid.make_cylinder(2.55,100,Plane(origin=(x,y,-50))))
holes={}
for n in ['cover-screw-2','cover-screw-3','cover-Main-spacer-2','cover-Main-spacer-3']:
 assert n in items,(n,list(items))
 gap=modified.distance_to(items[n]);holes[n]=gap
 assert gap>=.3-1e-7
for p,digest in d['source_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest
result=dict(status='PASS for delivered partial-study geometry; exact GH housing/plug still unavailable',roof_valid_solids=len(roof.solids()),assembly_valid_solids=len(assembly.solids()),hardware_analytic_volume_checks='four PASS',fly_170_volume_checks='baseline and redress PASS',hardware_openings=dict(diameter_mm=5.1,centers_mm=centers,exact_post_cut_gap_mm=holes),sources_hash_matched=True)
(OUT/'verification-b0.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
