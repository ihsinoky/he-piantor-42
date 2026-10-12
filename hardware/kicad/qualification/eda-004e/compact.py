"""Lossless reporting compaction of per-package captures, without new trials."""
import base64
import gzip
import json
import shutil
from capture import ROOT, save, digest
r=ROOT/'evidence';items=[]
for d in sorted((r/'processes').glob('kicad-extract-*')):
    items.append({'record':json.loads((d/'record.json').read_text()),'stdout_base64':base64.b64encode((d/'stdout').read_bytes()).decode(),'stderr_base64':base64.b64encode((d/'stderr').read_bytes()).decode()})
if items:
    target=r/'package-extractions.json.gz'
    target.write_bytes(gzip.compress((json.dumps(items,indent=2)+'\n').encode(),mtime=0))
    save(r/'package-extractions-index.json',{'count':len(items),'path':target.name,'sha256':digest(target),'format':'lossless JSON records + stdout/stderr base64; original commands, times, exits and hashes unchanged'})
    for d in (r/'processes').glob('kicad-extract-*'):shutil.rmtree(d)
# Compress large read-only raw pages and package downloads losslessly.
for d in (r/'processes').iterdir():
    p=d/'stdout'
    if p.is_file() and p.stat().st_size>12000:
        gz=d/'stdout.gz';gz.write_bytes(gzip.compress(p.read_bytes(),mtime=0));p.unlink()
for name in ['pr-10-failed-ci.txt']:
    p=r/name
    if p.is_file():
        (r/(name+'.gz')).write_bytes(gzip.compress(p.read_bytes(),mtime=0));p.unlink()
