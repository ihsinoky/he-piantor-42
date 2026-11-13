"""Independent no-CAD hash, all-pairs coverage and gate-evidence verification."""
from pathlib import Path
import hashlib,json,itertools,math
H=Path(__file__).resolve().parent;R=H.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for rel,digest in read(H/'inputs-sha256.json').items():assert sha(R/rel)==digest,rel
 for rel,digest in read(H/'artifact-sha256.json').items():assert sha(H/rel)==digest,rel
 for folder in sorted(H.glob('delta-*')):
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
   f=d['fly'];assert f['solid_count']==1 and abs(f['connected_length_mm']-170)<1e-6 and abs(f['volume_mm3']-170*math.pi)<1e-3
   assert d['cover_top_z_mm']==16.2+d['delta_mm']
   assert read(p/'invariants.json')['fly_scope_unchanged']
   gates=read(p/'gates.json');assert gates['all_gates_pass']==all(gates['gates'].values())
   assert gates['gates']['1_zero_interference']==a['interference_zero']
   assert len(a['exact_results'])+len(a['intended_pairs'])+a['aabb_rejected_pairs']==a['total_pairs']
   assert d['main_rev7_sha256']==sha(R/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb')
   m=read(p/'metrology.json');assert m['cover']['valid'] and m['cover']['solids']==1 and m['cover']['volume_difference_mm3']<1e-3
   if not all(v['valid'] and v['solids']==1 for v in m['wings'].values()):assert not gates['gates']['2_accessible_service']
   print(folder.name,p.name,'complete audit',a['total_pairs'],'pairs;',len(a['unexpected_interferences']),'unexpected contacts;',len(a['boolean_errors']),'errors; interference_zero=',a['interference_zero'])
 print('Evidence verification PASS; this does not convert a rejected assembly into a feasible design.')
if __name__=='__main__':main()
