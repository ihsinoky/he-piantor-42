"""Dependency-free final hashes and independent exhaustive-pair coverage replay."""
import json,hashlib,itertools,math
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
 for manifest,root in [(H/'artifact-sha256.json',H),(H/'inputs-sha256.json',R)]:
  for name,digest in read(manifest).items():assert sha(root/name)==digest,(manifest.name,name)
 frozen=read(H/'first-candidate-sha256.json')
 for n,digest in frozen['files'].items():assert sha(H/'first-candidate'/n)==digest,('first-candidate changed',n)
 assert set(frozen['files'])=={str(p.relative_to(H/'first-candidate')) for p in (H/'first-candidate').rglob('*') if p.is_file()}
 covered=set(read(H/'artifact-sha256.json'))
 actual={str(p.relative_to(H)) for p in H.rglob('*') if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in str(p)}
 assert covered==actual,('manifest coverage',covered.symmetric_difference(actual))
 for p in H.glob('*.py'):compile(p.read_text(),str(p),'exec')
 summary=[]
 for pitch in (17,16):
  out=H/f'{pitch}mm';idx=read(out/'assembly-index.json');physical=[r for r in idx if not r['name'].startswith('USB-reference-')];a=read(out/'audit.json')
  assert a['geometry_sha256']==sha(out/'assembly-index.json')
  assert a['all_pairs_enumerated'] and a['all_exact_candidates_completed']
  assert a['assembly_solids']==len(physical)
  broad=set();rejected=0
  for i,j in itertools.combinations(range(len(physical)),2):
   aa=physical[i]['bounds'];bb=physical[j]['bounds']
   if any(min(aa[1][k],bb[1][k])-max(aa[0][k],bb[0][k])<=1e-7 for k in range(3)):rejected+=1
   else:broad.add((i,j))
  intended={(r['i'],r['j']) for r in a['intended_pairs']};exact={(r['i'],r['j']) for r in a['exact_results']}
  assert not intended.intersection(exact)
  assert intended.union(exact)==broad
  assert len(exact)==a['exact_candidates']==len(a['exact_results'])
  assert rejected==a['aabb_rejected_pairs']
  assert a['total_pairs']==math.comb(len(physical),2)==rejected+len(broad)
  positive={(r['i'],r['j']) for r in a['exact_results'] if r.get('volume_mm3',0)>1e-6}
  listed={(r['i'],r['j']) for r in a['unexpected_interferences']+a['clearance_reservation_overlaps']}
  assert positive==listed
  for r in a['unexpected_interferences']:
   assert physical[r['i']]['name']==r['a'] and physical[r['j']]['name']==r['b']
  proof=read(out/'retention-completion.json') if (out/'retention-completion.json').exists() else None
  support=read(out/'support-restoration.json') if (out/'support-restoration.json').exists() else None
  prior_index=idx
  if support:
   prior_index=support['previous_index']
   assert hashlib.sha256((json.dumps(prior_index,indent=2,ensure_ascii=False)+'\n').encode()).hexdigest()==support['previous_geometry_sha256']
   assert support['geometry_sha256']==sha(out/'assembly-index.json')
   assert len(prior_index)==len(idx)
   for old,new in zip(prior_index,idx):
    if new['name'] not in support['changed_names']:assert old==new
  if proof:
   prefix=prior_index[:proof['unchanged_prefix_count']]
   assert hashlib.sha256((json.dumps(prefix,indent=2,ensure_ascii=False)+'\n').encode()).hexdigest()==proof['previous_geometry_sha256']
   assert [r['sha256'] for r in prefix]==proof['unchanged_operand_sha256']
   assert proof['geometry_sha256']==(support['previous_geometry_sha256'] if support else sha(out/'assembly-index.json'))
  reusepath=out/'audit-E-restoration-reuse.json'
  if reusepath.exists():
   proof=read(reusepath);assert proof['geometry_sha256']==a['geometry_sha256']
   parent=proof['parent'];oldidx=read(out/parent['index_file']);old_a=read(out/parent['audit_file'])
   assert sha(out/parent['index_file'])==parent['geometry_sha256']==old_a['geometry_sha256']
   oldphysical=[r for r in oldidx if not r['name'].startswith('USB-reference-')]
   oldresults={(r['i'],r['j']):r for r in old_a['exact_results']};newresults={(r['i'],r['j']):r for r in a['exact_results']}
   assert len(proof['reused_pairs'])==proof['reused_pair_count']
   for pair in proof['reused_pairs']:
    for k in pair:assert oldphysical[k]['sha256']==physical[k]['sha256'] and oldphysical[k]['name']==physical[k]['name'] and oldphysical[k]['solid']==physical[k]['solid']
    assert oldresults[tuple(pair)]==newresults[tuple(pair)]
  prints=read(out/'manufacturing.json');verification=read(out/'export-verification.json');checks={r['part']:r for r in verification['checks']}
  assert len(prints['parts'])==len(checks)==19
  assert verification['geometry_sha256']==sha(out/'assembly-index.json')
  for item in prints['parts']:
   stem=out/'manufacturing'/item['filename'];c=checks[item['name']]
   assert sha(stem.with_suffix('.step'))==item['step_sha256']==c['step_sha256']
   assert sha(stem.with_suffix('.stl'))==item['stl_sha256']==c['stl_sha256']
   assert stem.with_suffix('.svg').exists()
   assert stem.with_suffix('.stl').read_bytes()[:80].startswith(b'PROVISIONAL')
   if item['name'].startswith('post-'):assert item.get('free_peg_od_mm',3.15)==3.15
   else:
    fitted=[r for r in physical if r['name']==item['name']]
    assert len(fitted)==item['solids']
    assert abs(sum(r['volume_mm3'] for r in fitted)-item['volume_mm3'])<1e-4
  drawing=read(out/'manufacturing/dimension-register.json')
  assert drawing['parts']==prints['parts']
  assert sha(out/'fitted-assembly-PROVISIONAL.step')==prints['preview_sha256']
  assert verification['preview_inventory_passed'] and verification['preview_reloaded_solids']==len(physical)
  cm=read(out/'collision-map.json');assert cm['complete'] and len(cm['contacts'])==len(a['unexpected_interferences'])
  assert cm['geometry_sha256']==a['geometry_sha256']
  for witness,contact in zip(cm['contacts'],a['unexpected_interferences']):
   assert (witness['i'],witness['j'],witness['a'],witness['b'])==(contact['i'],contact['j'],contact['a'],contact['b'])
   assert 'witness_error' not in witness and 'common_bounds_mm' in witness
   assert abs(witness['replay_volume_mm3']-contact['volume_mm3'])<1e-6
  cw=read(out/'cap-witnesses.json');assert len(cw['witnesses'])==42
  assert cw['geometry_sha256']==a['geometry_sha256']
  diagnostic=read(out/'shell-diagnostics.json')
  assert diagnostic['geometry_sha256']==a['geometry_sha256']
  assert diagnostic['step_sha256']==checks['shell-central']['step_sha256']
  assert diagnostic['stl_sha256']==checks['shell-central']['stl_sha256']
  assert len(diagnostic['nonmanifold_edges'])==checks['shell-central']['mesh']['nonmanifold_edges']
  assert len(diagnostic['solids'])==checks['shell-central']['solids']
  lengths=read(out/'length-fly.json')
  for w in lengths['conductors']:
   assert len(w['all_conductors'])==14 and abs(w['minimum_reserve_mm']-30.2)<1e-6
   assert abs(w['cut_length_upper_mm']-w['longest_mm']-w['total_unrouted_wire_bound_mm'])<1e-6
   assert w['complete_cut_length_verified']
   assert w['passed']==(w['cut_length_upper_mm']<=200 and all(a['minimum_straight_slack_mm']>0 and a['minimum_bend_radius_mm']>=5-1e-7 for a in w['all_conductors']))
  assert lengths['dressed_164_8_reference_only']
  assert read(out/'caps.json')['certified']
  assert not cw['solver_inconsistencies']
  assert read(out/'hardware-inventory.json')['all_E_replacements_passed']
  assert read(out/'hardware-inventory.json')['geometry_sha256']==a['geometry_sha256']
  assert read(out/'invariants.json')['passed']
  gates=read(out/'gates.json');assert len(gates['gates'])==8 and not gates['production_release']
  if cw['solver_inconsistencies']:assert not gates['gates'][5]['passed']
  usb=read(out/'usb.json');service=read(out/'service.json');caps=read(out/'caps.json');inv=read(out/'invariants.json');ret=read(out/'retention-check.json')
  for data in (lengths,usb,service,caps,inv,ret):assert data['geometry_sha256']==a['geometry_sha256']
  flyhits=[r for r in a['unexpected_interferences'] if 'Fly-170mm' in (r['a'],r['b'])]
  hardware_ok=read(out/'hardware-inventory.json')['all_E_replacements_passed']
  expected=[a['passed'] and hardware_ok,all(r['passed'] for r in lengths['conductors']),a['passed'] and hardware_ok and service['geometric_motion_passed'] and inv['passed'] and ret['local_geometry_passed'],lengths['fly']['passed'] and not flyhits,usb['passed'],caps['certified'] and caps['passed'] and not cw['solver_inconsistencies'],verification['passed'] and all(r['envelope_passed'] for r in prints['parts']),verification['preview_exists'] and verification['preview_inventory_passed']]
  assert [g['passed'] for g in gates['gates']]==expected
  assert service['accessible_reserve_certified']==expected[2]

  summary.append(dict(pitch_mm=pitch,solids=len(physical),all_pairs=a['total_pairs'],unexpected=len(a['unexpected_interferences']),boolean_operation_errors=len(a['boolean_errors']),manufacturing_checks_passed=sum(c['passed'] for c in checks.values()),gates=[g['passed'] for g in gates['gates']]))
 print(json.dumps(dict(artifact_and_input_hashes='PASS',independent_pair_coverage='PASS',pitches=summary),indent=2))
if __name__=='__main__':run()
