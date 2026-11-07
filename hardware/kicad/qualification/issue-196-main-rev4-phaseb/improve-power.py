"""Improve actual copper without placement changes: PGND plane tap and clearance-bounded widening."""
from common import *
import pcbnew as p,math,importlib.util
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
src=E/'runs/auto04/out.kicad_pcb';assert src.exists()
b=p.LoadBoard(str(src));layers=list(b.GetEnabledLayers().CuStack());tracks=list(b.GetTracks());pads=[(pad,l,a.pad_polygon(pad,l)) for f in b.GetFootprints() for pad in f.Pads() if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH for l in layers if pad.IsOnLayer(l)]
def copper(t):return Point(a.xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2,quad_segs=128) if isinstance(t,p.PCB_VIA) else LineString([a.xy(t.GetStart()),a.xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128)
def obstacles(net,l):return unary_union([g for pad,pl,g in pads if pl==l and pad.GetNetname()!=net]+[copper(t) for t in b.GetTracks() if t.GetNetname()!=net and t.IsOnLayer(l)]+[a.polygons(z.Outline()) for z in b.Zones() if z.GetIsRuleArea() and z.IsOnLayer(l)])
# PGND is driven specifically at U6.10. A near local plane tap prevents a long
# 0.1mm detour through control grounds before the first plane barrel.
origin=[97.425,101.0];allpads=unary_union([g for _,_,g in pads]);foreign={l:obstacles('GND',l) for l in layers}
origins=[a.xy(pad.GetPosition()) for f in b.GetFootprints() if f.GetReference()=='U6' for pad in f.Pads() if pad.GetNetname()=='GND']
origins += [a.xy(t.GetStart()) for t in b.GetTracks() if not isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and math.dist(a.xy(t.GetStart()),origin)<2]
candidates=sorted([(round(97.425+i*.05,6),round(101+j*.05,6)) for i in range(-70,71) for j in range(-70,71)],key=lambda q:math.dist(q,[97.425,101]))
chosen=None
for pos in candidates:
 pt=Point(pos)
 if pt.distance(allpads)<.42505:continue
 if any(pt.distance(foreign[l])<.40005 for l in layers):continue
 choices=[q for q in origins if LineString([q,pos]).distance(foreign[p.F_Cu])>=.15005]
 if not choices:continue
 origin=min(choices,key=lambda q:math.dist(q,pos));chosen=pos;break
assert chosen is not None,'No PGND local via candidate'
v=p.PCB_VIA(b);v.SetPosition(a.point(chosen));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(next(pad.GetNetCode() for pad,_,_ in pads if pad.GetNetname()=='GND'));b.Add(v)
t=p.PCB_TRACK(b);t.SetStart(a.point(origin));t.SetEnd(a.point(chosen));t.SetLayer(p.F_Cu);t.SetWidth(p.FromMM(.1));t.SetNetCode(v.GetNetCode());b.Add(t)
pgnd_stub_uuid=t.m_Uuid.AsString()
changes=[]
outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline);board=a.polygons(outline)
for net in ['V5V2','HALL_5V','VBUS','GND']:
 foreign={l:obstacles(net,l) for l in layers}
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) or t.GetNetname()!=net:continue
  old=p.ToMM(t.GetWidth());line=LineString([a.xy(t.GetStart()),a.xy(t.GetEnd())]);distance=min(line.distance(foreign[t.GetLayer()])-.10005,line.distance(board.boundary)-.20005)
  new=min(2.0,math.floor(2*distance/.025)*.025)
  if new>old+.00001:t.SetWidth(p.FromMM(new));changes.append(dict(uuid=t.m_Uuid.AsString(),net=net,from_mm=old,to_mm=new))
w=E/'runs/power01';w.mkdir(parents=True,exist_ok=True);p.SaveBoard(str(w/'out.kicad_pcb'),b)
save(w/'changes.json',dict(source_sha256=digest(src),PGND_via=dict(uuid=v.m_Uuid.AsString(),position_mm=chosen,stub_uuid=pgnd_stub_uuid,all_pad_gap_mm=Point(chosen).distance(allpads)-.3),widened=changes,method='Distance to all foreign pads/tracks/vias and rule areas; 0.10005mm gap, 0.20005mm edge; width quantized down at 0.025mm; cap 2mm'))
print('PGND via',chosen,'widened',len(changes),flush=True)
