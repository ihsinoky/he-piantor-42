from process import *
base=Path(os.environ.get('EDA004D_WORK_DIR', '/tmp/eda004d'))
apt=base/'apt';apt.mkdir()
for p in ['lists/partial','archives/partial','kicad','config','cache','data','state']:(base/p).mkdir(parents=True,exist_ok=True)
(apt/'sources.list').write_text('deb [trusted=yes] https://ppa.launchpadcontent.net/kicad/kicad-9.0-releases/ubuntu noble main\ndeb [trusted=yes] http://archive.ubuntu.com/ubuntu noble main universe\ndeb [trusted=yes] http://archive.ubuntu.com/ubuntu noble-updates main universe\ndeb [trusted=yes] http://security.ubuntu.com/ubuntu noble-security main universe\n')
(apt/'status').touch()
conf=apt/'apt.conf'
conf.write_text(f'''Dir::Etc::sourcelist "{apt}/sources.list";
Dir::Etc::sourceparts "-";
Dir::State::lists "{base}/lists";
Dir::State::status "{apt}/status";
Dir::Cache::archives "{base}/archives";
Dir::Cache::pkgcache "{apt}/pkgcache.bin";
Dir::Cache::srcpkgcache "{apt}/srcpkgcache.bin";
APT::Sandbox::User "{os.environ.get('USER','codespace')}";
Debug::NoLocking "true";
''')
run('kicad-download',['curl','-fL','https://ppa.launchpadcontent.net/kicad/kicad-9.0-releases/ubuntu/pool/main/k/kicad/kicad_9.0.9~ubuntu24.04.1_amd64.deb','-o',str(base/'kicad.deb')],base,180)
assert digest(base/'kicad.deb')=='b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0'
run('kicad-apt-update',['apt-get','-c',str(conf),'update'],base,180,artifacts=[('apt.conf',conf),('sources.list',apt/'sources.list')])
run('kicad-dependency-download',['apt-get','-c',str(conf),'--download-only','--no-install-recommends','-y','install',str(base/'kicad.deb')],base,240)
packages=[base/'kicad.deb']+sorted((base/'archives').glob('*.deb'))
save(EVIDENCE/'kicad-package-hashes.json',{str(p):digest(p) for p in packages})
for i,p in enumerate(packages):
 run(f'kicad-extract-{i:03}',['dpkg-deb','-x',str(p),str(base/'kicad')],base)
env={'LD_LIBRARY_PATH':str(base/'kicad/usr/lib/x86_64-linux-gnu')+':'+str(base/'kicad/usr/lib/kicad'),'PYTHONPATH':str(base/'kicad/usr/lib/python3/dist-packages'),'KICAD9_SYMBOL_DIR':str(base/'kicad/usr/share/kicad/symbols'),'KICAD9_FOOTPRINT_DIR':str(base/'kicad/usr/share/kicad/footprints'),'KICAD9_3DMODEL_DIR':str(base/'kicad/usr/share/kicad/3dmodels'),'KICAD_STOCK_DATA_HOME':str(base/'kicad/usr/share/kicad'),'XDG_CONFIG_HOME':str(base/'config'),'XDG_CACHE_HOME':str(base/'cache'),'XDG_DATA_HOME':str(base/'data'),'XDG_STATE_HOME':str(base/'state')}
save(EVIDENCE/'kicad-env.json',env)
run('kicad-version',[str(base/'kicad/usr/bin/kicad-cli'),'--version'],base,env=env)
run('pcbnew-probe',['/usr/bin/python3','-c',"import pcbnew; print(pcbnew.GetBuildVersion()); print(pcbnew.ExportSpecctraDSN.__doc__); print(pcbnew.ImportSpecctraSES.__doc__)"],base,env=env)
