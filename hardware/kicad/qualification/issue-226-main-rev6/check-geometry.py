"""Independent parsed design diff, actual-copper clearance and case subset checks."""
from common import *
import sexpdata as sx,collections,math,importlib.util
import pcbnew as p
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import unary_union
V=E.parent/'issue-221-main-rev5';W=E/'inspection/final'
def tag(q):return str(q[0]) if isinstance(q,list) and q else ''
def child(q,t):return next(x for x in q if tag(x)==t)
def ref(q):return next(x[2] for x in q if tag(x)=='property' and x[1]=='Reference')
def clean(q):
 if not isinstance(q,list):return q
 if tag(q)=='fill':q=[x for x in q if str(x)!='yes']
 return [clean(x) for x in q if tag(x) not in ['polygon','filled_polygon','fill_segments','filled_areas_thickness']]
a=sx.loads((V/'inspection/final/main.kicad_pcb').read_text());c=sx.loads((W/'main.kicad_pcb').read_text())
fa={ref(q):q for q in a if tag(q)=='footprint'};fc={ref(q):q for q in c if tag(q)=='footprint'}
assert fa==fc,'Footprints changed'
ignore={'gr_line','zone'}
def rest(root):
 return collections.Counter(sx.dumps(q) for q in root[1:] if tag(q) not in ignore or (tag(q)=='gr_line' and child(q,'layer')[1]!='Edge.Cuts'))
assert rest(a)==rest(c),'Non-outline/non-zone data changed'
assert [q for q in a if tag(q)=='zone' and any(tag(x)=='keepout' for x in q)]==[q for q in c if tag(q)=='zone' and any(tag(x)=='keepout' for x in q)],'Keepout changed'
za=[clean(q) for q in a if tag(q)=='zone'];zc=[clean(q) for q in c if tag(q)=='zone'];assert za==zc,'Zone rules changed'
assert (W/'main.kicad_pro').read_bytes()==(V/'inspection/final/main.kicad_pro').read_bytes()
plan=json.loads((E/'geometry-plan.json').read_text());old=Polygon(plan['rev5_polygon_mm']);new=Polygon(plan['rev6_polygon_mm']);assert new.difference(old).area==0
actual_edges={tuple(sorted([tuple(child(q,'start')[1:]),tuple(child(q,'end')[1:])])) for q in c if tag(q)=='gr_line' and child(q,'layer')[1]=='Edge.Cuts'}
vs=plan['rev6_polygon_mm'];assert actual_edges=={tuple(sorted([tuple(a),tuple(b)])) for a,b in zip(vs,vs[1:]+vs[:1])}
angles=[]
for i,v in enumerate(vs):
 u=[(vs[(i+d)%6][0]-v[0],vs[(i+d)%6][1]-v[1]) for d in [-1,1]]
 angle=math.degrees(math.acos(sum(x*y for x,y in zip(*u))/(math.hypot(*u[0])*math.hypot(*u[1]))));assert 119.9999<angle<120.0001;angles.append(angle)
