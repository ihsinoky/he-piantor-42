"""M2x10 replacement at all eight unchanged E-stack seats."""
from common import *
def run(pitch):
 from restore_floor import run as preserve_floor
 preserve_floor(pitch)
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);groups={};inventory=[]
 for n,k,q in raw:groups.setdefault(n,[]).append(q)
 for n,ss in list(groups.items()):
  if not n.startswith('plate-screw-'):continue
  q=ss[0];b=bounds(q);x=(b[0][0]+b[1][0])/2;y=(b[0][1]+b[1][1])/2
  # Retain washer, head envelope and under-head datum Z13.85. Change shaft only.
  new=cylinder(x,y,.8,3.85,10).fuse(cylinder(x,y,1.7,13.85,1.3))
  groups[n]=[new];side='left' if '-left-' in n else 'right';tray=fuseall(groups['tray-'+side])
  post_top=7.35;engagement=post_top-3.85
  # Source pilot bottom Z2.4, floor top Z2, socket root Z1.2 unchanged.
  rootprobe=cylinder(x,y,1.0,.8,1.2)
  row=dict(part=n,quantity=1,hardware='M2x10 polymer-compatible thread-forming; head OD3.4 x1.3 max',replaces='M2x12',under_head_z_mm=13.85,tip_z_mm=3.85,boss_top_z_mm=post_top,nominal_engagement_mm=engagement,old_engagement_mm=5.5,root_material_mm=1.2,pilot_bottom_z_mm=2 if n.endswith(('left-H4','right-H2')) else 2.4,tip_above_pilot_bottom_mm=1.85 if n.endswith(('left-H4','right-H2')) else 1.45,floor_top_z_mm=2,tip_above_floor_mm=1.85,root_probe_volume_mm3=volume(rootprobe,tray),root_probe_expected_mm3=rootprobe.volume,passed=engagement>=3 and abs(volume(rootprobe,tray)-rootprobe.volume)<1e-6)
  inventory.append(row)
 # Local relief only at north E heads/washers, strictly below the untouched roof.
 relief=[]
 for side,hole in [('left','H4'),('right','H2')]:
  n=f'plate-screw-{side}-{hole}';b=bounds(groups[n][0]);x=(b[0][0]+b[1][0])/2;y=(b[0][1]+b[1][1])/2
  cutter=cylinder(x,y,2.2,PLATE,1.9)
  for name in ['shell-central','strip-'+side]:
   q=fuseall(groups[name]);before=q.volume;q=q.cut(cutter);groups[name]=list(q.solids())
   relief.append(dict(part=name,xy_mm=[x,y],opening_diameter_mm=4.4,z_mm=[PLATE,15.45],removed_volume_mm3=before-q.volume,roof_untouched=True,description='open-bottom clearance in wall below roof, not a roof pocket'))
 items={n:ss[0] if len(ss)==1 else Compound(children=ss) for n,ss in groups.items()};meta=read(out/'measurements.json')
 for k in ('status','pitch_mm','parameters'):meta.pop(k,None)
 meta['tuning_hardware']=inventory;meta['north_hardware_relief']=relief
 save_geometry(pitch,items,meta);save(out/'hardware-inventory.json',dict(status=P['status'],E_stack=inventory,all_E_replacements_passed=all(r['passed'] for r in inventory),unchanged_hardware='All other fitted hardware retained, including two M2x4 shell retainers and OD3.2 x4 inserts; see assembly-index.json',procurement_requirement='M2x10 must match existing polymer-compatible thread geometry and retained head envelope; nominal CAD engagement verified, physical retention not tested'))
 print(pitch,'M2x10',all(r['passed'] for r in inventory),[(r['part'],r['root_probe_volume_mm3'],r['root_probe_expected_mm3']) for r in inventory],flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
