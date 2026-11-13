import pcbnew as p,json
from pathlib import Path
from shapely.geometry import LineString,Point
from shapely.ops import unary_union
E=Path('hardware/kicad/qualification/issue-240-main-rev7').resolve();old=p.LoadBoard(str(E.parent/'issue-226-main-rev6/inspection/final/main.kicad_pcb'));new=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'))
def copper(b):
 out={}
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   xy=(p.ToMM(t.GetPosition().x),p.ToMM(t.GetPosition().y));g=Point(xy).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2,quad_segs=64);ls=list(b.GetEnabledLayers().CuStack())
  else:g=LineString([[p.ToMM(t.GetStart().x),p.ToMM(t.GetStart().y)],[p.ToMM(t.GetEnd().x),p.ToMM(t.GetEnd().y)]]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=64);ls=[t.GetLayer()]
  for l in ls:out.setdefault((t.GetNetname(),l),[]).append(g)
 return {k:unary_union(v) for k,v in out.items()}
a,b=copper(old),copper(new);rows=[]
for k in a.keys()|b.keys():
 x=a.get(k,Point().buffer(0));y=b.get(k,Point().buffer(0));remove=x.difference(y.buffer(.000002));add=y.difference(x.buffer(.000002))
 if remove.area+add.area>1e-6:rows.append(dict(net=k[0],layer=old.GetLayerName(k[1]),removed_mm2=remove.area,added_mm2=add.area,removed_bounds_mm=list(remove.bounds) if not remove.is_empty else None,added_bounds_mm=list(add.bounds) if not add.is_empty else None))
(E/'routing-geometry-diff.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
