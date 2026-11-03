"""Add runtime libraries used by retained KiCad 9.0.9, beyond Ubuntu stock KiCad 7."""
import pathlib,subprocess,json,time,hashlib
E=pathlib.Path(__file__).resolve().parent;T=pathlib.Path('/tmp/issue-105-fab-router');A=T/'apt';K=T/'kicad'
opts=['-o','APT::Sandbox::User=root','-o','Dir::State::lists='+str(A/'lists'),'-o','Dir::Cache='+str(A/'cache'),'-o','Dir::Etc::sourcelist='+str(A/'sources.list'),'-o','Dir::Etc::sourceparts=-']
argv=['apt-get',*opts,'--download-only','--no-install-recommends','-y','install','libprotobuf32t64','libgit2-1.7','libnng1'];t=time.monotonic()
with (E/'extra-kicad-deps-download.log').open('w') as out:r=subprocess.run(argv,stdout=out,stderr=subprocess.STDOUT)
(E/'extra-kicad-deps-record.json').write_text(json.dumps(dict(argv=argv,exit_code=r.returncode,elapsed_seconds=time.monotonic()-t),indent=2)+'\n');assert r.returncode==0
# Exclude Ubuntu stock KiCad 7: the actual oracle runtime must remain KiCad 9.0.9.
debs=[p for p in (A/'cache/archives').glob('*.deb') if not p.name.startswith('kicad_')];debs.append(pathlib.Path('/tmp/issue-97-fastroute/kicad.deb'))
for p in debs:subprocess.run(['dpkg-deb','-x',p,K],check=True)
(E/'kicad-package-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in debs},indent=2)+'\n')
