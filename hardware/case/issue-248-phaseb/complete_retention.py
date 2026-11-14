"""Append nominal insert bodies; reuse only exact results with unchanged operand hashes."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';cache=RUN/f'geometry{pitch}';idx,raw=cached(pitch)
 if any(r['name']=='shell-insert-0' for r in idx):return
 old_hash=sha(out/'assembly-index.json');prior=read(out/'audit.json');assert prior['geometry_sha256']==old_hash
 old_index=list(idx)
 for i,x in [(0,-8),(1,8)]:
  q=cylinder(x,-30,1.6,TOP-6,4).cut(cylinder(x,-30,.8,TOP-6.01,4.02));n=len(idx)
  BRepTools.Write_s(q.wrapped,str(cache/f'{n}.brep'))
  idx.append(dict(name=f'shell-insert-{i}',solid=0,bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(cache/f'{n}.brep')))
 # Every reused operand is still byte-identical; no old pair is inferred clear.
 assert idx[:len(old_index)]==old_index
 for i,r in enumerate(old_index):assert sha(cache/f'{i}.brep')==r['sha256']
 save(cache/'index.json',idx);save(out/'assembly-index.json',idx);new_hash=sha(out/'assembly-index.json')
 proof=dict(status=P['status'],previous_geometry_sha256=old_hash,geometry_sha256=new_hash,unchanged_prefix_count=len(old_index),unchanged_operand_sha256=[r['sha256'] for r in old_index],new_parts=['shell-insert-0','shell-insert-1'],reused_exact_pair_count=len(prior['exact_results']),rule='Only exact Common results whose two serialized BRep operands are unchanged are seeded. Audit enumerates all unordered pairs again, including every new insert pair.')
 save(out/'retention-completion.json',proof)
 results={f"{r['i']}:{r['j']}":{k:v for k,v in r.items() if k not in ('i','j')} for r in prior['exact_results']}
 save(RUN/f'audit{pitch}-progress.json',dict(geometry_hash=new_hash,results=results,reuse_proof=proof))
 d=read(out/'measurements.json');d['retention_insert_model']='Two nominal OD3.2 x4.0 M2 annular bounds, minor bore OD1.6, in the specified north pilots. Knurls/threads are not reconstructed.';save(out/'measurements.json',d)
 # Preview changes only; nineteen independently checked print files are unchanged.
 _,raw=cached(pitch);groups={}
 for n,k,q in raw:
  if not n.startswith('USB-reference-'):groups.setdefault(n,[]).append(q)
 ass=[]
 for n,ss in groups.items():
  q=ss[0] if len(ss)==1 else Compound(children=ss);q.label=n+'-PROVISIONAL-q1.50';ass.append(q)
 export_step(Compound(children=ass),out/'fitted-assembly-PROVISIONAL.step')
 m=read(out/'manufacturing.json');m['preview_sha256']=sha(out/'fitted-assembly-PROVISIONAL.step');save(out/'manufacturing.json',m)
 v=read(out/'export-verification.json');assert v['geometry_sha256']==old_hash
 checked={r['part']:r for r in v['checks']}
 for p in m['parts']:
  c=checked[p['name']];base=out/'manufacturing'/p['filename']
  assert sha(base.with_suffix('.step'))==p['step_sha256']==c['step_sha256']
  assert sha(base.with_suffix('.stl'))==p['stl_sha256']==c['stl_sha256']
 v.update(geometry_sha256=new_hash,unchanged_print_verification_reuse_from_geometry=old_hash);save(out/'export-verification.json',v)
 local=read(out/'local-measures.json');assert local['geometry_sha256']==old_hash
 local.update(geometry_sha256=new_hash,unchanged_operands_reuse_from_geometry=old_hash);save(out/'local-measures.json',local)
 print(pitch,'two retention insert bounds included; all prior operands hash-identical',flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
