"""Saved-native geometry, unchanged Rev.2 keys, all pads and probe access audit."""
from pathlib import Path
import json,csv,math,hashlib,sys
import pcbnew as p
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
from shapely.affinity import affine_transform
from verify import polys,padgeom,xy,shape_signature
E=Path(__file__).resolve().parent;R=E.parents[3]
geometry=json.loads((R/'hardware/case/issue-200-stage1/geometry.json').read_text());results=[]
for g in geometry['variants']:
 if len(sys.argv)>1 and 'wing-rev3-'+g['variant'] not in sys.argv[1:]:continue
 w=E/('wing-rev3-'+g['variant']);spec=json.loads((w/'definition.json').read_text());b=p.LoadBoard(str(w/'main.kicad_pcb'));old=p.LoadBoard(str(E.parent/'issue-194-wing-rev2'/w.name.replace('rev3','rev2')/'main.kicad_pcb'))
 assert spec['keys']==json.loads((E.parent/'issue-194-wing-rev2'/w.name.replace('rev3','rev2')/'definition.json').read_text())['keys']
 sig=shape_signature(b);previous=shape_signature(old)
 for ref in previous:
  if ref.startswith(('U_H','C_H','MH_')):assert sig[ref]==previous[ref],(w.name,ref)
 ps=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(ps);board=polys(ps);expected=Polygon([(100+x,100-y) for x,y in g['outline_local']]);assert board.symmetric_difference(expected).area<.0001
 fs={f.GetReference():f for f in b.GetFootprints()};keyshapes=[];mounts=[]
 for k in spec['keys']:
  a=math.radians(k['rotation_ccw_deg']);cx,cy=k['x_mm'],k['y_mm']
  key=Polygon([(100+cx+dx*math.cos(a)-dy*math.sin(a),100-cy-dx*math.sin(a)-dy*math.cos(a)) for dx,dy in [(-7.9,-7.9),(7.9,-7.9),(7.9,7.9),(-7.9,7.9)]])
  assert key.difference(board).area<1e-8;keyshapes.append(key)
 for i,h in enumerate(spec['mounting_holes'],1):
  q=Point(xy(fs[f'H{i}'].GetPosition()));assert math.dist(q.coords[0],[100+h['x_mm'],100-h['y_mm']])<.000002
  gap=min(q.distance(k)-2.5 for k in keyshapes);edge=q.distance(board.boundary);assert gap>=.24999 and edge>=2.99999
  mounts.append(dict(ref=f'H{i}',local=[h['x_mm'],h['y_mm']],edge_mm=edge,key_gap_mm=gap))
 m=g['transform']['matrix'];t=g['transform']['translation']
 def to_native(coords):
  return Polygon([(100+m[0][0]*(x-t[0])+m[1][0]*(y-t[1]),100-m[0][1]*(x-t[0])-m[1][1]*(y-t[1])) for x,y in coords])
 ghbody=to_native(g['connector']['body_assembly']) if 'body_assembly' in g['connector'] else None
 bodies=[]
 for c in spec['components']:
  if c['kind'] in ('hall','testpoint'):continue
  if c['reference']=='J_WING':
   # Stage1 assembly GH body is independent of the pad-centre footprint anchor.
   cx=-27 if g['side']=='left' else 27;body=to_native(list(box(cx-11,-42,cx+11,-35).exterior.coords))
  else:
   hx,hy=(2.55,3.3) if c['kind']=='mux' else (.9,.5)
   # Capacitor actual pads extend farther than body; include both in the obstacle.
   a=math.radians(c['rotation_ccw_deg']);cx=100+c['x_mm'];cy=100-c['y_mm']
   body=Polygon([(cx+x*math.cos(a)-y*math.sin(a),cy-x*math.sin(a)-y*math.cos(a)) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]])
  pads=unary_union([padgeom(a,p.F_Cu) for a in fs[c['reference']].Pads() if a.IsOnLayer(p.F_Cu)])
  body=body.union(pads);assert body.difference(board).area<1e-7,(w.name,c['reference'],'off board');bodies.append((c['reference'],body))
 tp=[]
 for c in spec['components']:
  if c['kind']!='testpoint':continue
  q=Point(xy(fs[c['reference']].GetPosition()));probe=q.buffer(.6,quad_segs=128)
  gap=min(probe.distance(k) for k in keyshapes);bodygap=min(probe.distance(b) for _,b in bodies)
  othergap=min(q.distance(Point(xy(fs[o['reference']].GetPosition())))-1.2 for o in spec['components'] if o['kind']=='testpoint' and o['reference']!=c['reference'])
  assert probe.difference(board).area<1e-8 and gap>0 and bodygap>0 and othergap>0
  tp.append(dict(ref=c['reference'],probe_diameter_mm=1.2,key_gap_mm=gap,body_or_land_gap_mm=bodygap,other_probe_gap_mm=othergap))
 south=unary_union([LineString([(100+x,100-y) for x,y in ab]) for ab in g['south_trim_line_local']]);band=south.buffer(2,join_style=2).intersection(board)
 forbidden=[];power_area={}
 for item in b.GetTracks():
  disk=Point(xy(item.GetPosition())).buffer(.3) if isinstance(item,p.PCB_VIA) else LineString([xy(item.GetStart()),xy(item.GetEnd())]).buffer(p.ToMM(item.GetWidth())/2)
  if disk.intersection(band).area>1e-9 and (isinstance(item,p.PCB_VIA) or item.GetNetname() not in ('GND','HALL_5V')):forbidden.append(item.m_Uuid.AsString())
 # Routing exclusion includes 2mm of interior material, not only a narrow edge strip.
 for z in b.Zones():
  if not z.GetIsRuleArea():
   for l in (p.F_Cu,p.B_Cu):
    if z.IsOnLayer(l):power_area[z.GetNetname()+'@'+b.GetLayerName(l)]=polys(z.GetFilledPolysList(l)).intersection(band).area
 assert not forbidden,(w.name,'south signal/via intrusion',forbidden)
 results.append(dict(board=w.name,sha256=hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest(),stage1b_outline_matches=True,rev2_keys_sensors_local_caps_locators_unchanged=True,mounting=mounts,testpoints=tp,south_band_mm=2,south_band_area_mm2=band.area,south_signal_or_via_intrusions=forbidden,south_power_fill_area_mm2=power_area))
(E/'mechanical-verification.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps([{k:v for k,v in r.items() if k not in ('testpoints','mounting')} for r in results],indent=2))
