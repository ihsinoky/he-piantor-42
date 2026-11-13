"""Full bounded study regeneration; scratch stays under .issue235-runtime only."""
from pathlib import Path
import json,subprocess,sys,os,shutil
E=Path(__file__).resolve().parent;ROOT=E.parents[3];T=ROOT/'.issue235-runtime';T.mkdir(exist_ok=True)
def run(argv,name,env=None,timeout=3600):
 with (T/(name+'.log')).open('w') as f:subprocess.run(argv,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=timeout)
 print(name,'finished',flush=True)
run([sys.executable,str(E/'setup-runtime.py')],'setup')
c=json.loads((E/'toolchain.json').read_text());native=[str(T/'run'),c['ROUTER_PYTHON']]
def script(name,*args):run([*native,str(E/(name+'.py')),*args],name+('-'+args[0] if args else ''))
for w in E.glob('wing-rev4-*'):shutil.rmtree(w)
if (E/'case').exists():shutil.rmtree(E/'case')
script('build');script('connector-pose-check');script('placement-check');script('electrical-check');script('body-clearance');script('route')
for w in sorted(E.glob('wing-rev4-*')):
 script('diagnose',w.name)
 if not json.loads((w/'qualification.json').read_text())['pass']:
  shutil.copyfile(w/'qualification.json',w/'initial-qualification.json');shutil.copyfile(w/'drc.json',w/'initial-drc.json')
  script('plane-repair',w.name);script('audit',w.name);script('cleanup',w.name);script('audit',w.name)
 if not json.loads((w/'qualification.json').read_text())['pass']:
  script('repair-service-landing',w.name);script('audit',w.name)
 script('electrical-check')
 if json.loads((w/'qualification.json').read_text())['pass']:script('extract-resistance',w.name)
script('verify-fem');script('congestion')
cadenv={**os.environ,'TMPDIR':str(T/'tmp'),'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':c['GEOMETRY_SITE'],'XDG_CACHE_HOME':str(T/'cache'),'XDG_CONFIG_HOME':str(T/'config')}
for name in ('case-study','mating-study','case-verify'):run([c['CAD_PYTHON'],str(E/(name+'.py'))],name,cadenv)
script('refresh-case-placement');script('power-summary')
for p in E.rglob('*.kicad_prl'):
 dest=T/'ui-cache'/p.relative_to(E);dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(dest))
run([sys.executable,str(E/'write-report.py')],'report')
run([sys.executable,str(E/'record-evidence.py')],'evidence')
run([sys.executable,str(E/'verify-study.py')],'verification')
print('Regenerated evidence. Design qualification is whatever the independent gates report.')
