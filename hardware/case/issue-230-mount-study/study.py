#!/usr/bin/env python3
"""Reproducible Issue 230 geometry / screening model; no production writes.
Dependencies: numpy, shapely, sexpdata. Run from repo root using runtime venv.
All drawing coordinates Wing local (X right, Y north); assembly transforms saved.
"""
import csv, hashlib, json, math
from pathlib import Path
import numpy as np
import sexpdata as sx
from shapely.geometry import Point, Polygon, LineString, box, mapping
from shapely.affinity import rotate, translate, affine_transform
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
CASE=ROOT/'hardware/case/issue-228-final'; PCB=ROOT/'hardware/kicad/qualification/issue-200-wing-rev3'
def save(p,x): p.write_text(json.dumps(x,indent=2)+'\n')
def rows(p):return list(csv.DictReader(p.open()))
def tag(n):return str(n[0]) if isinstance(n,list) and n else ''
def cs(n,t):return [x for x in n if tag(x)==t]
def c(n,t):return next(iter(cs(n,t)),None)
def xy(n):return float(n[1])-100,100-float(n[2])
def rect(x,y,a,w,h=None):return translate(rotate(box(-w/2,-(h or w)/2,w/2,(h or w)/2),a),x,y)
def data_csv(path,rs):
 with path.open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def audit_native(path):
 b=sx.loads(path.read_text());lands=[];drills=[];cu=[]
 for f in cs(b,'footprint'):
  at=c(f,'at');x,y=xy(at);a=float(at[3]) if len(at)>3 else 0
  ref=next((str(z[2]) for z in cs(f,'property') if str(z[1])=='Reference'),'?')
  for p in cs(f,'pad'):
   pa=c(p,'at');sz=c(p,'size');w,h=map(float,sz[1:3]);ang=float(pa[3]) if len(pa)>3 else a
   dx,dy=float(pa[1]),float(pa[2]);r=math.radians(a)
   px=x+dx*math.cos(r)+dy*math.sin(r);py=y+dx*math.sin(r)-dy*math.cos(r)
   g=Point(px,py).buffer(w/2,quad_segs=24) if str(p[3])=='circle' else rect(px,py,ang,w,h)
   if str(p[2])=='np_thru_hole':drills.append((ref,g))
   else:lands.append((ref,g));cu.append((ref,g))
 for s in cs(b,'segment'):cu.append(('track',LineString([xy(c(s,'start')),xy(c(s,'end'))]).buffer(float(c(s,'width')[1])/2)))
 for s in cs(b,'via'):
  g=Point(xy(c(s,'at'))).buffer(float(c(s,'size')[1])/2);cu.append(('via',g));lands.append(('via',g))
 # Filled zone polygons: count power planes as copper, including GND.
 for z in cs(b,'zone'):
  for fp in cs(z,'filled_polygon'):
   pts=c(fp,'pts')
   if pts:
    vs=[xy(v) for v in cs(pts,'xy')]
    if len(vs)>=3:cu.append(('zone',Polygon(vs).buffer(0)))
 return lands,drills,cu

def svg(path,plate,board,ks,holes,supports):
 # SVG Y inverted so local north points up; mm units, exact polygons.
 def d(g):
  rings=[g.exterior,*g.interiors]
  return ' '.join('M '+' L '.join(f'{x:.6f},{-y:.6f}' for x,y in r.coords)+' Z' for r in rings)
 x0,y0,x1,y1=board.bounds
 s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{x1-x0+10}mm" height="{y1-y0+10}mm" viewBox="{x0-5} {-y1-5} {x1-x0+10} {y1-y0+10}">',f'<path d="{d(board)}" fill="none" stroke="#777" stroke-width="0.15"/>',f'<path d="{d(plate)}" fill="#bcd6e8" fill-rule="evenodd" stroke="#123" stroke-width="0.12"/>']
 for k in ks:
  x,y=float(k['x_mm']),float(k['y_mm']);s.append(f'<text x="{x}" y="{-y}" font-size="2" text-anchor="middle">{k["key"]}</text>')
 for x,y in supports:s.append(f'<circle cx="{x}" cy="{-y}" r="1.5" fill="none" stroke="#d50" stroke-width="0.3"/>')
 s.append('</svg>');path.write_text('\n'.join(s))

