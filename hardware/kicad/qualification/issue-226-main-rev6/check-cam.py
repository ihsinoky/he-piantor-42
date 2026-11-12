"""Independent Gerbonara CAM readback: four copper layers, actual plane, mask,
outline, drill, CPL, and every native polygon stencil opening."""
from common import *
sys.path.insert(0,str(BASE/'.issue147-runtime/viewer-venv/lib/python3.12/site-packages'))
import warnings,csv,math,collections,zipfile,importlib.util
import pcbnew as p
from gerbonara import GerberFile,ExcellonFile
from gerbonara.graphic_objects import Line,Flash,Region,Arc
from gerbonara.graphic_primitives import Rectangle
from shapely.geometry import Polygon,Point
from shapely import make_valid
from shapely.ops import unary_union
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));s=json.loads((E/'inspection/final/snapshot.json').read_text());dest=E/'manufacturing';fab=dest/'gerber';native=json.loads((E/'cam-native-zones.json').read_text())
pt=lambda q:tuple(round(float(v),6) for v in q)
xy=lambda q:pt([q[0],-q[1]])
def seg(aa,bb,width):return (*sorted([pt(aa),pt(bb)]),round(width,6))
def bounds(o):
 # Gerbonara 1.5 Rectangle.bounding_box uses signed trig terms at 120deg.
 # Derive an independent conservative AABB from its decoded primitive.
 if isinstance(o,Flash):
  prim=list(o.to_primitives())
  if len(prim)==1 and isinstance(prim[0],Rectangle):
   q=prim[0];dx=(abs(q.w*math.cos(q.rotation))+abs(q.h*math.sin(q.rotation)))/2;dy=(abs(q.w*math.sin(q.rotation))+abs(q.h*math.cos(q.rotation)))/2
   return pt((q.x-dx,q.y-dy,q.x+dx,q.y+dy))
 return tuple(round(v,6) for pair in o.bounding_box() for v in pair)
with warnings.catch_warnings():
 warnings.simplefilter('ignore');files={f.suffix:GerberFile.open(f) for f in fab.iterdir() if f.suffix not in ['.drl','.gbrjob']};pth=ExcellonFile.open(fab/'main-rev6-PTH.drl',plated=True);npth=ExcellonFile.open(fab/'main-rev6-NPTH.drl',plated=False)
vias=[t for t in s['tracks'] if t['kind']=='via'];rows=[];padmap={pad.m_Uuid.AsString():pad for f in b.GetFootprints() for pad in f.Pads()}
for ext,layer in [('.gtl',0),('.g1',4),('.g2',6),('.gbl',2)]:
 objects=files[ext].objects;lines=[o for o in objects if isinstance(o,Line)];flashes=[o for o in objects if isinstance(o,Flash)];regions=[o for o in objects if isinstance(o,Region)]
 assert collections.Counter(seg((o.x1,o.y1),(o.x2,o.y2),o.aperture.diameter) for o in lines)==collections.Counter(seg(xy(t['start']),xy(t['end']),t['width']) for t in s['tracks'] if t.get('layer')==layer)
 vf=[o for o in flashes if dict(o.aperture.attrs).get('.AperFunction')==('ViaPad',)];assert collections.Counter((pt((o.x,o.y)),round(o.aperture.diameter,6)) for o in vf)==collections.Counter((xy(t['position']),t['size']) for t in vias)
 pending=[o for o in flashes if o not in vf];expected=[pad for pad in s['pads'] if pad['attribute']=='PTH' or (pad['attribute']=='SMD' and layer==0)]
 for pad in expected:
  matches=[o for o in pending if pt((o.x,o.y))==xy(pad['position']) and (o.attrs.get('.P')==(pad['ref'],pad['number']) or o.attrs.get('.C')==(pad['ref'],))];assert len(matches)==1,(ext,pad['ref'],pad['number']);o=matches[0];pending.remove(o)
  g=a.pad_polygon(padmap[pad['uuid']],p.F_Cu);bb=g.bounds;expectedbounds=(bb[0],-bb[3],bb[2],-bb[1]);assert max(abs(x-y) for x,y in zip(bounds(o),expectedbounds))<.00003,(pad['ref'],pad['number'],bounds(o),expectedbounds)
 assert not pending and len(objects)==len(lines)+len(flashes)+len(regions)
 assert not regions or ext=='.g1'
 rows.append(dict(layer=ext,tracks=len(lines),vias=len(vf),pads=len(expected),regions=len(regions)))
