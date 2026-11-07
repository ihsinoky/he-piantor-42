"""Read-only Phase A-2 placement witness. No board save, route or zone refill."""
from pathlib import Path
import json, math, hashlib, itertools, csv
import pcbnew as p
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely.affinity import translate, rotate
E=Path(__file__).resolve().parent
R=E.parents[3]
SOURCE=R/'hardware/kicad/qualification/issue-185-main-rev3/inspection/final/main.kicad_pcb'
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def save(f,v): (E/f).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def xy(v): return [v.x/1e6,v.y/1e6]
def padpoly(a):
 ps=p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps,p.F_Cu,0,10,p.ERROR_OUTSIDE)
 return unary_union([Polygon([xy(ps.Outline(j).CPoint(i)) for i in range(ps.Outline(j).PointCount())]) for j in range(ps.OutlineCount())])
def coords(g): return [list(q) for q in list(g.exterior.coords)[:-1]]
assert sha(SOURCE)=='0e81ba42b194e03fb0422b58a64c967fe83166d0495d84f28c4171184b665bae'
c=math.sqrt(3)/2; gap=2.; clearance=2.
wing={}
for pitch in [16,17]:
 sides={}
 for side in ['left','right']:
  path=E/f'inputs/wing/definition-{pitch}mm-{side}.proposal.json';d=json.loads(path.read_text())
  sign=1 if side=='left' else -1
  # Mirror right local X into left frame before rotating, then mirror global X back.
  xmax=max(sign*x for x,y in d['outline_mm']);ymax=max(y for x,y in d['outline_mm'])
  def tr(x,y):
   x=sign*x
   return [sign*(-gap/2+c*(x-xmax)+.5*(y-ymax)), .5*(x-xmax)-c*(y-ymax)]
  op=Polygon([tr(x,y) for x,y in d['outline_mm']]);keys=[Polygon([tr(x,y) for x,y in k['envelope_mm']]) for k in d['keys']]
  ymin=min(y for x,y in d['outline_mm'])
  sides[side]=dict(source_sha256=sha(path),local_inner_edge_x_mm=sign*xmax,local_north_y_mm=ymax,transform_matrix=[[c,sign*.5],[sign*.5,-c]],translation_xy_mm=tr(0,0),outline_xy_mm=coords(op),keys=[dict(key=k['key'],envelope_xy_mm=coords(g)) for k,g in zip(d['keys'],keys)],inner_edge_endpoints_xy_mm=[tr(sign*xmax,ymax),tr(sign*xmax,ymin)],J1_xy_mm=tr(sign*-37,-23),J1_south_edge_projection_xy_mm=tr(sign*-37,ymin),south_switch_y_mm=max(g.bounds[3] for g in keys),south_pcb_y_mm=op.bounds[3])
 wing[str(pitch)]=sides
# Use the smaller south envelope, round northward at 0.1 mm. No pitch-specific main.
base=math.floor(min(w['left']['south_switch_y_mm'] for w in wing.values())*10)/10
apex=(clearance-c*gap/2)/.5
half=(base-apex)/math.sqrt(3)
outline=Polygon([[0,apex],[half,base],[-half,base]])
assert outline.is_valid
holes={'H1':[0,apex+7], 'H2':[-half+6,base-3.5], 'H3':[half-6,base-3.5]}
# GH long axis follows each side; service envelope uses prior 26 x 8 contract.
placements={};envs={};padgeoms={};fps={};native={};bodyassumptions={}
b=p.LoadBoard(str(SOURCE));assert b
for f in b.GetFootprints():
 r=f.GetReference();fps[r]=f
 native[r]=dict(at_mm=xy(f.GetPosition()),angle_deg=f.GetOrientationDegrees(),value=f.GetValue(),pad_nets=sorted([[a.GetNumber(),a.GetNetname()] for a in f.Pads()]))
removed={'J1','R1','R2','U2'}
# Keep MCU USB termination resistors R3/R4 on the Main.
retained=set(fps)-removed-{r for r in fps if r.startswith('H')}

