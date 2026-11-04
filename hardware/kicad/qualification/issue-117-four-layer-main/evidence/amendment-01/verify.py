"""Final independent evidence audit, with no routing or copper mutation."""
from helpers import *
import ast
base=json.loads((E/'preflight.json').read_text())['base'];prior='7917d82'
failures=[];base_files=0
for row in subprocess.check_output(['git','--git-dir='+GIT,'ls-tree','-r','-z',base]).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');_,typ,h=meta.decode().split()
 if typ!='blob':continue
 p=R/os.fsdecode(name);data=p.read_bytes()
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=h:failures.append(os.fsdecode(name))
 base_files+=1
assert not failures,failures
# Every previously submitted evidence byte is preserved except the Issue README.
prior_changed=[];prior_checked=0
for row in subprocess.check_output(['git','--git-dir='+GIT,'ls-tree','-r','-z',prior,'--',str(E.relative_to(R))]).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');_,typ,h=meta.decode().split()
 if typ!='blob':continue
 p=R/os.fsdecode(name);data=p.read_bytes()
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=h:prior_changed.append(os.fsdecode(name))
 prior_checked+=1
assert not prior_changed,prior_changed
reuse=json.loads((A/'main-reuse-and-runtime-revalidation.json').read_text())
for path,row in reuse['files'].items():assert sha(E/path)==row['sha256']
# Old source identity manifests are checked again after both runs.
runtime=[]
for issue,filename,root in [('113','source-manifest.json',KRT),('113','inspection-runtime-hashes.json',RT),('103','source-manifest.json',FAB)]:
 folder={'113':'issue-113-kicad-routing-tools-falsification','103':'issue-103-fab-router-falsification'}[issue]
 hashes=json.loads((R/'hardware/kicad/qualification'/folder/'evidence'/filename).read_text())
 assert all((root/p).exists() and sha(root/p)==h for p,h in hashes.items())
 runtime.append(dict(manifest=folder+'/'+filename,files=len(hashes),all_equal=True))
smoke=json.loads((A/'smoke-gate.json').read_text());assert smoke['pass']
for router,row in smoke['checks'].items():
 assert sha(A/'inspection/smoke-02'/router/'independent.json')==row['independent_result_sha256']
 assert all(v==0 for v in row['metrics'].values())
assert smoke['utc']<'2026-11-04T09:52:54+00:00'
equiv=json.loads((A/'equivalence-gate-02.json').read_text());assert equiv['pass_equivalence']
assessment=json.loads((A/'assessment.json').read_text());routes=[]
for router in ['fab','krt']:
 row=assessment['stage1'][router];assert row['main_runs']==1 and not row['existing_rule_floor_decreases']
 rec=json.loads((E/'processes'/('amend01-main-'+router+'-route')/'record.json').read_text())
 assert smoke['utc']<rec['start_utc'] and rec['exit_code']==0 and not rec['timed_out'] and rec['headless']
 assert rec['end_utc']<'2026-11-04T11:22:54+00:00'
 assert row['plane_role_pass'] and row['tracks_per_layer'].get('In1.Cu',0)==0
 if row['unconnected_count']>0:assert all(v is None for v in row['independent_metrics'].values())
 assert set(row['width_distribution'])=={'0.2'} and all(k=='0.6/0.3' for k in row['via_distribution'])
 w=A/'runs/main'/router
 assert sha(w/'in.kicad_pcb')==sha(E/'inputs/main/main.kicad_pcb') and sha(w/'corrected.dsn')==sha(E/'inputs/main/corrected.dsn')
 assert sha(w/'in.kicad_pro')==sha(E/'inputs/main/main.kicad_pro')
 # The complete command and driver match the smoke execution; only paths change.
 smoke_rec=json.loads((E/'processes'/('amend01-smoke-02-'+router+'-route')/'record.json').read_text())
 if router=='krt':assert rec['argv'][4:]==smoke_rec['argv'][4:]
 else:
  assert rec['argv'][:3]==smoke_rec['argv'][:3]
  effective=json.loads((w/'result.json').read_text())['report']['effectiveSettings']
  historical=json.loads((R/'hardware/kicad/qualification/issue-103-fab-router-falsification/evidence/processes/main/result.json').read_text())['report']['effectiveSettings']
  assert effective==historical
  assert json.loads((w/'requested-settings.json').read_text())==json.loads((A/'runs/smoke-02/fab/requested-settings.json').read_text())
 routes.append(dict(router=router,start=rec['start_utc'],end=rec['end_utc'],exit_code=0))
assert len(list((A/'runs/main').glob('*/launch.json')))==2
assert len(list((E/'processes').glob('amend01-main-*-route/launch.json')))==2
assert len(list((A/'runs').glob('smoke*/*/launch.json')))==4
assert assessment['stage1_restarts']==0 and not assessment['main_rebuilt']
old=(A/'report-before-amendment.md').read_text();report=(R/'docs/issue-117-four-layer-main-and-wing-outlook.md').read_text()
wing=old[old.index('## Wing：'):old.index('## D-012 改定の判断材料')]
assert wing==report[report.index('## Wing：'):report.index('## D-012 改定の判断材料')]
wingdata=json.loads((E/'wing-outlook.json').read_text());assert not wingdata['consumed_layout_paths'] and wingdata['routing_runs']==0
assert all(sha(R/path)==h for path,h in wingdata['source_hashes'].items())
# Enforce submitted scope against the previous commit and base (including staged new files).
changes=subprocess.check_output(['git','--git-dir='+GIT,'diff','--cached','--name-status',prior],text=True).splitlines()
for line in changes:
 status,path=line.split('\t',1)
 assert status in ['A','M'] and (path=='docs/issue-117-four-layer-main-and-wing-outlook.md' or path.startswith('hardware/kicad/qualification/issue-117-four-layer-main/')),line
assert changes
json_count=0;py_count=0
for p in A.rglob('*'):
 if p.suffix=='.json':json.loads(p.read_text());json_count+=1
 if p.suffix=='.py':ast.parse(p.read_text());py_count+=1
 if p.suffix in ['.py','.ts'] and p.parent==A:
  assert all(line==line.rstrip() for line in p.read_text().splitlines()),p
assert not list(A.rglob('*.pyc')) and not list(A.rglob('*.so'))
assert all(line==line.rstrip() for line in report.splitlines())
save(A/'verification.json',dict(utc=utc(),pass_audit=True,qualification_pass=assessment['status']=='PASS',base=base,base_files_checked=base_files,base_mismatches=failures,prior_commit=prior,prior_evidence_files_checked=prior_checked,prior_evidence_changed=prior_changed,main_inputs_byte_identical=True,main_hashes_unchanged=True,runtime_hashes=runtime,smoke_gate_pass=True,smoke_gate_before_Main=True,smoke_gate_within_30_minutes=True,Main_each_once=True,Main_restarts=0,Main_settings_unchanged=True,main_route_records=routes,Main_In1_signal_tracks_zero=True,unfinished_metrics_null=True,output_project_floor_relaxations_zero=True,wing_section_verbatim=True,wing_new_runs=0,wing_source_hashes_unchanged=True,staged_scope=changes,json_files_valid=json_count,python_AST_files_valid=py_count,authored_whitespace_pass=True,tools_not_bundled=True))
# This manifest covers both historical and new evidence, excluding itself.
save(A/'manifest.json',{str(p.relative_to(E)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p!=A/'manifest.json'})
print('AUDIT PASS; qualification:',assessment['status'])