plane=unary_union([make_valid(Polygon(o.outline)) for o in files['.g1'].objects if isinstance(o,Region)]);expected=unary_union([Polygon(r['outer'],r['holes']) for r in native['zones']]);area=plane.symmetric_difference(expected).area;assert area<1e-8
plan=json.loads((E.parent/'issue-196-main-rev4-phasea2/geometry-plan.json').read_text())
for h in plan['main']['holes']:
 x,y=h['xy_mm'];assert plane.intersection(Point(x+100,-y-70).buffer(2.5,quad_segs=1024)).area<1e-9
assert collections.Counter(seg((o.x1,o.y1),(o.x2,o.y2),o.aperture.diameter) for o in files['.gm1'].objects)==collections.Counter(seg(xy(e['start']),xy(e['end']),e['width']) for e in s['edges'])
assert len(pth.objects)==len(vias) and len(npth.objects)==3
pending=[(xy(t['position']),t['drill']) for t in vias];errors=[]
for o in pth.objects:
 matches=[(i,q) for i,q in enumerate(pending) if abs(o.aperture.diameter-q[1])<1e-8 and max(abs(o.x-q[0][0]),abs(o.y-q[0][1]))<=.0005001];assert len(matches)==1;i,q=matches[0];pending.pop(i);errors.append(math.dist((o.x,o.y),q[0]))
assert not pending
pending=[(xy(pad['position']),pad['drill'][0]) for pad in s['pads'] if pad['attribute']=='NPTH']
for o in npth.objects:
 matches=[(i,q) for i,q in enumerate(pending) if abs(o.aperture.diameter-q[1])<1e-8 and max(abs(o.x-q[0][0]),abs(o.y-q[0][1]))<=.0005001];assert len(matches)==1;i,q=matches[0];pending.pop(i);errors.append(math.dist((o.x,o.y),q[0]))
assert not pending
for mask,cu in [('.gts','.gtl'),('.gbs','.gbl')]:
 expected=[o for o in files[cu].objects if isinstance(o,Flash) and dict(o.aperture.attrs).get('.AperFunction')!=('ViaPad',)];assert collections.Counter(bounds(o) for o in files[mask].objects)==collections.Counter(bounds(o) for o in expected)
cpl=list(csv.DictReader((dest/'CPL.csv').open()));bom=list(csv.DictReader((dest/'BOM.csv').open()));assert len(cpl)==len(bom)==55;lookup={q['ref']:q for q in s['components']};assert {r['Designator'] for r in cpl}=={r['Designator'] for r in bom}
for row in cpl:
 c=lookup[row['Designator']];assert pt((float(row['Mid X'][:-2]),float(row['Mid Y'][:-2])))==pt((c['position'][0]-62.107317799,137.9-c['position'][1])) and float(row['Rotation'])==c['angle']
paste=[]
for ext,layer in [('.gtp','F.Paste'),('.gbp','B.Paste')]:
 f=next((dest/'paste').glob('*'+ext));data=GerberFile.open(f);regions=[o for o in data.objects if isinstance(o,Region)];flashes=[o for o in data.objects if isinstance(o,Flash)];arcs=[o for o in data.objects if isinstance(o,Arc)];source=[r for r in native['paste'] if r['layer']==layer];polys=[Polygon(r['points']) for r in source if r['kind']=='poly'];assert len(polys)==len(regions)
 union=unary_union([make_valid(Polygon(o.outline)) for o in regions]);diff=union.symmetric_difference(unary_union(polys)).area;assert diff<1e-8
 expectedpads=[r for r in native['paste_pads'] if r['layer']==layer];assert len(flashes)==len(expectedpads)
 for row in expectedpads:assert sum(pt((o.x,o.y))==pt(row['position_mm']) and o.attrs.get('.C')==(row['ref'],) for o in flashes)==1
 circles=[r for r in source if r['kind']=='circle'];assert len(arcs)==2*len(circles)
 assert len(data.objects)==len(regions)+len(flashes)+len(arcs)
 paste.append(dict(layer=layer,polygons=len(polys),polygon_difference_mm2=diff,native_pad_flashes=len(flashes),circles=len(circles)))
members=sorted(f for f in fab.iterdir() if f.suffix!='.gbrjob');archive=dest/'main-rev6-fabrication-review.zip';assert len(members)==11
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in members:z.write(f,f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and all(z.read(f.name)==f.read_bytes() for f in members)
save(E/'cam-check.json',dict(pass_check=True,board_sha256=digest(E/'inspection/final/main.kicad_pcb'),copper_layers=rows,plane_symmetric_difference_mm2=area,holes=3,via_drills=len(vias),drill_max_displacement_mm=max(errors),paste=paste,BOM_CPL_parts=55,CPL_origin_xy_mm=[62.107317799,137.9],archive_sha256=digest(archive),archive_members=[dict(name=f.name,sha256=digest(f)) for f in members],manufacturer_release=False))
print('CAM PASS: exact copper, plane, outline, drills, masks, stencil polygons, BOM/CPL')
