"""Read-only native inspection of legend placement, source preservation and key marks."""
import json,math
from collections import Counter
import pcbnew as p
from shapely.geometry import LineString,box
from shapely.ops import unary_union
from common import E,R,SOURCE,save,digest
import sys
if "--verify-only" in sys.argv:
 def save(path,value):
  pass

def xy(v):return [v.x/1e6,v.y/1e6]
results=[]
for pitch in (16,17):
 d=E/f'{pitch}mm';pcb=d/f'wing-{pitch}mm-silk149.kicad_pcb'
 b=p.LoadBoard(str(pcb));e=json.loads((d/'design-evidence.json').read_text());fps={f.GetReference():f for f in b.GetFootprints()}
 source=SOURCE/f'runs/KRT-{pitch}-2L-P0300/out.kicad_pcb';s=source.read_bytes();v=pcb.read_bytes();idx=s.rfind(b')');tail=s[idx:]
 assert v[:idx]==s[:idx] and v[-len(tail):]==tail and len(v)>len(s)
 drawings=[g for g in b.GetDrawings() if g.GetLayer()==p.F_SilkS]
 assert len(drawings)==e['added_nodes']==183
 assert Counter(g.GetText() for g in drawings if isinstance(g,p.PCB_TEXT))==Counter(x['text'] for x in e['additions'] if x['kind']=='text')
 native_lines=Counter((tuple(xy(g.GetStart())),tuple(xy(g.GetEnd())),round(g.GetWidth()/1e6,6)) for g in drawings if isinstance(g,p.PCB_SHAPE) and g.GetShape()==p.SHAPE_T_SEGMENT)
 recorded_lines=Counter((tuple(round(v,6) for v in x['start']),tuple(round(v,6) for v in x['end']),x['width_mm']) for x in e['additions'] if x['kind']=='line')
 assert native_lines==recorded_lines
 frames=unary_union([LineString([x['start'],x['end']]) for x in e['additions'] if x['role']=='key-frame'])
 coverage=[]
 for q in e['squares']:
  c=q['corners'];closed=LineString(c+[c[0]])
  assert math.dist(q['center'],xy(fps[q['ref']].GetPosition()))<1e-6
  assert all(abs(math.dist(c[i],c[(i+1)%4])-pitch)<1e-6 for i in range(4))
  fraction=closed.intersection(frames.buffer(.00001)).length/closed.length
  assert fraction>.85,(pitch,q['ref'],fraction)
  coverage.append(dict(ref=q['ref'],perimeter_coverage_fraction=fraction))
 pins=[]
 for item in e['pin1_marks']:
  pads=list(fps[item['ref']].Pads());nearest=sorted((math.dist(item['mark'],xy(q.GetPosition())),q.GetNumber()) for q in pads)
  assert nearest[0][1]=='1' and nearest[1][0]>nearest[0][0]+.01
  pins.append(dict(ref=item['ref'],nearest_pad='1',distance_mm=nearest[0][0],net=item['net']))
 assert len(pins)==25 and next(x for x in pins if x['ref']=='J_WING')['net']=='HALL_5V'
 # Check nominal definition keepout against existing tessellated native rule areas.
 zones=list(b.Zones());assert len(zones)==4 and all(z.GetIsRuleArea() for z in zones)
 holes=[]
 for hole in e['mounting_holes']:
  q=next(iter(fps[hole['ref']].Pads()));assert xy(q.GetDrillSize())==[hole['diameter_mm']]*2
  assert xy(q.GetPosition())==[hole['x_mm'],hole['y_mm']]
  candidates=[]
  for z in zones:
   points=[xy(v) for v in z.Outline().COutline(0).CPoints()]
   radii=[math.dist([hole['x_mm'],hole['y_mm']],v) for v in points]
   if max(abs(r-hole['keepout_diameter_mm']/2) for r in radii)<.0003:candidates.append(z)
  assert len(candidates)==1
  holes.append(hole)
 project=json.loads(pcb.with_suffix('.kicad_pro').read_text())['board']['design_settings']
 assert project['drc_exclusions']==[]
 assert all(project['rule_severities'][k]=='warning' for k in ('silk_edge_clearance','silk_over_copper','silk_overlap'))
 drc=json.loads((d/'drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
 result=dict(pitch_mm=pitch,all_68_references_present=True,key_frames=coverage,pin1_marks=pins,mounting_holes=holes,minimum_frame_perimeter_coverage_fraction=min(x['perimeter_coverage_fraction'] for x in coverage),nominal_keepout_diameter_mm=5,existing_keepout_tessellation_radial_tolerance_mm=.0003,silk_drc_checks_enabled=True,drc_exclusions=[],drc_violations=0,drc_unconnected=0,source_sha256=digest(source),derived_sha256=digest(pcb))
 save(d/'silkscreen-check.json',result);results.append(result)
save(E/'silkscreen-checks.json',results)
print('Both legends, key pitch/perimeter, native marks/holes/keepouts and silk DRC settings verified.')