def place(r,x,y,ang=None,kind='pad_bbox_plus_body'):
 f=fps[r]; f.SetOrientationDegrees(native[r]['angle_deg'] if ang is None else ang);f.SetPosition(p.VECTOR2I(round(x*1e6),round(y*1e6)))
 pads=unary_union([padpoly(a) for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]); padgeoms[r]=pads
 if r in ['J2','J3']:
  # Source native GH local service x[-13,13],y[-1.5,6.5].
  g=box(-13,-1.5,13,6.5);g=translate(rotate(g,-f.GetOrientationDegrees(),origin=(0,0)),x,y)
 elif r=='J4':
  # C3 native connector datum: pad row y=-4.775; mouth y=0. Reserve 5 mm insertion.
  g=box(-3.65,-5.8,3.65,5);g=translate(rotate(g,-f.GetOrientationDegrees(),origin=(0,0)),x,y)
 else:
  # Native Main has no fab/courtyard geometry. Use pad bbox union explicit package body.
  bounds=pads.bounds;g=box(*bounds)
  dims={'U1':(7,7),'U3':(2,3),'U4':(3,3),'U5':(2.2,2.5),'U6':(3,3),'Y1':(3.2,2.5),'L1':(4,4)}.get(r)
  if dims:
   body=translate(rotate(box(-dims[0]/2,-dims[1]/2,dims[0]/2,dims[1]/2),-f.GetOrientationDegrees(),origin=(0,0)),x,y)
   g=g.union(body).envelope;bodyassumptions[r]=dims
  # 0.15 mm modeling allowance around pad/body envelopes.
  g=g.buffer(.15,join_style=2)
 envs[r]=g
 placements[r]=dict(ref=r,at_mm=xy(f.GetPosition()),angle_deg=f.GetOrientationDegrees(),side='F.Cu',value=f.GetValue(),pad_nets=sorted([[a.GetNumber(),a.GetNetname()] for a in f.Pads()]),envelope_xy_mm=coords(g),envelope_model=kind)

# Locate GH at y=42, inset enough for full access rectangle; cable bends outward in +Z.
for r,sign,ang in [('J2',-1,240),('J3',1,120)]:
 y=42.; x=sign*((y-apex)/math.sqrt(3)-6.)
 place(r,x,y,ang,'26x8_service_reservation')
# Reuse C3's actual connector footprint only in RAM, remap pin-net names in proposal.
ub=p.LoadBoard(str(E/'inputs/udb/c3.kicad_pcb'))
uf=next(f for f in ub.GetFootprints() if f.GetReference()=='J2');uf.SetReference('J4');fps['J4']=uf
native['J4']=dict(at_mm=xy(uf.GetPosition()),angle_deg=0,value=uf.GetValue())
place('J4',0,20,180,'C3_native_pads_plus_5mm_cable_access')
placements['J4']['pad_nets']=[['1','VBUS'],['2','USB_DM_ESD'],['3','USB_DP_ESD'],['4','GND'],['','mechanical_NC'],['','mechanical_NC']]
# Preserve functional groups with rigid translations wherever practical.
power=['U6','L1','C23','C24','C25','C26','C27','C28','R17','R18','R19']
for r in power:
 x,y=native[r]['at_mm'];place(r,x-88,y-73.5+31)
core=retained-set(power)-{'J2','J3'}
for r in sorted(core):
 x,y=native[r]['at_mm'];place(r,x-100,y-100+49)
# Fix collisions/edge margins by a bounded deterministic nearest-grid placement search.
# Anchors retain RP2040, crystal, flash, converter and connectors; small passives can move.
anchors=['J2','J3','J4','U1','U3','Y1','C1','C2','U6','L1']
# Reposition a cluster only if necessary; search has no routing objective.
order=anchors+sorted(set(placements)-set(anchors),key=lambda r:(-envs[r].area,r))
placed={};moves=[]
for r in order:
 orig=placements[r]['at_mm'][:];a=placements[r]['angle_deg'];g0=envs[r]
 def good(g):
  return outline.covers(g) and outline.boundary.distance(g)>=.25-1e-8 and all(g.distance(h)>=.3-1e-8 for h in placed.values()) and all(g.distance(Point(pt))>=2.5002 for pt in holes.values())
 if not good(g0):
  candidates=[]
  # 0.5mm grid nearest witness, full area; never infer infeasibility from search failure.
  for iy in range(20,134):
   yy=iy*.5
   for ix in range(-72,73):
    xx=ix*.5
    candidates.append(((xx-orig[0])**2+(yy-orig[1])**2,xx,yy))
  found=False
  for _,xx,yy in sorted(candidates):
   g=translate(g0,xx-orig[0],yy-orig[1])
   if good(g):
    place(r,xx,yy,a,placements[r]['envelope_model']);moves.append(dict(ref=r,from_mm=orig,to_mm=[xx,yy]));found=True;break
  assert found, f'No placement witness for {r}'
 placed[r]=envs[r]
