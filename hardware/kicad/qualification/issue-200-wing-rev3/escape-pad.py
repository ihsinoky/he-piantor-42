"""Native-checked service-pad via escape; logs every displaced copper item.
Run plane-repair.py, cleanup.py and full qualification after any change.
"""
import sys,json,math
from pathlib import Path
import pcbnew as p
from shapely.geometry import Point,LineString
E=Path(__file__).resolve().parent;sys.path.insert(0,str(E))
from verify import xy,padgeom
V=lambda q:p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
name,ref,pin,tx,ty=sys.argv[1:];target=[float(tx),float(ty)];w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));manager=p.GetSettingsManager();manager.LoadProject(str(w/'main.kicad_pro'));b.SetProject(manager.Prj())
f=next(f for f in b.GetFootprints() if f.GetReference()==ref);a=next(a for a in f.Pads() if a.GetNumber()==pin);net=a.GetNetname();width=.3 if net in ('GND','HALL_5V') else .1
track=p.PCB_TRACK(b);track.SetStart(a.GetPosition());track.SetEnd(V(target));track.SetWidth(p.FromMM(width));track.SetLayer(p.F_Cu);track.SetNetCode(a.GetNetCode())
via=p.PCB_VIA(b);via.SetPosition(V(target));via.SetWidth(600000);via.SetDrill(300000);via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(a.GetNetCode())
line=LineString([xy(a.GetPosition()),target]).buffer(width/2);circle=Point(target).buffer(.3)
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  for l in (p.F_Cu,p.B_Cu):
   if not pad.IsOnLayer(l):continue
   g=padgeom(pad,l);assert g.distance(circle)>=.12499,(f.GetReference(),pad.GetNumber(),'via-pad',g.distance(circle))
   if l==p.F_Cu and pad.GetNetname()!=net:assert g.distance(line)>=.09999,(f.GetReference(),pad.GetNumber(),'track-pad')
rips=[]
for t in list(b.GetTracks()):
 if t.GetNetname()==net:continue
 g=Point(xy(t.GetPosition())).buffer(.3) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)
 if g.distance(circle)<.10001 or (t.IsOnLayer(p.F_Cu) and g.distance(line)<.10001):
  rips.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname()));b.Delete(t)
b.Add(track);b.Add(via);b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b)
path=w/'pad-escape.json';history=json.loads(path.read_text()) if path.exists() else [];history.append(dict(ref=ref,pin=pin,net=net,via_mm=target,rips=rips));path.write_text(json.dumps(history,indent=2)+'\n');print(net,'escape',target,'ripped',len(rips))
