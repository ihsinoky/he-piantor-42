"""Targeted fail-closed mutation tests, no board/router execution."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('restore',ROOT/'restore-clearance.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
raw=Path('/tmp/issue87/smoke/input.dsn').read_bytes();good,record=m.restore(raw)
assert b'(clearance 200 (type smd_smd))' in good
cases={'unexpected-unit':raw.replace(b'(unit um)',b'(unit mm)'), 'unexpected-resolution':raw.replace(b'(resolution um 10)',b'(resolution um 100)'), 'wrong-target-value':raw.replace(b'(clearance 50 (type smd_smd))',b'(clearance 40 (type smd_smd))'), 'duplicate-target':raw.replace(b'(clearance 50 (type smd_smd))',b'(clearance 50 (type smd_smd)) (clearance 50 (type smd_smd))'), 'missing-target':raw.replace(b'(clearance 50 (type smd_smd))',b''),'target-outside-global-rule':raw.replace(b'(clearance 50 (type smd_smd))',b'').replace(b'(wiring',b'(clearance 50 (type smd_smd)) (wiring')}
results={}
for name,data in cases.items():
    try:m.restore(data)
    except (AssertionError,ValueError) as e:results[name]=dict(rejected=True,reason=str(e))
    else:raise AssertionError(('invalid input escaped',name))
# An unrelated literal50 must survive intact.
extra=raw.replace(b'(parser',b'(unrelated 50) (parser');changed,_=m.restore(extra);assert b'(unrelated 50)' in changed
(ROOT/'evidence/restoration-tests.json').write_text(json.dumps(dict(negative_cases=results,unrelated50_preserved=True,status='PASS_WITH_SCOPE'),indent=2)+'\n')
print('known-node-only edit and six structural/unit/count failure detections pass')
