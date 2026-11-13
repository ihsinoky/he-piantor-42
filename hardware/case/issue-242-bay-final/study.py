"""Final dedicated under-cover study; study outputs only, exhaustive AABB/exact audit.
All scratch belongs to .issue242-runtime. No pair-count shortcut or early reject.
"""
import sys, os, json, math, hashlib, itertools, time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; RUNTIME=ROOT/'.issue242-runtime'
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; RUNTIME=ROOT/".issue242-runtime"
sys.path.insert(0,str(HERE.parent/'issue-240-bay-cover'))
import importlib.util
spec=importlib.util.spec_from_file_location("issue240_study",HERE.parent/"issue-240-bay-cover/study.py");old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
fast_volume=old.fast_volume;fly_curve=old.fly_curve
spec=importlib.util.spec_from_file_location("issue232_verify",HERE.parent/"issue-232-final/verify.py");prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
inherited_intended=prior.intended
from build123d import Shape
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder

def bounds(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def read(p):return json.loads(p.read_text())
def cached_source(pitch):
 source=HERE.parent/f'issue-232-final/{pitch}mm/assembly.step'; cache=RUNTIME/f'cache{pitch}'; cache.mkdir(exist_ok=True)
 digest=sha(source); index=cache/'index.json'
 if index.exists() and read(index)['sha256']==digest:
  result={}
  for i,n in enumerate(read(index)['names']):
   s=TopoDS_Shape(); BRepTools.Read_s(s,str(cache/f'{i}.brep'),BRep_Builder());result[n]=Shape.cast(s)
  return result
 print('Import source',pitch,flush=True);items=dict(leaves(import_step(source)))
 for i,(n,s) in enumerate(items.items()):BRepTools.Write_s(s.wrapped,str(cache/f'{i}.brep'))
 save(index,dict(sha256=digest,names=list(items)));return items

def wing(sgn,south):
 # Keep the original fourteen Wing exits. Dedicated U replaces the #232 rack route.
 fan=[];fl=[]
 for i in range(14):
  pts=[[sgn*27+(i-6.5)*1.25,-35.45,8.4],[sgn*27+(i-6.5)*1.25,-31.5,8.4],[sgn*27,-24,5],[sgn*14,-18.8,5]]
  q,p=tube(pts,.5);fan.append(q);fl.append(p.length)
 lowpts=[[sgn*27,-24,5],[sgn*7,-16,5],[sgn*7,south,5],[sgn*23,south,5],[sgn*23,8,5]]
 lower,lp=tube(lowpts,2.5)
 # Deliberate outside-edge return/rise; its crossing of fixed electronics is audited.
 upper=[];ul=[];epoints=[];samples=[]
 positions=[(i-2,-1) for i in range(5)]+[(i-2,0) for i in range(5)]+[(i-1.5,1) for i in range(4)]
 for i,(off,dz) in enumerate(positions):
  theta=math.radians(120 if sgn==1 else -120);u=(i-6.5)*1.25
  ep=[sgn*15.5+u*math.cos(theta)+7.4*math.sin(theta),43-u*math.sin(theta)+7.4*math.cos(theta),12.8]
  approach=[ep[0]+9*math.sin(theta),ep[1]+9*math.cos(theta),12.8]
  pts=[lowpts[-1],[sgn*31+off,18,12.8+dz],approach,ep]
  q,p=tube(pts,.5);upper.append(q);ul.append(p.length);epoints.append(ep)
  samples.append([[v.X,v.Y,v.Z] for v in p.positions([j/160 for j in range(161)])])
 length=max(fl[i]+lp.length-math.dist([sgn*27,-24,5],[sgn*14,-18.8,5])+ul[i] for i in range(14))
 return {'entry':Compound(children=fan),'lower':lower,'upper':Compound(children=upper)},dict(longest_conductor_mm=length,lower_waypoints_mm=lowpts,lower_length_mm=lp.length,upper_samples_mm=samples,upper_conductor_lengths_mm=ul,entry_conductor_lengths_mm=fl,main_exits_mm=epoints)

def make(pitch):
 out=HERE/f'{pitch}mm';out.mkdir(exist_ok=True);items=cached_source(pitch)
 fixed={n:s for n,s in items.items() if not n.startswith(('GH-','EZmate-170mm','Main-envelope-','USB-reference-','cap-gauge-')) and n!='cable-rack'}
 inv={a['ref']:a for a in read(HERE.parent/'issue-238-bay-study/main-inventory.json')}
 for c in read(ROOT/'hardware/kicad/qualification/issue-235-wing-round2/main-native-obstacles.json'):
  ref=c['ref'];h=inv[ref]['study_height_mm']
  if ref not in ('J2','J3') and h:fixed['Main-study-'+ref]=prism(shape(c['geometry']).buffer(.5,join_style=2),11.2,h)
 ghpolys=[];new={};wings=[];cutters=[]
 for side,sgn,angle in [('left',-1,-120),('right',1,120)]:
  a=math.radians(angle);x=sgn*17.102146;y=42.075
  def xy(u,v):return [x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)]
  g=Polygon([xy(u,v) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]])
  ghpolys.append(g);new['Main-GH-'+side]=prism(g,11.2,4.55)
  parts,data=wing(sgn,38);_,ref=wing(sgn,22)
  data.update(side=side,reference_conductor_mm=ref['longest_conductor_mm'],represented_reserve_mm=data['longest_conductor_mm']-ref['longest_conductor_mm'],accessible_reserve_certified=False,minimum_bend_radius_mm=5,lower_bundle_diameter_mm=5,unmodeled_length_mm=0)
  wings.append(data)
  for n,s in parts.items():new[f'Wing-{side}-{n}']=s
  cutter,_=tube(data['lower_waypoints_mm'],3.0);cutters.append(cutter)
  # The upper transition gets a manufacturable cleared case channel, not an exemption.
  for row in data['upper_samples_mm']:
   g=LineString([(p[0],p[1]) for p in row]).simplify(.02).buffer(.82,quad_segs=8)
   cutters.append(prism(g,3.9,10.0))
 d=read(HERE.parent/f'issue-228-final/{pitch}mm/dimensions.json')
 lo,hi=61.0001,68.
 for _ in range(40):
  mid=(lo+hi)/2
  if fly_curve(d,mid)[0].length<170:lo=mid
  else:hi=mid
 path,pts=fly_curve(d,(lo+hi)/2)
 fly=sweep(Face(Wire.make_circle(1,Plane(origin=Vector(*pts[0]),z_dir=(0,1,0)))),path=path)
 assert fly.is_valid and len(fly.solids())==1 and abs(path.length-170)<1e-7
 new['Fly-170mm']=fly;fs=[[v.X,v.Y,v.Z] for v in path.positions([i/2000 for i in range(2001)])]
 # New case revision only: screw pilots and bosses relocated within the two splices.
 reloc=[]
 for row,y in [(1,-8),(2,55)]:
  for oldx,newx in [(-5,0),(12,15)]:
   key=f'joint-screw-{row}-{float(oldx):.1f}'.replace('.','_')
   assert key in fixed,key
   fixed[key]=fixed[key].translate((newx-oldx,0,0));reloc.append(dict(row=row,old_xy=[oldx,y],new_xy=[newx,y]))
  splice=fixed[f'splice-{row}']
  for newx in (0,15):splice=splice.cut(cylinder(newx,y,1.1,-3.01,4.22))
  fixed[f'splice-{row}']=splice
 sites=[(-8,-30),(8,-30),(-31.892683,64.4),(31.892682,64.4)];case_deltas=[]
 for name in ('screw-main-H2','screw-main-H3'):del fixed[name]
 for side in ('left','right'):
  tray=fixed['tray-'+side];before=tray.volume
  for y in (-8,55):
   for oldx in (-5,12):
    tray=tray.cut(cylinder(oldx,y,3.5,2,6.001))
    # Fill old pilot only where original floor existed; prevents material across seam.
   for x in (0,15):
    if (x<3.5)==(side=='left'):tray=tray.fuse(cylinder(x,y,3.5,1.2,6.8)).cut(cylinder(x,y,.85,-.01,8.02))
  for cutter in cutters:tray=tray.cut(cutter)
  # Remove inward rim nibs: Z14.7 roof must seat without force.
  cp=shape(read(HERE.parent/f'issue-238-bay-study/{pitch}mm-measurements.json')['cover_outline'])
  trim=cp.intersection(box(-200,-39,200,100))
  tray=tray.cut(prism(trim,14.699,1.502))
  for i,(x,y) in enumerate(sites):
   if (x<3.5)!=(side=='left'):continue
   if y>0:
    # Shared existing Main H2/H3 sites: removable spacers, no PCB trapping bridge.
    new[f'cover-Main-spacer-{i}']=cylinder(x,y,2.25,11.7,3).cut(cylinder(x,y,1.1,11.699,3.002))
    shaft=cylinder(x,y,.8,6.2,9)
   else:
    pillar=cylinder(x,y,4,1,13.7)
    nutpoly=Polygon([(x+2.31*math.cos(j*math.pi/3),y+2.31*math.sin(j*math.pi/3)) for j in range(6)])
    pocket=nutpoly.buffer(.10,join_style=2).union(box(x-4.1,y-2.1,x,y+2.1))
    pillar=pillar.cut(prism(pocket,11.4,1.7)).cut(cylinder(x,y,1.1,10,5))
    tray=tray.fuse(pillar)
    new[f'cover-nut-{i}']=prism(nutpoly.difference(Point(x,y).buffer(.8,quad_segs=32)),11.5,1.6)
    shaft=cylinder(x,y,.8,10.2,5)
   head=Solid.make_cone(.8,2,1.0,Plane(origin=(x,y,15.2)))
   new[f'cover-screw-{i}']=shaft.fuse(head)
  fixed['tray-'+side]=tray
  case_deltas.append(dict(part='tray-'+side,volume_before_mm3=before,volume_after_mm3=tray.volume,valid=tray.is_valid,solids=len(tray.solids())))
 print(pitch,'case revision built',case_deltas,flush=True)
 coverpoly=cp;edge_fits=[]
 # D-037 seat/opening region is immutable. Fit the lid perimeter to its rim,
 # rather than shaving retained Fly-area case material as #240 did.
 north=coverpoly.intersection(box(-200,-100,200,-39))
 probe=prism(north,14.699,1.502)
 for side in ('left','right'):
  for obstruction in items['tray-'+side].intersect(probe):
   for solid in obstruction.solids():
    if solid.volume<1e-6:continue
    b=bounds(solid);mask=box(b[0][0],b[0][1],b[1][0],b[1][1]).buffer(.3,quad_segs=16)
    coverpoly=coverpoly.difference(mask);edge_fits.append(dict(side=side,obstruction_bbox_mm=b,edge_clearance_mm=.3))
 reliefs=[('GH',unary_union(ghpolys).buffer(.3),15.95),('Fly',LineString([(p[0],p[1]) for p in fs]).simplify(.02).buffer(1.22,quad_segs=8),15.8),('USB',box(-5,-55,5,-45),15.2)]
 # Disjoint cover tiles are exact distributive CSG; pairwise audit checks every tile.
 tiles=[]
 for ix in range(-5,5):
  for iy in range(-6,8):
   cp=coverpoly.intersection(box(ix*10,iy*10,(ix+1)*10,(iy+1)*10))
   if cp.is_empty or cp.area<1e-9:continue
   tile=prism(cp,14.7,1.5)
   for name,g,z in reliefs:
    cut=cp.intersection(g)
    if not cut.is_empty and cut.area>1e-9:tile=tile.cut(prism(cut,14.699,z-14.699))
   for x,y in sites:
    if not cp.buffer(2.1).contains(Point(x,y)):continue
    tile=tile.cut(cylinder(x,y,1.1,14.699,1.502)).cut(Solid.make_cone(.8,2.1,1.,Plane(origin=(x,y,15.2))))
   tiles+=list(tile.solids())
 new['Cover']=Compound(children=tiles)
 assembly={**fixed,**new};raw=[]
 for n,s in assembly.items():
  for k,q in enumerate(s.solids()):raw.append((n,k,q))
 for n,s in assembly.items():s.label=n
 export_step(Compound(children=list(assembly.values())),out/'assembly-with-cover-REJECTED.step')
 for side in ('left','right'):
  fixed['tray-'+side].parent=None
  export_step(fixed['tray-'+side],out/f'tray-{side}-study.step')
  export_step(Compound(children=[s for n,s in new.items() if n.startswith('Wing-'+side)]),out/f'wing-{side}.step')
 new['Cover'].parent=None;fly.parent=None
 export_step(new['Cover'],out/'cover-study.step');export_step(fly,out/'fly-170mm.step')
 # Save exact BReps separately for audit-only reproduction/resume, never trust old counts.
 cache=RUNTIME/f'audit{pitch}';cache.mkdir(exist_ok=True)
 meta=[]
 for i,(n,k,q) in enumerate(raw):
  BRepTools.Write_s(q.wrapped,str(cache/f'{i}.brep'));meta.append(dict(name=n,solid=k,bounds=bounds(q),brep_sha256=sha(cache/f'{i}.brep')))
 save(cache/'index.json',meta)
 usb=[]
 for n in ('USB-reference-shell','USB-reference-overmold','USB-reference-cable-exit'):
  b=bounds(items[n]);reservation=prism(box(b[0][0],b[0][1]-30,b[1][0],b[1][1]),b[0][2],b[1][2]-b[0][2])
  hits={}
  # All changed case/lid/cables/hardware, plus retained case from the actual assembly.
  for m,s in assembly.items():
   if m.startswith(('Fly-official','EZmate','Main-study','Main-GH')) or m in ('main',):continue
   v=sum(fast_volume(q,t) for q in s.solids() for t in reservation.solids())
   if v>1e-6:hits[m]=v
  usb.append(dict(part=n,continuous_30mm_insertion_overlaps_mm3=hits))
 result=dict(pitch_mm=pitch,wings=wings,fly=dict(connected_length_mm=path.length,solid_count=len(fly.solids()),volume_mm3=fly.volume,waypoints_mm=pts,path_samples_mm=fs,unmodeled_length_mm=0),case_deltas=case_deltas,splice_relocations=reloc,cover_outline=mapping(coverpoly),retained_rim_edge_fits=edge_fits,retention_sites_mm=sites,cover_reliefs=[dict(name=n,ceiling_z_mm=z,remaining_skin_mm=16.2-z) for n,g,z in reliefs],cover_top_z_mm=16.2,usb_insertion=usb,usb_pass=all(not r['continuous_30mm_insertion_overlaps_mm3'] for r in usb),main_rev7_sha256=sha(ROOT/'hardware/kicad/qualification/issue-240-main-rev7/inspection/final/main.kicad_pcb'),assembly_solid_count=len(raw))
 save(out/'measurements.json',result);print(pitch,'geometry exported',len(raw),flush=True)
 return raw

