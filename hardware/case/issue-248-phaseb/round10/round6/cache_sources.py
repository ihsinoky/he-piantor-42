"""Cache only; all scratch and OCCT BReps stay in .issue248-runtime."""
from common import *
def run():
 for pitch in (17,16):
  p=HERE.parent/f'issue-232-final/{pitch}mm/assembly.step';out=RUN/f'source{pitch}';out.mkdir(exist_ok=True)
  if (out/'index.json').exists() and read(out/'index.json')['sha256']==sha(p):continue
  parts=dict(leaves(import_step(p)));idx=[]
  for i,(n,s) in enumerate(parts.items()):
   BRepTools.Write_s(s.wrapped,str(out/f'{i}.brep'));idx.append(dict(name=n,bounds=bounds(s)))
  save(out/'index.json',dict(sha256=sha(p),parts=idx))
 cache=ROOT/'.issue248-runtime/b0-source'
 if not (cache/'index.json').exists():
  cache.mkdir(exist_ok=True);p=HERE.parent/'issue-246-delta6-tuning/packed/delta-6/17mm/assembly-with-cover.step'
  parts=dict(leaves(import_step(p)))
  names=['main','Main-GH-left','Main-GH-right','cover-screw-2','cover-screw-3','cover-Main-spacer-2','cover-Main-spacer-3']
  for i,n in enumerate(names):BRepTools.Write_s(parts[n].wrapped,str(cache/f'{i}.brep'))
  save(cache/'index.json',dict(source_sha256=sha(p),names=names))
if __name__=='__main__':run()
