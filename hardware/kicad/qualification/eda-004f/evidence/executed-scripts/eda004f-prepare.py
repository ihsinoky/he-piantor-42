import sys
from pathlib import Path
sys.path.insert(0,'/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f')
from capture import run,save,digest,utc
base=Path('/tmp/eda004f'); ev=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f/evidence')
run('library-identity',['git','-C','/tmp/eda004f-library','log','-1','--format=fuller'],base)
run('library-source',['git','-C','/tmp/eda004f-library','archive','--format=tar.gz','-o',str(ev/'library-source.tar.gz'),'505bca23e91cf3fa6e3b66976e529e775eada3ba'],base)
run('python-venv',['python3','-m','venv',str(base/'venv')],base)
run('library-install',[str(base/'venv/bin/pip'),'install','--report',str(ev/'pip-install-report.json'),'/tmp/eda004f-library'],base,240)
run('dependencies',[str(base/'venv/bin/pip'),'freeze','--all'],base)
run('symbols-commit',['curl','-fL','https://api.github.com/repos/KiCad/kicad-symbols/commits/master','-o',str(ev/'symbols-commit.json')],base)
import json
commit=json.loads((ev/'symbols-commit.json').read_text())['sha']
lib=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f/library');lib.mkdir(exist_ok=True)
for name in ['74xGxx.kicad_sym','Device.kicad_sym','power.kicad_sym','LICENSE.md']:
 run('symbols-'+name.replace('.','-'),['curl','-fL',f'https://raw.githubusercontent.com/KiCad/kicad-symbols/{commit}/{name}','-o',str(lib/name)],base)
save(ev/'preparation.json',{'finished_utc':utc(),'library_commit':'505bca23e91cf3fa6e3b66976e529e775eada3ba','symbols_commit':commit,'library_sha256':digest(ev/'library-source.tar.gz'),'symbol_hashes':{p.name:digest(p) for p in lib.iterdir()}})
