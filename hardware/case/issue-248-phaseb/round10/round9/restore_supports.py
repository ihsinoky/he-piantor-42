"""Restore north load-bearing pillars after bay trim; clear removable shell walls."""
from common import *
from export import mesh_absolute
def run(pitch):
 out=HERE/f'{pitch}mm';cache=RUN/f'geometry{pitch}';idx,raw=cached(pitch);d=read(out/'measurements.json')
 if d.get('retention_support_restored'):return
 oldidx=read(out/'assembly-index.json');oldhash=sha(out/'assembly-index.json');old_audit=read(out/'audit.json');assert old_audit['geometry_sha256']==oldhash
 groups={}
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 changed=['tray-left','tray-right','shell-central'];actions=[]
 central=fuseall(groups['shell-central'])
 for x in (-8,8):
  n='tray-left' if x<0 else 'tray-right'
  pillar=cylinder(x,-30,3,2,TOP-4).cut(cylinder(x,-30,1.4,TOP-6,6))
  q=fuseall(groups[n]).fuse(pillar);assert q.is_valid and len(q.solids())==1
  groups[n]=[q]
  x0,x1=(-12.1,-9.7) if x<0 else (9.7,12.1)
  central=central.cut(prism(box(x0,-33.3,x1,-26.7),PLATE,TOP-2-PLATE))
  actions.append(dict(pillar_xy_mm=[x,-30],pillar_od_mm=6,root_z_mm=2,top_z_mm=TOP-2,pilot_od_mm=2.8,pilot_depth_mm=4,wall_service_opening_xyz_mm=[[x0,-33.3,PLATE],[x1,-26.7,TOP-2]],reason='restore load path cut by broad bay-seat trim; open nominal 2 mm wall locally around fixed pillar, retaining full roof'))
 fixed=central.fix()
 if fixed.is_valid and abs(fixed.volume-central.volume)<1e-6:central=fixed
 groups['shell-central']=sorted(central.solids(),key=lambda q:-bounds(q)[1][2])
 for n in changed:assert len(groups[n])==sum(r['name']==n for r in oldidx),('unexpected solid-count change',n)
 changed_physical=[];phys_index=0
 for i,r in enumerate(idx):
  if r['name'] in changed:
   q=groups[r['name']][r['solid']]
   # New geometry only for these three manufactured components.
   BRepTools.Write_s(q.wrapped,str(cache/f'{i}.brep'))
   r.update(bounds=bounds(q),valid=q.is_valid,volume_mm3=q.volume,sha256=sha(cache/f'{i}.brep'))
   changed_physical.append(phys_index)
  if not r['name'].startswith('USB-reference-'):phys_index+=1
 save(cache/'index.json',idx);save(out/'assembly-index.json',idx);newhash=sha(out/'assembly-index.json')
 proof=dict(status=P['status'],previous_geometry_sha256=oldhash,geometry_sha256=newhash,previous_index=oldidx,changed_names=changed,changed_physical_indices=changed_physical,actions=actions,service_reuse_proof='Added pillar material lies only at Y[-33,-27], disjoint from every U-motion envelope Y>=-16.52. Central shell is removed during service. Retention inserts are above the motion slab. Existing U/tray and plate-screw motion contacts therefore remain unchanged.',usb_reuse_proof='New pillars Y[-33,-27] are disjoint from all north USB 30mm insertion reservation Y ranges; every other insertion obstacle is unchanged.',fly_reuse_proof='Shell change is material removal at Y[-33.3,-26.7], Z>=13.55. Prior Fly minimum 0.30 witness at storage (0,50,12.95) -> (0,50,13.25) is unchanged. Added pillars are independently included in full fitted collision audit.')
 save(out/'support-restoration.json',proof)
 seed={f"{r['i']}:{r['j']}":{k:v for k,v in r.items() if k not in ('i','j')} for r in old_audit['exact_results'] if r['i'] not in changed_physical and r['j'] not in changed_physical}
 save(RUN/f'audit{pitch}-progress.json',dict(geometry_hash=newhash,results=seed,reuse_proof='Unchanged serialized operand hashes only; all changed tray/shell pairs recomputed.'))
 for i,r in enumerate(idx):
  if r['name'] not in changed:assert r==oldidx[i] and sha(cache/f'{i}.brep')==r['sha256']
 # Explicitly check USB/new-pillar separation before reusing insertion results.
 for n,k,q in raw:
  if n.startswith('USB-reference-'):assert bounds(q)[1][1]<-33
 d['retention_support_restored']=True;d['retention_wall_openings']=actions;save(out/'measurements.json',d)
 # Only the three changed print files are rebuilt; free-state posts stay intact.
 m=read(out/'manufacturing.json')
 for p in m['parts']:
  if p['name'] not in changed:continue
  ss=groups[p['name']];q=ss[0] if len(ss)==1 else Compound(children=ss);q.label=p['name']+'-PROVISIONAL'
  base=out/'manufacturing'/p['filename'];export_step(q,base.with_suffix('.step'));mesh_absolute(import_step(base.with_suffix('.step')),base.with_suffix('.stl'))
  b=bounds(q);size=[b[1][j]-b[0][j] for j in range(3)];brim=[size[0]+10,size[1]+10,size[2]]
  p.update(bounds_mm=b,valid=q.is_valid,solids=len(ss),volume_mm3=q.volume,with_5mm_brim_xyz_mm=brim,envelope_passed=brim[0]<=220 and brim[1]<=220 and brim[2]<=250,manufacturing_geometry_passed=q.is_valid and len(ss)==1,step_sha256=sha(base.with_suffix('.step')),stl_sha256=sha(base.with_suffix('.stl')))
 ass=[]
 for n,ss in groups.items():
  if n.startswith('USB-reference-'):continue
  q=ss[0] if len(ss)==1 else Compound(children=ss);q.label=n+'-PROVISIONAL-q1.50';q.parent=None;ass.append(q)
 export_step(Compound(children=ass),out/'fitted-assembly-PROVISIONAL.step');m['preview_sha256']=sha(out/'fitted-assembly-PROVISIONAL.step');save(out/'manufacturing.json',m)
 local=read(out/'local-measures.json');local['geometry_sha256']=newhash;local['clearance_replay_qualification']='Prior local replay predates north wall relief; GH/Fly roof and south openings unchanged. See support-restoration.json.';save(out/'local-measures.json',local)
 print(pitch,'north load path restored; changed components',changed,'reused exact unchanged pairs',len(seed),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
