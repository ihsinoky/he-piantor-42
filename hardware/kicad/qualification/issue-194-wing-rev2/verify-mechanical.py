"""Independent all-key, locator, mounting and cut-copper inspection of saved PCBs."""
from pathlib import Path
import csv,json,math,sys
import pcbnew as p
from shapely.geometry import Polygon,Point,LineString
from verify import xy,polys,padgeom
E=Path(__file__).resolve().parent;R=E.parents[3]
sys.path.insert(0,str(R/'hardware/jitx'))
from wing.rev2 import define_rev2
results=[]
for pitch in (16,17):
 for side in ('left','right'):
  s=define_rev2(pitch,side);w=E/s['name'];b=p.LoadBoard(str(w/'main.kicad_pcb'))
  assert json.loads((w/'definition.json').read_text())==s
  ps=p.SHAPE_POLY_SET();b.GetBoardPolygonOutlines(ps);board=polys(ps)
  expected=Polygon([(100+x,100-y) for x,y in s['outline_mm']]);assert board.symmetric_difference(expected).area<.0001
  fs={f.GetReference():f for f in b.GetFootprints()};rows=[];locators=[];envelopes=[]
  cut=LineString([(100+x,100-y) for x,y in (s['outline_mm'][1:3] if side=='left' else s['outline_mm'][:2])])
  for i,k in enumerate(s['keys'],1):
   a=math.radians(k['rotation_ccw_deg']);cx,cy=k['x_mm'],k['y_mm']
   key=Polygon([(100+cx+dx*math.cos(a)-dy*math.sin(a),100-cy-dx*math.sin(a)-dy*math.cos(a)) for dx,dy in [(-7.9,-7.9),(7.9,-7.9),(7.9,7.9),(-7.9,7.9)]])
   assert key.difference(board).area<1e-8
   envelopes.append(key)
   rows.append(dict(key=k['key'],outside_area_mm2=key.difference(board).area,cut_gap_mm=key.distance(cut),outline_gap_mm=key.distance(board.boundary)))
   for j,dx in enumerate((-5.08,5.08),1):
    h=next(iter(fs[f'MH_{i}_{j}'].Pads()));target=(100+cx+dx*math.cos(a),100-cy-dx*math.sin(a));assert math.dist(xy(h.GetPosition()),target)<.000003
    keep=Point(xy(h.GetPosition())).buffer(1.1);assert keep.difference(board).area<1e-9
    locators.append(keep.distance(cut))
  mount=[]
  for i,h in enumerate(s['mounting_holes'],1):
   f=fs[f'H{i}'];target=(100+h['x_mm'],100-h['y_mm']);assert math.dist(xy(f.GetPosition()),target)<.000003
   assert xy(next(iter(f.Pads())).GetDrillSize())==[2.2,2.2]
   q=Point(xy(f.GetPosition()));gap=min(q.distance(k)-2.5 for k in envelopes);assert gap>=.24999
   assert q.distance(board.boundary)>=2.99999
   mount.append(gap)
  copper=[]
  for t in b.GetTracks():
   copper.append(Point(xy(t.GetPosition())).buffer(.3) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2))
  for f in b.GetFootprints():
   for h in f.Pads():
    if h.GetAttribute()!=p.PAD_ATTRIB_NPTH:
     copper.extend(padgeom(h,l) for l in (p.F_Cu,p.B_Cu) if h.IsOnLayer(l))
  for z in b.Zones():
   if not z.GetIsRuleArea():
    copper.extend(polys(z.GetFilledPolysList(l)) for l in (p.F_Cu,p.B_Cu) if z.IsOnLayer(l))
  copper_gap=min(g.distance(cut) for g in copper);assert copper_gap>=.29998
  with (w/'mechanical-key-audit.csv').open('w',newline='') as f:
   writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
  result=dict(board=w.name,keys_checked=len(rows),locator_keepouts_checked=len(locators),mounting_key_pairs_checked=4*len(rows),south_limit_mm=min(y for x,y in s['outline_mm']),switch_south_limit_mm=min(y for k in s['keys'] for x,y in k['envelope_mm']),south_overhang_mm=0,inner_corner_cut_mm=s['south_cut']['inner_corner_cut_mm'],T2_to_cut_mm=rows[-1]['cut_gap_mm'],all_key_to_cut_min_mm=min(r['cut_gap_mm'] for r in rows),locator_keepout_to_cut_min_mm=min(locators),mounting_keepout_to_key_min_mm=min(mount),copper_to_cut_min_mm=copper_gap,pass_all=True)
  results.append(result);print(result,flush=True)
(E/'mechanical-verification.json').write_text(json.dumps(results,indent=2)+'\n')
