from process import *
import shutil
base=Path('/tmp/eda004c')
metadata=json.loads((ROOT.parent/'eda-004b/evidence/selected-package-metadata.json').read_text())
asset=next(x for x in metadata['freerouting']['assets'] if x['name']=='freerouting-2.5.0.jar')
run('freerouting-download',['curl','-fL',asset['browser_download_url'],'-o',str(base/'freerouting.jar')],base,180)
assert digest(base/'freerouting.jar')=='f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7'
env=json.loads((EVIDENCE/'kicad-env.json').read_text())
run('freerouting-help',['java','-Djava.awt.headless=true','-jar',str(base/'freerouting.jar'),'--user_data_path='+str(base/'config/freerouting'),'-help'],base,120,env=env)
run('kicad-help',[str(base/'kicad/usr/bin/kicad-cli'),'--help'],base,env=env)
# All smoke footprints/schematic definitions are embedded. No external library resolution.
save(EVIDENCE/'environment.json',{'prior_exact_pins':json.loads((ROOT.parent/'eda-004b/evidence/environment.json').read_text()),'observed_pins':'preflight.json and process version records','bun_archive_sha256':digest(base/'bun.zip'),'bun_executable_sha256':digest(base/'bun-linux-x64/bun'),'router_jar_sha256':digest(base/'freerouting.jar'),'kicad_deb_sha256':digest(base/'kicad.deb'),'kicad_cli_sha256':digest(base/'kicad/usr/bin/kicad-cli'),'kicadts_dist_sha256':digest(base/'kicadts/dist/index.js'),'libraries':'Embedded synthetic definitions only; no external symbols/footprints/3D models used. Installed stock resource/schema snapshot below.','resources':{str(p.relative_to(base/'kicad')):digest(p) for p in (base/'kicad/usr/share/kicad').rglob('*') if p.is_file()},'config_paths':env,'config_files_before_generate':{str(p.relative_to(base)):digest(p) for d in ['config','data','state'] for p in (base/d).rglob('*') if p.is_file()},'os_release':Path('/etc/os-release').read_text(),'display_policy':'DISPLAY/WAYLAND_DISPLAY unset for every process; Java headless; no GUI/IPC/virtual display/cloud','frontend_lock_sha256':digest(base/'frontend/package-lock.json'),'converter_lock_sha256':digest(base/'converter/package-lock.json')})
shutil.copyfile(ROOT/'smoke.tsx',base/'frontend/smoke.tsx')
run('smoke-generation',[str(base/'bun-linux-x64/bun'),str(base/'frontend/smoke.tsx'),str(base/'smoke.circuit.json')],base/'frontend',120,artifacts=[('smoke.circuit.json',base/'smoke.circuit.json')],env={'PATH':str(base/'bun-linux-x64')+':'+os.environ['PATH']})