def dxf(path,g):
 s=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','9','$MEASUREMENT','70','1','0','ENDSEC','0','SECTION','2','ENTITIES']
 for ring in [g.exterior,*g.interiors]:
  pts=list(ring.coords)[:-1];s+=['0','LWPOLYLINE','8','CUT','90',str(len(pts)),'70','1']
  for x,y in pts:s+=['10',f'{x:.6f}','20',f'{y:.6f}']
 s+=['0','ENDSEC','0','EOF'];path.write_text('\n'.join(s)+'\n')

def stats(v):return dict(min=float(min(v)),median=float(np.median(v)),max=float(max(v)),spread=float(max(v)-min(v)),std=float(np.std(v)))
summary=[];manifest={};allchecks=[]
for pitch in (17,16):
 for side in ('left','right'):
  name=f'{pitch}mm-{side}';out=OUT/name;out.mkdir(exist_ok=True)
  files=[CASE/'inputs/rev3-final'/f'{kind}-{name}.csv' for kind in ('keys','holes','outline')]
  ks=rows(files[0]);hr=rows(files[1]);board=Polygon([(float(r['x_mm']),float(r['y_mm'])) for r in rows(files[2])])
  old=np.array([(float(r['x_mm']),float(r['y_mm'])) for r in hr if r['kind']=='mounting'])
  keys=np.array([(float(k['x_mm']),float(k['y_mm'])) for k in ks])
  native=PCB/f'wing-rev3-{name}'/'main.kicad_pcb';definition=PCB/f'wing-rev3-{name}'/'definition.json'
  manifest.update({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*files,native,definition,CASE/f'{pitch}mm/dimensions.json']})
  lands,drills,cu=audit_native(native)
  spec=json.loads(definition.read_text());dims=json.loads((CASE/f'{pitch}mm/dimensions.json').read_text());tr=dims['wing_transforms'][side]
  m=tr['matrix'];t=tr['translation'];transform=[m[0][0],m[0][1],m[1][0],m[1][1],*t]
  bodies=[];top_bodies=[]
  for v in spec['components']:
   if v['kind']=='testpoint':continue
   x,y=v['x_mm'],v['y_mm'];a=v['rotation_ccw_deg'];kind=v['kind']
   if kind=='hall':g=rect(x,y,a,3.4,3.4)
   elif kind=='capacitor':g=rect(x,y,a,2.4,1.6)
   elif kind=='mux':g=rect(x,y,a,5.1,6.6)
   elif v['reference']=='J_WING':
    inv=np.linalg.inv(np.array(m));pts=[inv@(np.array(q)-t) for q in [( (-27 if side=='left' else 27)+dx,-41+dy) for dx,dy in [(-11,-1),(11,-1),(11,6),(-11,6)]]];g=Polygon(pts)
   else:g=rect(x,y,a,3,3)
   if v.get('side')=='bottom':bodies.append((v['reference'],g))
   else:top_bodies.append((v['reference'],g))
  obstacle=unary_union([g for _,g in lands+drills+bodies])
  candidates=[]
  for x in np.arange(math.ceil(board.bounds[0])+2,board.bounds[2]-2,1):
   for y in np.arange(math.ceil(board.bounds[1])+2,board.bounds[3]-2,1):
    p=Point(x,y)
    if board.covers(p.buffer(1.7)) and p.distance(obstacle)>=1.9 and min(np.linalg.norm(old-[x,y],axis=1))>4.5:candidates.append([x,y])
  cand=np.array(candidates);supp=old.tolist();available=list(range(len(cand)))
  # Add six pads minimizing largest key-to-nearest-support distance.
  for _ in range(6):
   ds=np.min(np.linalg.norm(keys[:,None,:]-np.array(supp)[None,:,:],axis=2),axis=1)
   scores=[]
   for i in available:
    v=np.minimum(ds,np.linalg.norm(keys-cand[i],axis=1));scores.append((max(v),sum(v**3),i))
   _,_,i=min(scores);supp.append(cand[i].tolist());available.remove(i)
  added=supp[4:];support_rows=[]
  for i,(x,y) in enumerate(added,1):
   support_rows.append(dict(id=f'R{i}',x_mm=x,y_mm=y,contact_diameter_mm=3,shaft_diameter_mm=3,top_z_mm=10.0,base_z_mm=2.0,land_drill_body_edge_gap_mm=Point(x,y).distance(obstacle)-1.5,assembly_x_mm=m[0][0]*x+m[0][1]*y+t[0],assembly_y_mm=m[1][0]*x+m[1][1]*y+t[1]))
  data_csv(out/'supports.csv',support_rows)
  # Plate follows existing pocket, no projecting tabs over flush shelf.
  plate=board.buffer(-.2,join_style=2)
  for k in ks:
   cut=rect(float(k['x_mm']),float(k['y_mm']),float(k['rotation_deg']),14.02)
   # Four R0.2 internal corners, size remains 14.02 across flats.
   cut=cut.buffer(-.2,join_style=2).buffer(.2,quad_segs=12)
   assert plate.covers(cut),(name,k['key']);plate=plate.difference(cut)
  for x,y in old:plate=plate.difference(Point(x,y).buffer(1.1,quad_segs=32))
  # Full-depth GH access: 0.5 around actual inherited mated body reservation.
  for ref,g in top_bodies:
   if ref=='J_WING':plate=plate.difference(g.buffer(.5,join_style=2))
  assert plate.geom_type=='Polygon' and plate.is_valid
  # Upper component bodies except GH fit below Z14.7, nominal gap3.5.
  svg(out/'plate.svg',plate,board,ks,old,added);dxf(out/'plate.dxf',plate)
  save(out/'plate.geojson',mapping(plate));data_csv(out/'cutouts.csv',[dict(key=k['key'],x_mm=k['x_mm'],y_mm=k['y_mm'],rotation_ccw_deg=k['rotation_deg'],width_mm=14.02,height_mm=14.02,corner_radius_mm=.2) for k in ks])
  data_csv(out/'tie-holes.csv',[dict(id=f'H{i+1}',x_mm=x,y_mm=y,plate_hole_diameter_mm=2.2,spacer_od_mm=3.8,spacer_id_mm=2.2,spacer_height_mm=3.5,assembly_x_mm=m[0][0]*x+m[0][1]*y+t[0],assembly_y_mm=m[1][0]*x+m[1][1]*y+t[1]) for i,(x,y) in enumerate(old)])
  # D candidates: screws need top housing clearance, electrical copper clearance incl fills.
  housings=unary_union([rect(float(k['x_mm']),float(k['y_mm']),float(k['rotation_deg']),15.8) for k in ks])
  cap=unary_union([rect(float(k['x_mm']),float(k['y_mm']),float(k['rotation_deg']),17) for k in ks])
  extra=[]
  for x,y in added:
   q=Point(x,y);intr=[label for label,g in cu if q.buffer(1.35).intersects(g)]
   extra.append(dict(x_mm=x,y_mm=y,housing_gap_for_dia3p8_head_mm=q.distance(housings)-1.9,copper_collision_count=len(intr),collision_types=sorted(set(intr)),status='reject' if intr or q.distance(housings)<1.9 else 'candidate'))
  save(out/'rev4-boss-screen.json',extra)
  # Existing holes for C enlarged to3mm: include original keepout, exclude original NPTH.
  tad_audit=[]
  for i,(x,y) in enumerate(old):
   intr=[label for label,g in cu if Point(x,y).buffer(1.75).intersects(g)]
   tad_audit.append(dict(id=f'T{i+1}',x_mm=x,y_mm=y,plate_tab_hole_mm=3.05,head_socket_diameter_mm=5.2,cap_gap_for_socket_od6p0_mm=Point(x,y).distance(cap)-3,copper_intrusions_3p5_drill=sorted(set(intr))))
  save(out/'tadpole-screen.json',tad_audit)
  # Two deliberately transparent stiffness limits, same effective strip width17.
  # No shear-transfer/sandwich benefit claimed between discrete ties.
  b=float(pitch);web=float(pitch-14);EIpcb=20000*b*1.2**3/12
  # PMMA E=3300 MPa: PLEXIGLAS GS/XT technical information, ISO 527.
  # Nominal short-term screening modulus; not a sheet-lot certificate.
  eis={'FR4':EIpcb+20000*web*1.5**3/12,'aluminium':EIpcb+69000*web*1.5**3/12,'POM':EIpcb+2800*web*1.5**3/12,'PC':EIpcb+2300*web*1.5**3/12,'PMMA':EIpcb+3300*web*1.5**3/12}
  # Give floating plates a fairer six-point layout too: use the whole
  # pocket, without a socket over any 17mm keycap or tall connector.
  float_cand=[];drill_cand=[]
  allcu=unary_union([g for label,g in cu if label!='zone']);topobs=unary_union([g for _,g in top_bodies])
  for x in np.arange(math.ceil(board.bounds[0])+4,board.bounds[2]-4,1):
   for y in np.arange(math.ceil(board.bounds[1])+4,board.bounds[3]-4,1):
    q=Point(x,y)
    if not board.covers(q.buffer(4)):continue
    if q.distance(cap)>=4.25 and q.distance(topobs)>=4.25 and min(np.linalg.norm(old-[x,y],axis=1))>5:float_cand.append([x,y])
    if q.distance(housings)>=2.1 and q.distance(allcu)>=1.35 and q.distance(obstacle)>=2.5 and min(np.linalg.norm(old-[x,y],axis=1))>5:drill_cand.append([x,y])
  def choose(points,n,start):
   selected=list(start)
   for _ in range(n):
    if not points:break
    def score(q):
     d=np.min(np.linalg.norm(keys[:,None,:]-np.array(selected+[q])[None,:,:],axis=2),axis=1)
     return max(d),sum(d**3),q[0],q[1]
    q=min(points,key=score);selected.append(q);points=[p for p in points if math.dist(p,q)>=8]
   return np.array(selected)
  floating6=choose(float_cand,6,[]);legalD=choose(drill_cand,4,old.tolist())
  pcbfloat=choose([q for q in float_cand if Point(q).distance(allcu)>=1.75],6,[])
  data_csv(out/'pcb-floating-rev4-candidates.csv',[dict(id=f'C{i+1}',x_mm=x,y_mm=y,hole_diameter_mm=3.05,local_plane_clearance_required=any(Point(x,y).buffer(2.5).intersects(g) for label,g in cu if label=='zone')) for i,(x,y) in enumerate(pcbfloat)])
  data_csv(out/'floating-six-point-candidates.csv',[dict(id=f'T{i+1}',x_mm=x,y_mm=y,plate_hole_diameter_mm=3.05,socket_od_mm=8,status='screened XY; bracket and retention not released') for i,(x,y) in enumerate(floating6)])
  data_csv(out/'rev4-legal-boss-candidates.csv',[dict(id=f'D{i+1}',x_mm=x,y_mm=y,hole_diameter_mm=2.2,keepout_diameter_mm=5,local_plane_clearance_required=any(Point(x,y).buffer(2.5).intersects(g) for label,g in cu if label=='zone')) for i,(x,y) in enumerate(legalD)])
  options={'baseline':(old,EIpcb),'A_ribs_plateless':(np.array(supp),EIpcb),'C_pcb_tadpole':(old,EIpcb),'D_added_bosses_plateless_ideal':(np.array(supp),EIpcb),'E_tray_ribs_al_plate':(np.array(supp),eis['aluminium']),'E_tray_al_plate_no_ribs':(old,eis['aluminium'])}
  options.update({f'B_plate_tadpole_{mat}':(old,ei) for mat,ei in eis.items()})
  # E floating+retained screw fallback: screws absent while floating => same as B.
  options['E_float_with_screw_fallback']=(floating6,eis['aluminium'])
  options['B_six_point_al_plate']=(floating6,eis['aluminium'])
  for mat,ei in eis.items():options[f'B_six_point_{mat}']=(floating6,ei)
  options['C_pcb_tadpole_rev4six']=(pcbfloat,EIpcb)
  options['D_legal_added_bosses_plateless']=(legalD,EIpcb)
  options['D_legal_added_bosses_al_plate']=(legalD,eis['aluminium'])
  # PMMA supplement: preserve all original options, add matching rigid layouts.
  options['E_tray_ribs_PMMA_plate']=(np.array(supp),eis['PMMA'])
  options['D_legal_added_bosses_PMMA_plate']=(legalD,eis['PMMA'])
  options['E_float_with_screw_fallback_PMMA']=(floating6,eis['PMMA'])
  per=[]
  for opt,(supports,ei) in options.items():
   dist=np.min(np.linalg.norm(keys[:,None,:]-supports[None,:,:],axis=2),axis=1)
   # Clamped strip of span2d midpoint: d^3/(24EI). Single-arm cantilever: d^3/(3EI).
   lo=dist**3/(24*ei);hi=dist**3/(3*ei)
   s=dict(variant=name,option=opt,EI_Nmm2=ei,distance_mm=stats(dist),bend_lower_mm=stats(lo),bend_upper_mm=stats(hi),keys_beyond40=int(sum(dist>40)))
   summary.append(s)
   for k,d,l,h in zip(ks,dist,lo,hi):per.append(dict(key=k['key'],option=opt,nearest_support_mm=d,bend_bracket_low_mm=l,bend_bracket_high_mm=h,load_N=1))
  data_csv(out/'per-key.csv',per)
  # Rigid plate on 4 equal bilateral springs: includes tilt; uplift preload required.
  float_rows=[]
  for layout,points in [('existing4',old),('screened6',floating6),('pcb_rev4six',pcbfloat)]:
   A=np.column_stack([np.ones(len(points)),points]);M=np.linalg.inv(A.T@A)
   H=np.column_stack([np.ones(len(keys)),keys]);compliance=np.einsum('ij,jk,ik->i',H,M,H)
   reactions=A@M@H.T
   for shore,k in [(50,3.0),(70,6.75),(80,11.5)]:
    for i,key in enumerate(ks):float_rows.append(dict(key=key['key'],layout=layout,shore_A=shore,pin_k_N_per_mm=k,sink_1N_mm=compliance[i]/k,sink_low_mm=compliance[i]/(2*k),sink_high_mm=compliance[i]/(.5*k),max_uplift_reaction_per_N=max(0,-min(reactions[:,i])),weight_1N_uniform_settle_mm=1/(len(points)*k)))
  data_csv(out/'floating.csv',float_rows)
  hull=Polygon(old).convex_hull
  outside=[k['key'] for k,pt in zip(ks,keys) if not hull.covers(Point(pt))]
  checks=dict(variant=name,keys=len(ks),mounts=len(old),supports_total=len(supp),plate_area_mm2=plate.area,plate_bounds_mm=plate.bounds,plate_within_original_pcb=True,plate_to_pocket_nominal_mm=.7,support_min_component_land_drill_gap_mm=min(r['land_drill_body_edge_gap_mm'] for r in support_rows),keys_outside_existing_support_hull=outside,pcb_rev4six_max_tadpole_compliance_factor=float(max(compliance)),pcb_rev4six_min_spring_reaction_per_N=float(reactions.min()),tadpole_socket_cap_min_gap_mm=min(x['cap_gap_for_socket_od6p0_mm'] for x in tad_audit),transform=tr,production_writes=False)
  allchecks.append(checks);save(out/'checks.json',checks)
save(OUT/'summary.json',summary);save(OUT/'checks.json',allchecks);save(OUT/'inputs-sha256.json',manifest)
print(json.dumps([s for s in summary if s['variant']=='17mm-left'],indent=2))
