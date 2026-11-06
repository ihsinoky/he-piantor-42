"""Parse CAM with Gerbonara; exact tracks/pads/vias, actual plane polygons and drill matching."""
from common import *
import csv,math,collections,warnings,zipfile,importlib.metadata,re
from gerbonara import GerberFile, ExcellonFile
from gerbonara.graphic_objects import Line,Flash,Region,Arc
from shapely.geometry import Polygon,Point
from shapely import make_valid
from shapely.ops import unary_union
dest=E/'manufacturing-seed-a-review';fab=dest/'gerber';s=json.loads((E/'inspection/final/snapshot.json').read_text())
def pt(a):return tuple(round(v,6) for v in a)
def xy(a):return pt([a[0],-a[1]])
def seg(a,b,w):return (*sorted([pt(a),pt(b)]),round(w,6))
def bounds(o):return tuple(round(v,6) for pair in o.bounding_box() for v in pair)
with warnings.catch_warnings(record=True) as caught:
 warnings.simplefilter('always')
 files={f.suffix:GerberFile.open(f) for f in fab.iterdir() if f.suffix not in ['.drl','.gbrjob']}
 # Gerbonara 1.5 rejects KiCad's valid inline G85 alternate slots. Parse those
 # four commands strictly here, leaving manufacturing bytes untouched; feed
 # only round commands to its Excellon parser. Tool selection is preserved.
 raw=(fab/'main-stage2-PTH.drl').read_text();round_commands=[];slot_commands=[];tools={};tool=None
 for line in raw.splitlines():
  define=re.fullmatch(r'T(\d+)C([\d.]+)',line)
  select=re.fullmatch(r'T(\d+)',line)
  if define:tools[define[1]]=float(define[2])
  if select:tool=select[1]
  if 'G85' in line:
   match=re.fullmatch(r'X(-?[\d.]+)Y(-?[\d.]+)G85X(-?[\d.]+)Y(-?[\d.]+)',line);assert match and tool in tools
   x1,y1,x2,y2=map(float,match.groups());slot_commands.append(seg((x1,y1),(x2,y2),tools[tool]))
  else:round_commands.append(line)
 pth=ExcellonFile.from_string('\n'.join(round_commands)+'\n',plated=True);npth=ExcellonFile.open(fab/'main-stage2-NPTH.drl',plated=False)
 parser_warnings=sorted(set(str(w.message) for w in caught))
vias=[t for t in s['tracks'] if t['kind']=='via'];results=[]
for ext,layer in [('.gtl',0),('.g1',4),('.g2',6),('.gbl',2)]:
 objects=files[ext].objects;lines=[o for o in objects if isinstance(o,Line)]
 assert collections.Counter(seg((o.x1,o.y1),(o.x2,o.y2),o.aperture.diameter) for o in lines)==collections.Counter(seg(xy(t['start']),xy(t['end']),t['width']) for t in s['tracks'] if t.get('layer')==layer)
 flashes=[o for o in objects if isinstance(o,Flash)];vf=[o for o in flashes if dict(o.aperture.attrs).get('.AperFunction')==('ViaPad',)]
 assert collections.Counter((pt((o.x,o.y)),round(o.aperture.diameter,6)) for o in vf)==collections.Counter((xy(t['position']),t['size']) for t in vias)
 pf=[o for o in flashes if o not in vf];expected=[a for a in s['pads'] if a['attribute']=='PTH' or (a['attribute']=='SMD' and layer==0)]
 for a in expected:
  hits=[o for o in pf if pt((o.x,o.y))==xy(a['position']) and (o.attrs.get('.P')==(a['ref'],a['number']) or o.attrs.get('.C')==(a['ref'],))]
  assert len(hits)==1,(ext,a['ref'],a['number']);o=hits[0];pf.remove(o)
  left,bottom,right,top=bounds(o);size=a['size'][::-1] if round(a['angle'])%180==90 else a['size']
  assert abs(right-left-size[0])<3e-6 and abs(top-bottom-size[1])<3e-6
 assert not pf
 regions=[o for o in objects if isinstance(o,Region)];assert not regions or ext=='.g1'
 assert len(lines)+len(flashes)+len(regions)==len(objects) and all(o.polarity_dark for o in objects)
 results.append(dict(layer=ext,tracks=len(lines),vias=len(vf),pads=len(expected),regions=len(regions)))
