"""Round 14 assembly: copy every round-5 fixed operand byte for byte
(same pattern as assemble_round9); regenerate only the 28 strands from
routes_round14 (Candidate A v13: A6 corridor + rise, optimised feed,
distributed +30.2 mm stored slack)."""
import sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import *
import shutil
import routes_round14 as rr

def run(pitch,kind='stored'):
 out=HERE/f'{pitch}mm';baseline=HERE/f'round5/{pitch}mm';found=read(ROOT/'.issue248-runtime/round7/frozen-operands.json');old=read(baseline/'assembly-index.json');cache=RUN/f'geometry{pitch}';cache.mkdir(exist_ok=True)
 wires={};rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  built=rr.build_side(sgn,kind)
  lengths=[]
  for pin in range(1,15):
   wires[f'Wire-{side}-{pin:02d}']=built[pin]['solid'];lengths.append(built[pin]['length'])
  rows.append(dict(side=side,conductor_lengths_mm=lengths,
                   longest_conductor_mm=max(lengths),
                   margin_to_200_mm=200-(max(lengths)+7.3),
                   alphas=[built[p]['alpha'] for p in range(1,15)],
                   added_slack_mm=[built[p]['added'] for p in range(1,15)],
                   taut_lengths_mm=[built[p]['taut'] for p in range(1,15)],
                   unmodeled_length_mm=7.3,
                   route_qualification='Round 14 Candidate A v13: round-13 A6 corridor/rise + numerically optimised feed; +30.2 mm service slack distributed in the feed (stored vs taut fitted lengths); unplug-first service (PO 2026-11-15).'))
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
 meta=read(baseline/'measurements.json');meta['wings']=rows
 meta['wire_sweep_checks']=[dict(part=n,volume_mm3=q.volume,expected_volume_mm3=rows[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25,volume_error_mm3=abs(q.volume-rows[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25),passed=q.is_valid and len(q.solids())==1 and abs(q.volume-rows[0 if '-left-' in n else 1]['conductor_lengths_mm'][int(n[-2:])-1]*math.pi*.25)<.001) for n,q in wires.items()]
 save(out/'measurements.json',meta)
 save(out/f'round14-fixed-scope-{kind}.json',dict(geometry_sha256=sha(out/'assembly-index.json'),baseline_index_sha256=sha(baseline/'assembly-index.json'),all_fixed_byte_identical=all(a==b for a,b in zip(old,idx) if not a['name'].startswith('Wire-')),changed_names=[a['name'] for a,b in zip(old,idx) if a!=b]))
 shutil.copyfile(baseline/'audit.json',out/'audit.json')
 save(out/'E-boss-audit-parent.json',dict(index_file=f'../round5/{pitch}mm/assembly-index.json',audit_file=f'../round5/{pitch}mm/audit.json',geometry_sha256=sha(baseline/'assembly-index.json'),reason='Every fixed round5 operand byte-identical; round-14 strands recomputed.'))
 print(pitch,'round5 fixed bodies byte-identical; 28 strands regenerated (round 14)',flush=True)
if __name__=='__main__':run(int(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else 'stored')
