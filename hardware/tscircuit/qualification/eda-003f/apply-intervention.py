"""Apply the single predeclared via-segment intervention to an isolated copy.

Usage: python3 apply-intervention.py ENV [MANIFEST_OUTPUT]
Fails on any input other than the exact accepted stock artifact.
"""
import hashlib
import json
from pathlib import Path
import sys

here = Path(__file__).resolve().parent
definition = json.loads((here/'evidence/intervention-definition.json').read_text())
env = Path(sys.argv[1]).resolve()
accepted = here.parent/'eda-003c/latest-stock'
assert env != accepted.resolve() and env != here.parents[1].resolve()
p = env/definition['file']
original = p.read_bytes()
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert sha(original)==definition['original_sha256'], 'Requires exact unchanged stock file'
code = original.decode()
manifest = {'package':definition['package'],'file':definition['file'],'original_sha256':sha(original),'sites':[],'effective_target_mm':.2,'parameter_candidates':1}
for site in definition['sites']:
    before, after = site['before'], site['after']
    assert code.count(before)==1
    manifest['sites'].append({'name':site['name'],'original_offset':original.decode().index(before),'before':before,'after':after})
    code = code.replace(before,after,1)
patched = code.encode()
manifest.update(patched_sha256=sha(patched),original_size_bytes=len(original),patched_size_bytes=len(patched),net_byte_delta=len(patched)-len(original))
p.write_bytes(patched)
if len(sys.argv)>2:
    Path(sys.argv[2]).write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest,indent=2))
