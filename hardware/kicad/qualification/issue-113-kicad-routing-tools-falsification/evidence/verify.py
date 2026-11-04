"""Verify the frozen inputs, run ordering, unchanged base, scope and time box."""
import runpy,subprocess,hashlib,datetime
from pathlib import Path
E=Path(__file__).resolve().parent;globals().update(runpy.run_path(str(E/'prepare-inputs.py')))
G=['git','--git-dir=/tmp/issue-113-krt/git','--work-tree='+str(R)]
base=json.loads((E/'start.json').read_text())['base'];mismatches=[];count=0
for row in subprocess.check_output(G+['ls-tree','-rz',base]).split(b'\0'):
 if not row:continue
 meta,path=row.split(b'\t');mode,kind,sha=meta.split();p=R/path.decode();count+=1
 if not p.is_file():mismatches.append(str(p));continue
 data=p.read_bytes();s=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if s!=sha.decode():mismatches.append(str(p))
assert not mismatches,mismatches
provenance=json.loads((E/'input-provenance.json').read_text())
for path,row in provenance.items():assert digest(E/path)==digest(R/row['source'])==row['sha256']
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence']
gate=json.loads((E/'smoke-gate.json').read_text());assert gate['pass']
route_records={}
for name in ['smoke','main']:
 record=json.loads((E/f'processes/{name}-route/record.json').read_text());route_records[name]=record
 assert record['argv'][1:] == ['py_router/route.py',str(E/f'runs/{name}/in.kicad_pcb'),str(E/f'runs/{name}/out.kicad_pcb')]
 assert record['display_unset']
 for ext in ['kicad_pcb','kicad_pro']:assert digest(E/f'runs/{name}/in.{ext}')==digest(E/f'inputs/{name}/main.{ext}')
assert route_records['smoke']['end_utc'] < gate['utc'] < route_records['main']['start_utc']
for name in ['smoke','main']:
 out=E/f'runs/{name}/out.kicad_pcb'
 if out.exists():
  assert digest(out)==digest(E/f'inspection/{name}/main.kicad_pcb')
  assert digest(E/f'inputs/{name}/main.kicad_pro')==digest(E/f'inspection/{name}/main.kicad_pro')
  a=json.loads((E/f'{name}-independent.json').read_text())
  if a['measured_kicad_unconnected_items']:assert all(x is None for x in a['metrics'].values())
# No native executables, wheel/deb dependencies or caches in deliverables.
assert not [p for p in E.rglob('*') if p.is_file() and (p.suffix in ['.so','.whl','.deb','.pyc','.pyd'] or '__pycache__' in p.parts)]
now=datetime.datetime.now(datetime.timezone.utc);deadline=datetime.datetime.fromisoformat('2026-11-04T07:16:00+00:00');assert now<deadline
for row in subprocess.check_output(G+['diff','--cached','--name-status',base],text=True).splitlines():
 status,path=row.split('\t',1);assert status=='A';assert path.startswith('hardware/kicad/qualification/issue-113-kicad-routing-tools-falsification/') or path=='docs/issue-113-kicad-routing-tools-falsification.md'
save(E/'verification.json',dict(pass_verification=True,base_files_unchanged=count,input_hashes_match=True,stages=dict(smoke=1,main=1),smoke_gate_before_main=True,default_argv=True,independent_original_rules=True,added_only=True,no_runtime_binaries=True,checked_utc=now.isoformat(),elapsed_seconds=(now-datetime.datetime.fromisoformat('2026-11-04T05:16:00+00:00')).total_seconds()))
print('Frozen inputs, ordering, default argv, base immutability, original rules, scope and time box verified')
