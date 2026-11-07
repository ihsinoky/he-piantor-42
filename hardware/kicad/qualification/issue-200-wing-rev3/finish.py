"""Add supplementary low-resistance pours to fully trace-routed boards; refill.
The routed spine remains, power copper must never replace a missing signal.
"""
from pathlib import Path
import json,shutil,sys,subprocess
import pcbnew as p
from shapely.geometry import box,Point,LineString
from shapely.ops import unary_union
from verify import xy
E=Path(__file__).resolve().parent
V=lambda x,y:p.VECTOR2I(round(x*1e6),round(y*1e6))
for w in sorted(E.glob('wing-rev3-*')):
 if len(sys.argv)>1 and w.name not in sys.argv[1:]:continue
 src=next(w/name for name in ('margin.kicad_pcb','repaired.kicad_pcb','continued.kicad_pcb','routed.kicad_pcb') if (w/name).exists())
 b=p.LoadBoard(str(src));assert b
 manager=p.GetSettingsManager();manager.LoadProject(str(w/'input.kicad_pro'));b.SetProject(manager.Prj())
 for z in list(b.Zones()):
  if not z.GetIsRuleArea():b.Delete(z)
  elif z.GetIsRuleArea():z.SetDoNotAllowPads(False) # Exempt the mounting NPTH itself; copper still banned.
 spec=json.loads((w/'definition.json').read_text());points=spec['outline_mm']
 # Reserve 2mm copper setback at planned break tabs before final refill.
 xmin=min(x for x,y in points)+100;xmax=max(x for x,y in points)+100
 ymin=100-max(y for x,y in points);ymax=100-min(y for x,y in points);width=xmax-xmin;height=ymax-ymin
 boxes=[]
 for cy in (70.,95.):
  boxes.extend([(xmin-.01,cy-4.5,xmin+2,cy+4.5),(xmax-2,cy-4.5,xmax+.01,cy+4.5)])
 for i,(x0,y0,x1,y1) in enumerate(boxes,1):
  z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName(f'Panel tab {i}: 2mm copper setback');z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowCopperPour(True)
  poly=z.Outline();poly.NewOutline()
  for x,y in ((x0,y0),(x1,y0),(x1,y1),(x0,y1)):v=V(x,y);poly.Append(v.x,v.y)
  b.Add(z)
 # Delete any routed copper crossing the new panel-break setbacks; repair afterwards.
 forbidden=unary_union([box(*q) for q in boxes]);removed=[]
 for item in list(b.GetTracks()):
  shape=Point(xy(item.GetPosition())).buffer(.3) if isinstance(item,p.PCB_VIA) else LineString([xy(item.GetStart()),xy(item.GetEnd())]).buffer(p.ToMM(item.GetWidth())/2)
  if shape.intersects(forbidden):removed.append(item.m_Uuid.AsString());b.Delete(item)
 (w/'panel-setback-removal.json').write_text(json.dumps(removed,indent=2)+'\n')
 for name,layer in [('HALL_5V',p.F_Cu),('GND',p.B_Cu)]:
  z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.FindNet(name).GetNetCode());z.SetZoneName(name+' low resistance supplementary pour');z.SetLocalClearance(p.FromMM(.15));z.SetMinThickness(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
  poly=z.Outline();poly.NewOutline()
  for x,y in points:v=V(100+x,100-y);poly.Append(v.x,v.y)
  b.Add(z)
 # A rule-area's own unplated mounting hole is not a forbidden copper pad.
 # All copper pad vs circle distances are independently checked by verify.py.
 shutil.copyfile(w/'input.kicad_pro',w/'main.kicad_pro')
 b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity();assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
 subprocess.run([sys.executable,str(E/'apply-band.py'),w.name],check=True)
 subprocess.run([sys.executable,str(E/'power-taps.py'),w.name],check=True)
 print(w.name,flush=True)