regions=[o for o in files['.g1'].objects if isinstance(o,Region)]
assert all(not any(o.arc_centers) for o in regions)
plane=unary_union([make_valid(Polygon(o.outline)) for o in regions])
native=json.loads((E/'cam-native-zones.json').read_text());expected=unary_union([Polygon(r['outer'],r['holes']) for r in native['zones'] if r['layer']=='In1.Cu'])
area=plane.symmetric_difference(expected).area;assert area<1e-8,area
for pos in [(79,92),(121,81),(79,119),(102,111.5)]:assert plane.intersection(Point(xy(pos)).buffer(2.5,quad_segs=4096)).area<1e-9
assert collections.Counter(seg((o.x1,o.y1),(o.x2,o.y2),o.aperture.diameter) for o in files['.gm1'].objects)==collections.Counter(seg(xy(e['start']),xy(e['end']),e['width']) for e in s['edges'])
expected_npth=collections.Counter((xy(a['position']),a['drill'][0]) for a in s['pads'] if a['attribute']=='NPTH')
assert collections.Counter((pt((o.x,o.y)),round(o.aperture.diameter,6)) for o in npth.objects)==expected_npth
rounds=[o for o in pth.objects if isinstance(o,Flash)];slots=slot_commands
assert len(rounds)==len(pth.objects)==110 and len(slots)==4 and len(npth.objects)==6
pending=[(xy(v['position']),v['drill']) for v in vias];errors=[]
for o in rounds:
 matches=[(i,v) for i,v in enumerate(pending) if abs(o.aperture.diameter-v[1])<1e-8 and abs(o.x-v[0][0])<=.0005001 and abs(o.y-v[0][1])<=.0005001]
 assert len(matches)==1
 i,v=matches[0];pending.pop(i);errors.append(math.dist((o.x,o.y),v[0]))
assert not pending
pending_slots=[]
for a in s['pads']:
 if a['attribute']!='PTH':continue
 x,y=xy(a['position']);dw,dh=a['drill'];dx=max(dw-dh,0)/2;dy=max(dh-dw,0)/2;angle=math.radians(a['angle']);rx=dx*math.cos(angle)-dy*math.sin(angle);ry=dx*math.sin(angle)+dy*math.cos(angle)
 pending_slots.append(seg((x-rx,y-ry),(x+rx,y+ry),min(dw,dh)))
assert collections.Counter(slots)==collections.Counter(pending_slots)
# Mask openings match actual component lands. Mechanical holes have no copper/mask pad flashes.
top=[o for o in files['.gtl'].objects if isinstance(o,Flash) and dict(o.aperture.attrs).get('.AperFunction')!=('ViaPad',)]
bottom=[o for o in files['.gbl'].objects if isinstance(o,Flash) and dict(o.aperture.attrs).get('.AperFunction')!=('ViaPad',)]
assert collections.Counter(bounds(o) for o in files['.gts'].objects)==collections.Counter(bounds(o) for o in top)
assert collections.Counter(bounds(o) for o in files['.gbs'].objects)==collections.Counter(bounds(o) for o in bottom)
native_pos=list(csv.DictReader((dest/'native-pos-absolute.csv').open()));lookup={a['ref']:a for a in s['components']};assert len(native_pos)==62
for row in native_pos:
 c=lookup[row['Ref']];assert pt((float(row['PosX']),float(row['PosY'])))==xy(c['position']) and float(row['Rot'])==c['angle'] and row['Side']=='top'
cpl=list(csv.DictReader((dest/'CPL.csv').open()));bom=list(csv.DictReader((dest/'BOM.csv').open()))
assert len(cpl)==len(bom)==58 and {a['Designator'] for a in cpl}=={a['Designator'] for a in bom}
for row in cpl:
 c=lookup[row['Designator']];assert pt((float(row['Mid X'][:-2]),float(row['Mid Y'][:-2])))==pt((c['position'][0]-76,122-c['position'][1])) and float(row['Rotation'])==c['angle']
