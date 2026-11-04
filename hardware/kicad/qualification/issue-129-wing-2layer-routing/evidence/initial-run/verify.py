"""Final submission audit; no routing or gate rerun."""
from common import *
import ast
base='96166d3f266f6d423173fcd8cdc3a38a46a6767d';git=['git','--git-dir='+str(T/'git'),'--work-tree='+str(R)]
rows=subprocess.check_output(git+['ls-tree','-rz',base]).split(b'\0');changed=[];count=0
for row in rows:
 if not row:continue
 header,path=row.split(b'\t',1);mode,kind,sha=header.decode().split();assert kind=='blob';f=R/os.fsdecode(path)
 if not f.exists():changed.append(str(f));continue
 data=os.fsencode(os.readlink(f)) if mode=='120000' else f.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 if actual!=sha:changed.append(str(f))
 count+=1
assert not changed,changed
hashes=json.loads((E/'input-hashes.json').read_text())
for name,files in hashes.items():
 for f,v in files.items():assert digest(E/'inputs'/name/f)==v
assert json.loads((E/'equivalence-gate.json').read_text())['pass_equivalence'] is False
assert not json.loads((E/'equivalence-gate.json').read_text())['boards']
assessment=json.loads((E/'assessment.json').read_text());assert not assessment['routing_started'] and assessment['gate_attempts']==1
for cell in assessment['cells'].values():assert cell['runs']==0 and cell['status']=='NOT_RUN_INPUT_GATE' and cell['measured_unconnected'] is None and all(v is None for v in cell['metrics'].values())
assert not list(E.rglob('*.ses')) and not list(E.rglob('*.dsn'))
jsons=0;pys=0
for f in E.rglob('*'):
 if not f.is_file():continue
 assert f.suffix not in ['.so','.pyc','.deb','.zip'] and 'node_modules' not in f.parts
 if f.suffix=='.json':json.loads(f.read_text());jsons+=1
 if f.suffix=='.py':ast.parse(f.read_text(),filename=str(f));pys+=1
staged=subprocess.check_output(git+['diff','--cached','--name-status','--diff-filter=ACDMRT']).decode().splitlines()
assert staged
for row in staged:
 status,path=row.split('\t',1);assert status=='A';assert path=='docs/issue-129-wing-2layer-routing.md' or path.startswith('hardware/kicad/qualification/issue-129-wing-2layer-routing/')
assert subprocess.check_output(git+['rev-parse','--abbrev-ref','HEAD'],text=True).strip()=='issue-129-wing-2layer-routing'
assert subprocess.check_output(git+['rev-parse','origin/main'],text=True).strip()==base
save(E/'verification.json',dict(utc=now(),base=base,base_files_verified_byte_identical=count,changed_base_files=changed,staged_files=len(staged),only_allowed_additions=True,input_hashes_unchanged=True,failed_gate_preserved=True,no_gate_retry=True,no_routing=True,all_six_paths_explicitly_unrun=True,parsed_json_files=jsons,parsed_python_files=pys,runtime_or_dependency_packages_in_evidence=False))
# Self is excluded to avoid a recursive hash. The manifest is generated after verification.
save(E/'manifest.json',{str(f.relative_to(E)):dict(bytes=f.stat().st_size,sha256=digest(f)) for f in sorted(E.rglob('*')) if f.is_file() and f.name!='manifest.json'})
print((E/'verification.json').read_text())
