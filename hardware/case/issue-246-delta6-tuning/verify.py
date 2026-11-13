"""Independent no-CAD hash, all-pairs coverage and gate-evidence verification."""
from pathlib import Path
import hashlib,json,itertools,math,ast
H=Path(__file__).resolve().parent;R=H.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rounded_length(points,radius=5):
 distances=[math.dist(a,b) for a,b in zip(points,points[1:])]
 trims=[0.0]*len(points);arcs=0
 for i in range(1,len(points)-1):
  u=[(points[i-1][k]-points[i][k])/distances[i-1] for k in range(3)]
  v=[(points[i+1][k]-points[i][k])/distances[i] for k in range(3)]
  theta=math.acos(max(-1,min(1,sum(a*b for a,b in zip(u,v)))))
  trims[i]=radius/math.tan(theta/2);arcs+=radius*(math.pi-theta)
 for i,d in enumerate(distances):assert trims[i]+trims[i+1]<d-1e-6
 return sum(distances)-2*sum(trims)+arcs

def main():
 if (H/'packed/delta-6/16mm/audit.json').exists():assert read(H/'packed/delta-6/17mm/gates.json')['all_gates_pass']
 # Changes to routing never weaken the inherited audit or classification.
 def audit_functions(path):
  tree=ast.parse(path.read_text())
  return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('reason','audit')}
 assert audit_functions(H/'study.py')==audit_functions(H.parent/'issue-244-height-search/study.py')
 for rel,digest in read(H/'inputs-sha256.json').items():assert sha(R/rel)==digest,rel
 for rel,digest in read(H/'artifact-sha256.json').items():assert sha(H/rel)==digest,rel
 for folder in sorted((H/'packed').glob('delta-*')):
  for p in sorted(folder.glob('*mm')):
   if not (p/'audit.json').exists():continue
   d=read(p/'measurements.json');a=read(p/'audit.json');idx=read(p/'assembly-index.json')
   assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
   assert a['geometry_index_sha256']==sha(p/'assembly-index.json')
   n=len(idx);assert n==a['assembly_solids'] and a['total_pairs']==n*(n-1)//2
   ex={(r['i'],r['j']) for r in a['exact_results']};it={(r['i'],r['j']) for r in a['intended_pairs']}
   assert len(ex)==a['exact_candidates']==len(a['exact_results']) and not ex&it
   rej=0;needed=set()
   for i,j in itertools.combinations(range(n),2):
    ab=idx[i]['bounds'];bb=idx[j]['bounds']
    if any(min(ab[1][k],bb[1][k])-max(ab[0][k],bb[0][k])<=1e-7 for k in range(3)):rej+=1
    else:needed.add((i,j))
   assert needed==ex|it and rej==a['aabb_rejected_pairs']
   assert a['total_pairs']==rej+len(ex)+len(it)
   assert len(a['boolean_errors'])==sum('error' in x for x in a['exact_results'])
   assert a['interference_zero']==(not a['boolean_errors'] and not a['unexpected_interferences'])
   assert len(read(p/'collision-map.json'))==len(a['unexpected_interferences'])
   for w in d['wings']:
    assert w['represented_reserve_mm']>=30-1e-8 and w['unmodeled_length_mm']==0
    assert len(w['conductor_lengths_mm'])==len(w['conductor_waypoints_mm'])==14
    assert max(w['conductor_lengths_mm'])==w['longest_conductor_mm']
    assert min(w['per_conductor_reserve_mm'])>=30
    for length,ref,reserve in zip(w['conductor_lengths_mm'],w['reference_conductor_lengths_mm'],w['per_conductor_reserve_mm']):
     assert abs(length-ref-reserve)<1e-8 and abs(reserve-30.2)<1e-7
    for length,pts in zip(w['conductor_lengths_mm'],w['conductor_waypoints_mm']):
     assert abs(rounded_length(pts)-length)<1e-6
     refpts=[p[:] for p in pts];refpts[4][1]=refpts[5][1]=7
     assert abs(length-rounded_length(refpts)-30.2)<1e-6
     assert pts[0][1:]==[-35.45,8.4] and pts[-1][2]==12.8
   f=d['fly'];assert f['solid_count']==1 and abs(f['connected_length_mm']-170)<1e-6 and abs(f['volume_mm3']-170*math.pi)<1e-3
   assert d['cover_top_z_mm']==16.2+d['delta_mm']
   assert read(p/'invariants.json')['fly_scope_unchanged']
   gates=read(p/'gates.json');assert gates['all_gates_pass']==all(gates['gates'].values())
   assert gates['gates']['1_zero_interference']==a['interference_zero']
   assert all(w['accessible_reserve_certified']==gates['gates']['2_accessible_service'] for w in d['wings'])
   assert gates['gates']['6_conductor_200mm']==all(w['longest_conductor_mm']<=200 for w in d['wings'])
   assert a['tolerance_volume_mm3']==1e-6
   if gates['all_gates_pass']:
    assert all(q['valid'] and q['solids']==1 and q['within_220x220x250'] for q in read(p/'metrology.json')['printing'].values())
   assert len(a['exact_results'])+len(a['intended_pairs'])+a['aabb_rejected_pairs']==a['total_pairs']
   assert d['main_rev7_sha256']==sha(R/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb')
   m=read(p/'metrology.json')
   assert m['geometry_index_sha256']==sha(p/'assembly-index.json')
   for filename,digest in m['delivered_sha256'].items():assert sha(p/filename)==digest
   for side,wm in m['wings'].items():
    if 'reused_from_pitch_mm' in wm:
     peer=p.parent/f"{wm['reused_from_pitch_mm']}mm";pi=read(peer/'assembly-index.json')
     assert wm['source_geometry_index_sha256']==sha(peer/'assembly-index.json')
     def sig(index):return [(r['name'],r['solid'],r['brep_sha256']) for r in index if r['name'].startswith('Wing-'+side)]
     assert sig(idx)==sig(pi)
     assert wm['identical_constituent_sha256']==[t[2] for t in sig(idx)]
     assert sha(p/f'wing-{side}.step')==sha(peer/f'wing-{side}.step')
   assert m['cover']['valid'] and m['cover']['solids']==1 and m['cover']['volume_difference_mm3']<1e-3
   sv=read(p/'service.json')
   assert sv['continuous_motion_bounded'] and sv['volume_threshold_mm3']==1e-6
   if gates['gates']['2_accessible_service']:
    assert sv['pass_clearance'] and all(not r['unexpected_contacts'] for r in sv['sides'])
    assert all(all(r['valid'] and r['solids']==1 and r['nondecreasing'] for r in v['merge_checks']) for v in m['wings'].values())
   if not all(v['valid'] and v['solids']==1 for v in m['wings'].values()):assert not gates['gates']['2_accessible_service']
   print(folder.name,p.name,'complete audit',a['total_pairs'],'pairs;',len(a['unexpected_interferences']),'unexpected contacts;',len(a['boolean_errors']),'errors; interference_zero=',a['interference_zero'])
 print('Evidence verification PASS; CAD acceptance only, no production release.')
if __name__=='__main__':main()
