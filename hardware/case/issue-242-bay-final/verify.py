"""No-CAD independent evidence/coverage verifier. PASS means a consistent rejection."""
from pathlib import Path
import json,hashlib,math,itertools
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 for rel,digest in read(HERE/'inputs-sha256.json').items():assert sha(ROOT/rel)==digest,rel
 for rel,digest in read(HERE/'artifact-sha256.json').items():assert sha(HERE/rel)==digest,rel
 for pitch in (16,17):
  p=HERE/f'{pitch}mm';d=read(p/'measurements.json');a=read(p/'audit.json');idx=read(p/'assembly-index.json')
  assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed'] and not a['early_stop']
  assert a['geometry_index_sha256']==sha(p/'assembly-index.json')
  n=len(idx);assert a['assembly_solids']==n and a['total_pairs']==n*(n-1)//2
  exact={(r['i'],r['j']) for r in a['exact_results']};intent={(r['i'],r['j']) for r in a['intended_pairs']}
  assert len(exact)==a['exact_candidates']==len(a['exact_results']) and not exact&intent
  rejected=0;needed=set()
  for i,j in itertools.combinations(range(n),2):
   ab=idx[i]['bounds'];bb=idx[j]['bounds']
   if any(min(ab[1][k],bb[1][k])-max(ab[0][k],bb[0][k])<=1e-7 for k in range(3)):rejected+=1
   else:needed.add((i,j))
  assert needed==exact|intent and rejected==a['aabb_rejected_pairs']
  assert a['total_pairs']==rejected+len(exact)+len(intent)
  assert a['unexpected_interferences'] and not a['interference_zero']
  contacts=read(p/'collision-map.json')
  assert len(contacts)==len(a['unexpected_interferences'])
  for mapped,hit in zip(contacts,a['unexpected_interferences']):
   assert all(mapped[k]==v for k,v in hit.items())
   assert abs(mapped['remeasured_volume_mm3']-hit['volume_mm3'])<mapped['repeat_volume_tolerance_mm3']==1e-4
   lo,hi=mapped['overlap_bounds_mm']
   assert all(lo[k]<hi[k] for k in range(3))

  # An error must never be silently counted as a zero result.
  assert len(a['boolean_errors'])==sum('error' in r for r in a['exact_results'])
  assert all(w['unmodeled_length_mm']==0 and w['represented_reserve_mm']>=30-1e-8 and w['longest_conductor_mm']<=200 for w in d['wings'])
  f=d['fly'];assert f['solid_count']==1 and abs(f['connected_length_mm']-170)<1e-6 and abs(f['volume_mm3']-170*math.pi)<1e-3
  assert all(r['valid'] and r['solids']==1 for r in d['case_deltas'])
  inv=read(p/'invariants.json');assert inv['fly_scope_unchanged']
  assert d['main_rev7_sha256']==sha(ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb')
  print(pitch,'complete coverage',a['total_pairs'],'pairs;',len(a['unexpected_interferences']),'positive overlaps;',len(a['boolean_errors']),'Boolean errors; REJECTED')
 print('Evidence verification PASS. Covered assembly feasibility FAIL. No adoption.')
if __name__=='__main__':main()
