"""Independent physical copper graph: #87 predicates extended to four layers and actual filled zones."""
from common import *
import pcbnew as p,collections,importlib.util,inspect
from shapely.geometry import Polygon,LineString
from shapely import make_valid
label=sys.argv[1];w=E/'inspection'/label;b=p.LoadBoard(str(w/'main.kicad_pcb'))
spec=importlib.util.spec_from_file_location('oracle87',R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
code=inspect.getsource(m.connectivity);code=code.replace('    parent=list(range(len(copper)))',"    bounds=[a['geometry'].bounds for a in copper]\n    parent=list(range(len(copper)))")
needle="            z=copper[j]\n";assert code.count(needle)==1
code=code.replace(needle,needle+"            aa,bb=bounds[i],bounds[j]\n            if aa[0]-bb[2]>.000002 or bb[0]-aa[2]>.000002 or aa[1]-bb[3]>.000002 or bb[1]-aa[3]>.000002:continue\n")
exec(compile(code,'<conservative-bounds-connectivity>','exec'),m.__dict__)
snap=json.loads((w/'snapshot.json').read_text());layers=list(b.GetEnabledLayers().CuStack());padmap={a.m_Uuid.AsString():a for f in b.GetFootprints() for a in f.Pads()};viamap={a.m_Uuid.AsString():a for a in b.GetTracks() if isinstance(a,p.PCB_VIA)}
copper=[]
for a in snap['pads']:
 if a['attribute']=='NPTH':continue
 native=padmap[a['uuid']];ls=[x for x in layers if native.IsOnLayer(x)]
 copper.append(dict(id=a['ref']+'.'+a['number']+'@'+a['uuid'],net=a['net'],layers=ls,geometry=m.shape(a),pad=True,nc=not a['net']))
for t in snap['tracks']:
 if t['kind']=='track':g=LineString([t['start'],t['end']]).buffer(t['width']/2,quad_segs=512);ls=[t['layer']]
 else:g=m.capsule(t['position'],[t['size']]*2).difference(m.capsule(t['position'],[t['drill']]*2));ls=[x for x in layers if viamap[t['uuid']].IsOnLayer(x)]
 copper.append(dict(id=t['uuid'],net=t['net'],layers=ls,geometry=g,pad=False,nc=False))
def ring(line):return [(p.ToMM(line.CPoint(i).x),p.ToMM(line.CPoint(i).y)) for i in range(line.PointCount())]
zone_rows=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for layer in layers:
  if not z.IsOnLayer(layer):continue
  poly=z.GetFilledPolysList(layer)
  for i in range(poly.OutlineCount()):
   outer=ring(poly.Outline(i));holes=[ring(poly.Hole(i,j)) for j in range(poly.HoleCount(i))]
   g=make_valid(Polygon(outer,holes))
   assert not g.is_empty and g.is_valid
   copper.append(dict(id=f'zone:{z.m_Uuid.AsString()}:{layer}:{i}',net=z.GetNetname(),layers=[layer],geometry=g,pad=False,nc=False));zone_rows.append(dict(layer=b.GetLayerName(layer),net=z.GetNetname(),outline=i,holes=len(holes),area_mm2=g.area))
shorts,groups,disconnected,find=m.connectivity(copper);required=collections.defaultdict(list)
for i,a in enumerate(copper):
 if a['pad'] and not a['nc']:required[a['net']].append((find(i),a['id']))
rows=[dict(net=n,required_pad_count=len(ps),component_count=len(set(k for k,_ in ps)),components=[dict(root=k,pads=[name for root,name in ps if root==k]) for k in sorted(set(k for k,_ in ps))]) for n,ps in sorted(required.items())]
assert len(rows)==44
save(w/'graph-method.json',dict(oracle_sha256=digest(R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py'),executed_connectivity_source=code,reference_predicates_unchanged=True,extension='Four-layer native memberships for PTH/vias; filled zone outer rings and holes converted to valid actual copper polygons. No net-name union. 512 segments per quadrant in round copper.'))
save(w/'connectivity.json',dict(utc=now(),method='Independent actual copper geometry union-find; #87 physical predicates with conservative 2nm bounds prefilter; 4-layer barrel memberships and actual GND fill included',nets_checked=len(rows),required_unconnected=sum(v-1 for v in disconnected.values()),wrong_net_contacts=len(shorts),wrong_contacts=shorts,disconnected=disconnected,nets=rows,filled_zones=zone_rows,copper_objects=len(copper)))
print('All-net connectivity',len(rows),disconnected,len(shorts))
