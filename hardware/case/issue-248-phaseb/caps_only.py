"""Recheck changed shell clearance, preserving independently measured cable lengths."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);geometry_hash=sha(out/'assembly-index.json')
 shells=[(n,k,s) for n,k,s in raw if n in ('shell-central','strip-left','strip-right')]
 caps=[];witness=[]
 for k in read(out/'cap-plan.json'):
  cap=prism(shape(k['cap']),PLATE+.4,TOP-PLATE-.4)
  records=[]
  for n,j,s in shells:
   gap,pc,ps=cap.distance_to_with_closest_points(s);records.append((gap,n,pc,ps,s))
  gap,n,pc,ps,s=min(records,key=lambda r:r[0]);coordinates=list(ps);b=bounds(s)
  outside=any(coordinates[i]<b[0][i]-1e-5 or coordinates[i]>b[1][i]+1e-5 for i in range(3))
  caps.append(dict(key=k['key'],nominal_gap_mm=gap,allowance_mm=.5,remaining_gap_mm=gap-.5,nearest_part=n,passed=gap-.5>=.3-1e-6))
  witness.append(dict(key=k['key'],nearest_part=n,distance_mm=gap,cap_witness_mm=list(pc),part_witness_mm=coordinates,part_witness_outside_all_part_bounds=outside))
 save(out/'caps.json',dict(status=P['status'],geometry_sha256=geometry_hash,assumption='16x16 swept cap, plate+0.4 to provisional plateau; combined XY/process allowance 0.50 mm',keys=caps,passed=all(k['passed'] for k in caps),full_press_skirt_physical_gate='OPEN: actual Junana q/skirt/full-press test required'))
 save(out/'cap-witnesses.json',dict(status=P['status'],geometry_sha256=geometry_hash,witnesses=witness,solver_inconsistencies=[r for r in witness if r['part_witness_outside_all_part_bounds']],note='Zero distance with a witness outside the operand bounds is an ambiguous kernel result, not certified physical contact.'))
 # Repeat the Fly/shell minimum after the wall relief; no length or path changes.
 f=next(s for n,k,s in raw if n=='Fly-170mm');lf=read(out/'length-fly.json');distance=min(s.distance_to(f) for n,k,s in shells)
 lf['fly'].update(shell_gap_mm=distance,passed=abs(lf['fly']['length_mm']-170)<1e-6 and lf['fly']['minimum_straight_slack_mm']>0 and lf['fly']['valid'] and lf['fly']['solid_count']==1 and lf['fly']['volume_error_mm3']<.001 and distance>=.3-1e-6)
 save(out/'length-fly.json',lf)
 print(pitch,'caps',all(k['passed'] for k in caps),'Fly gap',distance,flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
