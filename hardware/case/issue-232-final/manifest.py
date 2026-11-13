"""Bind every source, package and result in this new tree; no external writes."""
from pathlib import Path
import json,hashlib,sys
HERE=Path(__file__).resolve().parent
TARGET=HERE/'exports-sha256.json'
def current():return {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.rglob('*')) if p.is_file() and p!=TARGET and '__pycache__' not in p.parts}
if __name__=='__main__':
 if '--write' in sys.argv:
  data=current();TARGET.write_text(json.dumps(data,indent=2)+'\n');print('Bound',len(data),'files')
 else:
  expected=json.loads(TARGET.read_text());actual=current();assert expected==actual,[(k,expected.get(k),actual.get(k)) for k in expected.keys()|actual.keys() if expected.get(k)!=actual.get(k)];print('All',len(actual),'artifact hashes match')
