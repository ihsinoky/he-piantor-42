"""Independently reload STEP/STL/DXF; record all failures without suppressing them."""
from geometry import *
import collections,struct,itertools,argparse

def meshcheck(path,step):
 data=path.read_bytes();count=struct.unpack_from('<I',data,80)[0];assert len(data)==84+50*count
 edges=collections.Counter();vol=0.;degenerate=0
 for i in range(count):
  r=struct.unpack_from('<12fH',data,84+i*50);v=[tuple(r[j:j+3]) for j in (3,6,9)]
  degenerate+=len(set(v))!=3
  for a,b in zip(v,v[1:]+v[:1]):edges[tuple(sorted((a,b)))]+=1
  a,b,c=v;vol+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 return dict(triangles=count,nonmanifold_edges=sum(n!=2 for n in edges.values()),degenerate_triangles=degenerate,volume_relative_error=abs(abs(vol)-step.volume)/step.volume)

def intended(a,b):
 # Explicit connector internals retained under D-037 accepted qualification limit.
 if a.startswith('Fly-official-') and b.startswith('Fly-official-'):return 'D-037 official source internal solids'
 if 'USB-reference-shell' in (a,b) and any(n.startswith(('Fly-official-41','Fly-official-42')) for n in (a,b)):return 'D-037 accepted defective USB source mating envelope'
 if any(n.startswith('GH-') for n in (a,b)):
  for side,ref in [('left','J2'),('right','J3')]:
   gh=lambda n:n in ('GH-fanout-'+side,'GH-bundle-'+side)
   if gh(a) and gh(b):return 'connected conservative bundle/fanout envelope union'
   if (gh(a) and b in ('underside-'+side+'-J_WING','Main-envelope-'+ref)) or (gh(b) and a in ('underside-'+side+'-J_WING','Main-envelope-'+ref)):return 'own intended mated GH termination'
 if {a,b}=={'EZmate-Main-plug','Main-envelope-J4'}:return 'own intended Main EZmate mate'
 if a.startswith('Fly-official-67') and b=='EZmate-Fly-plug' or b.startswith('Fly-official-67') and a=='EZmate-Fly-plug':return 'own intended Fly EZmate mate'
 if 'EZmate-170mm-route' in (a,b) and a.startswith('EZmate-') and b.startswith('EZmate-'):return 'own intended EZmate termination'
 return None

