"""Download/extract KiCad runtime dependencies without system installation."""
import pathlib,subprocess,hashlib,json,time
E=pathlib.Path(__file__).resolve().parent; T=pathlib.Path('/tmp/issue-103-fab-router'); A=T/'apt'; K=T/'kicad'
for p in [A/'lists/partial',A/'cache/archives/partial',K]:p.mkdir(parents=True,exist_ok=True)
(A/'sources.list').write_text('deb http://azure.archive.ubuntu.com/ubuntu noble main universe\ndeb http://azure.archive.ubuntu.com/ubuntu noble-updates main universe\ndeb http://azure.archive.ubuntu.com/ubuntu noble-security main universe\n')
opts=['-o','APT::Sandbox::User=root','-o','Dir::State::lists='+str(A/'lists'),'-o','Dir::Cache='+str(A/'cache'),'-o','Dir::Etc::sourcelist='+str(A/'sources.list'),'-o','Dir::Etc::sourceparts=-']
def run(name,args):
 t=time.monotonic()
 with (E/(name+'.log')).open('w') as out:r=subprocess.run(args,stdout=out,stderr=subprocess.STDOUT)
 (E/(name+'-record.json')).write_text(json.dumps(dict(argv=list(map(str,args)),exit_code=r.returncode,elapsed_seconds=time.monotonic()-t),indent=2)+'\n'); assert r.returncode==0
run('apt-update',['apt-get',*opts,'update'])
run('kicad-deps-download',['apt-get',*opts,'--download-only','--no-install-recommends','-y','install','kicad'])
debs=list((A/'cache/archives').glob('*.deb')); debs.append(pathlib.Path('/tmp/issue-97-fastroute/kicad.deb'))
for p in debs:subprocess.run(['dpkg-deb','-x',p,K],check=True)
(E/'kicad-package-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in debs},indent=2)+'\n')
run('geometry-venv',['python3','-m','venv',T/'geometry'])
run('geometry-install',[T/'geometry/bin/pip','install','shapely','sexpdata'])
