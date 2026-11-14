"""Bounded via-in-pad relocation; same nets, no placement or rule changes.
Full native checks and independent graph follow this search.
"""
from pathlib import Path
import pcbnew as p,sys,json,math
from shapely.geometry import Point,LineString
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
def search(w):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));tracks=list(b.GetTracks());feet=list(b.GetFootprints());pads=[a for f in feet for a in f.Pads()];vias=[v for v in tracks if isinstance(v,p.PCB_VIA)];layers=list(b.GetEnabledLayers().CuStack());history=[];held=[]
 areas=[(polys(z.Outline()),set(z.GetLayerSet().Seq()),z.GetDoNotAllowTracks(),z.GetDoNotAllowVias()) for z in list(b.Zones())+[z for f in feet for z in f.Zones()] if z.GetIsRuleArea()]
 def mingap(v,pos):return min((a.GetEffectiveShape(l).Distance(pos)/1e6-.3 for a in pads for l in layers if a.IsOnLayer(l) and v.IsOnLayer(l)),default=999)
 def clearseg(start,end,width,layer,net,skip):
  sh=p.SHAPE_SEGMENT(start,end,p.FromMM(width));g=LineString([xy(start),xy(end)]).buffer(width/2)
  if any(layer in ls and t and g.intersects(poly) for poly,ls,t,v in areas):return False
  for a in pads:
   if not a.IsOnLayer(layer) or a.GetNetname()==net:continue
   if a.GetEffectiveShape(layer).Collide(sh,100001):return False
  for t in tracks:
   if t in skip or t.GetNetname()==net or not t.IsOnLayer(layer):continue
   if isinstance(t,p.PCB_VIA):
    if sh.Collide(p.SHAPE_CIRCLE(t.GetPosition(),int(t.GetWidth(p.F_Cu)/2)),100001):return False
   elif sh.Collide(p.SHAPE_SEGMENT(t.GetStart(),t.GetEnd(),t.GetWidth()),100001):return False
  return True
 for v in vias:
  old=v.GetPosition();gap=mingap(v,old)
  if gap>=.125-2e-6:continue
  net=v.GetNetname();attached=[t for t in tracks if not isinstance(t,p.PCB_VIA) and t.GetNetname()==net and any(math.dist(xy(pos),xy(old))<.000002 for pos in (t.GetStart(),t.GetEnd()))]
  contact_layers=[l for l in layers if any(a.GetNetname()==net and a.IsOnLayer(l) and a.GetEffectiveShape(l).Distance(old)<300000 for a in pads)]
  found=None
  for radius in [.025,.05,.075,.1,.125,.15,.2,.25,.3,.35,.4,.45,.5,.55,.6,.65,.7,.75,.8,.9,1.,1.2,1.5,2.]:
   for angle in range(0,360,15):
    th=math.radians(angle);pos=V(round(p.ToMM(old.x)+radius*math.cos(th),3),round(p.ToMM(old.y)+radius*math.sin(th),3))
    if mingap(v,pos)<.125-2e-6:continue
    if any(math.dist(xy(pos),xy(q.GetPosition()))<.7-1e-6 for q in vias if q!=v):continue
    if any(vb and any(l in ls for l in layers if v.IsOnLayer(l)) and poly.distance(Point(xy(pos)))<.3 for poly,ls,t,vb in areas):continue
    if any(a.GetNetname()!=net and any(a.IsOnLayer(l) and v.IsOnLayer(l) and a.GetEffectiveShape(l).Distance(pos)<400001 for l in layers) for a in pads):continue
    if any((Point(xy(t.GetPosition())).buffer(.3) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2)).distance(Point(xy(pos)))<.400001 for t in tracks if t.GetNetname()!=net):continue
    segs=[]
    for t in attached:
     st,en=t.GetStart(),t.GetEnd();st=pos if math.dist(xy(st),xy(old))<.000002 else st;en=pos if math.dist(xy(en),xy(old))<.000002 else en
     segs.append((st,en,p.ToMM(t.GetWidth()),t.GetLayer(),t))
    width=.3 if net in ('GND','HALL_5V') else .1
    segs.extend((old,pos,width,l,None) for l in contact_layers)
    if not all(clearseg(st,en,width,l,net,attached+[v]) for st,en,width,l,t in segs):continue
    found=(pos,segs);break
   if found:break
  if not found:history.append(dict(via=v.m_Uuid.AsString(),net=net,status='FAILED bounded .025..2mm radial search',before_gap_mm=gap));continue
  pos,segs=found;v.SetPosition(pos)
  for st,en,width,l,t in segs:
   if t:t.SetStart(st);t.SetEnd(en)
   else:
    t=p.PCB_TRACK(b);t.SetStart(st);t.SetEnd(en);t.SetWidth(p.FromMM(width));t.SetLayer(l);t.SetNetCode(v.GetNetCode());b.Add(t);held.append(t);tracks.append(t)
  history.append(dict(via=v.m_Uuid.AsString(),net=net,before_mm=xy(old),after_mm=xy(pos),before_gap_mm=gap,after_gap_mm=mingap(v,pos),status='relocated'))
 # Widen only if full native obstacle clearance is preserved.
 for t in tracks:
  if isinstance(t,p.PCB_VIA) or t.GetNetname() not in ('GND','HALL_5V') or p.ToMM(t.GetWidth())>=.3-1e-9:continue
  if clearseg(t.GetStart(),t.GetEnd(),.3,t.GetLayer(),t.GetNetname(),[t]):
   history.append(dict(track=t.m_Uuid.AsString(),before_width_mm=p.ToMM(t.GetWidth()),after_width_mm=.3));t.SetWidth(p.FromMM(.3))
  else:history.append(dict(track=t.m_Uuid.AsString(),status='FAILED .30mm widening blocked by foreign copper or reservation',width_mm=p.ToMM(t.GetWidth())))
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(w/'main.kicad_pcb'),b)
 (w/'via-width-repair.json').write_text(json.dumps(history,indent=2)+'\n');print(w.name,history,flush=True)
for name in sys.argv[1:]:search(E/name)
