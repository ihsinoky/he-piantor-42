"""Independent length arithmetic, exact clearances, USB and continuous reserve sweep."""
from common import *
def analytic(points,r=5):
 p=[np.array(v,float) for v in points];t=[0.];arcs=[]
 for i in range(1,len(p)-1):
  u=p[i-1]-p[i];v=p[i+1]-p[i];u/=np.linalg.norm(u);v/=np.linalg.norm(v)
  theta=math.acos(float(np.clip(np.dot(u,v),-1,1)));d=r/math.tan(theta/2)
  t.append(d);arcs.append(r*(math.pi-theta))
 t.append(0.);slack=[float(np.linalg.norm(p[i+1]-p[i]))-t[i]-t[i+1] for i in range(len(p)-1)]
 return dict(length_mm=sum(slack)+sum(arcs),minimum_straight_slack_mm=min(slack),minimum_bend_radius_mm=r)
def motion(sgn,i):
 from routes import segments
 a,b,r,mid=segments(sgn,i);z=mid[2];xc=sgn*13.55;yc=17.1-6.55
 arc=[(xc+sgn*r*math.cos(math.pi-j*math.pi/256),yc+r*math.sin(math.pi-j*math.pi/256)) for j in range(257)]
 # The U translates continuously 15.10 mm north; its two straight legs shorten.
 # Buffer covers circular chord error (<0.0002 mm) by >0.019 mm.
 strip=Polygon(arc+[(x,y-15.1) for x,y in reversed(arc)])
 return prism(strip.buffer(.52,quad_segs=32),z-.52,1.04)
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);d=read(out/'measurements.json')
 physical=[(n,k,s) for n,k,s in raw if not n.startswith('USB-reference-')]
 shells=[(n,k,s) for n,k,s in physical if n.startswith(('shell-central','strip-left','strip-right')) and '-screw-' not in n]
 lengths=[]
 for w in d['wings']:
  aa=[]
  for r in w['analytic_segments']:
   a=analytic(r['before']);b=analytic(r['after'])
   aa.append(dict(length_mm=a['length_mm']+b['length_mm']+r['turn_arc_length_mm'],minimum_straight_slack_mm=min(a['minimum_straight_slack_mm'],b['minimum_straight_slack_mm']),minimum_bend_radius_mm=min(5,r['turn_radius_mm'])))
  assert all(abs(a['length_mm']-v)<1e-6 for a,v in zip(aa,w['conductor_lengths_mm']))
  reserve=w['per_wire_reserve_mm']
  routed=max(a['length_mm'] for a in aa);dressed=max(w['dressed_reference_lengths_mm'])
  lengths.append(dict(side=w['side'],longest_mm=routed,margin_to_200_mm=200-routed,dressed_longest_mm=dressed,dressed_margin_to_164_8_mm=164.8-dressed,minimum_reserve_mm=min(reserve),maximum_reserve_mm=max(reserve),all_conductors=aa,routed_budget_passed=all(a['minimum_straight_slack_mm']>0 for a in aa) and routed<=200,cut_length_upper_mm=routed+11.4,cut_length_upper_margin_to_200_mm=200-routed-11.4,dressed_cut_length_upper_mm=dressed+11.4,internal_wire_bound_mm_per_end=5.7,complete_cut_length_verified=False,qualification='Curves end at nominal outlet dress planes, not sourced crimp wire-tip reference planes. Conservative internal allowance 5.70 mm/end uses B1 plug tip-to-wire-end drawing bound; actual crimp tails remain unqualified.',passed=False))
 fly=next(s for n,k,s in physical if n=='Fly-170mm')
 f=analytic(d['fly']['waypoints_mm']);from certified_distance import boundary_distance
 dist=min(boundary_distance(s,fly)[0] for n,k,s in shells)
 f.update(solid_count=len(fly.solids()),valid=fly.is_valid,volume_mm3=fly.volume,volume_error_mm3=abs(fly.volume-170*math.pi),shell_gap_mm=dist)
 f['passed']=abs(f['length_mm']-170)<1e-6 and f['minimum_straight_slack_mm']>0 and f['valid'] and f['solid_count']==1 and f['volume_error_mm3']<.001 and dist>=.3-1e-6
 save(out/'length-fly.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),conductors=lengths,fly=f))
 print(pitch,'length/Fly',f['shell_gap_mm'],flush=True)
 usb=[]
 for n,k,s in raw:
  if not n.startswith('USB-reference-'):continue
  hits=[];errors=[]
  for b,l,t in physical:
   if b.startswith(('Fly-official','Main-study','Main-GH','EZmate')) or b=='main':continue
   try:
    v=volume(s,t)
    if v>1e-6:hits.append(dict(part=b,solid=l,volume_mm3=v))
   except Exception as e:errors.append(dict(part=b,error=repr(e)))
  usb.append(dict(part=n,travel_mm=30,unexpected=hits,boolean_errors=errors,passed=not hits and not errors))
 save(out/'usb.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),reservations=usb,passed=all(r['passed'] for r in usb)))
 print(pitch,'USB complete',flush=True)
 caps=[]
 for k in read(out/'cap-plan.json'):
  cap=prism(shape(k['cap']),PLATE+.4,TOP-(PLATE+.4))
  gaps=[(cap.distance_to(s),n) for n,j,s in shells]
  gap,n=min(gaps);caps.append(dict(key=k['key'],nominal_gap_mm=gap,allowance_mm=.5,remaining_gap_mm=gap-.5,nearest_part=n,passed=gap-.5>=.3-1e-6))
 save(out/'caps.json',dict(status=P['status'],assumption='16x16 swept cap, from plate+0.4 to provisional plateau; combined XY/process allowance 0.50 mm',keys=caps,passed=all(k['passed'] for k in caps),full_press_skirt_physical_gate='OPEN: actual Junana q/skirt/full-press test required; never certified by this envelope'))
 print(pitch,'caps complete',flush=True)
 # Remove central/strip caps and Main for access, leaving Wing assemblies fitted.
 services=[]
 for side,sgn in [('left',-1),('right',1)]:
  envs=[motion(sgn,i) for i in range(14)];hits=[];errors=[]
  for n,k,s in physical:
   removed=n.startswith(('shell-central','strip-left','strip-right','shell-screw','Main-study','Main-GH','cover-screw','cover-Main-spacer','washer-main','screw-main','EZmate-Main','Wire-'+side)) or n=='main'
   if removed:continue
   for i,e in enumerate(envs):
    try:
     v=volume(e,s)
     if v>1e-6:hits.append(dict(part=n,solid=k,wire=i+1,volume_mm3=v))
    except Exception as error:errors.append(dict(part=n,wire=i+1,error=repr(error)))
  for i,e in enumerate(envs):e.label=f'{side}-wire-{i+1}-continuous-motion'
  export_step(Compound(children=envs),out/f'service-motion-{side}-PROVISIONAL.step')
  services.append(dict(side=side,turn_y_mm=[17.1,2],release_mm=30.2,method='continuous translated concentric R>=5 U strip; unchanged legs lie in fitted route; 0.020 mm per-strand envelope allowance',removed='central/strip caps, Main and its hardware; disconnect Main EZmate while retaining Fly cable in its dressed storage pose; own moving harness excluded',wing_stacks_remain_fitted=True,unexpected=hits,boolean_errors=errors,passed=not hits and not errors))
  print(pitch,side,'service',len(hits),'hits',flush=True)
 save(out/'service.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),sides=services,geometric_motion_passed=all(r['passed'] for r in services),accessible_reserve_certified=False,note='Accessible reserve additionally requires fitted collision gate and removable retention to pass.'))
 # Verify stack and palm datums from actual fitted parts, not prior verdicts.
 invariants=[]
 original=source(pitch)
 for n,k,s in physical:
  if n in ('main','wing_left','wing_right','plate-left','plate-right'):
   ref=original[n].translate((0,0,-2.65))
   invariants.append(dict(part=n,volume_difference_mm3=abs(ref.volume-s.volume),bounds_match=all(abs(a-b)<1e-6 for aa,bb in zip(bounds(ref),bounds(s)) for a,b in zip(aa,bb)),passed=abs(ref.volume-s.volume)<1e-6))
 palm=[]
 for side in ('left','right'):
  tray=next(s for n,k,s in physical if n=='tray-'+side);zs=[]
  for face in tray.faces():
   try:
    if face.normal_at().Z>.999999 and abs(face.center().Z-PLATE)<1e-5:zs.append(face.center().Z)
   except Exception:pass
  # Entire inherited south palm band, not just a sample of coplanar faces.
  probe=prism(box(-200,69.7001,200,100),PLATE-1.501,1.502)
  def clip(s):return Compound(children=list(s.intersect(probe) or []))
  oldband=clip(original['tray-'+side].translate((0,0,-2.65)));newband=clip(tray)
  common=volume(oldband,newband);removed=max(0,oldband.volume-common);added=max(0,newband.volume-common)
  palm.append(dict(side=side,plate_top_z_mm=PLATE,tray_top_faces_at_plate=len(zs),maximum_step_mm=max([abs(z-PLATE) for z in zs],default=999),protected_band_y_mm=[69.7001,100],palm_material_removed_mm3=removed,palm_material_added_mm3=added,passed=bool(zs) and max(abs(z-PLATE) for z in zs)<1e-6 and max(removed,added)<1e-4))
 save(out/'invariants.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),boards_and_plates=invariants,palm=palm,passed=all(r['passed'] for r in invariants+palm)))
if __name__=='__main__':run(int(sys.argv[1]))
