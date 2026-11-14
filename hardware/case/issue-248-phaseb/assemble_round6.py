"""Reassemble the frozen final round-3 operands, changing only numbered strands.

Round-3 paths are parametric. No solids-to-path fitting is needed. Missing
serialized case operands are read from their frozen manufacturing STEP files;
this representation roundtrip is recorded, with no healing or route relief.
"""
from common import *
import shutil

def run(pitch):
 out=HERE/f'{pitch}mm';baseline=HERE/f'round3/{pitch}mm';scratch=ROOT/'.issue248-runtime/round6'
 # Prefer byte-identical frozen operands found by content, never round-5 trays.
 found=read(scratch/'frozen-operands.json');old=read(baseline/'assembly-index.json')
 cache=RUN/f'geometry{pitch}';cache.mkdir(exist_ok=True)
 for f in out.iterdir():
  if f.is_file():f.unlink()
 for name in ('surface-plan.geojson','cap-plan.json'):
  shutil.copyfile(baseline/name,out/name)
 from routes import make_routes
 wires,wm=make_routes();idx=[];recovery=[]
 for i,r in enumerate(old):
  n=r['name'];target=cache/f'{i}.brep'
  if n.startswith('Wire-'):
   q=wires[n];BRepTools.Write_s(q.wrapped,str(target))
   row=dict(name=n,solid=r['solid'],bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(target))
  elif r['sha256'] in found:
   src=ROOT/found[r['sha256']];assert sha(src)==r['sha256'];shutil.copyfile(src,target);row=r.copy()
   recovery.append(dict(part=n,method='byte-identical frozen BRep',sha256=row['sha256']))
  else:
   assert n in ('tray-left','tray-right','shell-central'),n
   step=baseline/'manufacturing'/f'{n}-PROVISIONAL.step';q=import_step(step)
   assert len(q.solids())==1
   q=q.solids()[0];BRepTools.Write_s(q.wrapped,str(target))
   bd=bounds(q);dv=q.volume-r['volume_mm3'];db=max(abs(a-b) for a,b in zip(sum(bd,[]),sum(r['bounds'],[])))
   assert abs(dv)<.001 and db<1e-5,(n,dv,db)
   row=dict(name=n,solid=r['solid'],bounds=bd,valid=q.is_valid,volume_mm3=q.volume,sha256=sha(target))
   recovery.append(dict(part=n,method='frozen round-3 final manufacturing STEP representation roundtrip; no healing or geometry edits',source_file=str(step.relative_to(HERE)),source_sha256=sha(step),frozen_brep_sha256=r['sha256'],recovered_brep_sha256=row['sha256'],volume_delta_mm3=dv,maximum_bounds_delta_mm=db,valid=q.is_valid))
  idx.append(row)
 save(cache/'index.json',idx);save(out/'assembly-index.json',idx)
 meta=read(baseline/'measurements.json');meta['wings']=wm
 meta['wire_sweep_checks']=[dict(part=n,volume_mm3=q.volume,expected_volume_mm3=wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25,volume_error_mm3=abs(q.volume-wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25),passed=q.is_valid and len(q.solids())==1 and abs(q.volume-wm[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25)<.001) for n,q in wires.items()]
 save(out/'measurements.json',meta)
 save(out/'frozen-framework-recovery.json',dict(geometry_sha256=sha(out/'assembly-index.json'),baseline_index_sha256=sha(baseline/'assembly-index.json'),recovered_index=idx,recovery=recovery,unchanged_framework='Frozen final round-3 trays including fitted-route channels and seating relief; central shell, strips, retainers ±8,-30 and all hardware. No service envelope or corrected-route tray recuts.',parametric_path_source='round3/routes-round3.json',path_source_sha256=sha(HERE/'round3/routes-round3.json')))
 print(pitch,'frozen assembly restored, only strands reassigned',max(w['longest_conductor_mm']+7.3 for w in wm),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
