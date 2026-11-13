"""Issue 240 closed-top trial. Exact BRep checks, millimetres. Never edits inputs."""
import sys,json,math,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
from shapely.affinity import affine_transform
import routes

def read(p):return json.loads(p.read_text())
def bounds(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def fly_curve(d,south):
 start=d['fly']['cable']['waypoints_mm'][0]
 pts=[start,[0,-37,8.6],[.9,-25,14.6],[.9,5,14.6],[0,20,14.6],[0,south,14.6],[-14.6,south,14.6],[-14.6,51,14.6],[-4,45,14.6],[-4,25,14.6],[0,17.435,12.6]]
 return rounded(pts),pts

def fast_volume(a,b,skip_distance=False):
 aa=a.bounding_box();bb=b.bounding_box()
 if any(min(getattr(aa.max,k),getattr(bb.max,k))-max(getattr(aa.min,k),getattr(bb.min,k))<1e-7 for k in 'XYZ'):return 0.
 if not skip_distance and a.distance_to(b)>1e-7:return 0.
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 from OCP.BRepGProp import BRepGProp
 from OCP.GProp import GProp_GProps
 op=BRepAlgoAPI_Common(a.wrapped,b.wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
 if not op.IsDone():raise RuntimeError('Boolean intersection failed')
 if op.Shape().IsNull():return 0.
 props=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),props,True,False,False)
 return abs(props.Mass())

