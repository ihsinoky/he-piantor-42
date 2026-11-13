"""Build both E-R full-cover Wing decks over the D-037 silhouette; package only."""
from geometry import *
import argparse,shutil

def run(pitch):
 out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True);manufacture=out/'plate-package';manufacture.mkdir(exist_ok=True)
 d=json.loads((BASE/f'{pitch}mm/dimensions.json').read_text())
 od=json.loads((BASE/f'{pitch}mm/outline-check.json').read_text());outer=Polygon(od['outer_xy_mm']);cavity=Polygon(od['cavity_xy_mm'])
 from native_curves import configure
 old=json.loads((HERE.parent/f'issue-198-final/{pitch}mm/dimensions.json').read_text());configure({k:Polygon(v) for k,v in old['boards'].items()})
 # Keep the central electronics/service bay, never cut a notch at a Wing GH.
 service=unary_union([Polygon(d['boards']['main']).buffer(2,join_style=2),Polygon([(-12,-100),(12,-100),(12,-18),(0,0),(-12,-18)])])
 decks={side:max(polygons(outer.intersection(box(-300,-200,0,200) if side=='left' else box(0,-200,300,200)).difference(service)),key=lambda g:g.area) for side in ('left','right')}
 # 1.00mm rim; 0.20mm seam; broad original shelf supports whole shelf at Z14.7.
 rim=outer.difference(outer.buffer(-1.0,join_style=2)).simplify(.003,preserve_topology=True)
 # Do not bridge, narrow, or raise the approved Fly opening/seat.
 flybay=box(-13,-100,13,-39)
 ring=outer.difference(cavity).difference(flybay).simplify(.003,preserve_topology=True)
 rim=rim.difference(flybay)
 source_items=leaves(import_step(BASE/f'{pitch}mm/assembly.step'))
 items={};source_fly=[]
 for n,s in source_items:
  if n.startswith(('tray-','GH-','Wing-GH-','washer-wing_','screw-wing_')):continue
  if n.startswith('Fly-official-'):source_fly.append((n,s));continue
  items[n]=s
 printable={};plate_data=[];post_data=[];cap_data=[];routes=[]
 # Original daughterboard geometry including defective USB shell is untouched.
 for i,(n,s) in enumerate(source_fly):items[n+f'-instance-{i}']=s
 # Fit in source frame, with the published shaft/collar and a compliant split peg.
 post=cylinder(0,0,1.5,2.5,7.5).fuse(cylinder(0,0,2.25,2,.5)).fuse(cylinder(0,0,1.575,1.2,.8))
 slot=prism(box(-.3,-2,.3,2),1.19,.91)
 post=post.cut(slot)
 export(post,HERE/'support-post',True)
 for side,sgn in [('left',-1),('right',1)]:
  print(pitch,side,'case and deck',flush=True)
  from routing import route
  routed,fanout,channel,route_data=route(side,sgn)
  clip=box(-300,-200,3.5,200) if side=='left' else box(3.5,-200,300,200)
  original=import_step(BASE/f'{pitch}mm/tray-{side}.step')
  from receiver import make
  tray=make(original,outer,cavity,decks[side],clip,flybay,d,pitch,side,channel)
  blank=decks[side].buffer(-1.2,join_style=2).simplify(.003,preserve_topology=True)
  blank=max(polygons(blank),key=lambda g:g.area)
  # Plate holes come only from the #230 key/tie CSVs, independently per hand/pitch.
  t=d['wing_transforms'][side];apertures=[];cutouts=rows(STUDY/f'{pitch}mm-{side}/cutouts.csv')
  for r in cutouts:
   g=transform(local_round_square(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg'])),t);apertures.append(g)
   cap=transform(rect_key(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg']),17),t)
   # Acceptance envelope, not a purchased keycap profile. Retain every datum.
   cap_data.append(dict(key=r['key'],skirt_lower_bound_z_mm=16.6,clearance_mm=.4,status='REQUIRED ACCEPTANCE ENVELOPE; actual cap not supplied'))
   capshape=prism(cap,16.6,8.6).cut(prism(transform(rect_key(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg']),16.2),t),16.59,6))
   items['cap-gauge-'+r['key']]=capshape
   # Housing occupancy is stepped around its clip seating plane; an envelope.
   lower=transform(rect_key(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg']),15.8),t)
   neck=transform(local_round_square(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg']),13.98,.2),t)
   items['switch-envelope-'+r['key']]=prism(lower,11.2,3.5).fuse(prism(neck,14.7,1.5)).fuse(prism(lower,16.2,2))
  tie_rows=rows(STUDY/f'{pitch}mm-{side}/tie-holes.csv')
  tie_shapes=[]
  for r in tie_rows:
   x,y=float(r['assembly_x_mm']),float(r['assembly_y_mm']);tie_shapes.append(Point(x,y).buffer(1.1,quad_segs=32))
   spacer=cylinder(x,y,1.9,11.2,3.5).cut(cylinder(x,y,1.1,11.2,3.5));items[f'POM-{side}-{r["id"]}']=spacer
   # M2x12 E-R screw + 0.3 nylon washer, original 4 sites, outside palm shelf.
   washer=cylinder(x,y,1.9,16.2,.3).cut(cylinder(x,y,1.1,16.2,.3))
   screw=cylinder(x,y,.8,4.5,12).fuse(cylinder(x,y,1.7,16.5,1.3))
   items[f'plate-washer-{side}-{r["id"]}']=washer;items[f'plate-screw-{side}-{r["id"]}']=screw
  plate_polygon=blank.difference(unary_union(apertures+tie_shapes))
  plate=prism(plate_polygon,14.7,1.5)
  # Underside C0.20 aperture lead-in: loft opening14.42 at bottom to14.02 atZ14.90.
  for r,g in zip(cutouts,apertures):
   bottom=transform(local_round_square(float(r['x_mm']),float(r['y_mm']),float(r['rotation_ccw_deg']),14.42,.4),t)
   w0=Wire.make_polygon([Vector(x,y,14.7) for x,y in list(bottom.exterior.coords)[:-1]],close=True)
   w1=Wire.make_polygon([Vector(x,y,14.9) for x,y in list(g.exterior.coords)[:-1]],close=True)
   plate=plate.cut(Solid.make_loft([w0,w1]))
  assert len(plate.solids())==1 and plate.is_valid
  export(plate,manufacture/f'plate-{side}')
  dxf(manufacture/f'plate-{side}.dxf',plate_polygon)
  save(manufacture/f'plate-{side}.geojson',mapping(plate_polygon))
  shutil.copy2(STUDY/f'{pitch}mm-{side}/cutouts.csv',manufacture/f'apertures-{side}-local.csv')
  shutil.copy2(STUDY/f'{pitch}mm-{side}/tie-holes.csv',manufacture/f'ties-{side}.csv')
  items['plate-'+side]=plate
  for r in rows(STUDY/f'{pitch}mm-{side}/supports.csv'):
   x,y=float(r['assembly_x_mm']),float(r['assembly_y_mm'])
   tray=tray.cut(cylinder(x,y,1.55,1.2,.8))
   # Assembly depicts the compliant free-state peg compressed to socket ID.
   installed=cylinder(x,y,1.5,2.5,7.5).fuse(cylinder(x,y,2.25,2,.5)).fuse(cylinder(x,y,1.55,1.2,.8)).cut(prism(box(x-.3,y-2,x+.3,y+2),1.19,.91))
   items[f'post-{side}-{r["id"]}']=installed
   post_data.append(dict(side=side,id=r['id'],xy_mm=[x,y],socket_diameter_mm=3.1,socket_depth_mm=.8,floor_remaining_mm=1.2,top_z_mm=10.,pcb_gap_mm=0.,free_peg_diameter_mm=3.15,assembly_peg_diameter_mm=3.10))
  assert tray.is_valid and len(tray.solids())==1,('tray',pitch,side,len(tray.solids()))
  printable['tray-'+side]=tray;items['tray-'+side]=tray
  shelf=blank.difference(Polygon(d['boards']['wing_'+side]).buffer(.502,join_style=2)).difference(flybay)
  plate_data.append(dict(side=side,blank_outline_xy_mm=coords(blank),deck_outline_xy_mm=coords(decks[side]),apertures=len(apertures),tie_holes=len(tie_rows),plate_area_mm2=plate_polygon.area,palm_nominal_step_mm=0.,rim_seam_nominal_mm=.2,shelf_full_backing_area_mm2=shelf.area,additional_shelf_fasteners=0,reason='Solid existing shelf raised to underside datum; no unsupported shelf cantilever. Four existing ties retain plate against uplift.'))
  print(pitch,side,'connector and harness',flush=True)
  # Fresh D-039 underside service-body reservations.
  spec=json.loads((REV4/f'wing-rev4-{pitch}mm-{side}/definition.json').read_text())
  for c in spec['components']:
   kind=c['kind'];ref=c['reference']
   if kind=='testpoint':continue
   if ref=='J_WING':g=box(sgn*27-10.875,-43.1,sgn*27+10.875,-34.95);height=4.85
   else:
    w,h,height=(3.4,3.4,3.4) if kind=='hall' else (5.1,6.6,1.4) if kind=='mux' else (2.4,1.6,1.)
    from shapely.affinity import rotate,translate
    g=transform(translate(rotate(box(-w/2,-h/2,w/2,h/2),c['rotation_ccw_deg']),c['x_mm'],c['y_mm']),t)
   items[f'underside-{side}-{ref}']=prism(g,10-height,height)
  items['GH-bundle-'+side]=routed;items['GH-fanout-'+side]=fanout
  export(Compound(children=[routed,fanout]),out/f'harness-{side}-160mm')
  routes.append(route_data)
 for name in ('splice-1','splice-2','cable-rack'):
  items[name]=import_step(BASE/f'{pitch}mm/{name}.step');printable[name]=items[name]
 printable['support-post']=post
 for name,s in printable.items():
  if name=='support-post':continue
  export(s,out/name,True)
 save(out/'cap-skirt-gauges.json',cap_data)
 save(out/'plate-package/geometry.json',plate_data)
 from dress_fly import dressed
 items['EZmate-170mm-route'],fly_dressing=dressed(d)
 export_step(items['EZmate-170mm-route'],out/'fly-harness-170mm.step')
 # Keep names across STEP reimport, including intentionally defective official Fly shell.
 for name,s in items.items():s.label=name
 export_step(Compound(children=list(items.values())),out/'assembly.step')
 for h in d['mounts']:
  if h['board'].startswith('wing_'):h.update(screw='M2x12 polymer-compatible thread-forming',washer_thickness=.3,spacer_height_mm=3.5,seat_z_mm=16.2,engagement_mm=5.5)
 save(out/'dimensions.json',dict(schema='issue232-v1',pitch_mm=pitch,fly_dressing=fly_dressing,source_baseline='D-037 / issue-228-final',plate_bottom_z_mm=14.7,plate_top_z_mm=16.2,rim_top_z_mm=16.2,plate_thickness_mm=1.5,plates=plate_data,posts=post_data,routes=routes,wing_transforms=d['wing_transforms'],mounts=d['mounts'],fixed_point_count=13,fasteners=dict(pcb_sites=13,wing_stack_M2x12=8,main_and_Fly_M2x6=5,splice_M2x8=4,total_screws=17,additional_shelf_fasteners=0),printing=[dict(name=n,filename=('support-post' if n=='support-post' else f'{pitch}mm/{n}'),size_mm=[s.bounding_box().size.X,s.bounding_box().size.Y,s.bounding_box().size.Z],brim_xy_mm=[s.bounding_box().size.X+10,s.bounding_box().size.Y+10]) for n,s in printable.items()],assembly_leaf_count=sum(len(s.solids()) for s in items.values()),acceptance_envelopes=True,central_service_bay_open=True))
 save(out/'inputs-sha256.json',{str(p.relative_to(ROOT)):sha(p) for p in sorted(set([BASE/f'{pitch}mm/assembly.step',*[BASE/f'{pitch}mm/tray-{side}.step' for side in ('left','right')],REV4/'main-native-obstacles.json',*[REV4/f'wing-rev4-{pitch}mm-{side}/main.kicad_pcb' for side in ('left','right')],BASE/f'{pitch}mm/outline-check.json',BASE/f'{pitch}mm/dimensions.json',*[REV4/f'case/{pitch}mm/tray-{side}-channel-candidate.step' for side in ('left','right')],*[STUDY/f'{pitch}mm-{side}/{n}.csv' for side in ('left','right') for n in ('cutouts','tie-holes','supports')],*[REV4/f'wing-rev4-{pitch}mm-{side}/definition.json' for side in ('left','right')]]))})
 print(pitch,'exports complete',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--pitch',type=int,choices=(16,17),required=True);run(p.parse_args().pitch)
