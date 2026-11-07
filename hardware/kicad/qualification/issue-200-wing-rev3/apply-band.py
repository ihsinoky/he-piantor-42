"""Synchronize the full south 2mm no-track/no-via reservation before repair."""
from pathlib import Path
import json,sys
import pcbnew as p
from shapely.geometry import LineString,Polygon,Point
from verify import xy
E=Path(__file__).resolve().parent;R=E.parents[3];V=lambda q:p.VECTOR2I(round(q[0]*1e6),round(q[1]*1e6))
for g in json.loads((R/'hardware/case/issue-200-stage1/geometry.json').read_text())['variants']:
 name='wing-rev3-'+g['variant']
 if len(sys.argv)>1 and name not in sys.argv[1:]:continue
 w=E/name
 line=LineString([(100+x,100-y) for x,y in ([g['south_trim_line_local'][0][0]]+[ab[1] for ab in g['south_trim_line_local']])]);band=line.buffer(2,join_style=2).intersection(Polygon([(100+x,100-y) for x,y in g['outline_local']]))
 removed=[];native_boards=[]
 for filename in ('input.kicad_pcb','main.kicad_pcb'):
  if not (w/filename).exists():continue
  b=p.LoadBoard(str(w/filename));native_boards.append(b)
  for z in list(b.Zones()):
   if z.GetIsRuleArea() and z.GetZoneName().startswith('South reserved'):b.Delete(z)
  for part in getattr(band,'geoms',[band]):
   z=p.ZONE(b);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask());z.SetZoneName('South reserved band: no signal tracks or vias');z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(False);z.SetDoNotAllowCopperPour(False);poly=z.Outline();poly.NewOutline()
   for q in list(part.exterior.coords)[:-1]:v=V(q);poly.Append(v.x,v.y)
   b.Add(z)
  for item in list(b.GetTracks()):
   geom=Point(xy(item.GetPosition())).buffer(.3) if isinstance(item,p.PCB_VIA) else LineString([xy(item.GetStart()),xy(item.GetEnd())]).buffer(p.ToMM(item.GetWidth())/2)
   if geom.intersects(band):removed.append(dict(file=filename,uuid=item.m_Uuid.AsString(),net=item.GetNetname()));b.Delete(item)
  mgr=p.GetSettingsManager();mgr.LoadProject(str(w/filename.replace('.kicad_pcb','.kicad_pro')));b.SetProject(mgr.Prj());b.BuildConnectivity()
  if filename.startswith('main'):p.ZONE_FILLER(b).Fill(b.Zones());b.BuildConnectivity()
  p.SaveBoard(str(w/filename),b)
 (w/'south-band-update.json').write_text(json.dumps(removed,indent=2)+'\n');print(name,'south removals',len(removed),flush=True)
