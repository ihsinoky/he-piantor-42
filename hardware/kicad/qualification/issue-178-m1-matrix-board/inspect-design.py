"""Independent native geometry/pin readback against pitch9 and both block specs.
Includes all-via PCBA classification using #137 native effective-shape method.
"""
from common import *
import pcbnew as p,math,csv,io,collections
from itertools import product
spec=json.loads((SOURCE/'definition.json').read_text());path=E/'runs/final/out.kicad_pcb'
b=p.LoadBoard(str(path));fps={f.GetReference():f for f in b.GetFootprints()}
mm=lambda n:round(p.ToMM(n),6)
xy=lambda v:[mm(v.x),mm(v.y)]
assert b.GetCopperLayerCount()==2 and mm(b.GetDesignSettings().GetBoardThickness())==1.2
# Native pad-net identity, including all three unused MUX pins and GH MP pads.
for c in spec['components']:
 f=fps[c['reference']];assert f.GetValue()==c['mpn'];assert xy(f.GetPosition())==[100+c['x_mm'],100-c['y_mm']]
 assert f.GetOrientationDegrees()==c['rotation_ccw_deg']
 for q in f.Pads():assert q.GetNetname()==(c['pins'][q.GetNumber()] or '')
assert len(fps)==len(spec['components'])+4==65
sites=[]
for s in spec['sensor_sites']:
 pos=xy(fps[s['reference']].GetPosition());sites.append(dict(**s,kicad_xy_mm=pos))
left=[s for s in sites if s['block_pitch_mm']==16];right=[s for s in sites if s['block_pitch_mm']==17]
pairs=sorted([dict(left=a['reference'],right=z['reference'],distance_mm=math.dist(a['kicad_xy_mm'],z['kicad_xy_mm'])) for a,z in product(left,right)],key=lambda r:r['distance_mm'])
assert len(pairs)==81 and pairs[0]['distance_mm']==35
for pitch,block in [(16,left),(17,right)]:
 for a,z in product(block,block):
  assert a['kicad_xy_mm'][0]-z['kicad_xy_mm'][0]==(ord(a['column'])-ord(z['column']))*pitch
  assert a['kicad_xy_mm'][1]-z['kicad_xy_mm'][1]==(a['row']-z['row'])*pitch
# Compare frozen GH mapping and contact local geometry with existing pitch9 PCB.
pitch9=p.LoadBoard(str(R/'hardware/kicad/qualification/issue-129-wing-2layer-routing/evidence/inputs/pitch9-16mm/main.kicad_pcb'))
old=next(f for f in pitch9.GetFootprints() if f.GetReference()=='J_WING');new=fps['J_WING']
def pinmap(f):return sorted([(q.GetNumber(),q.GetNetname(),xy(q.GetPosition()-f.GetPosition()),xy(q.GetSize()),int(q.GetShape())) for q in f.Pads()])
assert pinmap(new)==pinmap(old)
# All mounting reservations independently checked vs actual pads, tracks and vias.
tracks=list(b.GetTracks());pads=[(f,a) for f in fps.values() for a in f.Pads()];holes=[]
for i,h in enumerate(spec['mounting_holes'],1):
 f=fps[f'H{i}'];a=list(f.Pads())[0];pos=xy(a.GetPosition());assert a.GetAttribute()==p.PAD_ATTRIB_NPTH and xy(a.GetDrillSize())==[2.2,2.2]
 assert pos==[100+h['x_mm'],100-h['y_mm']]
 circle=p.SHAPE_CIRCLE(a.GetPosition(),p.FromMM(2.5));hits=[]
 for f2,q in pads:
  if q.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  if q.GetEffectiveShape(p.F_Cu).Collide(circle):hits.append(f2.GetReference()+'.'+q.GetNumber())
 for t in tracks:
  if t.GetEffectiveShape(t.GetLayer()).Collide(circle):hits.append(t.m_Uuid.AsString())
 assert not hits
 holes.append(dict(ref=f.GetReference(),position_mm=pos,drill_mm=2.2,reservation_diameter_mm=5,copper_conflicts=hits))
assert all(z.GetIsRuleArea() and z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowCopperPour() for z in b.Zones())
assert all(not a.IsOnLayer(p.F_Paste) for f,a in pads if f.GetReference().startswith('TP_'))
save(E/'native-design-readback.json',dict(utc=now(),source_sha256=digest(path),components=61,footprints=65,keys=18,muxes=3,capacitors=21,GH14_pinmap_unchanged=True,GH14_pinmap=pinmap(new),all_component_pad_nets_equal_definition=True,all_81_interblock_pairs=pairs,minimum_interblock_key_center_distance_mm=35,geometry_basis='Native footprint origins coincide with inherited pitch9 Hall sensor/magnet target origins; field centre separation 68mm minus 16mm minus 17mm =35mm; both middle rows at Y90. Other pairs have |dx|>=35 and dy squared>=0.',holes=holes,key_sites=sites,physical_magnetic_isolation_measured=False))
reference=R/'hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/analyze-board.py';code=reference.read_text();defs=code[code.index('def mm('):code.index('all_vias=')]
scope=dict(pcbnew=p,pads=[(f.GetReference(),a) for f,a in pads],graphics=[g for g in b.GetDrawings() if g.GetLayer()==p.F_Paste]);exec(compile(defs,str(reference),'exec'),scope)
vias=[t for t in tracks if isinstance(t,p.PCB_VIA)];rows=[scope['inspect'](t) for t in vias]
for r in rows:
 hits=r['copper_pad_hits'];assert all(q['same_net'] for q in hits)
 mounted=[q for q in hits if not q['ref'].startswith('TP_')]
 r['classification']='mounted-center-in-pad' if any(q['via_center_in_pad'] for q in mounted) else 'mounted-drill-edge' if any(q['drill_overlaps_pad'] for q in mounted) else 'mounted-annulus-only' if mounted else 'bare-testpad' if hits else 'no-pad-overlap'
counts=dict(collections.Counter(r['classification'] for r in rows))
save(E/'via-pcba-review.json',dict(utc=now(),source_sha256=digest(path),total_vias=len(rows),classification_counts=counts,all_vias=rows,fabrication_requirement='ALL plated vias (146), epoxy filled and copper capped / plated over (POFV, IPC-4761 Type VII); no routing dimension change. Manufacturer acceptance and costs not requested. KiCad9 cannot express via filling/capping; fabrication notes control.',manufacturer_accepted=False))
s=io.StringIO();w=csv.writer(s,lineterminator='\n');w.writerow(['UUID','X mm','Y mm','Net','Diameter mm','Drill mm','Classification','Pads','Required process'])
for r in rows:w.writerow([r['uuid'],*r['position_mm'],r['net'],r['diameter_mm'],r['drill_mm'],r['classification'],';'.join(q['ref']+'.'+q['pad'] for q in r['copper_pad_hits']),'ALL plated vias: epoxy fill + copper cap + plate over'])
(E/'all-vias.csv').write_text(s.getvalue())
print('Native geometry/pinmap verified; all 81 distances; via classes',counts)
