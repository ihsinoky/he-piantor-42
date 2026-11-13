"""Widen existing positive conductors only, bounded by native foreign copper.
No centerline, pad, via, net, hole, outline or component changes.
"""
from common import *
import pcbnew as p,importlib.util,math
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
w=E/'inspection/final';b=p.LoadBoard(str(w/'main.kicad_pcb'));layers=list(b.GetEnabledLayers().CuStack());tracks=list(b.GetTracks());foreign={};rows=[]
for net in ['V5V2','HALL_5V']:
 for l in layers:
  gs=[]
  for f in b.GetFootprints():
   for a in f.Pads():
    if a.GetNetname()==net or not a.IsOnLayer(l):continue
    if a.GetAttribute()==p.PAD_ATTRIB_NPTH:gs.append(Point(m.xy(a.GetPosition())).buffer(p.ToMM(a.GetDrillSize().x)/2+.11))
    else:gs.append(m.pad_polygon(a,l))
  for t in tracks:
   if t.GetNetname()==net:continue
   if isinstance(t,p.PCB_VIA):
    if t.IsOnLayer(l):gs.append(Point(m.xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(l))/2))
   elif t.GetLayer()==l:gs.append(LineString([m.xy(t.GetStart()),m.xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2))
  foreign[net,l]=unary_union(gs)
for t in tracks:
 if isinstance(t,p.PCB_VIA) or t.GetNetname() not in ['V5V2','HALL_5V']:continue
 line=LineString([m.xy(t.GetStart()),m.xy(t.GetEnd())]);old=p.ToMM(t.GetWidth());new=min(2.,math.floor(max(0,2*(line.distance(foreign[t.GetNetname(),t.GetLayer()])-.105))*1000)/1000)
 if new>old+.01:
  t.SetWidth(p.FromMM(new))
  other='HALL_5V' if t.GetNetname()=='V5V2' else 'V5V2'
  foreign[other,t.GetLayer()]=unary_union([foreign[other,t.GetLayer()],line.buffer(new/2)])
  rows.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname(),layer=b.GetLayerName(t.GetLayer()),old_width_mm=old,new_width_mm=new,start_mm=m.xy(t.GetStart()),end_mm=m.xy(t.GetEnd())))
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b);save(E/'power-width-recovery.json',rows)
print('Widened',len(rows),'segments')
