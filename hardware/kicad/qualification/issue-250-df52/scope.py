"""Read-only copper-object and geometry deltas against frozen GH inputs."""
from pathlib import Path
import pcbnew as p,json,collections,hashlib
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
E=Path(__file__).resolve().parent;R=E.parents[3]
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def objs(b):
 out={}
 for t in b.GetTracks():
  via=isinstance(t,p.PCB_VIA);net=t.GetNetname();ls=list(b.GetEnabledLayers().CuStack()) if via else [t.GetLayer()]
  width=p.ToMM(t.GetWidth(p.F_Cu) if via else t.GetWidth());coords=[xy(t.GetPosition())] if via else [xy(t.GetStart()),xy(t.GetEnd())]
  geom=Point(coords[0]).buffer(width/2) if via else LineString(coords).buffer(width/2)
  if via:geom=geom.difference(Point(coords[0]).buffer(p.ToMM(t.GetDrillValue())/2))
  out[t.m_Uuid.AsString()]=dict(net=net,layers=ls,width_mm=width,coords=coords,geom=geom,via=via)
 return out
allrecords=[];held=[]
for w in [E/'main',*sorted(E.glob('wing-rev4-*'))]:
 c=json.loads((w/'construction.json').read_text());src=R/c['source'];b=p.LoadBoard(str(src));n=p.LoadBoard(str(w/'main.kicad_pcb'));held.extend([b,n]);a=objs(b);z=objs(n);regions=[Polygon(pts) for pts in c['routing_windows_native_mm']]
 rows=[];total=[]
 for net in sorted(set(v['net'] for v in list(a.values())+list(z.values()))):
  before=unary_union([v['geom'] for v in a.values() if v['net']==net]);after=unary_union([v['geom'] for v in z.values() if v['net']==net]);delta=before.symmetric_difference(after)
  if delta.area<1e-7:continue
  outside=delta.difference(unary_union(regions));total.append(delta)
  rows.append(dict(net=net,track_via_copper_delta_area_mm2=delta.area,bounds_native_mm=list(delta.bounds),outside_connector_windows_mm2=outside.area))
 union=unary_union(total);record=dict(board=w.name,track_via_only=True,native_zones_excluded_from_scope_delta=True,per_net=rows,bounds_native_mm=list(union.bounds),outside_requested_local_scope=any(x['outside_connector_windows_mm2']>1e-6 for x in rows),removed_object_count=len(set(a)-set(z)),added_object_count=len(set(z)-set(a)),changed_existing_objects=[i for i in set(a)&set(z) if any(a[i][k]!=z[i][k] for k in ('net','layers','width_mm','coords'))]);(w/'scope.json').write_text(json.dumps(record,indent=2)+'\n');allrecords.append(record)
(E/'scope-summary.json').write_text(json.dumps(allrecords,indent=2)+'\n')
