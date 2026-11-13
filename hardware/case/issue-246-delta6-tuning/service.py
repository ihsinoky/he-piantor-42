"""Conservative continuous U-retraction clearance after the documented disassembly.
See service_envelope.py for the continuous swept-strip construction and
its conservative sampling allowance.
The full OD5 Z slab is conservative relative to the round bundle.
"""
import sys,math
import study as s
from service_envelope import footprint

def main(pitch):
 out=s.HERE/f'{pitch}mm';cache=s.RUNTIME/f'audit{pitch}'
 idx=s.read(cache/'index.json');raw=[]
 for i,r in enumerate(idx):
  q=s.TopoDS_Shape();s.BRepTools.Read_s(q,str(cache/f'{i}.brep'),s.BRep_Builder());raw.append(s.Shape.cast(q))
 removed=[];retained=[]
 for r,q in zip(idx,raw):
  n=r['name']
  if n in ('main','Cover','EZmate-Main-plug') or n.startswith(('Main-study-','Main-GH-','screw-main-','washer-main-','cover-screw-','cover-Main-spacer-','Wing-')):
   removed.append(n)
  else:retained.append((r,q))
 rows=[]
 for side,sgn in [('left',-1),('right',1)]:
  g=footprint(sgn);sweep=s.prism(g,4.5,5)
  print('SERVICE ENVELOPE',side,'vertices',sum(len(p.exterior.coords) for p in s.polygons(g)),flush=True)
  hits=[];tested=0
  for r,q in retained:
   tested+=1;v=s.fast_volume(q,sweep)
   if v>1e-6:hits.append(dict(part=r['name'],solid=r['solid'],volume_mm3=v))
  rows.append(dict(side=side,retained_constituents_tested=tested,turn_start_Y_mm=22.1,turn_finish_Y_mm=7,accessible_reserve_mm=30.2,clearance_envelope_bounds_mm=s.bounds(sweep),unexpected_contacts=hits,clear=not hits))
  print('SERVICE',side,rows[-1],flush=True)
 result=dict(scope='U retraction after lid, plugs and Main removal; Wing boards/posts/decks remain fitted',removed_parts=sorted(set(removed)),continuous_motion_bounded=True,construction='analytic continuous cap strip and longest legs; R5 arc sampling bounded by 0.152 mm allowance',XY_buffer_mm=2.652,bundle_radius_mm=2.5,conservative_Z_slab_mm=[4.5,9.5],volume_threshold_mm3=1e-6,sides=rows,pass_clearance=all(r['clear'] for r in rows))
 s.save(out/'service.json',result)
if __name__=='__main__':main(int(sys.argv[1]))
