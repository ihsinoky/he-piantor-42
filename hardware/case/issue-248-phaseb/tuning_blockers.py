"""Explicit constraints behind unresolved gates; never authorize material deletion."""
from common import *
from certified_distance import boundary_distance

def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch)
 regions={r['properties']['name']:shape(r['geometry']) for r in read(out/'surface-plan.geojson')['features']}
 exceptions=unary_union([shape(b['outer']) for b in read(out/'measurements.json')['blisters']]+[Point(x,y).buffer(2.55,quad_segs=64) for x,y in P['south_opening_xy_mm']])
 low=fuseall(sloped(regions['low_south'].difference(exceptions),PLATE,0));slope=fuseall(sloped(regions['slope'].difference(exceptions),TOP+M*START,M))
 conflicts=[]
 for n,k,q in raw:
  if n.startswith('plate-') and not n.startswith('plate-screw-') or n.startswith('POM-'):
   for area,roof in [('low_south',low),('slope',slope)]:
    v=volume(roof,q)
    if v>1e-6:conflicts.append(dict(fixed_part=n,required_skin_region=area,intersection_mm3=v,roof_rule='2.00 mm normal skin beneath settled exterior',resolution_blocker='Clearing this fixed body by cutting required skin would violate the roof rule. Requires a changed exterior/footprint, changed fixed stack, or explicit different material ownership; none authorized.'))
 for n,k,q in raw:
  if n.startswith('tray-'):
   band=q.intersect(prism(box(-200,69.7001,200,100),PLATE-1.501,1.502))
   if band is not None:
    v=volume(low,Compound(children=list(band)))
    if v>1e-6:conflicts.append(dict(fixed_part=n+' protected south palm band',required_skin_region='low_south',intersection_mm3=v,roof_rule='2.00 mm roof and unchanged protected palm material Y69.7001..100',resolution_blocker='Tray relief here changes the protected palm material invariant; shell relief removes required roof skin. Neither waived.'))
 shell=[q for n,k,q in raw if n=='shell-central'];separation=[]
 for i in range(len(shell)):
  for j in range(i):
   gap,proof=boundary_distance(shell[i],shell[j]);separation.append(dict(solids=[i,j],gap_mm=gap,proof=proof))
 footprint=unary_union([regions[n] for n in ('plateau','slope','low_south')])
 first=read(HERE/'first-candidate'/f'{pitch}mm/audit.json')
 current=read(out/'audit.json')
 oldpairs={tuple(sorted([r['a'],r['b']])) for r in first['unexpected_interferences']}
 newpairs={tuple(sorted([r['a'],r['b']])) for r in current['unexpected_interferences']}
 save(out/'tuning-comparison.json',dict(geometry_sha256=sha(out/'assembly-index.json'),first_candidate_contacts=len(first['unexpected_interferences']),current_contacts=len(current['unexpected_interferences']),cleared_named_pairs=[list(r) for r in sorted(oldpairs-newpairs)],new_named_pairs=[list(r) for r in sorted(newpairs-oldpairs)],remaining_named_pairs=[list(r) for r in sorted(newpairs&oldpairs)]))
 save(out/'tuning-blockers.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),fixed_roof_conflicts=conflicts,central_shell_components=len(shell),central_shell_separations=separation,settled_footprint_components=[dict(area_mm2=p.area,bounds_mm=list(p.bounds)) for p in polygons(footprint)],shell_connection_blocker='Disconnected south surface footprint at 16 mm: a bridge would add exterior footprint or cross an excluded well. No bridge/deletion used.' if len(shell)>1 else None,wiring_blocker='See exhaustive constituent collision-map and continuous service-motion results. Candidate is not accepted unless all contacts clear; no strand/strand overlap exemption.'))
 print(pitch,'required-skin conflicts',len(conflicts),'shell solids',len(shell),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