assert len(placements)==len(retained)+1
assert set(placements)==retained|{'J4'}
assert all(placements[r]['pad_nets']==native[r]['pad_nets'] for r in retained)
# Independent aggregate checks, including pads not just the planning rectangles.
pairchecks=[dict(a=a,b=b,gap_mm=envs[a].distance(envs[b])) for a,b in itertools.combinations(sorted(envs),2)]
assert min(q['gap_mm'] for q in pairchecks)>=.3-1e-8
edgechecks=[dict(ref=r,envelope_edge_mm=outline.boundary.distance(g),pad_edge_mm=outline.boundary.distance(padgeoms[r]),inside=outline.covers(g) and outline.covers(padgeoms[r])) for r,g in envs.items()]
assert all(q['inside'] and q['pad_edge_mm']>=.2 for q in edgechecks)
assert all(envs[r].covers(padgeoms[r]) for r in envs)
holechecks=[]
for r,pt in holes.items():
 edge=outline.boundary.distance(Point(pt));near,ref=min((Point(pt).distance(g),ref) for ref,g in envs.items())
 assert edge>=3 and near>=2.5002
 holechecks.append(dict(ref=r,xy_mm=pt,npth_diameter_mm=2.2,boss_diameter_max_mm=4.5,copper_reservation_diameter_mm=5.0004,layers=['F.Cu','In1.Cu','In2.Cu','B.Cu'],prohibit=['tracks','vias','copperpour'],boss_to_edge_mm=edge-2.25,boss_to_envelope_mm=near-2.25,nearest_ref=ref))
wingchecks=[]
harness=[]
for pitch,sides in wing.items():
 for side,w in sides.items():
  g=Polygon(w['outline_xy_mm']); dist=g.distance(outline)
  assert abs(dist-clearance)<1e-7
  ref='J2' if side=='left' else 'J3';start=placements[ref]['at_mm'];end=w['J1_xy_mm'];chord=math.dist(start,end)
  # Explicit planning allowance only, not bend-radius certification.
  route=[start,w['inner_edge_endpoints_xy_mm'][1],w['J1_south_edge_projection_xy_mm'],end]
  route_length=sum(math.dist(a,b) for a,b in zip(route,route[1:]))
  harness.append(dict(pitch_mm=int(pitch),side=side,main_ref=ref,main_native_at_mm=start,wing_J1_xy_mm=end,chord_mm=chord,planning_route_xy_mm=route,planning_route_mm=route_length,planning_extra_mm=30,planning_length_mm=route_length+30,proposed_nominal_mm=200,old_100mm_short_even_for_chord=chord>100,route_note='Polyline via Wing south inner corner and south edge; requires cable space and bend/Z verification, not actual harness envelope'))
  wingchecks.append(dict(pitch_mm=int(pitch),side=side,pcb_gap_mm=dist,main_south_switch_inset_mm=w['south_switch_y_mm']-base,wing_south_pcb_beyond_switch_mm=w['south_pcb_y_mm']-w['south_switch_y_mm']))
