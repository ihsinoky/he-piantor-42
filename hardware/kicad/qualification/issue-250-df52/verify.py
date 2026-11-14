"""Independent actual copper graph, all-pairs via-pad audit, and baseline invariants.
Uses the Rev4 native polygon and physical union approach on 2 or 4 copper layers.
Does not replace native DRC/ERC. Failed gates remain failed.
"""
from pathlib import Path
import sys,json,hashlib,collections,csv,gzip,math
import pcbnew as p
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
from shapely import make_valid
from shapely.strtree import STRtree
E=Path(__file__).resolve().parent;R=E.parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def polys(ps):
 def ring(l):return [xy(l.CPoint(i)) for i in range(l.PointCount())]
 return unary_union([make_valid(Polygon(ring(ps.Outline(i)),[ring(ps.Hole(i,j)) for j in range(ps.HoleCount(i))])) for i in range(ps.OutlineCount())])
def padgeom(a,l):
 ps=p.SHAPE_POLY_SET();a.TransformShapeToPolygon(ps,l,0,10,p.ERROR_OUTSIDE);return polys(ps)
def signature(f):return dict(value=f.GetValue(),position=xy(f.GetPosition()),angle=f.GetOrientationDegrees(),layer=f.GetLayer(),pads=sorted((a.GetNumber(),a.GetNetname(),xy(a.GetPosition()),xy(a.GetSize()),xy(a.GetDrillSize()),a.GetOrientationDegrees(),list(a.GetLayerSet().Seq())) for a in f.Pads()))
def outline(b):return sorted((d.GetShapeStr(),xy(d.GetStart()),xy(d.GetEnd()),d.GetWidth()) for d in b.GetDrawings() if d.GetLayer()==p.Edge_Cuts)
def qualify(w):
 b=p.LoadBoard(str(w/'main.kicad_pcb'));construction=json.loads((w/'construction.json').read_text());src=R/construction['source'];base=p.LoadBoard(str(src));layers=list(b.GetEnabledLayers().CuStack())
 fs={f.GetReference():f for f in b.GetFootprints()};old={f.GetReference():f for f in base.GetFootprints()};conns={'J2','J3'} if w.name=='main' else {'J_WING'}
 invariant_errors=[]
 for ref in sorted(set(fs)|set(old)):
  if ref not in fs or ref not in old:invariant_errors.append(ref+' added/removed');continue
  if ref not in conns:
   if signature(fs[ref])!=signature(old[ref]):invariant_errors.append(ref+' altered')
  else:
   f=fs[ref];o=old[ref]
   if xy(f.GetPosition())!=xy(o.GetPosition()) or f.GetOrientationDegrees()!=o.GetOrientationDegrees() or f.GetLayer()!=o.GetLayer():invariant_errors.append(ref+' pose altered')
   expected={a.GetNumber():a.GetNetname() for a in o.Pads() if a.GetNumber() not in ('15','MP')};actual={a.GetNumber():a.GetNetname() for a in f.Pads() if a.GetNumber()!='MP'}
   if expected!=actual:invariant_errors.append(ref+' D024 cavity net changed')
   if any(a.GetNetname() for a in f.Pads() if a.GetNumber()=='MP'):invariant_errors.append(ref+' MP has net')
 if outline(b)!=outline(base):invariant_errors.append('outline changed')
 if b.GetCopperLayerCount()!=base.GetCopperLayerCount() or b.GetDesignSettings().GetBoardThickness()!=base.GetDesignSettings().GetBoardThickness():invariant_errors.append('stack/thickness changed')
 if w.name!='main' and any(f.GetLayer()!=p.B_Cu for f in fs.values() if any(a.GetAttribute()!=p.PAD_ATTRIB_NPTH for a in f.Pads())):invariant_errors.append('all B.Cu invariant changed')
 copper=[];padshapes=[];vias=[];widths=collections.defaultdict(list)
 def add(g,ls,n,ident,pad=False):
  if g.is_empty:return
  copper.append(dict(g=g,ls=set(ls),net=n,id=ident,pad=pad))
 for ref,f in fs.items():
  for a in f.Pads():
   ls=[l for l in layers if a.IsOnLayer(l)];padshapes.append((ref+'.'+a.GetNumber(),a,{l:a.GetEffectiveShape(l) for l in ls}))
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   for l in ls:add(padgeom(a,l),[l],a.GetNetname(),ref+'.'+a.GetNumber(),True)
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   vias.append(t);ls=[l for l in layers if t.IsOnLayer(l)];pos=Point(xy(t.GetPosition()));g=pos.buffer(p.ToMM(t.GetWidth(p.F_Cu))/2,quad_segs=128).difference(pos.buffer(p.ToMM(t.GetDrillValue())/2,quad_segs=128))
  else:
   width=p.ToMM(t.GetWidth());widths[t.GetNetname()].append(width);ls=[t.GetLayer()];g=LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(width/2,quad_segs=128)
  add(g,ls,t.GetNetname(),t.m_Uuid.AsString())
 for z in b.Zones():
  if z.GetIsRuleArea():continue
  for l in layers:
   if not z.IsOnLayer(l):continue
   g=polys(z.GetFilledPolysList(l))
   for i,part in enumerate(g.geoms if hasattr(g,'geoms') else [g]):add(part,[l],z.GetNetname(),'zone:'+z.m_Uuid.AsString()+f':{l}:{i}')
 tree=STRtree([a['g'] for a in copper]);parent=list(range(len(copper)))
 def find(i):
  while i!=parent[i]:parent[i]=parent[parent[i]];i=parent[i]
  return i
 shorts=[]
 for i,a in enumerate(copper):
  for j in tree.query(a['g'],predicate='intersects'):
   j=int(j)
   if j>=i:continue
   q=copper[j]
   if not a['ls']&q['ls']:continue
   if a['net']!=q['net'] or not a['net']:
    # Distinct NC mechanical nails need no electrical common; same-object layers
    # are not intersected unless physically overlapping on the same copper layer.
    shorts.append([a['id'],q['id'],a['net'],q['net']])
   parent[find(i)]=find(j)
 required=collections.defaultdict(lambda:collections.defaultdict(list))
 for i,a in enumerate(copper):
  if a['pad'] and a['net']:required[a['net']][find(i)].append(a['id'])
 # PTH pads/vias explicitly join their copper layers through their barrel.
 # Vias were one all-layer object; PTH pads above are separate layer objects.
 for ref,f in fs.items():
  for a in f.Pads():
   if not a.GetDrillSize().x or a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   ids=[i for i,x in enumerate(copper) if x['pad'] and x['id']==ref+'.'+a.GetNumber()]
   for i in ids[1:]:parent[find(i)]=find(ids[0])
 required=collections.defaultdict(lambda:collections.defaultdict(list))
 for i,a in enumerate(copper):
  if a['pad'] and a['net']:required[a['net']][find(i)].append(a['id'])
 disconnected={n:list(v.values()) for n,v in required.items() if len(v)>1}
 gaps=[];pairs=[]
 for v in vias:
  for ident,a,shapes in padshapes:
   common=[l for l in shapes if v.IsOnLayer(l)]
   if not common:continue
   gap=min(shapes[l].Distance(v.GetPosition())/1e6 for l in common)-p.ToMM(v.GetWidth(p.F_Cu))/2
   pairs.append([v.m_Uuid.AsString(),ident,a.GetNetname()==v.GetNetname(),round(gap,9)])
  gaps.extend([x[3] for x in pairs[-len(padshapes):]])
 with gzip.open(w/'via-pad-all-pairs.csv.gz','wt',newline='') as out:
  cw=csv.writer(out);cw.writerow(['via_uuid','pad','same_net','gap_mm']);cw.writerows(pairs)
 floorbad=[x for x in pairs if x[3]<.1-2e-6];targetbad=[x for x in pairs if x[3]<.125-2e-6]
 drc=json.loads((w/'drc.json').read_text());ercpath=w/'erc.json';erc=json.loads(ercpath.read_text()) if ercpath.exists() else None
 if erc is not None:erc['violations']=[v for sheet in erc.get('sheets',[]) for v in sheet['violations']]
 out=dict(name=w.name,board_sha256=sha(w/'main.kicad_pcb'),source_sha256=sha(src),invariant_errors=invariant_errors,cavity_contract_errors=[x for x in invariant_errors if 'D024' in x or 'MP' in x],native_drc_violations=len(drc['violations']),native_unconnected=len(drc['unconnected_items']),schematic_parity=len(drc.get('schematic_parity',[])),native_drc_types=dict(collections.Counter(v['type'] for v in drc['violations'])),erc_violations=len(erc['violations']) if erc else None,erc_status='tested' if erc else 'BLOCKED: no inherited native Wing schematic; logical contract is not ERC',independent_unconnected=sum(len(v)-1 for v in disconnected.values()),wrong_net_contacts=len(shorts),shorts=shorts,disconnected=disconnected,nets_checked=len(required),via_count=len(vias),via_pad_pairs=len(pairs),via_pad_min_mm=min(x[3] for x in pairs),via_pad_below_0p10=floorbad,via_pad_below_0p125=len(targetbad),via_pad_target_class='>=0.125 mm' if not targetbad else '0.100 mm floor only; misses 0.125 target',main_GND_below_0p30_disclosed=sum(v<.3-1e-9 for v in widths.get('GND',[])) if w.name=='main' else None,minimum_power_width_mm=min((v for n,vs in widths.items() if n in ('HALL_5V','GND') for v in vs),default=None),width_below_floor=sum(sum(v<(.3 if n=='HALL_5V' or (n=='GND' and w.name!='main') else .1)-1e-9 for v in vs) for n,vs in widths.items()),all_components_B_Cu=all(f.GetLayer()==p.B_Cu for f in fs.values() if any(a.GetAttribute()!=p.PAD_ATTRIB_NPTH for a in f.Pads())) if w.name!='main' else None)
 out['routing_pass']=not any((invariant_errors,drc['violations'],drc['unconnected_items'],out['independent_unconnected'],shorts,floorbad,out['width_below_floor']))
 out['full_gate_pass']=out['routing_pass'] and erc is not None and not erc['violations'] and not out['schematic_parity']
 out['gate_bundle_scope']='Native DRC/unrouted/parity/ERC plus physical graph/invariants/width/via-pad floor only; resistance, voltage, library release, mechanical and stock gates are separate.'
 (w/'qualification.json').write_text(json.dumps(out,indent=2)+'\n');print(w.name,{k:out[k] for k in ['native_drc_violations','native_unconnected','independent_unconnected','wrong_net_contacts','via_pad_min_mm','routing_pass','erc_violations']},flush=True)
 return out
if __name__=='__main__':
 results=[qualify(E/name) for name in sys.argv[1:]]
 (E/'qualification-summary.json').write_text(json.dumps(results,indent=2)+'\n')
