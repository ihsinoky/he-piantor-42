"""Case overlay against unmodified Issue 228 STEP, plus E-R rescreen.
Requires build123d, numpy, shapely. Every proposed path is a diagnostic candidate;
positive collisions are retained, never interpreted as accepted routing.
"""
from pathlib import Path
import json,csv,math,hashlib
import numpy as np
from shapely.geometry import Point,Polygon,LineString,box,mapping,shape as geometry_shape
from shapely.affinity import rotate,translate,affine_transform
from shapely.ops import unary_union
from build123d import Face,Wire,Vector,Edge,Plane,Compound,extrude,sweep,import_step,export_step
E=Path(__file__).resolve().parent;ROOT=E.parents[3];CASE=ROOT/'hardware/case/issue-228-final';MOUNT=ROOT/'hardware/case/issue-230-mount-study';OUT=E/'case';OUT.mkdir(exist_ok=True)
def save(p,o):p.write_text(json.dumps(o,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def prism(g,z,h):
 outer=Wire.make_polygon([Vector(x,y,z) for x,y in list(g.exterior.coords)[:-1]],close=True)
 return extrude(Face(outer),amount=h,dir=(0,0,1))
def rect(c,w,h):return translate(rotate(box(-w/2,-h/2,w/2,h/2),c['rotation_ccw_deg']),c['x_mm'],c['y_mm'])
_vcache={}
def volume(a,b):
 key=(id(a),id(b))
 if key in _vcache:return _vcache[key][2]
 aa=a.bounding_box();bb=b.bounding_box()
 if any(getattr(aa.max,k)<getattr(bb.min,k)-1e-7 or getattr(bb.max,k)<getattr(aa.min,k)-1e-7 for k in ('X','Y','Z')):v=0.
 else:
  hit=a.intersect(b);v=sum(s.volume for s in hit) if hit else 0.
 _vcache[key]=(a,b,v);return v
def rounded(points,radius):
 pts=[np.array(p,float) for p in points];corners={}
 for i in range(1,len(pts)-1):
  u=(pts[i-1]-pts[i]);u/=np.linalg.norm(u);v=(pts[i+1]-pts[i]);v/=np.linalg.norm(v)
  theta=math.acos(np.clip(float(np.dot(u,v)),-1,1));d=radius/math.tan(theta/2)
  if not math.isfinite(d) or d<1e-8:continue
  center=pts[i]+(u+v)/np.linalg.norm(u+v)*radius/math.sin(theta/2)
  a=pts[i]+u*d;b=pts[i]+v*d;mid=center+(pts[i]-center)/np.linalg.norm(pts[i]-center)*radius
  corners[i]=(a,mid,b,d)
 for i in range(len(pts)-1):
  need=(corners[i][3] if i in corners else 0)+(corners[i+1][3] if i+1 in corners else 0)
  assert need<np.linalg.norm(pts[i+1]-pts[i])-1e-6,('insufficient straight for R5',i,need)
 edges=[];prev=pts[0]
 for i in range(1,len(pts)-1):
  if i not in corners:continue
  a,mid,b,d=corners[i];edges.append(Edge.make_line(Vector(*prev),Vector(*a)));edges.append(Edge.make_three_point_arc(Vector(*a),Vector(*mid),Vector(*b)));prev=b
 edges.append(Edge.make_line(Vector(*prev),Vector(*pts[-1])))
 return Wire(edges)
def tube(points,radius,bend=5):
 path=rounded(points,bend);d=np.array(points[1],float)-np.array(points[0],float);profile=Face(Wire.make_circle(radius,Plane(origin=Vector(*points[0]),z_dir=Vector(*map(float,d)))))
 shape=sweep(profile,path=path);assert shape.is_valid;return shape,path
manifest={};summ=[]
for pitch in (16,17):
 out=OUT/f'{pitch}mm';out.mkdir(exist_ok=True);source=CASE/f'{pitch}mm';dims=json.loads((source/'dimensions.json').read_text())
 files=[source/n for n in ('dimensions.json','tray-left.step','tray-right.step','splice-1.step','splice-2.step')]
 trays={n:import_step(source/f'{n}.step') for n in ('tray-left','tray-right','splice-1','splice-2')}
 for f in files:manifest[str(f.relative_to(ROOT))]=sha(f)
 # Native production case solids already include Main ribs, joining bosses,
 # floor, outer walls and palms; no redefinition of those obstacles here.
 fixed={**trays};postrows=[];bodies={};xybodies={};supportsolids={};channelxy={};models={}
 for n,vs in dims['boards'].items():
  if n!='fly':fixed['pcb-'+n]=prism(Polygon(vs),10,1.2)
 for c in dims['main_components']:fixed['Main-'+c['ref']]=prism(Polygon(c['xy']),11.2,c['height_mm'])
 manifest[str((E/'main-native-obstacles.json').relative_to(ROOT))]=sha(E/'main-native-obstacles.json')
 for c in json.loads((E/'main-native-obstacles.json').read_text()):
  n='Main-'+c['ref'];part=prism(geometry_shape(c['geometry']),11.2,c['height_mm']);fixed[n]=fixed[n].fuse(part) if n in fixed else part
 for hand in ('left','right'):
  ks=json.loads((E/f'wing-rev4-{pitch}mm-{hand}'/'definition.json').read_text())['keys'];tr=dims['wing_transforms'][hand];m=tr['matrix'];t=tr['translation'];af=[m[0][0],m[0][1],m[1][0],m[1][1],*t]
  for k in ks:
   g=affine_transform(rect(k,17,17),af);fixed[hand+'-cap-'+k['key']]=prism(g,11.2,14)

 for side,sgn in [('left',-1),('right',1)]:
  name=f'{pitch}mm-{side}';w=E/f'wing-rev4-{name}';spec=json.loads((w/'definition.json').read_text());tr=dims['wing_transforms'][side];m=tr['matrix'];t=tr['translation'];af=[m[0][0],m[0][1],m[1][0],m[1][1],*t]
  files=[w/'definition.json',w/'pad-obstacles.json',MOUNT/name/'supports.csv']
  pad_union=unary_union([geometry_shape(r['geometry']) for r in json.loads((w/'pad-obstacles.json').read_text())])
  for f in files:manifest[str(f.relative_to(ROOT))]=sha(f)
  for c in spec['components']:
   ref=c['reference'];kind=c['kind']
   if kind=='testpoint':continue
   if ref=='J_WING':g=box(sgn*27-10.875,-43.1,sgn*27+10.875,-34.95);height=4.85
   else:
    ww,hh,height=(3.4,3.4,3.4) if kind=='hall' else (5.1,6.6,1.4) if kind=='mux' else (2.4,1.6,1.0)
    g=affine_transform(rect(c,ww,hh),af)
   key=side+'-'+ref;xybodies[key]=g;bodies[key]=prism(g,10-height,height)
  # Trial floor channel: terminal failure is modeled separately below. Its
  # horizontal connector start is explicitly conditional on a different exit.
  # Main rise outside the NW/NE board slope; back over it to unchanged J2/J3.
  pts=[[sgn*27,-24,5],[sgn*7,-16,5],[sgn*7,-16,28.5],[sgn*15.5,43,28.5],[sgn*15.5,43,18.5]]
  shape,path=tube(pts,2.5)
  key='trial-GH-'+side;models[key]=shape;channelxy[side]=unary_union([LineString([(p[0],p[1]) for p in pts]).buffer(2.5),box(sgn*27-8.625,-35.95,sgn*27+8.625,-23.5)])
  export_step(shape,out/f'{key}.step')
  # Fourteen actual horizontal wire exits (1 mm OD) precede the gathered
  # 5 mm channel. Mated length 7.15 measured from rear body edge y=-42.6.
  # Axis depth 1.6 is a drawing-derived planning value, screened +/-0.5.
  wiremodels=[];wirelengths=[]
  for i in range(14):
   x=sgn*27+(i-6.5)*1.25
   wp=[[x,-35.45,8.4],[x,-31.5,8.4],pts[0],[sgn*14,-18.8,5]]
   wire,wirepath=tube(wp,.5)
   wiremodels.append(wire);wirelengths.append(wirepath.length+path.length-math.dist(pts[0],[sgn*14,-18.8,5]))
  exitshape=Compound(children=wiremodels);models['actual-exit-'+side]=exitshape
  export_step(exitshape,out/f'actual-GH-exit-{side}.step')
  shape=Compound(children=[shape,exitshape]);models[key]=shape
  collisions=[]
  for label,ob in {**fixed,**bodies}.items():
   # Deliberate terminal envelope is not a third-party obstacle.
   if label==side+'-J_WING':continue
   vol=volume(shape,ob)
   if vol>1e-6:collisions.append({'obstacle':label,'overlap_mm3':vol})
  exitcoll=[{'obstacle':n,'overlap_mm3':volume(exitshape,s)} for n,s in trays.items() if volume(exitshape,s)>1e-6]
  split=LineString([(p[0],p[1]) for p in pts]).intersection(LineString([(3.5,-200),(3.5,200)]))
  summ.append(dict(variant=name,gh_nominal_mated_height_mm=4.35,gh_tolerance_allowance_mm=.5,gh_reserved_bottom_z_mm=5.15,gh_reserved_floor_gap_mm=3.15,real_exit_y_mm=-35.45,real_exit_axis_z_mm=8.4,exit_axis_uncertainty_mm=.5,wire_od_mm=1.,gathered_od_mm=5.,bend_radius_mm=5.,trial_waypoints_mm=pts,trial_length_mm=max(wirelengths),conductor_lengths_mm=wirelengths,conductor_pin_numbers=list(range(14,0,-1)),trial_with_30mm_service_mm=max(wirelengths)+30,trial_200mm_excess_mm=200-max(wirelengths),trial_collisions=collisions,split_crossing_geojson=mapping(split),trial_is_connected_to_GH=True,passed=False))

  # Re-screen the original six E-R posts, including collar and channel.
  for row in csv.DictReader((MOUNT/name/'supports.csv').open()):
   x=float(row['assembly_x_mm']);y=float(row['assembly_y_mm']);post=Point(x,y).buffer(1.5);collar=Point(x,y).buffer(2.25)
   near=[(g.distance(post),k) for k,g in xybodies.items()];gap,nearest=min(near)
   cable_gap=post.distance(channelxy[side]);hits=[k for k,g in xybodies.items() if post.intersects(g)]
   # At top only shaft3; collar4.5 is low (Z2..3) and checked against cable.
   cable_hit=collar.intersects(channelxy[side]);pad_gap=post.distance(pad_union);move=bool(hits or cable_hit or pad_gap<.4)
   n=side+'-'+row['id'];s=prism(post,2.5,7.5).fuse(prism(collar,2,.5));supportsolids[n]=s
   postrows.append(dict(variant=name,post=row['id'],xy_mm=[x,y],body_edge_gap_mm=gap,pad_drill_edge_gap_mm=pad_gap,nearest_body=nearest,body_hits=hits,trial_channel_shaft_gap_mm=cable_gap,trial_channel_collar_hits=cable_hit,must_move_for_this_trial=move))
 # Include all posts in route collision checking; shaft and low collars.
 for row in summ[-2:]:
  shape=models['trial-GH-'+row['variant'].split('-')[-1]]
  own='Main-'+('J2' if row['variant'].endswith('left') else 'J3');row['trial_collisions']=[{'obstacle':n,'overlap_mm3':volume(shape,s)} for n,s in {**fixed,**bodies}.items() if n not in (own,row['variant'].split('-')[-1]+'-J_WING') and volume(shape,s)>1e-6]
  # Concrete study-only internal-wall opening: 0.5 radial assembly margin.
  # It does not fix the inverted GH exit. Floor-channel cutter bottoms at Z2.
  cutter,_=tube(row['trial_waypoints_mm'],3.)
  candidate=trays['tray-'+row['variant'].split('-')[-1]].cut(cutter)
  export_step(candidate,out/('tray-'+row['variant'].split('-')[-1]+'-channel-candidate.step'))
  row['wall_channel_candidate_valid']=candidate.is_valid
  row['wall_channel_candidate_solids']=len(candidate.solids())
  removed=trays['tray-'+row['variant'].split('-')[-1]].intersect(cutter)
  row['floor_0_to_2_removed_mm3']=volume(Compound(children=list(removed)),prism(box(-300,-200,300,200),0,2)) if removed else 0.
  for clash in row['trial_collisions']:
   hit=shape.intersect({**fixed,**bodies}[clash['obstacle']]);bb=Compound(children=list(hit)).bounding_box();clash['overlap_bbox_mm']=[[bb.min.X,bb.min.Y,bb.min.Z],[bb.max.X,bb.max.Y,bb.max.Z]]
  row['wall_channel_removed_mm3']=trays['tray-'+row['variant'].split('-')[-1]].volume-candidate.volume
  row['wall_channel_candidate_overlap_mm3']=volume(shape,candidate)
  row['post_overlaps']=[{'post':n,'volume_mm3':volume(shape,s)} for n,s in supportsolids.items() if volume(shape,s)>1e-6]
 # Fly 170mm cable loses the above-deck storage. Recheck a shorter underboard
 # candidate at Z7.0; distinguish route length from installed stock length.
 start=dims['fly']['cable']['waypoints_mm'][0];end=dims['fly']['cable']['waypoints_mm'][-1]
 flypts=[start,[0,-12,7],[0,-12,18.2],[0,7,18.2],end]
 fly,flypath=tube(flypts,1)
 flyhits=[]
 for n,s in {**fixed,**bodies,**supportsolids,**models}.items():
  if n=='Main-J4':continue # intended cable termination
  vol=volume(fly,s)
  if vol>1e-6:
   hit=fly.intersect(s);bb=Compound(children=list(hit)).bounding_box();flyhits.append(dict(obstacle=n,overlap_mm3=vol,overlap_bbox_mm=[[bb.min.X,bb.min.Y,bb.min.Z],[bb.max.X,bb.max.Y,bb.max.Z]]))
 export_step(fly,out/'trial-Fly-short.step');models['trial-Fly-short']=fly
 save(out/'fly.json',dict(candidate_waypoints_mm=flypts,candidate_length_mm=flypath.length,with_30mm_allowance_mm=flypath.length+30,stock_length_mm=170,unstored_excess_mm=170-flypath.length,collisions=flyhits,route_geometry_clear=not flyhits,stock_170mm_storage_verified=False,passed=False))
 save(out/'post-rescreen.json',postrows)
 # Explicit Main holes and filled original boards in overlay for review.
 for n,vs in dims['boards'].items():
  if n=='fly':continue
  models['pcb-'+n]=prism(Polygon(vs),10,1.2)
 export_step(Compound(children=[*models.values(),*supportsolids.values(),*bodies.values()]),out/'diagnostic-overlay.step')
 # SVG plan overlay, exact footprints and trial channel union.
 x0,y0,x1,y1=unary_union([Polygon(v) for v in dims['boards'].values()]).bounds
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-5} {y0-5} {x1-x0+10} {y1-y0+10}">']
 def draw(g,fill,stroke):
  for p in g.geoms if hasattr(g,'geoms') else [g]:
   if p.geom_type!='Polygon':continue
   points=' '.join(f'{x},{y}' for x,y in p.exterior.coords);svg.append(f'<polygon points="{points}" fill="{fill}" fill-opacity=".35" stroke="{stroke}" stroke-width=".3"/>')
 for vs in dims['boards'].values():draw(Polygon(vs),'#ccd','#446')
 for g in xybodies.values():draw(g,'#e75','#a31')
 for g in channelxy.values():draw(g,'#5ad','#048')
 for row in postrows:
  x,y=row['xy_mm'];svg.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="green"/>')
 svg.append('<path d="M3.5,-80 V120" stroke="red" stroke-dasharray="2,2" stroke-width=".3"/></svg>');(out/'obstacle-map.svg').write_text('\n'.join(svg))
save(OUT/'summary.json',summ);save(OUT/'inputs-sha256.json',manifest)
print('Case diagnostic complete; all positive collisions retained')
