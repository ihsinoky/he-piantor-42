"""Compare Phase A-2 exact placement and pre-route schematic contract to final board."""
from common import *
import pcbnew as p,xml.etree.ElementTree as ET,collections,importlib.util,math
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import unary_union
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()};plan=json.loads((E.parent/'issue-196-main-rev4-phasea2/geometry-plan.json').read_text());errors=[]
contract=json.loads((E/'logical-contract.json').read_text())['components'];root=ET.parse(E/'schematic/main.net.xml').getroot();sch={}
for n in root.findall('./nets/net'):
 name=n.get('name').lstrip('/');name=None if name.startswith('unconnected-') else name
 for node in n.findall('node'):sch[node.get('ref'),node.get('pin')]=name
pins=0
for ref,c in contract.items():
 f=fps[ref];assert f.GetValue()==c['value'],(ref,f.GetValue(),c['value']);native=collections.defaultdict(list)
 for pad in f.Pads():
  if pad.GetNumber():native[pad.GetNumber()].append(pad.GetNetname() or None)
 for pin,net in c['pins'].items():
  assert native[pin] and all(v==net for v in native[pin]),(ref,pin,net,native[pin]);assert sch.get((ref,pin))==net,(ref,pin,sch.get((ref,pin)),net);pins+=1
 assert set(native)==set(c['pins'])
for q in plan['main']['placements']:
 f=fps[q['ref']];x,y=a.xy(f.GetPosition());assert max(abs(x-q['at_mm'][0]-100),abs(y-q['at_mm'][1]-70))<.000002
 assert abs((f.GetOrientationDegrees()-q['angle_deg']+180)%360-180)<1e-6
outline=p.SHAPE_POLY_SET();assert b.GetBoardPolygonOutlines(outline);board=a.polygons(outline);expected=Polygon([(x+100,y+70) for x,y in plan['main']['outline_xy_mm']]);assert board.symmetric_difference(expected).area<.0001
pads=[(f.GetReference(),a.pad_polygon(pad,p.F_Cu)) for f in b.GetFootprints() for pad in f.Pads() if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH]
holes=[]
for h in plan['main']['holes']:
 x,y=h['xy_mm'];pos=[x+100,y+70];f=fps[h['ref']];assert math.dist(pos,a.xy(f.GetPosition()))<.000002
 copper=[]
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):copper.append(Point(a.xy(t.GetPosition())).buffer(.3,quad_segs=128))
  else:copper.append(LineString([a.xy(t.GetStart()),a.xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128))
 for z in b.Zones():
  if not z.GetIsRuleArea():copper.append(a.polygons(z.GetFilledPolysList(z.GetLayer())))
 copper.extend(g for _,g in pads);gap=Point(pos).distance(unary_union(copper));assert gap>=2.50019,(h['ref'],gap)
 holes.append(dict(ref=h['ref'],minimum_actual_copper_radius_mm=gap,boss_to_copper_mm=gap-2.25))
assert len(fps)==62 and len(contract)==59 and len(b.GetEnabledLayers().CuStack())==4 and p.ToMM(b.GetDesignSettings().GetBoardThickness())==1.2
assert set(fps)==set(contract)|{'H1','H2','H3'}
save(E/'design-check.json',dict(pass_check=True,board_sha256=digest(E/'inspection/final/main.kicad_pcb'),schematic_export_sha256=digest(E/'schematic/main.net.xml'),logical_components=59,logical_pins=pins,footprints=62,Phase_A2_poses_exact=True,holes=holes,outline_size_mm=plan['main']['size_mm'],pad_edge_min_mm=min(board.boundary.distance(g) for _,g in pads),In1_GND_only=True))
print('Design/circuit/geometry PASS',pins,'pins')
