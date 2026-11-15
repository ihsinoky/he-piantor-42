"""Production-intent case remake. Failed gates are evidence, never suppressed."""
from common import *
from shapely.affinity import rotate,translate
def plan(pitch):
 d=read(HERE.parent/f'issue-232-final/{pitch}mm/dimensions.json')
 old=read(HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm/measurements.json')
 keys=[];strips=[];margins=[];decks=[]
 for side in ('left','right'):
  t=d['wing_transforms'][side];xf=lambda g:transform(g,t)
  deck=Polygon(next(p['deck_outline_xy_mm'] for p in d['plates'] if p['side']==side));decks.append(deck)
  rows=list(csv.DictReader((HERE.parent/f'issue-232-final/{pitch}mm/plate-package/apertures-{side}-local.csv').open()))
  row=sorted([r for r in rows if '_R0_' in r['key']],key=lambda r:float(r['x_mm']))
  pts=[(float(k['x_mm']),float(k['y_mm'])+9) for k in row]
  north=xf(Polygon([(-300,pts[0][1]),*pts,(300,pts[-1][1]),(300,300),(-300,300)]))
  half=box(-300,-300,0,300) if side=='left' else box(0,-300,300,300)
  strips.append(deck.intersection(north).intersection(half).intersection(box(-300,-300,300,START)))
  inner=box(24.055555556,-300,300,300) if side=='left' else box(-300,-300,-24.055555556,300)
  margins.append(deck.intersection(xf(inner)))
  for r in rows:
   x,y,a=map(float,[r['x_mm'],r['y_mm'],r['rotation_ccw_deg']])
   keys.append(dict(key=r['key'],cap=xf(translate(rotate(box(-8,-8,8,8),a),x,y)),well=xf(translate(rotate(box(-9,-9,9,9),a),x,y))))
 wells=unary_union([k['well'] for k in keys])
 foot=shape(old['cover_outline']).union(box(-10,-18,10,18)).union(unary_union(margins)).difference(wells)
 regions=dict(plateau=foot.intersection(box(-300,-300,300,START)),slope=foot.intersection(box(-300,START,300,TOE)),low_south=foot.intersection(box(-300,TOE,300,300)),north_left=strips[0].difference(wells),north_right=strips[1].difference(wells))
 if pitch==17:
  prior={f['properties']['name']:shape(f['geometry']) for f in read(HERE.parent/'issue-248-lowdeck-raise/raised-regions-a4.geojson')['features'] if f['properties']['role']=='current surface footprint'}
  assert all(regions[n].symmetric_difference(g).area<1e-6 for n,g in prior.items())
 return d,keys,regions,unary_union(decks),shape(old['cover_outline'])
def compress(s):
 # Remove the 2.65 mm neutral band Z3..5.65; preserve floor and all upper seats.
 lower=list(s.intersect(prism(box(-300,-200,300,200),-20,23)))
 upper=[q.translate((0,0,-2.65)) for q in s.intersect(prism(box(-300,-200,300,200),5.65,100))]
 return fuseall(lower+upper)
def gh(side):
 sgn=-1 if side=='left' else 1;a=math.radians(sgn*120);x=sgn*17.102146;y=42.075001
 def poly(u,v,U,V):return Polygon([(x+u0*math.cos(a)+v0*math.sin(a),y-u0*math.sin(a)+v0*math.cos(a)) for u0,v0 in [(u,v),(U,v),(U,V),(u,V)]])
 h=poly(-10.375,-1.6,10.375,2.45);p=poly(-9.375,-.15,9.375,5.55)
 return prism(h,8.65,4.25).fuse(prism(p,8.75,4.15)),h.union(p)
def make(pitch):
 out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True)
 for name in ('retention-completion.json','support-restoration.json'):
  p=out/name
  if p.exists():
   archive=out/'evidence';archive.mkdir(exist_ok=True)
   p.replace(archive/(read(p)['geometry_sha256'][:12]+'-'+name))
 items=source(pitch);d,keys,regions,decks,cover=plan(pitch)
 exclude=lambda n:n.startswith(('GH-','EZmate-170mm','Main-envelope-','USB-reference-','cap-gauge-')) or n=='cable-rack'
 fixed={n:s.translate((0,0,-2.65)) for n,s in items.items() if not exclude(n)}
 for n,s in items.items():
  if n.startswith(('splice-','joint-screw-','rubber-')):fixed[n]=s
 # Same adopted Main south screws and loose spacers as B0, including exact seats.
 b0=ROOT/'.issue248-runtime/b0-source';bm=read(b0/'index.json')
 assert bm['source_sha256']==sha(HERE.parent/'issue-246-delta6-tuning/packed/delta-6/17mm/assembly-with-cover.step')
 for i,n in enumerate(bm['names']):
  if n.startswith(('cover-screw-','cover-Main-spacer-')):fixed[n]=loadbrep(b0/f'{i}.brep').translate((0,0,-8.65))
 for n in ('screw-main-H2','screw-main-H3'):fixed.pop(n,None)
 for n,s in items.items():
  if n.startswith(('tray-','post-')):fixed[n]=compress(s)
 print(pitch,'floor-preserving compression complete',[(n,q.is_valid,len(q.solids())) for n,q in fixed.items() if n.startswith('tray-')],flush=True)
 # Exact Main GH B1 seated bounds replace inherited coarse reservations.
 ghfeet=[]
 for side in ('left','right'):
  q,g=gh(side);fixed['Main-GH-'+side+'-DRAWING-BOUND']=q;ghfeet.append(g)
 inv={a['ref']:a for a in read(HERE.parent/'issue-238-bay-study/main-inventory.json')}
 for c in read(ROOT/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json'):
  h=inv[c['ref']]['study_height_mm']
  if c['ref'] not in ('J2','J3') and h:fixed['Main-study-'+c['ref']]=prism(shape(c['geometry']).buffer(.5,join_style=2),8.55,h)
 flysource=HERE.parent/f'issue-246-delta6-tuning/packed/delta-6/{pitch}mm'
 fly=import_step(flysource/'fly-170mm.step').translate((0,0,-8.65));fixed['Fly-170mm']=fly
 fm=read(flysource/'measurements.json')['fly'];fpts=[[x,y,z-2.65] for x,y,z in fm['waypoints_mm']]
 fpath=rounded(fpts);assert abs(fpath.length-170)<1e-7
 fs=[[v.X,v.Y,v.Z] for v in fpath.positions([i/2000 for i in range(2001)])]
 # A4 is a surface UNION: north strips overlap its plateau in plan. Assign that
 # material to strips so three manufactured parts never occupy the same volume.
 strips_union=regions['north_left'].union(regions['north_right'])
 regions['plateau']=regions['plateau'].difference(strips_union)
 footprint=unary_union([regions[n] for n in ('plateau','slope','low_south')])
 roof=[]
 for n in ('plateau','slope','low_south'):
  a,m=(TOP+M*START,M) if n=='slope' else ((PLATE,0) if n=='low_south' else (TOP,0))
  roof+=sloped(regions[n],a,m)
 central=fuseall(roof)
 # Peripheral walls: deck-supported above the Wing, floor-supported in bay.
 ring=clean(footprint.difference(footprint.buffer(-2,join_style=2)))
 walls=[]
 for n in ('plateau','slope','low_south'):
  g=ring.intersection(regions[n]);a,m=(TOP+M*START,M) if n=='slope' else ((PLATE,0) if n=='low_south' else (TOP,0))
  for mask,z in [(box(-300,-200,300,200),PLATE)]:
   part=clean(g.intersection(mask))
   if part.is_empty:continue
   raw=prism(part,z,30-z)
   # Clip wall tops with a solid extending down from the piecewise surface.
   cap=fuseall(sloped(part,a,m,40))
   intersection=raw.intersect(cap)
   if intersection is not None:walls+=list(intersection)
 if walls:central=central.fuse(*walls)
 blistermeta=[]
 for name,g,ceil,top in [('GH-left',ghfeet[0],13.2,15.2),('GH-right',ghfeet[1],13.2,15.2),('Fly-storage',LineString([(x,y) for x,y,z in fs]).simplify(.003).buffer(1.003,quad_segs=16),13.25,15.25)]:
  cavity=g.buffer(.30,join_style=2);outer=g.buffer(2.30,join_style=2)
  # Restrict to where a lift is required; blending remains inside A4 plan.
  cross=START+(TOP-top)/M-.5
  outer=clean(outer.intersection(footprint).intersection(box(-300,cross,300,300)))
  if outer.is_empty:continue
  central=central.fuse(prism(outer,PLATE-2,top-(PLATE-2)))
  central=central.cut(prism(clean(cavity.intersection(outer)), -10,ceil+10))
  blistermeta.append(dict(name=name,ceiling_z_mm=ceil,top_z_mm=top,cavity=mapping(cavity),outer=mapping(outer),north_blend_extension_mm=.5))
 for x,y in P['south_opening_xy_mm']:central=central.cut(cylinder(x,y,2.55,-1,40))
 # Four independent M2 shell screws, all keyless; south Wing/Main screws no longer retain shell.
 sites=[(-8,-30),(8,-30)]
 retention=[]
 for i,(x,y) in enumerate(sites):
  top=TOP if y<=START else PLATE
  side='left' if x<0 else 'right'
  # Floor-rooted hollow pillar; M2 heat-set insert sized 3.2 OD x 4, pilot 2.8.
  boss=cylinder(x,y,3,2,top-4).cut(cylinder(x,y,1.4,top-6,6))
  fixed['tray-'+side]=fixed['tray-'+side].fuse(boss)
  central=central.cut(cylinder(x,y,1.1,top-3,5)).cut(cylinder(x,y,2,top-1,2))
  shaft=cylinder(x,y,.8,top-5,4)
  head=cylinder(x,y,1.8,top-1,1)
  fixed[f'shell-screw-{i}']=shaft.fuse(head)
  fixed[f'shell-insert-{i}']=cylinder(x,y,1.6,top-6,4).cut(cylinder(x,y,.8,top-6.01,4.02))
  retention.append(dict(part='central',xy_mm=[x,y],seat_top_z_mm=top,insert_pilot_od_mm=2.8,insert_depth_mm=4))
 # North strips are deck-supported; two tabs per side are captured beneath the
 # removable central roof. No new hole crosses an unchanged aluminium plate.
 for side in ('left','right'):
  g=clean(regions['north_'+side]);ring=g.difference(g.buffer(-2,join_style=2))
  strip=fuseall(sloped(g,TOP,0)+[prism(ring,PLATE,TOP-PLATE-2)])
  sgn=-1 if side=='left' else 1
  for y in (-40,-23):
   x0,x1=sorted([sgn*8,sgn*14])
   tab=box(x0,y-3,x1,y+3)
   strip=strip.fuse(prism(tab,TOP-4.3,2))
   central=central.cut(prism(tab.buffer(.3,join_style=2),2.99,TOP-4.99))
   retention.append(dict(part='strip-'+side,tab_xy_bounds_mm=list(tab.bounds),tab_z_mm=[TOP-4.3,TOP-2.3],capture_clearance_mm=.3,method='two tabs captured below central roof; open-bottom wall slots'))
  fixed['strip-'+side]=strip
 fixed['shell-central']=central
 print(pitch,'shells / local measures / retention built',flush=True)
 save(out/'surface-plan.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(name=n,status=P['status']),geometry=mapping(g)) for n,g in regions.items()]))
 save(out/'cap-plan.json',[dict(key=k['key'],cap=mapping(k['cap']),well=mapping(k['well'])) for k in keys])
 # Dedicated routing is imported separately so candidate iterations preserve case inputs.
 from routes import make_routes
 wires,wm=make_routes()
 fixed.update(wires)
 # Cut real case-only routing clearance and service relief; never alter boards or plates.
 for side in ('left','right'):
  q=fixed['tray-'+side]
  # Seat the low cover on the remade bay rim; the aluminium plates are untouched.
  bayseat=clean(footprint.difference(decks))
  q=q.cut(prism(bayseat,PLATE-2,20))
  print(pitch,side,'pre-channel',q.is_valid,len(q.solids()),flush=True)
  # Projected 0.85 mm clearance grooves avoid pathological coincident sweep booleans.
  # Grooves are conservative subtractive case geometry, never a wire simplification.
  for w in wm:
   for pts,samples in zip(w['conductor_waypoints_mm'],w['conductor_samples_mm']):
    g=LineString([(x,y) for x,y,z in samples]).simplify(.01).buffer(.87,quad_segs=8)
    z=max(2.,min(p[2] for p in pts)-.87);h=max(p[2] for p in pts)+.87-z
    cutter=prism(g,z,h)
    b,bq=bounds(cutter),bounds(q)
    if all(min(b[1][i],bq[1][i])-max(b[0][i],bq[0][i])>1e-7 for i in range(3)):q=q.cut(cutter)
  fixed['tray-'+side]=q
 # Bay seating must never truncate the dedicated north retention load path.
 for i,(x,y) in enumerate(sites):
  side='left' if x<0 else 'right'
  pillar=cylinder(x,y,3,2,TOP-4).cut(cylinder(x,y,1.4,TOP-6,6))
  fixed['tray-'+side]=fixed['tray-'+side].fuse(pillar)
  x0,x1=sorted([(-12.1 if x<0 else 9.7),(-9.7 if x<0 else 12.1)])
  fixed['shell-central']=fixed['shell-central'].cut(prism(box(x0,y-3.3,x1,y+3.3),PLATE,TOP-2-PLATE))
 # USB reservations use actual #232 positioned shells; translate with the board.
 usb=[]
 for n in ('USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit'):
  q=items[n].translate((0,0,-2.65));b=bounds(q)
  usb.append((n,prism(box(b[0][0],b[0][1]-30,b[1][0],b[1][1]),b[0][2],b[1][2]-b[0][2])))
 for n,q in usb:fixed[n]=q
 save_geometry(pitch,fixed,dict(wings=wm,fly=dict(connected_length_mm=fpath.length,minimum_radius_mm=5,waypoints_mm=fpts,path_samples_mm=fs,solid_count=len(fly.solids()),volume_mm3=fly.volume),blisters=blistermeta,retention=retention,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'parameters.json',HERE.parent/f'issue-232-final/{pitch}mm/assembly.step',flysource/'fly-170mm.step']}))
 print(pitch,'geometry checkpoint saved',flush=True)
if __name__=='__main__':make(int(sys.argv[1]))
