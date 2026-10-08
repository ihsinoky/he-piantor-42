from process import *
import shutil
base=Path('/tmp/eda004c')
bun=str(base/'bun-linux-x64/bun')
env={'PATH':str(base/'bun-linux-x64')+':'+os.environ['PATH'],'npm_config_cache':str(base/'npm-cache')}
# Reviewed upstream build: dependency lifecycle scripts disabled, regular build only.
run('kicadts-build-deps',['npm','install','--ignore-scripts','--package-lock-only'],base/'kicadts',180,env=env,artifacts=[('build-package-lock.json',base/'kicadts/package-lock.json')])
run('kicadts-build-install',['npm','ci','--ignore-scripts'],base/'kicadts',180,env=env)
run('kicadts-build',[bun,'run','build'],base/'kicadts',180,env=env,artifacts=[('index.js',base/'kicadts/dist/index.js'),('index.d.ts',base/'kicadts/dist/index.d.ts')])
run('kicadts-built-status',['git','status','--porcelain'],base/'kicadts')
front=base/'frontend';front.mkdir()
for p in ['package.json','package-lock.json']:
 shutil.copyfile(ROOT.parent/'eda-003c/latest-stock'/p,front/p)
run('frontend-install',['npm','ci','--ignore-scripts'],front,240,env=env)
conv=base/'converter';conv.mkdir()
for p in ['package.json','package-lock.json']:
 shutil.copyfile(ROOT.parent/'eda-004b'/('converter-'+p),conv/p)
run('converter-install',['npm','ci','--ignore-scripts'],conv,180,env=env)
# Attach ONLY regular build output from the exact upstream commit to its locked package.
# This is neither a dependency substitution nor a converter source patch.
shutil.copytree(base/'kicadts/dist',conv/'node_modules/kicadts/dist')
shutil.copyfile(ROOT.parent/'eda-004b/evidence/executed-convert.mjs',conv/'convert.mjs')
run('converter-module-load',['node','--input-type=module','-e',"import 'circuit-json-to-kicad'; console.log('module load PASS')"],conv,env=env)
save(EVIDENCE/'js-install-result.json',{'status':'PASS','kicadts_commit':'f3ea106bdc65ca901e9b23255ad3be0bd2a624ab','method':'upstream npm dependency install with lifecycle disabled, bun run build; exact built dist attached to locked Git dependency','frontend_lock_unchanged':digest(front/'package-lock.json')==digest(ROOT.parent/'eda-003c/latest-stock/package-lock.json'),'converter_lock_unchanged':digest(conv/'package-lock.json')==digest(ROOT.parent/'eda-004b/converter-package-lock.json')})
