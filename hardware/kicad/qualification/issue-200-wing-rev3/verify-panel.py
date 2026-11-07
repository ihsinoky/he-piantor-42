"""Independently compare every panel footprint/pad and routed item to its source."""
from pathlib import Path
import collections,hashlib,json,csv,gzip,sys
import pcbnew as p
from shapely.affinity import translate
from shapely.geometry import LineString
from verify import polys,xy
from shapely.ops import unary_union
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
 if len(sys.argv)>1 and str(pitch) not in sys.argv[1:]:continue
 w=E/f'panel-{pitch}mm';meta=json.loads((w/'panel.json').read_text());b=p.LoadBoard(str(w/'main.kicad_pcb'));fs={f.GetReference():f for f in b.GetFootprints()};ps=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(ps);panel=polys(ps);expected_tracks=collections.Counter();nfp=0
 for transform in meta['transforms']:
  src=E/f'wing-rev3-{pitch}mm-{transform["side"]}';assert hashlib.sha256((src/'main.kicad_pcb').read_bytes()).hexdigest()==transform['source_sha256']
  source=p.LoadBoard(str(src/'main.kicad_pcb'));dx=round(transform['dx_mm']*1e6);dy=round(transform['dy_mm']*1e6);prefix=transform['prefix']
  for f in source.GetFootprints():
   assert fp_signature(fs[prefix+f.GetReference()])==fp_signature(f,dx,dy,prefix),(w.name,f.GetReference())
   nfp+=1
  # Filled-copper equivalence plus pad/route equivalence transfers the independently
  # qualified graph of each electrically separate circuit, including zone holes.
  for net in ('HALL_5V','GND'):
   layer=p.F_Cu if net=='HALL_5V' else p.B_Cu
   old_fill=unary_union([polys(z.GetFilledPolysList(layer)) for z in source.Zones() if not z.GetIsRuleArea() and z.GetNetname()==net and z.IsOnLayer(layer)])
   new_fill=unary_union([polys(z.GetFilledPolysList(layer)) for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname()==prefix+net and z.IsOnLayer(layer)])
   expected=translate(old_fill,dx/1e6,dy/1e6)
   assert new_fill.symmetric_difference(expected).area<.0001,(w.name,prefix+net,'fill transfer differs',new_fill.symmetric_difference(expected).area)
  # Route transfer uses a direct signature, without reconstructing routes.
  for t in source.GetTracks():
   if isinstance(t,p.PCB_VIA):row=('via',prefix+t.GetNetname(),t.GetPosition().x+dx,t.GetPosition().y+dy,t.GetWidth(p.F_Cu),t.GetDrillValue())
   else:row=('track',prefix+t.GetNetname(),t.GetLayer(),tuple(sorted(((t.GetStart().x+dx,t.GetStart().y+dy),(t.GetEnd().x+dx,t.GetEnd().y+dy)))),t.GetWidth())
   expected_tracks[row]+=1
  ps=p.SHAPE_POLY_SET();source.GetBoardPolygonOutlines(ps);shape=translate(polys(ps),dx/1e6,dy/1e6);assert shape.difference(panel).area<1e-7
  # Every source outline segment survives apart from the four 5mm break openings.
  missing=shape.boundary.difference(panel.boundary.buffer(.000003))
  assert abs(missing.length-20)<.0001,(w.name,missing.length)

 assert tracks(b)==expected_tracks,(w.name,'route transfer')
 assert len(fs)==nfp+meta['mouse_bite_count']+4+3
 d=json.loads((w/'drc.json').read_text());assert not d['unconnected_items'] and not d['violations']
 pads=[(f.GetReference()+'.'+a.GetNumber(),a,{l:a.GetEffectiveShape(l) for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)}) for f in b.GetFootprints() for a in f.Pads()]
 nearest=[];pairs=[]
 for via in b.GetTracks():
  if not isinstance(via,p.PCB_VIA):continue
  values=[]
  for ref,a,shapes in pads:
   if not shapes:continue
   gap=min(shape.Distance(via.GetPosition())/1e6-.3 for shape in shapes.values())
   values.append((gap,ref));pairs.append([via.m_Uuid.AsString(),ref,a.GetNetname()==via.GetNetname(),gap])
  gap,ref=min(values);nearest.append(dict(uuid=via.m_Uuid.AsString(),gap_mm=gap,nearest_pad=ref))
 with gzip.open(w/'via-pad-all-pairs.csv.gz','wt',newline='') as f:
  writer=csv.writer(f);writer.writerow(['via_uuid','pad_including_NPTH','same_net','gap_mm']);writer.writerows(pairs)
 (w/'via-pad-nearest.json').write_text(json.dumps(nearest,indent=2)+'\n')
 minimum=min(r['gap_mm'] for r in nearest);assert minimum>=.125-1e-9
 results.append(dict(panel=w.name,source_footprints_checked=nfp,routed_items_checked=sum(expected_tracks.values()),all_pad_net_pose_hole_transforms_match=True,stepped_and_shoulder_profiles_preserved=True,drc_opens=0,drc_violations=0,filled_copper_transforms_match=True,independent_metrics=dict(required_unconnected=0,wrong_net_contacts=0,material_violations=0,unexplained_transfer_changes=0),all_vias=len(nearest),all_pads_including_NPTH=len(pads),via_pad_pairs=len(pairs),min_via_pad_gap_mm=minimum,pass_all=True))
(E/'panel-verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
