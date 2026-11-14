"""Certified bounded-face cap audit; no whole-solid inside-classifier shortcut."""
from common import *
from certified_distance import boundary_distance,box_lower
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);ghash=sha(out/'assembly-index.json')
 shells=[(n,k,s) for n,k,s in raw if n in ('shell-central','strip-left','strip-right')]
 caps=[];witness=[]
 for k in read(out/'cap-plan.json'):
  cap=prism(shape(k['cap']),PLATE+.4,TOP-PLATE-.4);best=float('inf');nearest=None;proof=None;commons=[]
  for n,j,s in shells:
   v=volume(cap,s);commons.append(dict(part=n,solid=j,common_mm3=v));assert v<1e-6,(k['key'],n,v)
   if box_lower(bounds(cap),bounds(s))>best+1e-7:continue
   gap,record=boundary_distance(cap,s)
   if gap<best:best=gap;nearest=n;proof=record
  caps.append(dict(key=k['key'],nominal_gap_mm=best,allowance_mm=.5,remaining_gap_mm=best-.5,nearest_part=nearest,certified=True,passed=best-.5>=.3-1e-6))
  witness.append(dict(key=k['key'],nearest_part=nearest,distance_mm=best,cap_witness_mm=proof['a_point_mm'],part_witness_mm=proof['b_point_mm'],part_witness_outside_all_part_bounds=False,boundary_distance_proof=proof,all_shell_cap_commons=commons))
 save(out/'caps.json',dict(status=P['status'],geometry_sha256=ghash,assumption='16x16 swept cap, plate+0.4 to provisional plateau; combined XY/process allowance 0.50 mm',method='All bounded face pairs with certified AABB exclusion and finite witnesses; zero cap/solid Common verified for every actual shell solid. No whole-solid distance classifier shortcut.',certified=True,keys=caps,passed=all(k['passed'] for k in caps),full_press_skirt_physical_gate='OPEN: actual Junana q/skirt/full-press test required'))
 save(out/'cap-witnesses.json',dict(status=P['status'],geometry_sha256=ghash,witnesses=witness,solver_inconsistencies=[]))
 print(pitch,'caps certified',min(k['remaining_gap_mm'] for k in caps),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
