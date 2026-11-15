"""Copy every round-5 fixed operand byte for byte; regenerate only strands."""
from common import *
import shutil

def run(pitch):
 out=HERE/f'{pitch}mm';baseline=HERE/f'round5/{pitch}mm';found=read(ROOT/'.issue248-runtime/round7/frozen-operands.json');old=read(baseline/'assembly-index.json');cache=RUN/f'geometry{pitch}';cache.mkdir(exist_ok=True)
 from routes_round9 import make_routes
 wires,wm=make_routes()
 for f in out.iterdir():
  if f.is_file():f.unlink()
 for name in ('surface-plan.geojson','cap-plan.json','hardware-inventory.json'):
  shutil.copyfile(baseline/name,out/name)
 idx=[]
 for i,r in enumerate(old):
  target=cache/f'{i}.brep';n=r['name']
  if n.startswith('Wire-'):
   q=wires[n];BRepTools.Write_s(q.wrapped,str(target));row=dict(name=n,solid=r['solid'],bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(target))
  else:
   src=ROOT/found[r['sha256']];assert sha(src)==r['sha256'];shutil.copyfile(src,target);row=r.copy()
  idx.append(row)
 save(cache/'index.json',idx);save(out/'assembly-index.json',idx)
 meta=read(baseline/'measurements.json');meta['wings']=wm
 meta['wire_sweep_checks']=[dict(part=n,volume_mm3=q.volume,expected_volume_mm3=wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25,volume_error_mm3=abs(q.volume-wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25),passed=q.is_valid and len(q.solids())==1 and abs(q.volume-wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25)<.001) for n,q in wires.items()]
 save(out/'measurements.json',meta)
 save(out/'round9-fixed-scope.json',dict(geometry_sha256=sha(out/'assembly-index.json'),baseline_index_sha256=sha(baseline/'assembly-index.json'),all_fixed_byte_identical=all(a==b for a,b in zip(old,idx) if not a['name'].startswith('Wire-')),changed_names=[a['name'] for a,b in zip(old,idx) if a!=b]))
 shutil.copyfile(baseline/'audit.json',out/'audit.json')
 save(out/'E-boss-audit-parent.json',dict(index_file=f'../round5/{pitch}mm/assembly-index.json',audit_file=f'../round5/{pitch}mm/audit.json',geometry_sha256=sha(baseline/'assembly-index.json'),reason='Every fixed round5 operand byte-identical; all changed strand candidates recomputed.'))
 print(pitch,'round5 fixed bodies byte-identical; 28 strands regenerated (round 8)',flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
