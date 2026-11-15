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
 tuning=read(H/'tuning-round-sha256.json')
 for n,digest in tuning['files'].items():assert sha(H/'tuning-round'/n)==digest,('tuning-round changed',n)
 assert set(tuning['files'])=={str(p.relative_to(H/'tuning-round')) for p in (H/'tuning-round').rglob('*') if p.is_file() and '__pycache__' not in str(p)}
 frozen_round3=read(H/'round3-sha256.json')
 for n,digest in frozen_round3['files'].items():assert sha(H/'round3'/n)==digest,('round3 changed',n)
 assert set(frozen_round3['files'])=={str(p.relative_to(H/'round3')) for p in (H/'round3').rglob('*') if p.is_file()}
 frozen_round4=read(H/'round4-sha256.json')
 for n,digest in frozen_round4['files'].items():assert sha(H/'round4'/n)==digest,('round4 changed',n)
 assert set(frozen_round4['files'])=={str(p.relative_to(H/'round4')) for p in (H/'round4').rglob('*') if p.is_file()}
 frozen_round5=read(H/'round5-sha256.json')
 for n,digest in frozen_round5['files'].items():assert sha(H/'round5'/n)==digest,('round5 changed',n)
 assert set(frozen_round5['files'])=={str(p.relative_to(H/'round5')) for p in (H/'round5').rglob('*') if p.is_file()}
 covered=set(read(H/'artifact-sha256.json'))
 actual={str(p.relative_to(H)) for p in H.rglob('*') if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in str(p)}
 assert covered==actual,('manifest coverage',covered.symmetric_difference(actual))
 for p in H.glob('*.py'):compile(p.read_text(),str(p),'exec')
 pinmap=read(H/'pinmap-round4.json');assert pinmap['passed'] and len(pinmap['wires'])==28
 assert pinmap['routes_sha256']==sha(H/'routes-round4.json')
 assert all(r['wing_pin']==r['main_pin']==r['wire'] and r['passed'] for r in pinmap['wires'])
 round5_pinmap=read(H/'pinmap-round5.json');assert round5_pinmap['routes_sha256']==sha(H/'routes-round5.json')
 current_pinmap=read(H/'pinmap-round6.json')
 assert current_pinmap['passed'] and len(current_pinmap['wires'])==28
 assert current_pinmap['routes_sha256']==sha(H/'routes-round6.json')
 for new,old in zip(current_pinmap['wires'],pinmap['wires']):
  assert new['wing_pin']==new['main_pin']==new['wire'] and new['passed']
  assert new['wing_endpoint_mm']==old['wing_endpoint_mm'] and new['main_endpoint_mm']==old['main_endpoint_mm']
 from verify_round6_framework import verify_paths,verify_fixed,verify_comparisons
 verify_paths()
 summary=[]
 for pitch in (17,16):
  verify_fixed(pitch);verify_comparisons(pitch)
  out=H/f'{pitch}mm';idx=read(out/'assembly-index.json');physical=[r for r in idx if not r['name'].startswith('USB-reference-')];a=read(out/'audit.json')
  assert a['geometry_sha256']==sha(out/'assembly-index.json')
  assert len(a.get('wire_sweep_checks',[]))==28
  for r in a['wire_sweep_checks']:
   wire=next(w for w in physical if w['name']==r['part'])
   assert abs(wire['volume_mm3']-r['volume_mm3'])<1e-6
   assert abs(r['volume_error_mm3']-abs(r['volume_mm3']-r['expected_volume_mm3']))<1e-6
   assert r['passed']==(r['volume_error_mm3']<.001)
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
  accepted=[]
  old_fly=[r for r in read(H/f'round3/{pitch}mm/assembly-index.json') if r['name']=='Fly-official-42-instance-42']
  for r in a['invalid_solids']:
   is_known=r['name']=='Fly-official-42-instance-42' and len(old_fly)==1 and r['sha256']==old_fly[0]['sha256']
   assert r['accepted_source_model_defect']==is_known
   if is_known:assert r['classification']=='KNOWN_SOURCE_MODEL_DEFECT_F-015_D-037'
   accepted.append(is_known)
  assert a['passed']==(not a['unexpected_interferences'] and not a['boolean_errors'] and all(accepted) and all(r['passed'] for r in a['wire_sweep_checks']))
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
  seatpath=out/'tray-seating-relief.json'
  if seatpath.exists():
   seat=read(seatpath);assert seat['geometry_sha256']==a['geometry_sha256']
   parent=read(out/'E-boss-audit-parent.json');before=read(out/parent['index_file'])
   assert sha(out/parent['index_file'])==seat['previous_geometry_sha256']==parent['geometry_sha256']
   assert len(before)==len(idx)
   unchanged=[]
   for i,(old,new) in enumerate(zip(before,idx)):
    if new['name'] not in ('tray-left','tray-right'):
     assert old==new;unchanged.append(dict(index=i,name=new['name'],sha256=new['sha256']))
   assert seat['unchanged_operands']==unchanged
   seamproof=read(out/'seam.json');assert seamproof['previous_geometry_sha256']==seat['previous_geometry_sha256']
   assert seamproof['geometry_sha256']==seat['geometry_sha256'] and 'geometry_rebind_proof' in seamproof
   for r in seat['changes']:
    old=next(w for w in before if w['name']==r['part']);new=next(w for w in idx if w['name']==r['part'])
    assert old['sha256']==r['before_sha256'] and new['sha256']==r['after_sha256']
    assert abs(old['volume_mm3']-new['volume_mm3']-r['removed_volume_mm3'])<1e-6
    assert r['new_shell_common_mm3']<1e-6 and r['protected_palm_min_y_mm']==69.7001
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
  for check in a['wire_sweep_checks']:
   side='left' if '-left-' in check['part'] else 'right';wire=int(check['part'][-2:])-1
   conductor=next(w for w in lengths['conductors'] if w['side']==side)['all_conductors'][wire]
   assert abs(check['expected_volume_mm3']-conductor['length_mm']*math.pi*.25)<1e-6
  assert lengths['dressed_164_8_reference_only']
  assert read(out/'caps.json')['certified']
  assert not cw['solver_inconsistencies']
  assert read(out/'hardware-inventory.json')['all_E_replacements_passed']
  assert read(out/'hardware-inventory.json')['geometry_sha256']==a['geometry_sha256']
  assert read(out/'invariants.json')['passed']
  assert len(read(out/'invariants.json')['source_floor_band'])==2
  assert all(r['passed'] for r in read(out/'invariants.json')['source_floor_band'])
  gates=read(out/'gates.json');assert len(gates['gates'])==8 and not gates['production_release']
  if cw['solver_inconsistencies']:assert not gates['gates'][5]['passed']
  usb=read(out/'usb.json');service=read(out/'service.json');caps=read(out/'caps.json');inv=read(out/'invariants.json');ret=read(out/'retention-check.json')
  for data in (lengths,usb,service,caps,inv,ret):assert data['geometry_sha256']==a['geometry_sha256']
  assert [r['side'] for r in service['sides']]==['left','right']
  for result in service['sides']:
   per_side=read(out/('service-'+result['side']+'.json'))
   assert per_side['geometry_sha256']==a['geometry_sha256'] and per_side['side']==result
   assert result['passed']==(not result['unexpected'] and not result['boolean_errors'])
   assert abs(result['release_mm']-30.2)<1e-6
  assert service['geometric_motion_passed']==all(r['passed'] for r in service['sides'])
  flyhits=[r for r in a['unexpected_interferences'] if 'Fly-170mm' in (r['a'],r['b'])]
  hardware_ok=read(out/'hardware-inventory.json')['all_E_replacements_passed']
  seam=read(out/'seam.json');assert seam['geometry_sha256']==a['geometry_sha256']
  fitted=a['passed'] and hardware_ok and seam['ownership_passed'] and seam['plate_contact_passed']
  expected=[fitted,all(r['passed'] for r in lengths['conductors']),fitted and service['geometric_motion_passed'] and inv['passed'] and ret['local_geometry_passed'],lengths['fly']['passed'] and not flyhits,usb['passed'],caps['certified'] and caps['passed'] and not cw['solver_inconsistencies'],verification['passed'] and all(r['envelope_passed'] for r in prints['parts']) and seam['skin_passed'] and inv['passed'],verification['preview_exists'] and verification['preview_inventory_passed']]
  assert [g['passed'] for g in gates['gates']]==expected
  assert service['accessible_reserve_certified']==expected[2]

  summary.append(dict(pitch_mm=pitch,solids=len(physical),all_pairs=a['total_pairs'],unexpected=len(a['unexpected_interferences']),boolean_operation_errors=len(a['boolean_errors']),manufacturing_checks_passed=sum(c['passed'] for c in checks.values()),gates=[g['passed'] for g in gates['gates']]))
 print(json.dumps(dict(artifact_and_input_hashes='PASS',independent_pair_coverage='PASS',pitches=summary),indent=2))
if __name__=='__main__':run()
