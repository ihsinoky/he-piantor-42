"""Create task-local environment; installed tools are read-only dependencies."""
from pathlib import Path
import json,hashlib,os
E=Path(__file__).resolve().parent;R=E.parents[3];T=R/'.issue250-runtime';T.mkdir(exist_ok=True)
for n in ('tmp','config','cache','data','state'):(T/n).mkdir(exist_ok=True)
s=(T/'run').read_text() if (T/'run').exists() else ''
# Kept as a standalone launcher in the qualification tree for reproduction.
if s:(E/'run.sh').write_text(s.replace('ROOT=/home/hatch/workspace/projects/he-piantor-df52','ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"'))
KR=Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime')
paths=[KR/'kicad/usr/bin/kicad-cli',KR/'kicad/usr/lib/python3/dist-packages/pcbnew.py',KR/'KiCadRoutingTools/py_router/route.py',KR/'KiCadRoutingTools/rust_router/grid_router.so']
(E/'toolchain.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