def run(pitch):
 out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True)
 source=HERE.parent/'issue-232-final'/f'{pitch}mm/assembly.step'
 items=dict(leaves(import_step(source)));d=read(HERE.parent/f'issue-228-final/{pitch}mm/dimensions.json')
 fixed={n:s for n,s in items.items() if not n.startswith(('GH-','EZmate-170mm','Main-envelope-','USB-reference-')) and n!='cable-rack'}
 inv={a['ref']:a for a in read(HERE.parent/'issue-238-bay-study/main-inventory.json')}
 for c in read(ROOT/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json'):
  ref=c['ref']
  if ref in ['J2','J3']:continue
  h=inv[ref]['study_height_mm']
  if h:fixed['Main-study-'+ref]=prism(shape(c['geometry']).buffer(.5,join_style=2),11.2,h)
 gh={};ghpolys=[];placement=[]
 for side,sgn,angle in [('left',-1,-120),('right',1,120)]:
  a=math.radians(angle);x=sgn*17.102146;y=42.075
  def xy(u,v):return [x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)]
  # Catalog rigid mated bounding reservation, including explicit 0.20 mount allowance.
  g=Polygon([xy(u,v) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]])
  ghpolys.append(g);gh['Main-GH-'+side]=prism(g,11.2,4.55)
  placement.append(dict(side=side,orientation_deg=angle,origin_mm=[x,y],wire_axis_z_mm=12.8,wire_exit_centre_mm=xy(0,5.55),mated_reference_top_z_mm=15.55,budget_top_z_mm=15.75))
 lo,hi=61.0001,68.
 assert fly_curve(d,lo)[0].length<170<fly_curve(d,hi)[0].length
 for _ in range(40):
  mid=(lo+hi)/2
  if fly_curve(d,mid)[0].length<170:lo=mid
  else:hi=mid
 path,pts=fly_curve(d,(lo+hi)/2);fly=sweep(Face(Wire.make_circle(1,Plane(origin=Vector(*pts[0]),z_dir=(0,1,0)))),path=path)
 samples=[[v.X,v.Y,v.Z] for v in path.positions([i/2000 for i in range(2001)])]
 assert fly.is_valid and len(fly.solids())==1 and abs(path.length-170)<1e-7
 assert abs(fly.volume-170*math.pi)<1e-3
 added={**gh,'Fly-170mm':fly};wd=[]
 for side,sgn in [('left',-1),('right',1)]:
  _,base_length=routes.wing_route(sgn,0)
  south=(160-base_length["longest_connected_conductor_mm"])/2
  parts,data=routes.wing_route(sgn,south)
  # A shorter R5-valid route in this same family, not a straight chord.
  _,short=routes.wing_route(sgn,-4.99)
  data.update(side=side,planning_length_mm=160,reference_route_mm=short['longest_connected_conductor_mm'],stored_service_mm=160-short['longest_connected_conductor_mm'],unmodeled_length_mm=0,minimum_bend_radius_mm=5,definition='One connected fanout/bundle/fanout envelope per harness; fanout overlap is subtracted once. Individual conductor OD1, lower bundle OD5; upper controlled 5x3 pack. No detached slack ring.')
  assert abs(data['longest_connected_conductor_mm']-160)<1e-7
  wd.append(data)
  for name,s in parts.items():added['Wing-'+side+'-'+name]=s
  export_step(Compound(children=list(parts.values())),out/f'wing-{side}-160mm.step')
 coverpoly=shape(read(HERE.parent/'issue-238-bay-study'/f'{pitch}mm-measurements.json')['cover_outline'])
 cover=prism(coverpoly,14.7,1.5)
 # Relief ceilings keep a continuous, flat Z16.20 top. Clearance budget 0.20.
 reliefs=[('GH',unary_union(ghpolys).buffer(.3),15.95),('Fly-cable',LineString([(p[0],p[1]) for p in samples]).simplify(.02).buffer(1.22,quad_segs=8),15.8)]
 # Fly external shell top14.9; underside ceiling15.2, skin1.0.
 reliefs.append(('Fly-USB-shell',box(-5,-55,5,-45),15.2))
 for name,g,z in reliefs:cover=cover.cut(prism(g.intersection(coverpoly),14.699,z-14.699))
 added['Cover']=cover
 # Four separate clip ledges. Their retention concept needs sample fit/load testing.
 band=coverpoly.buffer(.2).difference(coverpoly.buffer(-4)).intersection(unary_union([box(-60,-34,60,-30),box(-60,59,60,63)]))
 retention=[]
 for i,g in enumerate(polygons(band)):
  x,y=g.centroid.x,g.centroid.y;hole=Point(x,y).buffer(.9,quad_segs=32)
  clip=prism(g.difference(hole),13.2,1.5)
  headcone=Solid.make_cone(.9,1.6,.9,Plane(origin=(x,y,15.3)))
  cover=cover.cut(prism(hole,14.699,1.501)).cut(headcone)
  added[f'clip-ledge-{i+1}']=clip
  shaft=cylinder(x,y,.8,12.2,3.1)
  head=Solid.make_cone(.8,1.6,.9,Plane(origin=(x,y,15.3)))
  added[f'cover-screw-{i+1}']=shaft.fuse(head)
  nutpoly=Polygon([(x+1.85*math.cos(j*math.pi/3),y+1.85*math.sin(j*math.pi/3)) for j in range(6)])
  added[f'cover-nut-{i+1}']=prism(nutpoly.difference(Point(x,y).buffer(.8,quad_segs=32)),11.9,1.3)
  retention.append(dict(site=i+1,xy_mm=[x,y],screw='M1.6x4 countersunk',nut_AF_mm=3.2,clip_bond_area_nominal_mm2=6.,bond_and_load_qualified=False))
 added['Cover']=cover
 # Exact distributive partition of the cover CSG for tractable Boolean audits.
 cover_tiles=[]
 for ix in range(-5,5):
  for iy in range(-6,8):
   cp=coverpoly.intersection(box(ix*10,iy*10,(ix+1)*10,(iy+1)*10))
   if cp.is_empty or cp.area<1e-9:continue
   tile=prism(cp,14.7,1.5)
   for name,g,z in reliefs:
    cut=cp.intersection(g)
    if not cut.is_empty and cut.area>1e-9:tile=tile.cut(prism(cut,14.699,z-14.699))
   for site in retention:
    x,y=site['xy_mm']
    if not cp.buffer(1.7).contains(Point(x,y)):continue
    tile=tile.cut(prism(Point(x,y).buffer(.9,quad_segs=32),14.699,1.501)).cut(Solid.make_cone(.9,1.6,.9,Plane(origin=(x,y,15.3))))
   cover_tiles.extend(tile.solids())
 tile_volume=sum(t.volume for t in cover_tiles)
 assert abs(tile_volume-cover.volume)<1e-3,('cover partition mismatch',tile_volume,cover.volume)
 print(pitch,'cover tile volume agreement',abs(tile_volume-cover.volume),len(cover_tiles),flush=True)
 progress=read(out/"collision-progress.json") if "--resume" in sys.argv and (out/"collision-progress.json").exists() else {}
 resume_count=progress.get("pairs_checked",0)
 collisions=progress.get("collisions",[]);reject_known=("--reject-known" in sys.argv and bool(collisions));checks=resume_count if reject_known else 0;intended=[]
 def check(n,s,m,t):
  nonlocal checks
  if reject_known:return
  checks+=1
  if checks<=resume_count:return
  for si,ss in enumerate(cover_tiles if n=="Cover" else s.solids()):
   for ti,tt in enumerate(cover_tiles if m=="Cover" else t.solids()):
    v=fast_volume(ss,tt,skip_distance=(n=="Cover" or m=="Cover"))
    if v>1e-6:
     row=dict(a=n,b=m,a_solid=si,b_solid=ti,overlap_mm3=v);collisions.append(row);print('HIT',row,flush=True)
  save(out/'collision-progress.json',dict(last_pair=[n,m],pairs_checked=checks,collisions=collisions))
 for n,s in added.items():
  print(pitch,'check',n,flush=True)
  for m,t in fixed.items():
   own=(n=='Fly-170mm' and (m in ['EZmate-Fly-plug','EZmate-Main-plug','Main-study-J4'] or m.startswith('Fly-official-67')))
   own=own or (n.startswith('Wing-left') and m=='underside-left-J_WING') or (n.startswith('Wing-right') and m=='underside-right-J_WING')
   if own:intended.append([n,m]);continue
   check(n,s,m,t)
 names=list(added)
 for i,n in enumerate(names):
  for m in names[i+1:]:
   if n.startswith('Wing-left') and m.startswith('Wing-left') or n.startswith('Wing-right') and m.startswith('Wing-right'):
    intended.append([n,m]);continue # conservative one-cable envelope constituents
   check(n,added[n],m,added[m])
 usb=[]
 for n in ['USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit']:
  b=bounds(items[n]);s=prism(box(b[0][0],b[0][1]-30,b[1][0],b[1][1]),b[0][2],b[1][2]-b[0][2]);v=volume(cover,s)
  usb.append(dict(part=n,continuous_30mm_sweep_cover_overlap_mm3=v,gap_mm=cover.distance_to(s)))
 export_step(cover,out/'cover-trial.step');export_step(fly,out/'fly-170mm.step')
 # Source internals retain their documented #232/D-037 classifications.
 assembly={**fixed,**added}
 for n,s in assembly.items():s.label=n
 export_step(Compound(children=list(assembly.values())),out/'assembly-with-cover-REJECTED.step')
 result=dict(pitch_mm=pitch,all_pairs_audited=not reject_known,gate_evaluation="FAIL by measured counterexample" if reject_known else "All scheduled pairs evaluated",cover_partition_volume_error_mm3=abs(tile_volume-cover.volume),cover_audit_tiles=len(cover_tiles),source_assembly_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),verdict='INFEASIBLE for this evaluated routing candidate' if collisions else 'GEOMETRY PASS; service/retention qualification pending',unexpected_interferences=len(collisions),collisions=collisions,pairs_checked=checks,intended_mating_or_same_cable_pairs=intended,cover_top_z_mm=16.2,cover_bottom_z_mm=14.7,cover_outline= mapping(coverpoly),cover_reliefs=[dict(name=n,ceiling_z_mm=z,depth_mm=z-14.7,remaining_skin_mm=16.2-z) for n,g,z in reliefs],gh_placement=placement,fly=dict(connected_length_mm=path.length,waypoints_mm=pts,path_samples_mm=samples,solid_count=len(fly.solids()),volume_mm3=fly.volume,minimum_bend_radius_mm=5,bounds_mm=bounds(fly),unmodeled_length_mm=0),wings=wd,retention=retention,rack='Removed entirely; original Z22.2 rack cannot remain under a Z16.2 cover.',usb_insertion=usb,usb_pass=all(q['continuous_30mm_sweep_cover_overlap_mm3']<1e-6 for q in usb),source_fixed_pair_audit='Inherited #232 baseline; this file checks every new/replaced part against every retained leaf and against other new parts, except listed own mating and same-cable envelope constituents.',manufacturing_release=False)
 save(out/'measurements.json',result);print(pitch,'DONE',len(collisions),flush=True)
if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 17)
