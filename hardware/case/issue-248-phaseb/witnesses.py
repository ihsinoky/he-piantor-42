"""Reviewable Common bounds and cap distance witnesses, including solver inconsistencies."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch)
 physical=[(n,k,s) for n,k,s in raw if not n.startswith('USB-reference-')]
 audit=read(out/'audit.json');assert audit['geometry_sha256']==sha(out/'assembly-index.json')
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 contacts=[]
 for i,r in enumerate(audit['unexpected_interferences']):
  if 'common_bounds_mm' in r:
   contacts.append(dict(**r,replay_volume_mm3=r['volume_mm3']));continue
  a=physical[r['i']][2];b=physical[r['j']][2]
  op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
  try:
   assert op.IsDone();q=Shape.cast(op.Shape())
   contacts.append(dict(**r,common_bounds_mm=bounds(q),replay_volume_mm3=abs(q.volume)))
  except Exception as e:contacts.append(dict(**r,witness_error=repr(e)))
  if i%20==0:
   save(out/'collision-map.json',dict(status=P['status'],complete=False,contacts=contacts));print(pitch,'witness',i,flush=True)
 save(out/'collision-map.json',dict(status=P['status'],complete=True,contacts=contacts,bounds_qualification='OCCT BRep support bounds of each Common are conservative bounding boxes, not points on the contact surface.'))
 if (out/'cap-witnesses.json').exists() and read(out/'cap-witnesses.json').get('geometry_sha256')==audit['geometry_sha256']:return
 caps=read(out/'caps.json');capplan={r['key']:r for r in read(out/'cap-plan.json')};witness=[]
 for r in caps['keys']:
  cap=prism(shape(capplan[r['key']]['cap']),PLATE+.4,TOP-PLATE-.4)
  candidates=[s for n,k,s in physical if n==r['nearest_part']]
  distance,pc,ps=min([cap.distance_to_with_closest_points(s) for s in candidates],key=lambda row:row[0])
  coordinates=list(ps)
  box_issue=all(any(coordinates[i]<bounds(s)[0][i]-1e-5 or coordinates[i]>bounds(s)[1][i]+1e-5 for i in range(3)) for s in candidates)
  witness.append(dict(key=r['key'],nearest_part=r['nearest_part'],distance_mm=distance,cap_witness_mm=list(pc),part_witness_mm=list(ps),part_witness_outside_all_part_bounds=box_issue))
 save(out/'cap-witnesses.json',dict(status=P['status'],witnesses=witness,solver_inconsistencies=[r for r in witness if r['part_witness_outside_all_part_bounds']],note='A zero solid distance with a part witness outside its BRep bounds is a failed/ambiguous kernel result, not proof of a physical contact. Cap gate stays failed until rebuilt/reverified.'))
if __name__=='__main__':run(int(sys.argv[1]))
