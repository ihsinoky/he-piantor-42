"""Independent readback and exact AST audit of authoring; no authoring imports."""
from common import *
import pcbnew as p,sexpdata as sx,collections,math
from shapely.geometry import Polygon,Point
w=E/'inputs/revised';local=E/'inputs/local'
def children(n,k):return [x for x in n if isinstance(x,list) and x and str(x[0])==k]
def tag(n,k):return children(n,k)[0][1:]
def clean(n):
 if not isinstance(n,list):return n
 if n and str(n[0])=='fill':n=[x for x in n if str(x)!='yes']
 return [clean(x) for x in n if not (isinstance(x,list) and x and str(x[0]) in ['filled_polygon','fill_segments','filled_areas_thickness'])]
def inv(t):return collections.Counter(sx.dumps(x) for x in clean(t)[1:])
base=sx.loads((w/'canonical-source.kicad_pcb').read_text());rev=sx.loads((w/'main.kicad_pcb').read_text());loc=sx.loads((local/'main.kicad_pcb').read_text())
removed=list((inv(base)-inv(rev)).elements());added=list((inv(rev)-inv(base)).elements());assert not removed
addednodes=[sx.loads(x) for x in added];assert collections.Counter(str(x[0]) for x in addednodes)=={'footprint':4,'zone':4}
loc_removed=list((inv(rev)-inv(loc)).elements());loc_added=list((inv(loc)-inv(rev)).elements());assert not loc_added
expected=set(json.loads((E/'local-scope.json').read_text())['removed_segments'][i]['uuid'] for i in range(3))
assert len(loc_removed)==3 and {str(tag(sx.loads(x),'uuid')[0]) for x in loc_removed}==expected
assert digest(w/'main.kicad_pro')==digest(local/'main.kicad_pro')==digest(R/'hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inputs/main-cell1/main.kicad_pro')
b=p.LoadBoard(str(w/'main.kicad_pcb'));holes=[];areas=[];silk=[];pad_hits=[]
for f in b.GetFootprints():
 if f.GetReference() in ['H1','H2','H3','H4']:
  a=list(f.Pads());assert len(a)==1;a=a[0]
  holes.append(dict(ref=f.GetReference(),position_mm=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],drill_mm=[p.ToMM(a.GetDrillSize().x),p.ToMM(a.GetDrillSize().y)],npth=a.GetAttribute()==p.PAD_ATTRIB_NPTH,net=a.GetNetname(),number=a.GetNumber(),excluded_bom=bool(f.GetAttributes()&p.FP_EXCLUDE_FROM_BOM),excluded_cpl=bool(f.GetAttributes()&p.FP_EXCLUDE_FROM_POS_FILES)))
for z in b.Zones():
 if not z.GetIsRuleArea():continue
 pts=z.Outline().Outline(0);coords=[[p.ToMM(pts.CPoint(i).x),p.ToMM(pts.CPoint(i).y)] for i in range(pts.PointCount())];poly=Polygon(coords);center=poly.centroid
 assert len(coords)==256 and poly.buffer(.000002).covers(center.buffer(2.5,quad_segs=4096))
 layers=[b.GetLayerName(x) for x in z.GetLayerSet().CuStack()];assert set(layers)=={'F.Cu','In1.Cu','In2.Cu','B.Cu'}
 assert z.GetDoNotAllowTracks() and z.GetDoNotAllowVias() and z.GetDoNotAllowCopperPour() and not z.GetDoNotAllowPads() and z.GetDoNotAllowFootprints()
 areas.append(dict(name=z.GetZoneName(),layers=layers,vertices=len(coords),center_mm=[center.x,center.y],minimum_radius_mm=poly.exterior.distance(center),pads_allowed=True,tracks_vias_pour_footprints_prohibited=True))
 # Actual copper pads checked even though KiCad's pads prohibition must allow the mechanical NPTH.
 for f in b.GetFootprints():
  for a in f.Pads():
   if a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   circle=p.SHAPE_CIRCLE(p.VECTOR2I(p.FromMM(center.x),p.FromMM(center.y)),p.FromMM(2.5))
   if a.GetEffectiveShape(p.F_Cu).Collide(circle):pad_hits.append(dict(area=z.GetZoneName(),ref=f.GetReference(),pad=a.GetNumber()))
 for d in b.GetDrawings():
  if d.GetLayer() not in [p.F_SilkS,p.B_SilkS]:continue
  if d.GetEffectiveShape(d.GetLayer()).Collide(circle):silk.append(dict(area=z.GetZoneName(),uuid=d.m_Uuid.AsString()))
assert len(areas)==4 and not pad_hits
assert sorted((h['ref'],h['position_mm']) for h in holes)==[('H1',[79.,92.]),('H2',[121.,81.]),('H3',[79.,119.]),('H4',[102.,111.5])]
assert all(h['drill_mm']==[2.2,2.2] and h['npth'] and not h['net'] and not h['number'] and h['excluded_bom'] and h['excluded_cpl'] for h in holes)
save(E/'equivalence-gate.json',dict(pass_gate=True,utc=now(),source_to_revision=dict(removed=removed,added_types={'footprint':4,'zone':4},added=added),revision_to_local=dict(removed=loc_removed,added=loc_added),original_project_byte_identical=True,existing_components_nets_connectors_artwork_and_copper_unchanged=True,holes=holes,rule_areas=areas,existing_copper_pad_conflicts=pad_hits,silkscreen_conflicts=silk))
print('Gate PASS; silk conflicts',silk)
