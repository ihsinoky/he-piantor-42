import hashlib,json,sys
from pathlib import Path
E=Path(__file__).resolve().parent;out=E/'artifact-sha256.json'
def hashes():return {str(p.relative_to(E)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(E.rglob('*')) if p.is_file() and p!=out and '__pycache__' not in p.parts}
if '--write' in sys.argv:out.write_text(json.dumps(hashes(),indent=2)+'\n');print('Manifest written')
else:
 expected=json.loads(out.read_text());actual=hashes();assert expected==actual,('artifact hashes changed',sorted(k for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)))
 print('Artifact manifest PASS')
