"""Verify the terminal stop and unchanged qualified fallback, not candidate acceptance."""
from common import *
import collections,csv,zipfile
base='c741ade9550157333443784b90e2fe66f95ca297'
G=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
assert subprocess.check_output(G+['branch','--show-current'],text=True).strip()=='issue-173-main-dual-wing-final'
receipt=json.loads((E/'preflight-receipt.json').read_text());drc=json.loads((E/'preflight.json').read_text())
assert not receipt['pass_preflight'] and not receipt['routing_allowed']
assert receipt['board_sha256']==digest(E/'inputs/final/main.kicad_pcb')
assert receipt['project_sha256']==digest(E/'inputs/final/main.kicad_pro')
assert receipt['drc_sha256']==digest(E/'preflight.json')
assert collections.Counter(v['type'] for v in receipt['blocking_violations'])=={'clearance':1,'solder_mask_bridge':1}
assert not (E/'runs').exists() and not (E/'attempt-reserved.json').exists()
assert not list((E/'processes').glob('*krt-route*'))
guard=json.loads((E/'processes/guard-rejection/record.json').read_text())
assert guard['exit_code']==1 and 'assert receipt' in (E/'processes/guard-rejection/stderr').read_text()
assert json.loads((E/'processes/preflight-drc/record.json').read_text())['exit_code']==0
placement=json.loads((E/'placement-check.json').read_text())
assert set(placement['changed_footprints'])=={'C26'} and placement['all_seed_segments_and_vias_byte_canonical_identical']
assert placement['C26_to_SW2_seed_min_copper_gap_mm']>.1 and placement['C26_pad2_to_J3_pad15_overlap_mm2']>0
runtime=json.loads((E/'runtime-check.json').read_text());assert runtime['source_files']==2055 and not runtime['mismatches']
changes=subprocess.check_output(G+['diff','--name-only',base,'--'],text=True).splitlines()
allowed=[str(E.relative_to(R))+'/', 'docs/issue-173-main-dual-wing-final.md']
assert all(x.startswith(allowed[0]) or x==allowed[1] for x in changes),changes
provenance=json.loads((E/'fallback-provenance.json').read_text());n=0
for rel,row in provenance['byte_identical_copies'].items():
 target=E/rel;source=R/row['source'];blob=subprocess.check_output(G+['show',base+':'+row['source']])
 assert digest(target)==digest(source)==row['sha256']==hashlib.sha256(blob).hexdigest(),rel
 n+=1
f=E/'fallback-seed-a';board=f/'inspection/final/main.kicad_pcb';h=digest(board)
assert h=='19da98f4804c0117e7dd2b6606a8ddf02e0f3c263d1c14d5696beab10febc176'
assessment=json.loads((f/'inspection/final/assessment.json').read_text());assert assessment['pass_acceptance'] and assessment['all_44_nets_checked']
assert all(v==0 for v in assessment['metrics'].values())
graph=json.loads((f/'inspection/final/connectivity.json').read_text());assert graph['nets_checked']==44 and graph['required_unconnected']==graph['wrong_net_contacts']==0
assert json.loads((f/'circuit-check-final.json').read_text())['PCB_sha256']==h
for name in ['cam-check.json','export-provenance.json','pofv-reclassification-seed-a.json']:
 data=json.loads((f/name).read_text());assert data.get('source_sha256',data.get('board_sha256'))==h
bom=list(csv.DictReader((f/'manufacturing-seed-a-review/BOM.csv').open()));cpl=list(csv.DictReader((f/'manufacturing-seed-a-review/CPL.csv').open()))
assert len(bom)==len(cpl)==58
assert {x['Comment'] for x in bom if x['Designator'] in ['C26','C27','C28']}=={'GRM21BC81C226ME44L'}
with zipfile.ZipFile(f/'manufacturing-seed-a-review/main-stage2-fabrication-review.zip') as z:assert z.testzip() is None
save(E/'verification.json',dict(utc=now(),evidence_integrity_pass=True,candidate_qualified=False,preflight_failure_stopped_before_router=True,guard_negative_test_pass=True,global_routing_count=0,local_routing_count=0,placement_and_seed_integrity=True,source_files_checked=2055,unchanged_fallback_files_checked_against_base_Git_blobs=n,fallback_board_sha256=h,fallback_inherited_metrics=assessment['metrics'],fallback_nets_checked=44,matching_0805_BOM_CPL_rows=58,review_CAM_zip_integrity=True,prior_tracked_files_unchanged=True,forbidden_actions=[]))
save(E/'status.json',dict(utc=now(),state='stopped_preflight_failure_seed_a_handoff',issue_complete=False,candidate_qualified=False,reason='C26 move cleared SW2 but overlapped J3.15; mandatory preflight stop honored',global_runs=0,global_limit=1,local_runs=0,unused_routing_allowance_is_not_resume_authorization=True,selected_handoff='fallback-seed-a (qualified 0805, known output-capacitance limitation)',new_qualified_1210_board=False,new_resistance_extraction=False,new_manufacturing_data=False,new_POFV_classification=False,final_PCBA_quote_confirmed=False,final_PCBA_quote_total=None,manufacturing_GO=False,order=False,billing=False,merge=False,D019_relaxed=False))
files=[p for p in E.rglob('*') if p.is_file() and p.name!='manifest.json' and 'processes' not in p.relative_to(E).parts and p.name not in ['publication.json']]
files.append(R/'docs/issue-173-main-dual-wing-final.md')
save(E/'manifest.json',{str(p.relative_to(R)):digest(p) for p in sorted(files)})
print('PASS evidence integrity; preflight FAIL; router runs 0; unchanged seed-a handoff files',n)
