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
 items=source(pitch);d,keys,regions,decks,cover=plan(pitch)
 exclude=lambda n:n.startswith(('GH-','EZmate-170mm','Main-envelope-','USB-reference-','cap-gauge-')) or n=='cable-rack'
 fixed={n:s.translate((0,0,-2.65)) for n,s in items.items() if not exclude(n)}
 for n,s in items.items():
  if n.startswith(('tray-','post-')):fixed[n]=compress(s)
 print(pitch,'floor-preserving compression complete',flush=True)
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
  for mask,z in [(decks,PLATE),(box(-300,-200,300,200).difference(decks),3.)]:
   part=clean(g.intersection(mask))
   if part.is_empty:continue
   raw=prism(part,z,30-z)
   # Clip wall tops with a solid extending down from the piecewise surface.
   cap=fuseall(sloped(part,a,m,40))
   walls+=list(raw.intersect(cap))
 if walls:central=central.fuse(*walls)
 blistermeta=[]
 for name,g,ceil,top in [('GH-left',ghfeet[0],13.2,15.2),('GH-right',ghfeet[1],13.2,15.2),('Fly-storage',LineString([(x,y) for x,y,z in fs]).simplify(.003).buffer(1.003,quad_segs=16),13.25,15.25)]:
  cavity=g.buffer(.30,join_style=2);outer=g.buffer(2.30,join_style=2)
  # Restrict to where a lift is required; blending remains inside A4 plan.
  cross=START+(TOP-top)/M
  outer=clean(outer.intersection(footprint).intersection(box(-300,cross,300,300)))
  if outer.is_empty:continue
  central=central.fuse(prism(outer,PLATE-2,top-(PLATE-2)))
  central=central.cut(prism(clean(cavity.intersection(outer)), -10,ceil+10))
  blistermeta.append(dict(name=name,ceiling_z_mm=ceil,top_z_mm=top,cavity=mapping(cavity),outer=mapping(outer)))
 for x,y in P['south_opening_xy_mm']:central=central.cut(cylinder(x,y,2.55,-1,40))
 # Four independent M2 shell screws, all keyless; south Wing/Main screws no longer retain shell.
 sites=[(-8,-30),(8,-30),(-8,66),(8,66)]
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
  retention.append(dict(part='central',xy_mm=[x,y],seat_top_z_mm=top,insert_pilot_od_mm=2.8,insert_depth_mm=4))
 fixed['shell-central']=central
 # North strips are independent roof/wall caps, attached to tray rims outside plates.
 for side in ('left','right'):
  g=clean(regions['north_'+side]);ring=g.difference(g.buffer(-2,join_style=2))
  strip=fuseall(sloped(g,TOP,0)+[prism(ring,PLATE,TOP-PLATE-2)])
  # Select two well-separated interior sites with >=3 mm footprint land.
  safe=g.buffer(-3.2)
  candidates=[Point(x,y) for x in range(-150,151) for y in range(-65,2) if safe.contains(Point(x,y))]
  selected=[]
  if candidates:
   selected=[min(candidates,key=lambda p:p.x),max(candidates,key=lambda p:p.x)]
  for j,p in enumerate(selected):
   x,y=p.x,p.y
   sleeve=cylinder(x,y,3,PLATE,TOP-PLATE-2).cut(cylinder(x,y,1.1,PLATE-.01,TOP-PLATE+1))
   strip=strip.fuse(sleeve).cut(cylinder(x,y,1.1,PLATE-.01,TOP-PLATE+1)).cut(cylinder(x,y,2,TOP-1,2))
   # Screw into tray-supported raised boss; no plate/PCB alteration.
   b=cylinder(x,y,3,2,PLATE-2).cut(cylinder(x,y,1.4,PLATE-4,5))
   fixed['tray-'+side]=fixed['tray-'+side].fuse(b)
   fixed[f'strip-{side}-screw-{j}']=cylinder(x,y,.8,PLATE-3,TOP-PLATE+2).fuse(cylinder(x,y,1.8,TOP-1,1))
   retention.append(dict(part='strip-'+side,xy_mm=[x,y],seat_top_z_mm=TOP))
  fixed['strip-'+side]=strip
 print(pitch,'shells / local measures / retention built',flush=True)
 save(out/'surface-plan.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(name=n,status=P['status']),geometry=mapping(g)) for n,g in regions.items()]))
 save(out/'cap-plan.json',[dict(key=k['key'],cap=mapping(k['cap']),well=mapping(k['well'])) for k in keys])
 # Dedicated routing is imported separately so candidate iterations preserve case inputs.
 from routes import make_routes
 wires,wm=make_routes()
 fixed.update(wires)
 # Cut real case-only routing clearance and service relief; never alter boards or plates.
 cuts=[]
 for w in wm:
  for pts in w['conductor_waypoints_mm']:
   cut,_=tube(pts,.85);cuts.append(cut)
 for side in ('left','right'):
  q=fixed['tray-'+side]
  for cutter in cuts:
   # Each cut is exact; no largest-solid filtering.
   if volume(q,cutter)>1e-6:q=q.cut(cutter)
  fixed['tray-'+side]=q
 # USB reservations use actual #232 positioned shells; translate with the board.
 usb=[]
 for n in ('USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit'):
  q=items[n].translate((0,0,-2.65));b=bounds(q)
  usb.append((n,prism(box(b[0][0],b[0][1]-30,b[1][0],b[1][1]),b[0][2],b[1][2]-b[0][2])))
 for n,q in usb:fixed[n]=q
 save_geometry(pitch,fixed,dict(wings=wm,fly=dict(connected_length_mm=fpath.length,minimum_radius_mm=5,waypoints_mm=fpts,path_samples_mm=fs,solid_count=len(fly.solids()),volume_mm3=fly.volume),blisters=blistermeta,retention=retention,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in [HERE/'parameters.json',HERE.parent/f'issue-232-final/{pitch}mm/assembly.step',flysource/'fly-170mm.step']}))
 print(pitch,'geometry checkpoint saved',flush=True)
if __name__=='__main__':make(int(sys.argv[1]))
