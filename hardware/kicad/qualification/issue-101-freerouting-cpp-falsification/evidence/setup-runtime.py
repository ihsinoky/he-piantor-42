"""Extract downloaded Ubuntu debs to a disposable directory; no dpkg install."""
import pathlib,subprocess,json,hashlib,sys
E=pathlib.Path(__file__).resolve().parent; ROOT=E.parents[4]; R=ROOT/'.issue101-runtime'
mode=sys.argv[1]; assert mode in ('qt','kicad')
debs=list((R/'apt/cache/archives').glob('*.deb'))
if mode=='kicad': debs.append(pathlib.Path('/tmp/issue-97-fastroute/kicad.deb'))
for p in debs: subprocess.run(['dpkg-deb','-x',str(p),str(R/mode)],check=True)
(E/(mode+'-runtime-package-hashes.json')).write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in debs},indent=2)+'\n')
if mode=='qt':
 (R/'qt/usr/lib/qt6/bin/qt.conf').write_bytes((E/'qt.conf').read_bytes())
