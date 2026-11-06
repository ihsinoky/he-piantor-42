"""Read qualified board independently: hole reservations, POFV, J1, BOM/CPL identity."""
from common import *
import pcbnew as p, math, csv, io, collections, importlib.util
from shapely.geometry import Point, Polygon
label='local';w=E/'inspection'/label
assert not json.loads((w/'assessment.json').read_text())['pass_acceptance']  # diagnostic inventory only
b=p.LoadBoard(str(w/'main.kicad_pcb'))
spec=importlib.util.spec_from_file_location('oracle87',R/'hardware/kicad/qualification/issue-87-native-main-routing/check-main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
mm=lambda n:round(p.ToMM(n),6)
xy=lambda v:[mm(v.x),mm(v.y)]
footprints=list(b.GetFootprints());pads=[(f,a) for f in footprints for a in f.Pads()]
tracks=list(b.GetTracks());vias=[t for t in tracks if isinstance(t,p.PCB_VIA)]
layers=list(b.GetEnabledLayers().CuStack())
def ring(line):return [(mm(line.CPoint(i).x),mm(line.CPoint(i).y)) for i in range(line.PointCount())]
zone_shapes=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for layer in layers:
  if not z.IsOnLayer(layer):continue
  polys=z.GetFilledPolysList(layer)
  for i in range(polys.OutlineCount()):zone_shapes.append(Polygon(ring(polys.Outline(i)),[ring(polys.Hole(i,j)) for j in range(polys.HoleCount(i))]))
holes=[];drills=[]
for f,a in pads:
 if not any(xy(a.GetDrillSize())):continue
 drills.append((f.GetReference()+'.'+a.GetNumber()+'@'+a.m_Uuid.AsString(),m.capsule(xy(a.GetPosition()),xy(a.GetDrillSize()),a.GetOrientationDegrees())))
for t in vias:drills.append((t.m_Uuid.AsString(),m.capsule(xy(t.GetPosition()),[mm(t.GetDrillValue())]*2)))
art=list(b.GetDrawings())+[g for f in footprints for g in f.GraphicalItems()]+[a for f in footprints for a in (f.Reference(),f.Value()) if a.IsVisible()]
for ref,pos in [('H1',[79,92]),('H2',[121,81]),('H3',[79,119]),('H4',[102,111.5])]:
 f=next(f for f in footprints if f.GetReference()==ref);a=list(f.Pads())[0]
 assert xy(f.GetPosition())==pos and xy(a.GetDrillSize())==[2.2,2.2] and a.GetAttribute()==p.PAD_ATTRIB_NPTH and not a.GetNetname()
 circle=p.SHAPE_CIRCLE(a.GetPosition(),p.FromMM(2.5));conflicts=[]
 for f2,a2 in pads:
  if a2.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  if any(a2.IsOnLayer(l) and a2.GetEffectiveShape(l).Collide(circle) for l in layers):conflicts.append(f2.GetReference()+'.'+a2.GetNumber())
 for t in tracks:
  if t.GetEffectiveShape(t.GetLayer()).Collide(circle):conflicts.append(t.m_Uuid.AsString())
 silk=[g.m_Uuid.AsString() for g in art if g.GetLayer() in (p.F_SilkS,p.B_SilkS) and g.GetEffectiveShape(g.GetLayer()).Collide(circle)]
 disk=Point(pos).buffer(2.5,quad_segs=4096);overlap=sum(g.intersection(disk).area for g in zone_shapes)
 hole=m.capsule(pos,[2.2]*2);clearances=[dict(other=name,edge_gap_mm=hole.distance(g)) for name,g in drills if name!=ref+'.@'+a.m_Uuid.AsString()]
 edge=min(pos[0]-76,124-pos[0],pos[1]-70,122-pos[1])-1.1
 assert not conflicts and overlap<1e-9 and not silk
 holes.append(dict(ref=ref,position_mm=pos,drill_mm=2.2,npth=True,net='',copper_reservation_mm=5.0,copper_conflicts=conflicts,filled_zone_overlap_mm2=overlap,silk_conflicts=silk,hole_edge_to_board_mm=edge,reservation_edge_to_board_mm=edge-1.4,closest_other_drill=min(clearances,key=lambda x:x['edge_gap_mm'])))
save(E/'mechanical-readback.json',dict(utc=now(),source_sha256=digest(w/'main.kicad_pcb'),candidate_qualified=False,outline_bounds_mm=[76,70,124,122],outline_size_mm=[48,52],holes=holes,all_copper_layers_checked=[b.GetLayerName(l) for l in layers],method='Native KiCad copper and visible silk effective shapes vs solid reservation disk; actual filled-zone polygons vs disk; independent round/oval drill geometries',physical_validation_pending=['M2 head/washer/boss diameter <=4.5mm and combined radial tolerance <=0.25mm','Actual connector insertion loads and nonrectangular four-point deflection on 1.2mm board','Driver envelope, screw length and tightening torque','Bottom solder/POFV caps and insulating boss/washer heights','USB/GH plugs and actual cable/tool volumes; remove GH harness for H4 tool access as needed','Noise, USB signal integrity and ADC settling with changed GND return geometry']))
# Reuse only the native effective-shape observation functions from #137, not its old log/counts.
reference=R/'hardware/kicad/qualification/issue-137-main-manufacturing-review-prep/analyze-board.py'
code=reference.read_text();defs=code[code.index('def mm('):code.index('all_vias=')]
scope=dict(pcbnew=p,pads=[(f.GetReference(),a) for f,a in pads],graphics=[g for g in b.GetDrawings() if g.GetLayer()==p.F_Paste])
exec(compile(defs,str(reference),'exec'),scope)
observations=[scope['inspect'](t) for t in vias];counts=collections.Counter();candidates=[]
for row in observations:
 hits=row['copper_pad_hits'];paste=row['paste_graphic_hits']
 if not hits and not paste:row['classification']='no-pad-or-paste-overlap';continue
 assert all(h['same_net'] for h in hits)
 mounted=[h for h in hits if not h['ref'].startswith('TP')]
 if any(h['via_center_in_pad'] for h in mounted):kind='mounted-center-in-pad'
 elif any(h['drill_overlaps_pad'] for h in mounted):kind='mounted-drill-edge-overlap'
 elif mounted:kind='mounted-annulus-only'
 elif hits:kind='bare-testpad'
 else:kind='paste-only'
 row['classification']=kind;counts[kind]+=1;candidates.append(row)
out=dict(utc=now(),candidate_qualified=False,manufacturing_acceptance=False,source_sha256=digest(w/'main.kicad_pcb'),reference_method_sha256=digest(reference),method='All board vias scanned, not restricted to old router observations; native effective pad, solid via disk, drill disk and F.Paste graphic collisions. Nominal geometry, no process tolerance.',total_vias=len(vias),candidate_count=len(candidates),classification_counts=dict(counts),mounted_drill_overlap_count=sum(any(h['drill_overlaps_pad'] and not h['ref'].startswith('TP') for h in r['copper_pad_hits']) for r in candidates),drill_paste_overlap_count=sum(any(h['drill_overlaps_graphic'] for h in r['paste_graphic_hits']) for r in candidates),observations=observations,decision='D-022 POFV retained; submit every candidate and all-via inventory for manufacturer acceptance, including 0.60/0.30mm, scope, mask/paste and 4-layer surcharge. No order or acceptance obtained.')
save(E/'pofv-reclassification.json',out)
stream=io.StringIO();writer=csv.writer(stream,lineterminator="\n");writer.writerow(['x_mm','y_mm','net','uuid','diameter_mm','drill_mm','classification','pads','drill_overlaps_mounted_pad','drill_overlaps_paste'])
for r in candidates:writer.writerow([*r['position_mm'],r['net'],r['uuid'],r['diameter_mm'],r['drill_mm'],r['classification'],';'.join(h['ref']+'.'+h['pad'] for h in r['copper_pad_hits']),any(h['drill_overlaps_pad'] and not h['ref'].startswith('TP') for h in r['copper_pad_hits']),any(h['drill_overlaps_graphic'] for h in r['paste_graphic_hits'])])
(E/'pofv-sites.csv').write_text(stream.getvalue())

print("Unqualified candidate POFV inventory:",len(vias),"vias",len(candidates),"candidates",dict(counts))
