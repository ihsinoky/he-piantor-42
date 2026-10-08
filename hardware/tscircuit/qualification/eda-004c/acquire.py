from process import *
import shutil
base=Path('/tmp/eda004c')
run('kicadts-source', ['git','clone','https://github.com/tscircuit/kicadts.git',str(base/'kicadts')],base,120)
run('kicadts-checkout', ['git','checkout','--detach','f3ea106bdc65ca901e9b23255ad3be0bd2a624ab'],base/'kicadts')
run('bun-download',['curl','-fL','https://github.com/oven-sh/bun/releases/download/bun-v1.2.22/bun-linux-x64.zip','-o',str(base/'bun.zip')],base,120)
assert digest(base/'bun.zip')=='4c446af1a01d7b40e1e11baebc352f9b2bfd12887e51b97dd3b59879cee2743a'
run('bun-extract',['unzip','-q',str(base/'bun.zip')],base)
for p in ['package.json','bun.lock','scripts/prepare-git-dependency.ts','scripts/download-references.ts','README.md']:
 f=base/'kicadts'/p
 if f.is_file():
  t=EVIDENCE/'raw/kicadts-source'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(f.read_bytes())
run('kicadts-source-status',['git','status','--porcelain'],base/'kicadts')
