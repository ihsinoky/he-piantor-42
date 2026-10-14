"""Lossless post-STOP compaction; records/streams remain replayable."""
import base64
import gzip
import json
import shutil
from capture import ROOT, save, digest

EV = ROOT / 'evidence'
assert (EV / 'stop-decision.json').exists()
items = []
for directory in sorted((EV / 'processes').glob('kicad-extract-*')):
    items.append(dict(record=json.loads((directory/'record.json').read_text()),
                      stdout_base64=base64.b64encode((directory/'stdout').read_bytes()).decode(),
                      stderr_base64=base64.b64encode((directory/'stderr').read_bytes()).decode()))
if items:
    target = EV / 'package-extractions.json.gz'
    target.write_bytes(gzip.compress((json.dumps(items,indent=2)+'\n').encode(),mtime=0))
    save(EV/'package-extractions-index.json', dict(count=len(items),path=target.name,sha256=digest(target),
         format='Lossless process records + base64 raw stdout/stderr; original commands/times/exits/hashes unchanged.'))
    for directory in (EV/'processes').glob('kicad-extract-*'):
        shutil.rmtree(directory)
for directory in (EV/'processes').iterdir():
    for name in ('stdout','stderr'):
        path = directory/name
        if path.is_file() and path.stat().st_size:
            path.with_name(name+'.gz').write_bytes(gzip.compress(path.read_bytes(),mtime=0))
            path.unlink()
print('lossless compaction complete')
