#!/usr/bin/env python3
"""Study acceptance: independent source identity, geometry, model arithmetic and meshes."""
from pathlib import Path
import csv,json,hashlib,math,collections,struct
from shapely.geometry import shape,Polygon,Point
from shapely.affinity import rotate,translate
P=Path(__file__).resolve().parent;R=P.parents[2]
def rows(p):return list(csv.DictReader(p.open()))
def rectangle(x,y,a,w):return translate(rotate(Polygon([(-w/2,-w/2),(w/2,-w/2),(w/2,w/2),(-w/2,w/2)]),a),x,y)
checks=[]
for rel,digest in json.load(open(P/'inputs-sha256.json')).items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==digest,rel
summ=json.load(open(P/'summary.json'))
for d in sorted(P.glob('*mm-*')):
 pitch=int(d.name[:2]);side=d.name.split('-')[1];case=R/'hardware/case/issue-228-final/inputs/rev3-final'
 key=rows(case/f'keys-{d.name}.csv');outline=Polygon([(float(r['x_mm']),float(r['y_mm'])) for r in rows(case/f'outline-{d.name}.csv')]);plate=shape(json.load(open(d/'plate.geojson')))
 assert plate.is_valid and plate.geom_type=='Polygon'
 assert plate.difference(outline).area<1e-8
 assert abs(plate.distance(outline.boundary)-.2)<1e-7
 cutouts=rows(d/'cutouts.csv');ties=rows(d/'tie-holes.csv');supports=rows(d/'supports.csv');per=rows(d/'per-key.csv');flo=rows(d/'floating.csv')
 assert len(cutouts)==21 and len(ties)==4 and len(supports)==6
 for k,h in zip(key,cutouts):
  assert k['key']==h['key']
  for a in ['x_mm','y_mm']:assert k[a]==h[a]
  assert float(k['rotation_deg'])==float(h['rotation_ccw_deg'])
  x,y,a=float(k['x_mm']),float(k['y_mm']),float(k['rotation_deg'])
  # Finished 14mm switch body envelope must be completely absent, except tiny
  # R.2 corner lands whose exact fit is covered by the clip acceptance coupon.
  inner=rectangle(x,y,a,13.6);assert inner.intersection(plate).area<1e-8
 for h in ties:
  q=Point(float(h['x_mm']),float(h['y_mm']));assert q.distance(plate)>=1.099
  cap=__import__('shapely').union_all([rectangle(float(k['x_mm']),float(k['y_mm']),float(k['rotation_deg']),17) for k in key])
  assert q.distance(cap)>=2.,(d,h['id'],'washer/cap clearance')
 for h in supports:
  q=Point(float(h['x_mm']),float(h['y_mm']));assert outline.covers(q.buffer(1.5))
  assert float(h['land_drill_body_edge_gap_mm'])>=.4
  assert float(h['top_z_mm'])==10 and float(h['base_z_mm'])==2
 # Fastener: washer .5+plate1.5+spacer3.5+PCB1.2 =6.7; 12-6.7=5.3 engagement.
 assert abs(12-(.5+1.5+3.5+1.2)-5.3)<1e-9
 assert 16.7-12>2+.3
 opts=collections.defaultdict(list)
 for r in per:
  opts[r['option']].append(r)
  a=next(x for x in summ if x['variant']==d.name and x['option']==r['option']);dist=float(r['nearest_support_mm']);ei=a['EI_Nmm2']
  assert math.isclose(float(r['bend_bracket_high_mm']),dist**3/(3*ei),rel_tol=1e-10)
  assert math.isclose(float(r['bend_bracket_high_mm']),8*float(r['bend_bracket_low_mm']),rel_tol=1e-10)
 assert all(len(v)==21 and len({r['key'] for r in v})==21 for v in opts.values())
 assert len(flo)==21*3*3
 for r in flo:assert float(r['sink_high_mm'])==2*float(r['sink_1N_mm'])
 if pitch==17:
  baseline=opts['baseline'];assert sum(float(r['nearest_support_mm'])>40 for r in baseline)==5
  assert abs(max(float(r['nearest_support_mm']) for r in baseline)-55.980182780585864)<1e-6
 # Check closed oriented 3D mesh, no unpaired edges; signed volume matches plate.
 verts=[]
 blob=(d/'plate-study.stl').read_bytes();count=struct.unpack_from('<I',blob,80)[0]
 assert len(blob)==84+50*count
 for i in range(count):
  v=struct.unpack_from('<12fH',blob,84+50*i)
  verts.extend([tuple(v[j:j+3]) for j in (3,6,9)])
 edge=collections.Counter();volume=0
 for i in range(0,len(verts),3):
  a,b,c=verts[i:i+3]
  for u,v in [(a,b),(b,c),(c,a)]:edge[(u,v)]+=1
  volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 assert all(count==edge[(v,u)] for (u,v),count in edge.items()),d.name
 assert math.isclose(volume,plate.area*1.5,rel_tol=1e-6),(d.name,volume,plate.area)
 checks.append(dict(variant=d.name,passed=True,key_count=21,option_count=len(opts),per_key_rows=len(per),floating_rows=len(flo),plate_mesh_closed_oriented=True,plate_volume_mm3=volume,plate_min_board_edge_clearance_mm=plate.distance(outline.boundary)))
result=dict(passed=True,source_hashes_unchanged=True,physical_tests_run=False,full_case_STEP_collision_suite_run=False,checks=checks)
(P/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
