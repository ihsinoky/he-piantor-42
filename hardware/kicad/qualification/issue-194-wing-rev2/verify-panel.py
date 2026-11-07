"""Independently compare every panel footprint/pad and routed item to its source."""
from pathlib import Path
import collections,hashlib,json
import pcbnew as p
from shapely.affinity import translate
from shapely.geometry import LineString
from verify import polys
E=Path(__file__).resolve().parent

def fp_signature(f,dx=0,dy=0,prefix=''):
 def position(v):return (v.x+dx,v.y+dy)
 return (f.GetValue(),position(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),tuple(sorted((a.GetNumber(),prefix+a.GetNetname() if a.GetNetname() else '',position(a.GetPosition()),a.GetSize().x,a.GetSize().y,a.GetDrillSize().x,a.GetDrillSize().y,a.GetAttribute(),a.GetOrientationDegrees(),tuple(a.GetLayerSet().Seq())) for a in f.Pads())))
def tracks(b,dx=0,dy=0,prefix=''):
 rows=[]
 for t in b.GetTracks():
  if not t.GetNetname().startswith(prefix):continue
  net=prefix+t.GetNetname() if dx or dy else t.GetNetname()
  if isinstance(t,p.PCB_VIA):row=('via',net,t.GetPosition().x+dx,t.GetPosition().y+dy,t.GetWidth(p.F_Cu),t.GetDrillValue())
  else:row=('track',net,t.GetLayer(),tuple(sorted(((t.GetStart().x+dx,t.GetStart().y+dy),(t.GetEnd().x+dx,t.GetEnd().y+dy)))),t.GetWidth())
  rows.append(row)
 return collections.Counter(rows)
results=[]
for pitch in (16,17):
 w=E/f'panel-{pitch}mm';meta=json.loads((w/'panel.json').read_text());b=p.LoadBoard(str(w/'main.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};ps=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(ps);panel=polys(ps);expected_tracks=collections.Counter();nfp=0
 for transform in meta['transforms']:
  src=E/f'wing-rev2-{pitch}mm-{transform["side"]}';assert hashlib.sha256((src/'main.kicad_pcb').read_bytes()).hexdigest()==transform['source_sha256']
  source=p.LoadBoard(str(src/'main.kicad_pcb'));dx=round(transform['dx_mm']*1e6);dy=round(transform['dy_mm']*1e6);prefix=transform['prefix']
  for f in source.GetFootprints():
   assert fp_signature(fs[prefix+f.GetReference()])==fp_signature(f,dx,dy,prefix),(w.name,f.GetReference())
   nfp+=1
  # Route transfer uses a direct signature, without reconstructing routes.
  for t in source.GetTracks():
   if isinstance(t,p.PCB_VIA):row=('via',prefix+t.GetNetname(),t.GetPosition().x+dx,t.GetPosition().y+dy,t.GetWidth(p.F_Cu),t.GetDrillValue())
   else:row=('track',prefix+t.GetNetname(),t.GetLayer(),tuple(sorted(((t.GetStart().x+dx,t.GetStart().y+dy),(t.GetEnd().x+dx,t.GetEnd().y+dy)))),t.GetWidth())
   expected_tracks[row]+=1
  ps=p.SHAPE_POLY_SET();source.GetBoardPolygonOutlines(ps);shape=translate(polys(ps),dx/1e6,dy/1e6);assert shape.difference(panel).area<1e-7
  spec=json.loads((src/'definition.json').read_text());pts=spec['outline_mm'];chamfer=pts[1:3] if transform['side']=='left' else pts[:2];cut=LineString([(100+x+dx/1e6,100-y+dy/1e6) for x,y in chamfer]);assert cut.difference(panel.boundary.buffer(.000003)).length<.000003
 assert tracks(b)==expected_tracks,(w.name,'route transfer')
 assert len(fs)==nfp+72+4+3
 d=json.loads((w/'drc.json').read_text());assert not d['unconnected_items'] and not d['violations']
 results.append(dict(panel=w.name,source_footprints_checked=nfp,routed_items_checked=sum(expected_tracks.values()),all_pad_net_pose_hole_transforms_match=True,chamfers_preserved=True,drc_opens=0,drc_violations=0,pass_all=True))
(E/'panel-verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
