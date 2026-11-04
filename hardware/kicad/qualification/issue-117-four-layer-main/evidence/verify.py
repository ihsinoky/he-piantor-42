"""Submission audit. Read-only against baseline and all historical evidence."""
from common import *
import ast,collections
base=json.loads((E/'preflight.json').read_text())['base']
bad=[];count=0
for row in subprocess.check_output(['git','--git-dir='+GIT,'ls-tree','-r','-z',base]).split(b'\0'):
 if not row:continue
 meta,name=row.split(b'\t');_,typ,h=meta.decode().split()
 if typ!='blob':continue
 p=R/os.fsdecode(name);data=p.read_bytes()
 if hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()!=h:bad.append(os.fsdecode(name))
 count+=1
assert not bad,bad
assert subprocess.run(['git','--git-dir='+GIT,'merge-base','--is-ancestor',base,'HEAD']).returncode==0
staged=subprocess.check_output(['git','--git-dir='+GIT,'diff','--cached','--name-status',base],text=True).splitlines()
for row in staged:
 status,path=row.split('\t',1)
 assert status=='A' and (path=='docs/issue-117-four-layer-main-and-wing-outlook.md' or path.startswith('hardware/kicad/qualification/issue-117-four-layer-main/')),row
native=json.loads((E/'native-equivalence.json').read_text())
for stage in ['main','smoke']:
 w=E/'inputs'/stage;d=native['inputs'][stage]
 assert sha(w/'original.kicad_pcb')==d['original_pcb_sha256']
 assert sha(w/'main.kicad_pcb')==d['four_layer_pcb_sha256']
 assert sha(w/'main.kicad_pro')==sha(w/'original.kicad_pro')==d['original_project_sha256']
 assert json.loads((w/'dsn-projection.json').read_text())['exact_projected_AST_equals_previously_verified_DSN']
 for policy in ['default','explicit']:
  cfg=json.loads((E/'configuration'/f'{stage}-{policy}.json').read_text());assert cfg['routing_started'] is False
 assert json.loads((w/'fab-readback.json').read_text())['routingStarted'] is False
assert native['inputs']['main']['zone_requirement_pass'] is True
assert native['inputs']['smoke']['native_net_names']==['N']
assert native['inputs']['smoke']['zone_requirement_pass'] is False
gate=json.loads((E/'equivalence-gate.json').read_text());assert gate['pass_equivalence'] is False
assessment=json.loads((E/'assessment.json').read_text())
for row in assessment['stage1'].values():
 assert row['runs']==0 and all(v is None for v in row['independent_metrics'].values())
assert not list(E.rglob('*.ses')) and not list(E.rglob('out.kicad_pcb'))
assert not (E/'readback-never-written.kicad_pcb').exists()
assert not (E/'runs').exists()
wing=json.loads((E/'wing-outlook.json').read_text());assert wing['consumed_layout_paths']==[] and wing['routing_runs']==0
assert all(sha(R/p)==h for p,h in wing['source_hashes'].items())
# All process invocations are preparation, parsing, trace-aborted resolver or snapshot.
records=[]
for p in sorted((E/'processes').glob('*/record.json')):
 d=json.loads(p.read_text());assert d['headless'];records.append(dict(name=p.parent.name,exit_code=d['exit_code'],elapsed_seconds=d['elapsed_seconds']))
assert [r['name'] for r in records if r['exit_code']!=0]==['prepare-four-layer']
authored=[];json_count=0
for p in E.rglob('*'):
 if p.suffix=='.json':json.loads(p.read_text());json_count+=1
 if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
 if p.suffix in ['.py','.ts']:
  assert not any(line.rstrip()!=line for line in p.read_text().splitlines()),p
  authored.append(str(p.relative_to(R)))
for p in [R/'docs/issue-117-four-layer-main-and-wing-outlook.md',E.parent/'README.md']:
 assert not any(line.rstrip()!=line for line in p.read_text().splitlines()),p
 authored.append(str(p.relative_to(R)))
assert not list(E.rglob('*.so')) and not list(E.rglob('*.pyc'))
save(E/'verification.json',dict(utc=utc(),pass_audit=True,qualification_pass=False,base=base,base_files_checked=count,base_mismatches=bad,allowed_new_paths=['docs/issue-117-four-layer-main-and-wing-outlook.md','hardware/kicad/qualification/issue-117-four-layer-main/'],native_and_DSN_readbacks_verified=True,stage0_gate_closed=True,router_execution_count=0,independent_metrics_all_null=True,wing_analysis_only=True,wing_allowlist_hashes_unchanged=True,json_files_valid=json_count,python_AST_and_authored_whitespace_pass=True,authored_files=authored,processes=records,known_preparation_failure='Initial KiCad save normalized paste rectangle endpoints. Exact identity gate rejected it; final preparation transplants only the filled zone into the text-local layer/stackup addition.',tools_not_bundled=True))
save(E/'manifest.json',{str(p.relative_to(E)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(E.rglob('*')) if p.is_file() and p.name!='manifest.json'})
print('Audit PASS; qualification remains STAGE_0_STOP; routing count 0.')
