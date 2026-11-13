"""Create study-only runtime wrapper, using installed read-only tool stores.
Override KICAD_ROOT, GEOMETRY_SITE, ROUTER_PYTHON, KRT_HOME and CAD_PYTHON on
another host. No downloads, installs, baseline edits or external writes.
"""
from pathlib import Path
import os,shlex,json,subprocess,hashlib
E=Path(__file__).resolve().parent;ROOT=E.parents[3];T=ROOT/'.issue233-runtime'
old=Path('/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime')
config={k:os.environ.get(k,str(v)) for k,v in dict(KICAD_ROOT=old/'kicad',GEOMETRY_SITE=old/'geometry/lib/python3.12/site-packages',ROUTER_PYTHON=old/'venv/bin/python3',KRT_HOME=old/'KiCadRoutingTools',CAD_PYTHON=Path('/home/hatch/workspace/tools/cad-venv/bin/python')).items()}
for n in ('tmp','config','cache','data','state'):(T/n).mkdir(parents=True,exist_ok=True)
s='#!/bin/bash\nset -eu\n'+''.join(f'{k}={shlex.quote(v)}\n' for k,v in config.items())+f'TASK_RUNTIME={shlex.quote(str(T))}\n'
s+='''export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$KICAD_ROOT/usr/lib/python3/dist-packages:$GEOMETRY_SITE"
export LD_LIBRARY_PATH="$KICAD_ROOT/usr/lib/x86_64-linux-gnu:$KICAD_ROOT/usr/lib/kicad"
export KICAD_STOCK_DATA_HOME="$KICAD_ROOT/usr/share/kicad"
export KICAD_CLI="$KICAD_ROOT/usr/bin/kicad-cli"
export TMPDIR="$TASK_RUNTIME/tmp"
export XDG_CONFIG_HOME="$TASK_RUNTIME/config" XDG_CACHE_HOME="$TASK_RUNTIME/cache" XDG_DATA_HOME="$TASK_RUNTIME/data" XDG_STATE_HOME="$TASK_RUNTIME/state"
export PATH="$KICAD_ROOT/usr/bin:$PATH"
export ROUTER_PYTHON KRT_HOME CAD_PYTHON GEOMETRY_SITE
unset DISPLAY WAYLAND_DISPLAY
exec "$@"
'''
(T/'run').write_text(s);(T/'run').chmod(0o755)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
k=Path(config['KRT_HOME']);result={**config,'KRT_commit':subprocess.check_output(['git','-C',str(k),'rev-parse','HEAD'],text=True).strip(),'KRT_route_sha256':sha(k/'py_router/route.py'),'kicad_version':subprocess.check_output([str(T/'run'),config['ROUTER_PYTHON'],'-c','import pcbnew;print(pcbnew.Version())'],text=True).strip()}
# Pin router implementation, including its compiled core, not only launcher.
result['KRT_source_hashes']={str(p.relative_to(k)):sha(p) for pattern in ('py_router/*.py','rust_router/*.so') for p in sorted(k.glob(pattern))}
(E/'toolchain.json').write_text(json.dumps(result,indent=2)+'\n')
print('Runtime wrapper and tool identity recorded')
