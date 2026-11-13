"""Full study regeneration. All logs/caches/scratch remain in .issue233-runtime."""
from pathlib import Path
import json,subprocess,sys,os,shutil
E=Path(__file__).resolve().parent;ROOT=E.parents[3];T=ROOT/'.issue233-runtime';T.mkdir(exist_ok=True)
def run(argv,name,env=None):
 with (T/(name+'.log')).open('w') as f:subprocess.run(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
 for p in E.rglob('*.kicad_prl'):
  dest=T/'ui-cache'/p.relative_to(E);dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(dest))
run([sys.executable,str(E/'setup-runtime.py')],'setup')
conf=json.loads((E/'toolchain.json').read_text());native=[str(T/'run'),conf['ROUTER_PYTHON']]
for n in ('build','route','diagnose','placement-check','electrical-check','congestion'):
 run([*native,str(E/(n+'.py'))],n);print(n,'finished',flush=True)
cadenv={**os.environ,'TMPDIR':str(T/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':conf['GEOMETRY_SITE'],'XDG_CACHE_HOME':str(T/'cache'),'XDG_CONFIG_HOME':str(T/'config')}
run([conf['CAD_PYTHON'],str(E/'case-study.py')],'case',cadenv)
run([conf['CAD_PYTHON'],str(E/'case-verify.py')],'case-reload',cadenv)
for n in ('costs','verify-study'):run([sys.executable,str(E/(n+'.py'))],n)
print('Study regenerated. Design acceptance remains whatever the saved gates report.')