def verify(pitch):
 out=HERE/f'{pitch}mm';d=json.loads((out/'dimensions.json').read_text());failures=[]
 provenance={p:sha(ROOT/p)==v for p,v in json.loads((out/'inputs-sha256.json').read_text()).items()}
 print(pitch,'reloading prints',flush=True)
 prints={}
 for p in d['printing']:
  stem=HERE/p['filename'];s=import_step(stem.with_suffix('.step'));b=s.bounding_box();m=meshcheck(stem.with_suffix('.stl'),s)
  valid=s.is_valid and len(s.solids())==1;brim=[b.size.X+10,b.size.Y+10]
  passed=valid and max(brim)<=220 and b.size.Z<=250 and m['nonmanifold_edges']==0 and m['degenerate_triangles']==0 and m['volume_relative_error']<.001
  prints[p['name']]=dict(valid=valid,solids=len(s.solids()),with_5mm_brim_xy_mm=brim,passed=passed,**m)
  if not passed:failures.append('print '+p['name'])
 print(pitch,'reloading full assembly',flush=True)
 ass=import_step(out/'assembly.step');raw=[]
 for n,s in leaves(ass):
  for solid in s.solids():raw.append((n,solid))
 unexpected=[];contacts=[];reference_overlaps=[];self_envelope_pairs=[];count=0
 bbs=[s.bounding_box() for n,s in raw]
 for i,(na,a) in enumerate(raw):
  if i%40==0:print(pitch,'collision',i,'/',len(raw),flush=True)
  for j,(nb,b) in enumerate(raw[i+1:],i+1):
   ab=bbs[i];bb=bbs[j]
   if any(min(getattr(ab.max,k),getattr(bb.max,k))-max(getattr(ab.min,k),getattr(bb.min,k))<=1e-6 for k in ('X','Y','Z')):continue
   count+=1
   # These sweeps converge into one conservative fanout reservation. They
   # represent a connected envelope union, not independently colliding parts.
   # OCCT Common fails on a valid converging pair even with fuzzy tolerances
   # 1e-7 and 1e-6. Record every internal broadphase pair without claiming a
   # measured intersection. Each constituent is still checked against all
   # other parts, including its own bundle, rack, tray and fasteners.
   if na==nb and na.startswith('GH-fanout-'):
    self_envelope_pairs.append(dict(a=na,b=nb,solid_indices=[i,j],intersection_status='not evaluated: same conservative envelope union',volume_mm3=None,reason=intended(na,nb)))
    continue
   try:v=volume(a,b)
   except Exception as error:
    raise RuntimeError(f'Intersection failed at solids {i}/{j}: {na} / {nb}') from error
   if v<=1e-4:continue
   r=dict(a=na,b=nb,volume_mm3=v);reason=intended(na,nb)
   if reason:r['reason']=reason;contacts.append(r)
   elif na.startswith('cap-gauge-') or nb.startswith('cap-gauge-'):
    r['reason']='Inherited 17mm cap XY reservation is not an actual cap profile';reference_overlaps.append(r)
   else:unexpected.append(r)
 save(out/'collision-audit.json',dict(unexpected_overlaps=unexpected,intended_contacts=contacts,self_envelope_pairs=self_envelope_pairs,unqualified_cap_reservation_overlaps=reference_overlaps,broadphase_pairs=count,assembly_solids=len(raw)))
 print(pitch,'functional section checks',flush=True)
 tray={side:import_step(out/f'tray-{side}.step') for side in ('left','right')}
 original={side:import_step(BASE/f'{pitch}mm/tray-{side}.step') for side in ('left','right')}
 section=prism(box(-300,-200,300,200),0,1.199)
 floors={side:dict(removed_below_socket_bottom_mm3=volume(original[side],section)-volume(tray[side],section)) for side in tray}
 passage={}
 for side in tray:
  route=next(r for r in d['routes'] if r['side']==side);cutter,_=tube(route['waypoints_mm'],3.)
  source=import_step(REV4/f'case/{pitch}mm/tray-{side}-channel-candidate.step')
  floor=prism(box(-300,-200,300,200),0,2)
  removed=original[side].intersect(cutter);removed_shape=Compound(children=list(removed));rb=removed_shape.bounding_box()
  passage[side]=dict(original_wall_removed_mm3=removed_shape.volume,removed_bbox_mm=[[rb.min.X,rb.min.Y,rb.min.Z],[rb.max.X,rb.max.Y,rb.max.Z]],conservative_original_roof_mm=11.2-rb.max.Z,removed_floor_mm3=volume(cutter,floor),historical_study_removed_floor_mm3=max(0.,volume(original[side],floor)-volume(source,floor)),source_valid=source.is_valid,source_solid_count=len(source.solids()),tray_harness_overlap_mm3=sum(volume(tray[side],s) for n,s in raw if n in ('GH-bundle-'+side,'GH-fanout-'+side)))
 posts=[]
 for p in d['posts']:
  x,y=p['xy_mm'];owner=tray[p['side']]
  probe=dict(**p,socket_axis_open=not any(s.is_inside(Vector(x,y,1.6)) for s in owner.solids()),socket_bottom_closed=any(s.is_inside(Vector(x,y,1.19)) for s in owner.solids()),socket_wall_present=any(s.is_inside(Vector(x+1.56,y,1.6)) for s in owner.solids()))
  probe['passed']=probe['socket_axis_open'] and probe['socket_bottom_closed'] and probe['socket_wall_present'] and 0<=p['pcb_gap_mm']<=.02
  posts.append(probe)
 # Actual planar faces establish the two upper datums independently of metadata.
 palm=[]
 for pd in d['plates']:
  side=pd['side'];pl=import_step(out/f'plate-package/plate-{side}.step')
  def topfaces(s):
   vals=[]
   for f in s.faces():
    try:
     n=f.normal_at();c=f.center()
     if n.Z>.999999 and abs(c.Z-16.2)<.01:vals.append(c.Z)
    except Exception:pass
   return vals
  tz=topfaces(tray[side]);pz=topfaces(pl)
  # Nearest inward points along every sampled exterior of the plate.
  blank=Polygon(pd['blank_outline_xy_mm']);deck=Polygon(pd['deck_outline_xy_mm']);inner=deck.buffer(-1,join_style=2)
  seam=[Point(x,y).distance(inner.boundary) for x,y in blank.exterior.coords]
  od=json.loads((BASE/f'{pitch}mm/outline-check.json').read_text());curve=od['design']['south_left']['path_xy_mm'];south=LineString(curve if side=='left' else [(-x,y) for x,y in curve])
  south_seam=[Point(x,y).distance(inner.boundary) for x,y in blank.exterior.coords if Point(x,y).distance(south)<=8]
  palm.append(dict(side=side,max_step_mm=max(abs(a-b) for a in tz for b in pz),min_seam_gap_mm=min(south_seam),max_seam_gap_mm=max(south_seam),whole_perimeter_max_seam_mm=max(seam),datum_faces_case=len(tz),datum_faces_plate=len(pz),nominal_z_mm=16.2,physical_measurement=False))
 import ezdxf
 platecheck=[]
 for side in ('left','right'):
  doc=ezdxf.readfile(out/f'plate-package/plate-{side}.dxf');entities=list(doc.modelspace())
  geometry=shape(json.loads((out/f'plate-package/plate-{side}.geojson').read_text()))
  holes=[Polygon(r) for r in geometry.interiors]
  platecheck.append(dict(side=side,dxf_mm_units=doc.units==4,closed_loops=all(e.closed for e in entities),aperture_count=sum(p.area>100 for p in holes),tie_hole_count=sum(p.area<100 for p in holes),connector_notch=False))
 if unexpected:failures.append('unexpected assembly overlaps')
 if not all(provenance.values()):failures.append('input provenance')
 if not all(p['passed'] for p in posts):failures.append('post/socket fit')
 if not all(p['dxf_mm_units'] and p['closed_loops'] and p['aperture_count']==21 and p['tie_hole_count']==4 for p in platecheck):failures.append('plate DXF inventory')
 if any(abs(p['removed_below_socket_bottom_mm3'])>1e-5 for p in floors.values()):failures.append('floor invariant')
 result=dict(pitch_mm=pitch,cad_passed=not failures,failures=failures,provenance=provenance,printing=prints,assembly_solids=len(raw),broadphase_pairs=count,unexpected_overlaps=unexpected,intended_mating_contacts=contacts,self_envelope_pairs=self_envelope_pairs,unqualified_cap_reservation_overlaps=reference_overlaps,cap_skirt_actual_profile_verified=False,cap_acceptance_envelope_gap_mm=.4,cap_acceptance_envelope_keys=42,full_acceptance_passed=False,remaining_gate='Actual keycap skirt/profile and physical build acceptance are unavailable',plate_checks=platecheck,palm=palm,floor=floors,passages=passage,posts=posts,fasteners=d['fasteners'])
 save(out/'verification.json',result)
 print(pitch,'CAD failures',failures,'overlaps',len(unexpected),flush=True)
 for r in unexpected:print(r,flush=True)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('pitch',type=int,choices=(16,17));result=verify(p.parse_args().pitch);raise SystemExit(0 if result['cad_passed'] else 1)
