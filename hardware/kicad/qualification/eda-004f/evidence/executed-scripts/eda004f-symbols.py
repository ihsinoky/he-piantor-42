import sys,json
from pathlib import Path
sys.path.insert(0,'/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f')
from capture import run,save,digest,utc
base=Path('/tmp/eda004f'); ev=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f/evidence')
run('symbol-package-policy',['apt-cache','-c',str(base/'apt/apt.conf'),'policy','kicad-symbols'],base)
run('symbol-package-download',['apt-get','-c',str(base/'apt/apt.conf'),'download','kicad-symbols'],base,180)
p=next(base.glob('kicad-symbols*.deb'))
run('symbol-package-identity',['dpkg-deb','-I',str(p)],base)
run('symbol-package-extract',['dpkg-deb','-x',str(p),str(base/'symbols')],base)
lib=Path('/workspaces/he-piantor-42/hardware/kicad/qualification/eda-004f/library')
for name in ['74xGxx.kicad_sym','Device.kicad_sym','power.kicad_sym']:
 (lib/name).write_bytes((base/'symbols/usr/share/kicad/symbols'/name).read_bytes())
(lib/'copyright').write_bytes((base/'symbols/usr/share/doc/kicad-symbols/copyright').read_bytes())
save(ev/'preparation.json',{'finished_utc':utc(),'library_commit':'505bca23e91cf3fa6e3b66976e529e775eada3ba','symbol_package':p.name,'symbol_package_sha256':digest(p),'library_archive_sha256':digest(ev/'library-source.tar.gz'),'symbol_hashes':{p.name:digest(p) for p in lib.iterdir()}})
