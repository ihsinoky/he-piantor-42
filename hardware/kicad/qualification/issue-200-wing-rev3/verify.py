"""Independent saved-board qualification using native pad shapes and copper graph.
Every pad/via pair, both layers, includes same-net pairs. No saved PCB mutation.
"""
from pathlib import Path
import collections,csv,gzip,hashlib,json,math,sys
import pcbnew as p
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import unary_union
from shapely import make_valid
from shapely.strtree import STRtree
E=Path(__file__).resolve().parent;R=E.parents[3];MM=1e6

def save(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def xy(v):return [v.x/MM,v.y/MM]
def polys(ps):
 def ring(line):return [xy(line.CPoint(i)) for i in range(line.PointCount())]
 # KiCad weak polygons may touch themselves at a vertex. Split them at exact
 # intersections; discard zero-area line remnants, without a buffer tolerance.
 def area_parts(g):
  if g.geom_type=='Polygon':return [g]
  return [p for child in getattr(g,'geoms',[]) for p in area_parts(child)]
 return unary_union([part for i in range(ps.OutlineCount()) for part in area_parts(make_valid(Polygon(ring(ps.Outline(i)),[ring(ps.Hole(i,j)) for j in range(ps.HoleCount(i))])))])

def padgeom(a,l):
 ps=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(ps,l,0,10,p.ERROR_OUTSIDE);return polys(ps)
def shape_signature(b):
 return {f.GetReference():dict(value=f.GetValue(),position=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),side=f.GetLayer(),pads=sorted((a.GetNumber(),a.GetNetname(),xy(a.GetPosition()),xy(a.GetSize()),xy(a.GetDrillSize()),a.GetOrientationDegrees(),list(a.GetLayerSet().Seq())) for a in f.Pads())) for f in b.GetFootprints()}
