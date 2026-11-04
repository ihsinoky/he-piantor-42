"""Repair submission audit; reads evidence only, never re-executes a gate or route."""
from common import *
import ast,sys
sys.path.insert(0,str(T/'geometry/lib/python3.12/site-packages'))
import sexpdata as sx
git=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
base='96166d3f266f6d423173fcd8cdc3a38a46a6767d';initial='0e82629f7857a3c4590b28039b835f3425367f7b'
count=0
for row in subprocess.check_output(git+['ls-tree','-rz',base]).split(b'\0'):
 if not row:continue
 header,path=row.split(b'\t',1);mode,kind,sha=header.decode().split();assert kind=='blob';f=R/os.fsdecode(path)
 data=os.fsencode(os.readlink(f)) if mode=='120000' else f.read_bytes()
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==sha,str(f)
 count+=1
prefix=str(E.relative_to(R))+'/'
original_files=subprocess.check_output(git+['ls-tree','-r','--name-only',initial,'--',prefix],text=True).splitlines()
for name in original_files:
 old=subprocess.check_output(git+['show',initial+':'+name]);local=E/'initial-run'/Path(name).relative_to(E.relative_to(R))
 assert local.read_bytes()==old,str(local)
 if name.endswith(('.py','.ts')) and not name.endswith('/build-inputs.py'):assert (R/name).read_bytes()==old,name
assert (R/'docs/issue-129-wing-2layer-routing.md').read_bytes().startswith((E/'initial-run/report.md').read_bytes())
assert digest(E/'check-equivalence.py')==digest(E/'initial-run/check-equivalence.py')
old=json.loads((E/'initial-run/equivalence-gate.json').read_text());new=json.loads((E/'equivalence-gate.json').read_text())
assert old['pass_equivalence'] is False and not old['boards'];assert new['pass_equivalence'] and len(new['boards'])==3
gates=[p for p in (E/'processes').glob('*/record.json') if any(str(x).endswith('/check-equivalence.py') for x in json.loads(p.read_text())['argv'])];assert len(gates)==2
assert json.loads((E/'processes/repair-equivalence/record.json').read_text())['exit_code']==0
for name,files in json.loads((E/'input-hashes.json').read_text()).items():
 for f,h in files.items():assert digest(E/'inputs'/name/f)==h
assessment=json.loads((E/'assessment.json').read_text());assert assessment['gate_attempts']==2 and assessment['gate_pass'] and assessment['routing_started']
cells=['KRT-smoke','FAB-smoke','KRT-16','KRT-17','FAB-16','FAB-17']
previous_end=None;ses_path_counts={}
for cell in cells:
 w=E/'runs'/cell;assert w.exists();assert len(list((E/'processes').glob(cell+'-route/record.json')))==1
 rec=json.loads((E/'processes'/(cell+'-route')/'record.json').read_text());assert not rec['timed_out']
 if previous_end is not None:assert datetime.datetime.fromisoformat(rec['start_utc'])>=previous_end
 previous_end=datetime.datetime.fromisoformat(rec['end_utc'])
 assert datetime.datetime.fromisoformat(rec['end_utc'])<datetime.datetime(2026,11,4,23,56,tzinfo=datetime.timezone.utc)
 exe=json.loads((w/'execution.json').read_text());assert exe['input_unchanged'] and exe['project_unchanged']
 check=json.loads((E/'inspection'/cell/'assessment.json').read_text());assert assessment['cells'][cell]['metrics']==check['metrics']
 if check['measured_unconnected']:assert all(v is None for v in check['metrics'].values()) and not check['pass_acceptance']
 if cell.startswith('KRT'):
  eff=json.loads((w/'effective.json').read_text());assert eff['routing_started'] is False and eff['policy']=='off';assert eff['cli_namespace']['escalation']=='off'
 else:
  result=json.loads((w/'result.json').read_text());assert result['report']['effectiveSettings']['timeBudgetMs']==1800000
  assert json.loads((w/'import-result.json').read_text())['exit_code']==0
  def all_paths(node):
   if not isinstance(node,list) or not node:return []
   if str(node[0])=='path':return [node]
   return [p for child in node for p in all_paths(child)]
  paths=all_paths(sx.loads((w/'out.ses').read_text()))
  width=json.loads((E/'inspection'/cell/'width-audit.json').read_text())
  assert len(paths)==len(width['ses_paths']),cell
  ses_path_counts[cell]=len(paths)
json_count=py_count=0
for f in E.rglob('*'):
 if not f.is_file():continue
 assert f.suffix not in ['.so','.pyc','.deb','.zip'] and 'node_modules' not in f.parts
 if f.suffix=='.json':json.loads(f.read_text());json_count+=1
 if f.suffix=='.py':ast.parse(f.read_text(),filename=str(f));py_count+=1
assert subprocess.check_output(git+['rev-parse','--abbrev-ref','HEAD'],text=True).strip()=='issue-129-wing-2layer-routing'
for path in subprocess.check_output(git+['diff','--name-only',base],text=True).splitlines():assert path=='docs/issue-129-wing-2layer-routing.md' or path.startswith(prefix),path
save(E/'repair-verification.json',dict(utc=now(),base_files_verified_byte_identical=count,initial_committed_evidence_files_preserved=len(original_files),initial_report_preserved_as_prefix=True,only_existing_code_change='build-inputs.py',gate_code_byte_identical=True,gate_attempts=2,repair_gate_single_run=True,repair_gate_all_three_boards_pass=True,single_route_run_per_path=True,all_six_paths_run=True,route_order_as_instructed=True,all_imports_successful=True,all_serialized_ses_paths_covered=ses_path_counts,input_hashes_valid=True,json_files=json_count,python_files=py_count,no_runtime_packages_in_submission=True))
save(E/'manifest.json',{str(f.relative_to(E)):dict(bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(E.rglob('*')) if f.is_file() and f.name!='manifest.json'})
print((E/'repair-verification.json').read_text())