def reason(a,b):
 if a==b and (a=='Cover' or a.startswith('Wing-')):return 'same conservative envelope / partition, not separate physical parts'
 for side in ('left','right'):
  if a.startswith('Wing-'+side) and b.startswith('Wing-'+side):return 'same connected cable envelope'
  if (a.startswith('Wing-'+side) and b in ('underside-'+side+'-J_WING','Main-GH-'+side)) or (b.startswith('Wing-'+side) and a in ('underside-'+side+'-J_WING','Main-GH-'+side)):return 'own connector termination'
 if 'Fly-170mm' in (a,b) and any(n.startswith(('EZmate-','Fly-official-67')) or n=='Main-study-J4' for n in (b if a=='Fly-170mm' else a,)):return 'own EZmate termination'
 if {a,b}=={'Main-study-J4','EZmate-Main-plug'}:return 'own Main EZmate mate'
 return inherited_intended(a,b)

def audit(pitch,raw=None):
 out=HERE/f'{pitch}mm';cache=RUNTIME/f'audit{pitch}';meta=read(cache/'index.json')
 if raw is None:
  raw=[]
  for i,r in enumerate(meta):
   s=TopoDS_Shape();BRepTools.Read_s(s,str(cache/f'{i}.brep'),BRep_Builder());raw.append((r['name'],r['solid'],Shape.cast(s)))
 n=len(raw);total=n*(n-1)//2;reject=0;candidates=[];intended=[];hits=[];errors=[]
 for i,(a,k,s) in enumerate(raw):
  for j in range(i+1,n):
   b,l,t=raw[j];ab=meta[i]['bounds'];bb=meta[j]['bounds']
   if any(min(ab[1][d],bb[1][d])-max(ab[0][d],bb[0][d])<=1e-7 for d in range(3)):reject+=1;continue
   why=reason(a,b)
   if why:intended.append(dict(i=i,j=j,a=a,b=b,reason=why));continue
   candidates.append((i,j))
 print(pitch,'EXHAUSTIVE broadphase',total,'pairs;',len(candidates),'exact candidates',flush=True)
 progress=cache/'progress.json';done={}
 if '--resume' in sys.argv and progress.exists():
  p=read(progress);assert p['geometry_hash']==sha(cache/'index.json');done=p['results']
 for count,(i,j) in enumerate(candidates):
  key=f'{i}:{j}';a,k,s=raw[i];b,l,t=raw[j]
  if key not in done:
   try:done[key]=dict(volume_mm3=fast_volume(s,t,skip_distance=True))
   except Exception as error:done[key]=dict(error=str(error))
  r=dict(i=i,j=j,a=a,b=b,a_solid=k,b_solid=l,**done[key])
  if 'error' in r:errors.append(r)
  elif r['volume_mm3']>1e-6:hits.append(r);print('HIT',r,flush=True)
  if count%20==0:
   save(progress,dict(geometry_hash=sha(cache/'index.json'),results=done));print(pitch,'exact',count+1,'/',len(candidates),flush=True)
 save(progress,dict(geometry_hash=sha(cache/'index.json'),results=done))
 assert total==reject+len(intended)+len(candidates)
 reference_hits=[];measured_intended=[];physical_hits=[]
 for r in hits:
  if r['a'].startswith('Main-study-') and r['b'].startswith('Main-study-'):
   reference_hits.append(dict(**r,reason='Overlap of independent +0.50mm XY component clearance reservations; not actual physical body overlap'))
  elif r['a'].startswith('cover-nut-') and r['b']==r['a'].replace('nut','screw'):
   measured_intended.append(dict(**r,reason='Own nominal nut/thread mating; inscribed polygon bore vs circular minor-shaft discretization'))
  else:physical_hits.append(r)
 result=dict(all_pairs_enumerated=True,all_exact_candidates_completed=len(done)==len(candidates),assembly_solids=n,total_pairs=total,aabb_rejected_pairs=reject,intended_pairs=intended,exact_candidates=len(candidates),geometry_index_sha256=sha(cache/'index.json'),exact_results=[dict(i=i,j=j,**done[f'{i}:{j}']) for i,j in candidates],unexpected_interferences=physical_hits,clearance_reservation_overlaps=reference_hits,measured_intended_contacts=measured_intended,boolean_errors=errors,interference_zero=not physical_hits and not errors,tolerance_volume_mm3=1e-6,early_stop=False)
 save(out/'audit.json',result);print(pitch,'AUDIT COMPLETE unexpected',len(physical_hits),'reference',len(reference_hits),'measured intended',len(measured_intended),'errors',len(errors),flush=True)
if __name__=='__main__':
 pitch=int(sys.argv[1]);raw=None if '--audit-only' in sys.argv else make(pitch)
 audit(pitch,raw)