def qualify(w):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));source=p.LoadBoard(str(w/'input.kicad_pcb'));spec=json.loads((w/'definition.json').read_text())
 assert b.GetCopperLayerCount()==2 and p.ToMM(b.GetDesignSettings().GetBoardThickness())==1.2
 expected=shape_signature(source);actual=shape_signature(b)
 changes=[k for k in set(expected)|set(actual) if expected.get(k)!=actual.get(k)]
 def edges(board):return sorted((xy(d.GetStart()),xy(d.GetEnd()),d.GetWidth()) for d in board.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
 assert edges(b)==edges(source),'outline transfer changed'
 assert json.loads((w/'main.kicad_pro').read_text())==json.loads((w/'input.kicad_pro').read_text()),'effective rules changed'
 rows=json.loads((E.parent/'issue-129-wing-2layer-routing/evidence/library-pads.json').read_text())
 fs={f.GetReference():f for f in b.GetFootprints()}
 pose_checks=[]
 for c in spec['components']:
  f=fs[c['reference']];assert f.GetLayer()==(p.B_Cu if c['side']=='bottom' else p.F_Cu)
  assert dict((a.GetNumber(),a.GetNetname() or None) for a in f.Pads())==c['pins']
  ang=math.radians(c['rotation_ccw_deg']);pads=collections.defaultdict(list)
  for a in f.Pads():pads[a.GetNumber()].append(a)
  for a in rows[c['kind']]:
   dx=a['x_mm'];dy=(-1 if c['side']=='bottom' else 1)*a['y_mm']
   target=[100+c['x_mm']+dx*math.cos(ang)-dy*math.sin(ang),100-c['y_mm']-dx*math.sin(ang)-dy*math.cos(ang)]
   assert any(math.dist(target,xy(pad.GetPosition()))<.000003 for pad in pads[a['number']]),(c['reference'],a['number'],target)
  pose_checks.append(dict(ref=c['reference'],side=c['side'],angle=c['rotation_ccw_deg'],physical_pin_transform=True))
 # Independently recompute locator centers from K and key angle, not source hole arrays.
 for i,k in enumerate(spec['keys'],1):
  a=math.radians(k['rotation_ccw_deg'])
  assert math.dist(xy(fs[k['sensor']].GetPosition()),[100+k['x_mm'],100-k['y_mm']])<.000002
  for j,dx in enumerate((-5.08,5.08),1):
   hole=next(iter(fs[f'MH_{i}_{j}'].Pads()));assert xy(hole.GetDrillSize())==[1.7,1.7]
   assert math.dist(xy(hole.GetPosition()),[100+k['x_mm']+dx*math.cos(a),100-k['y_mm']-dx*math.sin(a)])<.000003
 copper=[];padshapes=[];vias=[];widths=collections.defaultdict(list)
 def add(g,layers,net,identity,pad=False):
  assert g.is_valid and not g.is_empty,identity
  copper.append(dict(geom=g,layers=set(layers),net=net,id=identity,pad=pad))
 for f in b.GetFootprints():
  for a in f.Pads():
   layers=[l for l in (p.F_Cu,p.B_Cu) if a.IsOnLayer(l)]
   shapes={l:a.GetEffectiveShape(l) for l in layers};padshapes.append((f.GetReference()+'.'+a.GetNumber(),a,shapes))
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   for l in layers:add(padgeom(a,l),[l],a.GetNetname(),f.GetReference()+'.'+a.GetNumber(),True)
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   assert p.ToMM(t.GetWidth(p.F_Cu))==.6 and p.ToMM(t.GetDrillValue())==.3
   vias.append(t);g=Point(xy(t.GetPosition())).buffer(.3,quad_segs=128).difference(Point(xy(t.GetPosition())).buffer(.15,quad_segs=128));layers=[p.F_Cu,p.B_Cu]
  else:
   width=p.ToMM(t.GetWidth());widths[t.GetNetname()].append(width)
   g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(width/2,quad_segs=128);layers=[t.GetLayer()]
  add(g,layers,t.GetNetname(),t.m_Uuid.AsString())
 zones=[]
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in (p.F_Cu,p.B_Cu):
   if not z.IsOnLayer(l):continue
   g=polys(z.GetFilledPolysList(l));zones.append(dict(net=z.GetNetname(),layer=b.GetLayerName(l),area_mm2=g.area))
   for i,part in enumerate(g.geoms if hasattr(g,'geoms') else [g]):add(part,[l],z.GetNetname(),z.m_Uuid.AsString()+f'.{i}')
 for h in spec['mounting_holes']:
  center=Point(100+h['x_mm'],100-h['y_mm'])
  assert all(a['geom'].distance(center)>=2.5-.00002 for a in copper),'mounting copper keepout'
 geoms=[x['geom'] for x in copper];tree=STRtree(geoms);parent=list(range(len(copper)))
 def find(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 shorts=[]
 for i,a in enumerate(copper):
  for j0 in tree.query(a['geom'],predicate='intersects'):
   j=int(j0)
   if j>=i:continue
   other=copper[j]
   if not a['layers']&other['layers']:continue
   if a['net']!=other['net'] or not a['net']:shorts.append([a['id'],other['id'],a['net'],other['net']])
   parent[find(i)]=find(j)
 required=collections.defaultdict(set)
 for i,a in enumerate(copper):
  if a['pad'] and a['net']:required[a['net']].add(find(i))
 disconnected={n:len(v) for n,v in required.items() if len(v)>1}
 distances=[];allpairs=[]
 for v in vias:
  nearest=[]
  for identity,a,shapes in padshapes:
   common=[l for l in shapes if v.IsOnLayer(l)]
   if not common:continue
   gap=min(shapes[l].Distance(v.GetPosition())/MM for l in common)-p.ToMM(v.GetWidth(p.F_Cu))/2
   nearest.append((gap,identity));allpairs.append([v.m_Uuid.AsString(),identity,a.GetNetname()==v.GetNetname(),round(gap,9)])
  gap,identity=min(nearest);distances.append(dict(uuid=v.m_Uuid.AsString(),position_mm=xy(v.GetPosition()),net=v.GetNetname(),gap_mm=round(gap,9),nearest_pad=identity))
 with gzip.open(w/'via-pad-all-pairs.csv.gz','wt',newline='') as f:
  writer=csv.writer(f);writer.writerow(['via_uuid','pad','same_net','gap_mm']);writer.writerows(allpairs)
 save(w/'via-pad-nearest.json',distances)
 gaps=sorted(x['gap_mm'] for x in distances)
 hist={f'{lo:.2f}..{hi:.2f}':sum(lo<=x<hi for x in gaps) for lo,hi in [(0,.1),(.1,.11),(.11,.15),(.15,.2),(.2,.3),(.3,.5),(.5,1),(1,1000)]}
 drc=json.loads((w/'drc.json').read_text());material=[x for x in drc['violations'] if x['type'] not in {'silk_overlap','silk_over_copper','text_height','lib_footprint_mismatch'}]
 metrics=dict(required_unconnected=sum(x-1 for x in disconnected.values()),wrong_net_contacts=len(shorts),material_violations=len(material),unexplained_transfer_changes=len(changes))
 out=dict(board=w.name,kicad=p.Version(),sha256=hashlib.sha256((w/'main.kicad_pcb').read_bytes()).hexdigest(),metrics=metrics,drc_unconnected=len(drc['unconnected_items']),drc_types=dict(collections.Counter(x['type'] for x in drc['violations'])),transfer_changed_refs=changes,physical_disconnected=disconnected,shorts=shorts,all_vias=len(vias),all_pads_including_npth=len(padshapes),via_pad_pairs=len(allpairs),min_via_pad_gap_mm=min(gaps),via_pad_below_0p10=sum(x<.1-1e-9 for x in gaps),via_pad_gap_histogram=hist,via_pad_gap_quantiles={str(q):gaps[round(q*(len(gaps)-1))] for q in (0,.1,.25,.5,.75,.9,1)},width_histogram={n:dict(collections.Counter(v)) for n,v in widths.items()},zones=zones,poses=pose_checks)
 out['width_below_floor']=sum(sum(v<(.3 if n in ('HALL_5V','GND') else .1)-1e-9 for v in values) for n,values in widths.items())
 out['pass']=not drc['violations'] and not out['width_below_floor'] and all(x==0 for x in metrics.values()) and not out['drc_unconnected'] and not out['via_pad_below_0p10']
 save(w/'qualification.json',out);print(w.name,metrics,'drc opens',out['drc_unconnected'],'via min',min(gaps),flush=True)
 return out
if __name__=='__main__':
 results=[qualify(w) for w in sorted(E.glob('wing-rev3-*')) if len(sys.argv)==1 or w.name in sys.argv[1:]]
 save(E/'qualification-summary.json',results)
 assert all(x['pass'] for x in results)