# UDB placement is parametric because case/USB opening has no frozen datum.
assert {a.GetNumber():a.GetNetname() for a in uf.Pads() if a.GetNumber()}=={'1':'VCC','2':'DA-','3':'DA+','4':'GND'}
udb_bounds=box(-9,-36.25,9,-19.75)
udb_gaps=[dict(pitch_mm=int(pitch),side=side,gap_mm=udb_bounds.distance(Polygon(w['outline_xy_mm']))) for pitch,sides in wing.items() for side,w in sides.items()]
assert all(q['gap_mm']>0 for q in udb_gaps)
udb=dict(status='conditional_case_datum_proposal',connector_J2_xy_mm=[0,-20],pcb_bbox_xy_mm=list(udb_bounds.bounds),wing_gaps=udb_gaps,main_J4_xy_mm=placements['J4']['at_mm'],chord_mm=math.dist([0,-20],placements['J4']['at_mm']),planning_extra_mm=30,proposed_cable_mm=100,main_exit_unit_xy=[0,-1],pin_contract={'1':'VBUS','2':'USB_DM_ESD (D-)','3':'USB_DP_ESD (D+)','4':'GND'},cable='1:1 JST SH 4way; SHR-04V-S housing, SSH-003T-P0.2 terminal candidate; verify supplier drawing')
for r,v in placements.items():
 v['source_native']=native[r]
 v['pads']=[dict(number=a.GetNumber(),source_net=a.GetNetname(),proposed_net=(dict(placements['J4']['pad_nets']).get(a.GetNumber()) if r=='J4' else a.GetNetname()),xy_mm=xy(a.GetPosition()),copper_polygons_xy_mm=[coords(g) for g in (list(padpoly(a).geoms) if hasattr(padpoly(a),'geoms') else [padpoly(a)])]) for a in fps[r].Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
inputs={str(f.relative_to(R)):sha(f) for f in sorted((E/'inputs').rglob('*')) if f.is_file()};inputs[str(SOURCE.relative_to(R))]=sha(SOURCE)
plan=dict(schema='issue196-phase-a2-v1',status='proposal_pending_PMO_review',phase='A-2',units='mm',frame='assembly top view X right Y south; KiCad angle degrees; PCB mapping X=100+x,Y=70+y',parameters=dict(wing_axis_angle_deg=120,wing_rotation_left_ccw_deg=-30,wing_rotation_right_ccw_deg=30,wing_north_inner_corner_gap_mm=gap,main_wing_normal_clearance_mm=clearance,base_y_mm=base,case_switch_clearance_proposal_mm=.25),wing=wing,main=dict(outline_xy_mm=coords(outline),bounds_xy_mm=list(outline.bounds),size_mm=[2*half,base-apex],area_mm2=outline.area,bbox_area_mm2=2*half*(base-apex),old_size_mm=[48,52],old_area_mm2=2496,removed_refs=sorted(removed),retained_refs=sorted(retained),placements=[placements[r] for r in sorted(placements)],holes=holechecks),harness=harness,udb=udb,package_body_assumptions_mm=bodyassumptions,phase_b_routing_authorized=False,inputs_sha256=inputs,input_commits={'Wing_PR195':'f9084be93faf3defdff3bb3b76e1db1edfe49976','UDB_C3':'2ecdd7e0482ecbd3ffe9af04966ab3555f7fc33c'})
save('geometry-plan.json',plan)
checks=dict(kicad_version=p.Version(),retained_count=len(retained),new_connector_count=1,new_hole_count=3,total_footprints=len(placements)+3,removed_count=len(removed),all_retained_pad_nets_unchanged=True,body_envelope_pair_checks=pairchecks,edge_checks=edgechecks,wing_checks=wingchecks,packing_adjustments=moves,source_sha256_after=sha(SOURCE),no_board_saved=True,no_router_started=True,no_zone_refill=True)
save('verification.json',checks)
with (E/'placements.csv').open('w') as f:
 wr=csv.writer(f,lineterminator='\n');wr.writerow(['ref','x_mm','y_mm','kicad_angle_deg','side','value'])
 for r in sorted(placements):
  v=placements[r];wr.writerow([r,*v['at_mm'],v['angle_deg'],'F.Cu',v['value']])
# CAD-native explanatory SVG. No manufacturing board or copper output.
def polygon(g,fill,stroke,width=.2): return f'<polygon points="{" ".join(f"{x:.5f},{y:.5f}" for x,y in coords(g))}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-180 -65 360 150" width="1440" height="600">','<rect x="-180" y="-65" width="360" height="150" fill="white"/>']
for side,w in wing['16'].items():
 svg.append(polygon(Polygon(w['outline_xy_mm']),'#edf1f6','#607080'))
 for k in w['keys']:svg.append(polygon(Polygon(k['envelope_xy_mm']),'#dae2eb','#9aa9b9',.1))
 x,y=w['J1_xy_mm'];svg.append(f'<circle cx="{x}" cy="{y}" r="2" fill="#c77229"/>')
 route=next(h['planning_route_xy_mm'] for h in harness if h['pitch_mm']==16 and h['side']==side)
 svg.append(f'<polyline points="{" ".join(f"{xx},{yy}" for xx,yy in route)}" fill="none" stroke="#c77229" stroke-dasharray="1 1" stroke-width=".4"/>')
svg.append(polygon(udb_bounds,'#e7ddf3','#705090',.3))
svg.append(polygon(outline,'#e4f3e9','#246540',.4))
for r,g in envs.items():
 svg.append(polygon(g,'#7da4cb' if r.startswith('J') else '#bfd8c1','#365843',.1));x,y=placements[r]['at_mm'];svg.append(f'<text x="{x}" y="{y}" font-size="1.5" text-anchor="middle">{r}</text>')
for r,pt in holes.items():
 x,y=pt;svg.extend([f'<circle cx="{x}" cy="{y}" r="2.5002" fill="none" stroke="#c77229" stroke-width=".15"/>',f'<circle cx="{x}" cy="{y}" r="1.1" fill="white" stroke="#555" stroke-width=".15"/>'])
svg.extend(['<text x="-170" y="80" font-size="3">Phase A-2: 16mm / 120 deg / proposal only; dashed lines are planning routes</text>','</svg>'])
(E/'assembly-proposal.svg').write_text('\n'.join(svg)+'\n')
svg2=[svg[0].replace('viewBox="-180 -65 360 150" width="1440" height="600"','viewBox="-42 0 84 73" width="840" height="730"')]+svg[1:]
(E/'main-placement.svg').write_text('\n'.join(svg2)+'\n')
print(json.dumps(dict(size_mm=plan['main']['size_mm'],area_mm2=outline.area,base_y=base,apex_y=apex,count=len(placements),min_envelope_gap_mm=min(q['gap_mm'] for q in pairchecks),wing=wingchecks,harness=harness,moves=moves),ensure_ascii=False,indent=2))
