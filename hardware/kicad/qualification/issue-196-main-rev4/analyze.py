"""Phase A read-only geometry study. Never saves/routes/refills a KiCad board."""
from pathlib import Path
import hashlib, json, math, itertools
import pcbnew as p
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
E = Path(__file__).resolve().parent
R = E.parents[3]
SOURCE = 'hardware/kicad/qualification/issue-185-main-rev3/inspection/final/main.kicad_pcb'
PROJECT = 'hardware/kicad/qualification/issue-175-main-dual-wing-final2/inputs/final/main.kicad_pro'
SQ = math.sqrt(2)
CORNERS = {'NW': (1,1,-146), 'NE': (-1,1,54), 'SW': (1,-1,46), 'SE': (-1,-1,246)}
CUTS = {'NW':5,'NE':5,'SW':6,'SE':6}
MOVES = {'J3':[100,73], 'J2':[100,116], 'L1':[85.5,77.3], 'C26':[100.5,84.3], 'TP2':[85,118], 'H3':[81.122,116.878]}
ORIGINAL_HOLES = {'H1':[79,92], 'H2':[121,81], 'H3':[79,119], 'H4':[102,111.5]}
VERTICES = [[81,70],[119,70],[124,75],[124,116],[118,122],[82,122],[76,116],[76,75]]
def save(name,data): (E/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(path): return hashlib.sha256((R/path).read_bytes()).hexdigest()
def xy(v): return [v.x/1e6,v.y/1e6]
def native_polygons(ps):
 def ring(line): return [xy(line.CPoint(i)) for i in range(line.PointCount())]
 return unary_union([Polygon(ring(ps.Outline(i)),[ring(ps.Hole(i,j)) for j in range(ps.HoleCount(i))]) for i in range(ps.OutlineCount())])
def pad_geom(a):
 ps=p.SHAPE_POLY_SET(); a.TransformShapeToPolygon(ps,p.F_Cu,0,10,p.ERROR_OUTSIDE)
 return native_polygons(ps)
def inventory(board):
 out={}
 for f in board.GetFootprints():
  out[f.GetReference()]={'at_mm':xy(f.GetPosition()),'angle_deg':f.GetOrientationDegrees(),'value':f.GetValue(),'pad_nets':sorted([[a.GetNumber(),a.GetNetname()] for a in f.Pads()])}
 return out
assert sha(SOURCE)=='0e81ba42b194e03fb0422b58a64c967fe83166d0495d84f28c4171184b665bae'
b=p.LoadBoard(str(R/SOURCE)); assert b
before=inventory(b)
assert len(before)==66
assert before['J3']['at_mm']==[105,73] and before['J2']['at_mm']==[110,116]
assert before['J1']['at_mm']==[85,81]
# Requirements refer to connector body-centre Y, not native footprint/pin-row Y.
for f in b.GetFootprints():
 if f.GetReference() in MOVES:
  v=MOVES[f.GetReference()]; f.SetPosition(p.VECTOR2I(round(v[0]*1e6),round(v[1]*1e6)))
after=inventory(b)
assert all(before[r]['pad_nets']==after[r]['pad_nets'] and before[r]['angle_deg']==after[r]['angle_deg'] and before[r]['value']==after[r]['value'] for r in before)
assert after['J1']==before['J1']
pads=[]
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetAttribute()==p.PAD_ATTRIB_NPTH: continue
  pads.append({'ref':f.GetReference(),'pad':a.GetNumber(),'net':a.GetNetname(),'geom':pad_geom(a)})
byref={r:unary_union([a['geom'] for a in pads if a['ref']==r]) for r in after if not r.startswith('H')}
# A conservative support function; native curved-pad polygons are ERROR_OUTSIDE (10nm).
def support(g,sx,sy,c):
 geoms=list(g.geoms) if hasattr(g,'geoms') else [g]
 return min(sx*x+sy*y+c for q in geoms for x,y in q.exterior.coords)
poly=Polygon(VERTICES); assert poly.is_valid and poly.area==2435 and poly.bounds==(76,70,124,122)
assert set(map(tuple,VERTICES))==set((200-x,y) for x,y in VERTICES)
project=json.loads((R/PROJECT).read_text()); edge=project['board']['design_settings']['rules']['min_copper_edge_clearance'];assert edge==.2
# Before secondary placement changes, find actual collisions from connector moves alone.
base=p.LoadBoard(str(R/SOURCE))
for f in base.GetFootprints():
 if f.GetReference() in ('J2','J3'): f.SetPosition(p.VECTOR2I(100000000,f.GetPosition().y))
basepads=[(f.GetReference(),a.GetNumber(),pad_geom(a)) for f in base.GetFootprints() for a in f.Pads() if a.GetAttribute()!=p.PAD_ATTRIB_NPTH]
collisions=[]
for ref in ('J2','J3'):
 g=unary_union([g for r,_,g in basepads if r==ref])
 for r,n,h in basepads:
  if r!=ref and g.distance(h)<.1:
   collisions.append(dict(connector=ref,ref=r,pad=n,gap_mm=g.distance(h),overlap_mm2=g.intersection(h).area))
# Unchanged routing inventory: identify work only, never modify copper.
tracks=[]
for t in b.GetTracks():
 via=isinstance(t,p.PCB_VIA)
 g=Point(xy(t.GetPosition())).buffer(t.GetWidth(p.F_Cu)/2e6,quad_segs=256) if via else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(t.GetWidth()/2e6,quad_segs=256)
 tracks.append(dict(uuid=t.m_Uuid.AsString(),kind='via' if via else 'segment',net=t.GetNetname(),layer='all_Cu' if via else b.GetLayerName(t.GetLayer()),geom=g))
corner_limits={}
for corner,(sx,sy,c) in CORNERS.items():
 a=sorted([(support(q['geom'],sx,sy,c)-SQ*edge,q['ref']+'.'+q['pad']) for q in pads])
 h=sorted([(sx*x+sy*y+c-SQ*3,r) for r,(x,y) in ORIGINAL_HOLES.items()])
 routes=sorted([(support(q['geom'],sx,sy,c)-SQ*edge,q['uuid'],q['net']) for q in tracks])
 hn=sorted([(sx*v['at_mm'][0]+sy*v['at_mm'][1]+c-SQ*3,r) for r,v in after.items() if r.startswith('H')])
 corner_limits[corner]=dict(fixed_pad_max_mm=a[0][0],limiting_pad=a[0][1],original_hole_max_mm=h[0][0],limiting_original_hole=h[0][1],proposed_hole_max_mm=hn[0][0],limiting_proposed_hole=hn[0][1],unchanged_trace_via_max_mm=routes[0][0],limiting_legacy_route=routes[0][1:],maximum_original_holes_mm=min(a[0][0],h[0][0]),maximum_proposed_holes_mm=min(a[0][0],hn[0][0]),recommended_cut_mm=CUTS[corner],closest_pads=[dict(max_mm=v,ref=r) for v,r in a[:5]])
# All moved non-hole copper pads must clear other parts by 0.10; preserve 0.20 edge.
placement_checks=[]
for ref in MOVES:
 if ref.startswith('H'): continue
 g=byref[ref]
 d,r=min((g.distance(h),r) for r,h in byref.items() if r!=ref)
 edgegap=poly.boundary.distance(g) if poly.covers(g) else -1
 placement_checks.append(dict(ref=ref,nearest_other_part=r,pad_gap_mm=d,edge_gap_mm=edgegap))
 assert d>=.1-1e-9 and edgegap>=edge
assert all(poly.covers(g) and poly.boundary.distance(g)>=edge-1e-9 for g in byref.values())
# All-layer reservations are a future layout contract, not a fabricated claim about old fills.
holes=[]
for ref,old in ORIGINAL_HOLES.items():
 new=after[ref]['at_mm'];pt=Point(new)
 reservation=Polygon([(new[0]+2.5002*math.cos(2*math.pi*i/256),new[1]+2.5002*math.sin(2*math.pi*i/256)) for i in range(256)])
 padgap,r=min((pt.distance(q['geom'])-2.25,q['ref']+'.'+q['pad']) for q in pads)
 edgegap=poly.boundary.distance(pt)-2.25
 assert poly.covers(reservation) and edgegap>=.75 and padgap>=.25
 hitroutes=[{k:v for k,v in t.items() if k!='geom'} for t in tracks if reservation.intersects(t['geom'])]
 fill=[]
 for layer in b.GetEnabledLayers().CuStack():
  gs=[]
  for z in b.Zones():
   if not z.GetIsRuleArea() and z.IsOnLayer(layer):
    g=native_polygons(z.GetFilledPolysList(layer))
    if not g.is_empty:gs.append(g)
  if gs:
   g=unary_union(gs);fill.append(dict(layer=b.GetLayerName(layer),legacy_boss_to_fill_mm=pt.distance(g)-2.25,overlap_reservation_mm2=g.intersection(reservation).area))
 holes.append(dict(ref=ref,old_xy_mm=old,xy_mm=new,delta_xy_mm=[new[i]-old[i] for i in range(2)],move_mm=math.dist(old,new),npth_diameter_mm=2.2,boss_diameter_max_mm=4.5,reservation_diameter_nominal_mm=5.0,reservation_polygon_xy_mm=[[x,y] for x,y in list(reservation.exterior.coords)[:-1]],layers=['F.Cu','In1.Cu','In2.Cu','B.Cu'],prohibit=['tracks','vias','copperpour'],boss_to_outline_mm=edgegap,boss_to_nearest_pad_mm=padgap,nearest_pad=r,reservation_min_inradius_mm=2.5002*math.cos(math.pi/256),guaranteed_boss_to_future_copper_mm=2.5002*math.cos(math.pi/256)-2.25,legacy_routes_needing_removal_or_relocation=hitroutes,legacy_fill_check=fill))
# Search a witness only: maximum pad-limited southern cut with H3 free to move.
# Constrains all other proposed hole positions; 0.05mm grid, exact geometry checks.
southmax=min(corner_limits[c]['fixed_pad_max_mm'] for c in ['SW','SE'])
maxpoly=Polygon([[81,70],[119,70],[124,75],[124,122-southmax],[124-southmax,122],[76+southmax,122],[76,122-southmax],[76,75]])
witness=[]
for ix in range(1580,1781):
 x=ix*.05
 for iy in range(2100,2381):
  y=iy*.05;pt=Point(x,y)
  if not maxpoly.covers(pt) or maxpoly.boundary.distance(pt)<3:continue
  if any(pt.distance(g)<2.5002 for g in byref.values()):continue
  if any(math.dist([x,y],h['xy_mm'])<5.0004 for h in holes if h['ref']!='H3'):continue
  witness.append((math.dist([x,y],ORIGINAL_HOLES['H3']),x,y))
assert witness
w=min(witness)
# Source routing intersections with connector sweep, and removed corners.
regions={'J3_sweep':[89.525,72.15,115.475,77.75],'J2_sweep':[89.525,115.15,120.475,120.75],'northwest_power_cluster':[77,70,103,86],'TP_row':[84,117.4,97.6,118.6]}
impacts={name:[{k:v for k,v in q.items() if k!='geom'} for q in tracks if box(*bounds).buffer(.1).intersects(q['geom'])] for name,bounds in regions.items()}
edgehits=[{k:v for k,v in q.items() if k!='geom'} for q in tracks if not poly.covers(q['geom'].buffer(edge))]
plan=dict(schema='issue-196-phase-a-v1',phase='A',status='proposal_pending_PMO_review',units='mm',frame='KiCad absolute, top view, X right Y down',source_board=SOURCE,source_sha256=sha(SOURCE),source_commit='0f6ea972d597c7620628a8c316eaa4e5b4818956',connector_center_datum={'offset_from_native_footprint_mm':[0,2.3],'J3':{'old_center_mm':[105,75.3],'center_mm':[100,75.3],'native_at_mm':[100,73],'angle_deg':0},'J2':{'old_center_mm':[110,118.3],'center_mm':[100,118.3],'native_at_mm':[100,116],'angle_deg':0}},outline={'vertices_xy_mm':VERTICES,'closed':True,'corner_leg_mm':CUTS,'old_bounds_xy_mm':[76,70,124,122],'bounds_xy_mm':list(poly.bounds),'old_area_mm2':2496,'area_mm2':poly.area,'area_delta_mm2':poly.area-2496,'copper_edge_keepout_mm':edge},footprints=[dict(ref=r,before=before[r],proposed=after[r],changed=before[r]!=after[r]) for r in sorted(after)],holes=holes,phase_b_routing_authorized=False)
save('geometry-plan.json',plan)
analysis=dict(source_sha256=sha(SOURCE),project_sha256=sha(PROJECT),kicad_version=p.Version(),native_corner_limits=corner_limits,connector_only_collisions=collisions,proposed_moved_part_checks=placement_checks,all_fixed_pads_clear_outline=True,pad_net_value_angle_changes=0,footprint_count=66,changed_footprints=sorted(MOVES),source_segment_count=sum(q['kind']=='segment' for q in tracks),source_via_count=sum(q['kind']=='via' for q in tracks),routing_regions_xy_mm=regions,legacy_routing_impacts=impacts,legacy_routing_fails_new_edge_clearance=edgehits,southern_free_H3_maximum={'cut_mm':southmax,'limiter':min((corner_limits[c]['fixed_pad_max_mm'],corner_limits[c]['limiting_pad']) for c in ['SW','SE'])[1]+' / 0.20mm copper-edge clearance','feasible_H3_witness_xy_mm':[w[1],w[2]],'witness_move_mm':w[0],'search_note':'0.05mm grid witness, not continuous minimum move proof; other recommended footprints and holes fixed'},H3_minimum_for_south_6={'required_dx_plus_minus_dy_mm':6+3*SQ-6,'minimum_each_axis_mm':3/SQ,'theoretical_xy_mm':[79+3/SQ,119-3/SQ],'minimum_euclidean_move_mm':3,'selected_xy_mm':MOVES['H3']},no_board_saved=True,no_routing_or_refill_performed=True)
save('analysis.json',analysis)
# Compact review image, code-native SVG, no manufacture data.
svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="72 65 57 65" width="570" height="650">','<rect x="72" y="65" width="57" height="65" fill="white"/>','<path d="M76 70H124V122H76Z" fill="none" stroke="#aaa" stroke-width=".2" stroke-dasharray="1 1"/>',f'<polygon points="{" ".join(f"{x},{y}" for x,y in VERTICES)}" fill="#e7f2ed" stroke="#174d37" stroke-width=".25"/>']
for h in holes:
 x,y=h['xy_mm'];svg += [f'<circle cx="{x}" cy="{y}" r="2.5" fill="none" stroke="#c47824" stroke-width=".15"/>',f'<circle cx="{x}" cy="{y}" r="1.1" fill="white" stroke="#555" stroke-width=".1"/>',f'<text x="{x+1}" y="{y-1}" font-size="1.4">{h["ref"]}</text>']
for ref in ['J1','J2','J3','L1','C26','C23','TP2']:
 x0,y0,x1,y1=byref[ref].bounds;svg += [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="#6b94c9" fill-opacity=".5" stroke="#28558a" stroke-width=".1"/>',f'<text x="{x0}" y="{y0-.4}" font-size="1.3">{ref}</text>']
svg += ['<text x="77" y="126" font-size="1.7">Phase A proposal: N5 / S6 mm, 48 x 52 mm</text>','<text x="77" y="128.5" font-size="1.4">Pad bounds only; no routing or manufacturing release</text>','</svg>']
(E/'layout-proposal.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps({'corners':corner_limits,'placement':placement_checks,'holes':[{k:v for k,v in h.items() if k not in ['reservation_polygon_xy_mm','legacy_fill_check','legacy_routes_needing_removal_or_relocation']} for h in holes],'southern_max':analysis['southern_free_H3_maximum'],'edge_affected_routes':len(edgehits)},ensure_ascii=False,indent=2))