allowed=unary_union([Point(v['original_xy_mm']).buffer(6) for v in plan['vertices']])
spec=importlib.util.spec_from_file_location('audit',E/'audit-vias.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
boards=[p.LoadBoard(str(x)) for x in [V/'inspection/final/main.kicad_pcb',W/'main.kicad_pcb']];b=boards[1];layers=list(b.GetEnabledLayers().CuStack());changes=[]
for l in layers:
 geoms=[]
 for board in boards:
  geoms.append(unary_union([m.polygons(z.GetFilledPolysList(l)) for z in board.Zones() if not z.GetIsRuleArea() and z.IsOnLayer(l)]))
 removed=geoms[0].difference(geoms[1]);added=geoms[1].difference(geoms[0]);outside=geoms[0].symmetric_difference(geoms[1]).difference(allowed)
 numerical=outside if geoms[0].is_empty else outside.difference(geoms[0].boundary.buffer(.000002))
 assert numerical.area<1e-12,(l,numerical.area);assert added.difference(geoms[0].buffer(.000002)).area<1e-12,(l,added.area)
 if removed.area:changes.append(dict(layer=b.GetLayerName(l),net='GND',removed_area_mm2=removed.area,added_area_mm2=added.area,outside_corner_regions_raw_mm2=outside.area,outside_corner_regions_beyond_2nm_mm2=numerical.area,corner_region_radius_mm=6,numeric_tolerance_mm=.000002))
objects=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH:
   for l in layers:
    if pad.IsOnLayer(l):objects.append((f'{f.GetReference()}.{pad.GetNumber()}', 'pad',m.pad_polygon(pad,l)))
  d=pad.GetDrillSize()
  if d.x:
   assert d.x==d.y
   objects.append((f'{f.GetReference()}.{pad.GetNumber()}','hole',Point(m.xy(pad.GetPosition())).buffer(d.x/2e6,quad_segs=1024)))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  g=Point(m.xy(t.GetPosition())).buffer(t.GetWidth(p.F_Cu)/2e6,quad_segs=1024);kind='via'
 else:g=LineString([m.xy(t.GetStart()),m.xy(t.GetEnd())]).buffer(t.GetWidth()/2e6,quad_segs=1024);kind='track'
 objects.append((t.m_Uuid.AsString(),kind,g))
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in layers:
  if z.IsOnLayer(l):objects.append((f'zone:{z.m_Uuid.AsString()}:{b.GetLayerName(l)}','zone',m.polygons(z.GetFilledPolysList(l))))
rows=[]
for v in plan['vertices']:
 edge=LineString(v['face_endpoints_mm']);measurements=[dict(object=name,kind=kind,gap_mm=edge.distance(g)) for name,kind,g in objects]
 nearest={kind:min((q for q in measurements if q['kind']==kind),key=lambda q:q['gap_mm']) for kind in {q['kind'] for q in measurements}}
 assert all(q['gap_mm']>=.5 for q in measurements),(v,nearest)
 rows.append(dict(vertex=v['vertex'],nearest_by_kind=nearest,minimum_gap_mm=min(q['gap_mm'] for q in measurements)))
holes=[pad for f in b.GetFootprints() for pad in f.Pads() if pad.GetAttribute()==p.PAD_ATTRIB_NPTH];support=[]
for h in holes:
 disk=Point(m.xy(h.GetPosition())).buffer(2.5,quad_segs=1024);assert new.covers(disk)
 support.append(dict(ref=h.GetParentFootprint().GetReference(),position_mm=m.xy(h.GetPosition()),diameter_mm=p.ToMM(h.GetDrillSize().x),diameter5_support_margin_mm=new.boundary.distance(Point(m.xy(h.GetPosition())))-2.5))
report=dict(pass_check=True,rev5_sha256=digest(V/'inspection/final/main.kicad_pcb'),rev6_sha256=digest(W/'main.kicad_pcb'),all_footprints_byte_structure_identical=True,all_62_positions_and_angles_identical=len(fa)==62,footprints=len(fa),tracks_unchanged=sum(tag(q)=='segment' for q in a),vias_unchanged=sum(tag(q)=='via' for q in a),net_changes=0,project_byte_identical=True,changes=['three Edge.Cuts segments replaced by six','In1.Cu GND zone boundary and fill clipped at three corners'],copper_changes=changes,new_edge_clearance=rows,all_six_interior_angles_deg=angles,minimum_new_edge_gap_mm=min(q['minimum_gap_mm'] for q in rows),objects_measured_per_edge=len(objects),geometry_method='Native 10nm ERROR_OUTSIDE pad polygons; actual filled-zone polygons; round tracks/vias/holes at1024 segments per quadrant (hole chord error<0.4nm). Distance to edge centerlines. Unchanged legacy sides retain Rev5 clearances.',rev6_outside_rev5_area_mm2=new.difference(old).area,case_interference_unaffected='Rev6 is a strict subset of Rev5; all component poses, hole centers and full diameter5mm mounting support disks preserved. No added board material, so no new case interference.',mounts=support)
save(E/'rev5-diff-and-clearance.json',report);print(json.dumps(report,indent=2))