paste={f.suffix:GerberFile.open(f) for f in (dest/'paste').iterdir() if f.suffix!='.gbrjob'}
paste_summary=[]
for ext,layer in [('.gtp','F.Paste'),('.gbp','B.Paste')]:
 source=[r for r in native['paste'] if r['layer']==layer];objects=paste[ext].objects
 lines=[o for o in objects if isinstance(o,Line)];regions=[o for o in objects if isinstance(o,Region)];arcs=[o for o in objects if isinstance(o,Arc)]
 flashes=[o for o in objects if isinstance(o,Flash)]
 expected_pads=[a for a in native['paste_pads'] if a['layer']==layer]
 assert len(flashes)==len(expected_pads)
 pending_flashes=list(flashes)
 for a in expected_pads:
  hits=[o for o in pending_flashes if pt((o.x,o.y))==pt(a['position_mm']) and o.attrs.get('.C')==(a['ref'],)]
  assert len(hits)==1,(a,hits)
  o=hits[0];pending_flashes.remove(o);left,bottom,right,top=bounds(o)
  expected_size=a['size_mm'][::-1] if round(a['angle'])%180==90 else a['size_mm']
  assert max(abs(right-left-expected_size[0]),abs(top-bottom-expected_size[1]))<3e-6
 assert not pending_flashes
 assert len(lines)+len(regions)+len(arcs)+len(flashes)==len(objects)
 assert collections.Counter(seg((o.x1,o.y1),(o.x2,o.y2),o.aperture.diameter) for o in lines)==collections.Counter(seg(r['start'],r['end'],r['width']) for r in source if r['kind']=='line')
 expected_rects=[]
 for r in source:
  if r['kind']=='rect':
   assert r['filled'] and r['width']==0
   x1,y1=r['start'];x2,y2=r['end'];expected_rects.append((min(x1,x2),min(y1,y2),max(x1,x2),max(y1,y2)))
 assert collections.Counter(bounds(o) for o in regions)==collections.Counter(tuple(round(v,6) for v in row) for row in expected_rects)
 circles=[r for r in source if r['kind']=='circle'];assert len(arcs)==2*len(circles)
 remaining=list(arcs)
 for r in circles:
  assert r['filled'] and r['width']==0
  x,y=r['start'];radius=math.dist(r['start'],r['end'])
  hits=[o for o in remaining if all([bounds(o)[0]>=x-radius-2e-6,bounds(o)[1]>=y-radius-2e-6,bounds(o)[2]<=x+radius+2e-6,bounds(o)[3]<=y+radius+2e-6])]
  assert len(hits)==2
  combined=(min(bounds(o)[0] for o in hits),min(bounds(o)[1] for o in hits),max(bounds(o)[2] for o in hits),max(bounds(o)[3] for o in hits))
  assert all(abs(a-b)<2e-6 for a,b in zip(combined,(x-radius,y-radius,x+radius,y+radius)))
  for o in hits:remaining.remove(o)
 assert not remaining
 paste_summary.append(dict(layer=layer,rectangles=len(regions),circles=len(circles),slot_strokes=len(lines),native_pad_flashes=len(flashes),objects=len(objects)))
members=sorted(f for f in fab.iterdir() if f.suffix!='.gbrjob');archive=dest/'main-stage2-fabrication-review.zip';assert len(members)==11
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for f in members:z.write(f,f.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and all(z.read(f.name)==f.read_bytes() for f in members)
save(E/'cam-check.json',dict(utc=now(),pass_check=True,gerbonara_version=importlib.metadata.version('gerbonara'),source_sha256=digest(E/'inspection/final/main.kicad_pcb'),copper_layers=results,plane_symmetric_difference_mm2=area,ideal_reservation_plane_overlap_mm2=0,outline_centerlines_match=True,npth=6,pth_round_vias=110,pth_slots=4,drill_max_quantization_displacement_mm=max(errors),front_mask_openings=len(files['.gts'].objects),back_mask_openings=len(files['.gbs'].objects),paste=paste_summary,native_pos_rows=62,assembled_bom_cpl_rows=58,origins_verified=True,parser_warnings=parser_warnings,slot_parser='Four inline G85 commands parsed separately with active tool diameter; round-only in-memory stream passed to Gerbonara, export bytes untouched.',archive_sha256=digest(archive),archive_members=[dict(name=f.name,sha256=digest(f)) for f in members],exclusions='BOM/CPL, paste, previews and gbrjob are separate from fabrication-only review zip. Not a manufacturing release.'))
print('CAM PASS: exact 4 copper layers, plane, 66 vias, 4 plated slots, 6 NPTH, masks and CPL transform')
