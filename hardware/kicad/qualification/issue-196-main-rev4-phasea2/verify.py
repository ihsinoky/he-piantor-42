"""Independent stdlib-only polygon verification of the proposal (no KiCad import)."""
from pathlib import Path
import json, math, hashlib, itertools
E=Path(__file__).resolve().parent;R=E.parents[3]
d=json.loads((E/'geometry-plan.json').read_text());m=d['main'];P=m['outline_xy_mm']
def sub(a,b):return [a[0]-b[0],a[1]-b[1]]
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def cross(a,b):return a[0]*b[1]-a[1]*b[0]
def edges(p):return list(zip(p,p[1:]+p[:1]))
def pseg(p,a,b):
 ab=sub(b,a);t=max(0,min(1,dot(sub(p,a),ab)/dot(ab,ab)));return math.dist(p,[a[i]+t*ab[i] for i in [0,1]])
def inside(p,poly):
 z=[cross(sub(b,a),sub(p,a)) for a,b in edges(poly)];return min(z)>=-1e-7 or max(z)<=1e-7
# Separation via independent SAT for all convex reservation polygons.
def separated(a,b,gap=0):
 for poly in [a,b]:
  for p,q in edges(poly):
   v=sub(q,p);n=[-v[1],v[0]];norm=math.hypot(*n)
   aa=[dot(n,p) for p in a];bb=[dot(n,p) for p in b]
   if max(aa)<=min(bb)-gap*norm+1e-7 or max(bb)<=min(aa)-gap*norm+1e-7:return True
 return False
area=abs(sum(cross(a,b) for a,b in edges(P)))/2
assert abs(area-m['area_mm2'])<1e-7
assert {tuple(p) for p in P}=={(-x,y) for x,y in P}
for f,h in d['inputs_sha256'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h,f
refs={v['ref']:v for v in m['placements']};assert len(refs)==59
assert set(refs)==set(m['retained_refs'])|{'J4'}
assert set(m['removed_refs'])=={'J1','R1','R2','U2'}
assert {'U1','U3','U4','U5','U6','Y1','L1','R3','R4'}<=set(refs)
min_edge=1000.;min_body=1000.
for v in refs.values():
 env=v['envelope_xy_mm']
 assert all(inside(p,P) for p in env)
 assert min(pseg(p,a,b) for p in env for a,b in edges(P))>=.25-1e-7
 for pad in v['pads']:
  for poly in pad['copper_polygons_xy_mm']:
   assert all(inside(p,env) and inside(p,P) for p in poly)
   dist=min(pseg(p,a,b) for p in poly for a,b in edges(P));min_edge=min(min_edge,dist);assert dist>=.2-1e-7
for a,b in itertools.combinations(refs.values(),2):
 aa=a['envelope_xy_mm'];bb=b['envelope_xy_mm'];assert separated(aa,bb),(a['ref'],b['ref'])
 dist=min([pseg(p,x,y) for p in aa for x,y in edges(bb)]+[pseg(p,x,y) for p in bb for x,y in edges(aa)])
 min_body=min(min_body,dist);assert dist>=.3-1e-7
for h in m['holes']:
 p=h['xy_mm'];assert inside(p,P)
 assert min(pseg(p,a,b) for a,b in edges(P))>=3-1e-7
 for f in refs.values():
  env=f['envelope_xy_mm'];assert not inside(p,env)
  assert min(pseg(p,a,b) for a,b in edges(env))>=2.5002-1e-7
for pitch,sides in d['wing'].items():
 for side,w in sides.items():
  src=json.loads((E/f'inputs/wing/definition-{pitch}mm-{side}.proposal.json').read_text());mat=w['transform_matrix'];t=w['translation_xy_mm']
  tr=lambda p:[dot(row,p)+t[i] for i,row in enumerate(mat)]
  # Check actual Stage 1 keys through the independent matrix transform.
  for a,b in zip(src['keys'],w['keys']):
   assert a['key']==b['key']
   for pt,target in zip(a['envelope_mm'],b['envelope_xy_mm']):assert math.dist(tr(pt),target)<1e-7
  assert separated(P,w['outline_xy_mm'])
  a,b=w['inner_edge_endpoints_xy_mm'];length=math.dist(a,b)
  ds=[abs(cross(sub(b,a),sub(pt,a)))/length for pt in P]
  assert abs(min(ds)-2)<1e-7
for h in d['harness']:
 assert h['chord_mm']>100
 assert h['planning_length_mm']<h['proposed_nominal_mm']
 assert abs(h['planning_route_mm']-sum(math.dist(a,b) for a,b in zip(h['planning_route_xy_mm'],h['planning_route_xy_mm'][1:])))<1e-7
assert d['phase_b_routing_authorized'] is False
print(json.dumps({'status':'PASS','placement_count':len(refs),'pair_count':math.comb(len(refs),2),'minimum_envelope_gap_mm':min_body,'minimum_pad_edge_mm':min_edge,'area_mm2':area,'wing_variants_checked':4},indent=2))
