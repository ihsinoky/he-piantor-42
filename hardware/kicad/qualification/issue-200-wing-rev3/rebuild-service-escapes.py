"""Rebuild the north routing window with frozen native TSSOP fanouts.
Straight, staggered dogbones prevent power/signal repair from boxing in each
other. No pad, net, component, rule or existing copper outside the window moves.
"""
from pathlib import Path
import json,math,sys
import pcbnew as p
from shapely.geometry import Point,LineString,box
from verify import xy,padgeom,polys
E=Path(__file__).resolve().parent;name=sys.argv[1];w=E/name;b=p.LoadBoard(str(w/'main.kicad_pcb'));mgr=p.GetSettingsManager();mgr.LoadProject(str(w/'main.kicad_pro'));b.SetProject(mgr.Prj());V=lambda q:p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
window=box(50,15,110,68);removed=[]
for t in list(b.GetTracks()):
 geom=Point(xy(t.GetPosition())) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())])
 if not geom.intersects(window):continue
 removed.append(dict(uuid=t.m_Uuid.AsString(),net=t.GetNetname()))
 if not isinstance(t,p.PCB_VIA):
  outside=geom.difference(window.buffer(.001))
  for part in getattr(outside,'geoms',[outside]):
   if part.is_empty or part.length<.001:continue
   copy=p.PCB_TRACK(b);copy.SetStart(V(part.coords[0]));copy.SetEnd(V(part.coords[-1]));copy.SetLayer(t.GetLayer());copy.SetWidth(t.GetWidth());copy.SetNetCode(t.GetNetCode());b.Add(copy)
 b.Delete(t)
spec=json.loads((w/'definition.json').read_text());g=next(g for g in json.loads((E.parents[3]/'hardware/case/issue-200-stage1/geometry.json').read_text())['variants'] if 'wing-rev3-'+g['variant']==name);m=g['transform']['matrix'];tr=g['transform']['translation']
fs={f.GetReference():f for f in b.GetFootprints()};pads=[a for f in b.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
centers={ref:m[0][0]*(xy(fs[ref].GetPosition())[0]-100)+m[0][1]*(100-xy(fs[ref].GetPosition())[1])+tr[0] for ref in ('U_MUX_A','U_MUX_B','U_MUX_C')}
ps=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(ps);board=polys(ps);records=[]
for ref,cx in centers.items():
 f=fs[ref];angle=math.radians(f.GetOrientationDegrees());cos=math.cos(angle);sin=math.sin(angle)
 for a in f.Pads():
  if not a.GetNetname():continue
  dx=a.GetPosition().x/1e6-f.GetPosition().x/1e6;dy=a.GetPosition().y/1e6-f.GetPosition().y/1e6
  lx=dx*cos-dy*sin;ly=-dx*sin-dy*cos;side=1 if lx>0 else -1;index=round((2.275-ly)/.65)
  outer=(cx==min(centers.values()) and side<0) or (cx==max(centers.values()) and side>0)
  reach=(1.15 if (index+(1 if side>0 else 0))%2==0 else (1.45 if outer else 1.85))
  target=[a.GetPosition().x/1e6+side*reach*cos,a.GetPosition().y/1e6-side*reach*sin];pos=V(target)
  width=.3 if a.GetNetname() in ('HALL_5V','GND') else .1
  stub=p.PCB_TRACK(b);stub.SetStart(a.GetPosition());stub.SetEnd(pos);stub.SetLayer(p.F_Cu);stub.SetWidth(p.FromMM(width));stub.SetNetCode(a.GetNetCode());sg=stub.GetEffectiveShape(p.F_Cu)
  via=p.PCB_VIA(b);via.SetPosition(pos);via.SetWidth(600000);via.SetDrill(300000);via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetNetCode(a.GetNetCode());disk=p.SHAPE_CIRCLE(pos,300000)
  assert board.buffer(-.60001).contains(Point(xy(pos))),(ref,a.GetNumber(),'edge')
  assert all(aa.GetEffectiveShape(l).Distance(pos)/1e6-.3>=.125 for aa in pads for l in (p.F_Cu,p.B_Cu) if aa.IsOnLayer(l)),(ref,a.GetNumber(),'via-pad')
  assert all(aa.GetNetname()==a.GetNetname() or not aa.IsOnLayer(p.F_Cu) or not aa.GetEffectiveShape(p.F_Cu).Collide(sg,100001) for aa in pads),(ref,a.GetNumber(),'stub-pad')
  for t in b.GetTracks():
   if t.GetNetname()==a.GetNetname():continue
   assert not t.GetEffectiveShape(t.GetLayer()).Collide(disk,100001),(ref,a.GetNumber(),'via-track',t.GetNetname())
   if t.IsOnLayer(p.F_Cu):assert not t.GetEffectiveShape(p.F_Cu).Collide(sg,100001),(ref,a.GetNumber(),'stub-track',t.GetNetname())
  b.Add(stub);b.Add(via);records.append(dict(ref=ref,pin=a.GetNumber(),net=a.GetNetname(),via_mm=xy(pos),width_mm=width,reach_mm=reach))
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();p.SaveBoard(str(w/'main.kicad_pcb'),b,True)
(w/'service-rebuild.json').write_text(json.dumps(dict(window_mm=list(window.bounds),removed=removed,fanouts=records),indent=2)+'\n');print(name,'staggered fanouts',len(records))
