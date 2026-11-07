"""Trim native-DRC free tails while retaining mid-segment T junctions.
A one-sided via is replaced by same-layer copper spokes before removing the
barrel, preserving annulus-mediated contacts. All passes get fresh native DRC.
"""
from pathlib import Path
import json,subprocess,sys,math
import pcbnew as p
from shapely.geometry import Point,LineString
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;V=lambda a:p.VECTOR2I(round(a[0]*1e6),round(a[1]*1e6))
def geom(t):
 if isinstance(t,p.PCB_VIA):return Point(xy(t.GetPosition())).buffer(.3,quad_segs=128).difference(Point(xy(t.GetPosition())).buffer(.15,quad_segs=128))
 return LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128)
def prune(b,drc):
 changes=[]
 ids={a['uuid'] for q in drc['violations'] if q['type'] in ('track_dangling','via_dangling') for a in q['items']}
 for uuid in ids:
  matches=[t for t in b.GetTracks() if t.m_Uuid.AsString()==uuid]
  if not matches:continue
  item=matches[0];net=item.GetNetname()
  if isinstance(item,p.PCB_VIA):
   center=Point(xy(item.GetPosition()));spokes=[]
   for t in b.GetTracks():
    if isinstance(t,p.PCB_VIA) or t.GetNetname()!=net or not geom(t).intersects(geom(item)):continue
    line=LineString([xy(t.GetStart()),xy(t.GetEnd())]);q=line.interpolate(line.project(center))
    if q.distance(center)<.000001:continue
    stub=p.PCB_TRACK(b);stub.SetStart(item.GetPosition());stub.SetEnd(V(q.coords[0]));stub.SetWidth(p.FromMM(.3 if net in ('GND','HALL_5V') else .1));stub.SetLayer(t.GetLayer());stub.SetNetCode(item.GetNetCode());b.Add(stub);spokes.append(stub.m_Uuid.AsString())
   b.Delete(item);changes.append(dict(uuid=uuid,action='replace one-sided barrel by copper spokes',spokes=spokes));continue
  line=LineString([xy(item.GetStart()),xy(item.GetEnd())]);layer=item.GetLayer();contacts=[]
  if line.length<1e-9:b.Delete(item);changes.append(dict(uuid=uuid,action='remove zero length'));continue
  others=[]
  for f in b.GetFootprints():
   for a in f.Pads():
    if a.GetAttribute()!=p.PAD_ATTRIB_NPTH and a.GetNetname()==net and a.IsOnLayer(layer):others.append(padgeom(a,layer))
  others.extend(geom(t) for t in b.GetTracks() if t.m_Uuid.AsString()!=uuid and t.GetNetname()==net and t.IsOnLayer(layer))
  for z in b.Zones():
   if not z.GetIsRuleArea() and z.GetNetname()==net and z.IsOnLayer(layer):others.append(polys(z.GetFilledPolysList(layer)))
  for other in others:
   hit=line.intersection(other)
   if hit.is_empty:continue
   parts=list(hit.geoms) if hasattr(hit,'geoms') else [hit]
   positions=[]
   for part in parts:
    if hasattr(part,'coords'):positions.extend(line.project(Point(v)) for v in part.coords)
   if positions:contacts.append((min(positions)+max(positions))/2)
  if len(contacts)<2 or max(contacts)-min(contacts)<.00001:
   b.Delete(item);changes.append(dict(uuid=uuid,action='remove free leaf'))
  else:
   start=line.interpolate(min(contacts));end=line.interpolate(max(contacts));old=[xy(item.GetStart()),xy(item.GetEnd())];item.SetStart(V(start.coords[0]));item.SetEnd(V(end.coords[0]));changes.append(dict(uuid=uuid,action='trim free tails preserving junctions',before=old,after=[xy(item.GetStart()),xy(item.GetEnd())]))
 return changes
if __name__=='__main__':
 for name in sys.argv[1:]:
  w=E/name;history=json.loads((w/'cleanup.json').read_text()) if (w/'cleanup.json').exists() else []
  for iteration in range(15):
   subprocess.run(['kicad-cli','pcb','drc','--format','json','--severity-all','-o',str(w/'drc.json'),str(w/'main.kicad_pcb')],check=True,stdout=subprocess.PIPE)
   drc=json.loads((w/'drc.json').read_text())
   if drc['unconnected_items']:print(w.name,'needs connectivity repair',len(drc['unconnected_items']),flush=True);break
   if not any(v['type'] in ('track_dangling','via_dangling') for v in drc['violations']):print(w.name,'cleanup stopped; remaining violations',len(drc['violations']),flush=True);break
   b=p.LoadBoard(str(w/'main.kicad_pcb'));manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj());changes=prune(b,drc);assert changes
   b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b);history.append(dict(changes=changes))
  (w/'cleanup.json').write_text(json.dumps(history,indent=2)+'\n')
