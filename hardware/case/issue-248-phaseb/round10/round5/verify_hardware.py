"""Verify material, not just nominal screw and boss datums."""
from common import *
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);trays={n:q for n,k,q in raw if n.startswith('tray-')};hw=read(out/'hardware-inventory.json')
 for row in hw['E_stack']:
  name=row['part'];q=next(q for n,k,q in raw if n==name);b=bounds(q);x=sum(v[0] for v in b)/2;y=sum(v[1] for v in b)/2;side='left' if '-left-' in name else 'right'
  z=row['tip_z_mm'];h=row['boss_top_z_mm']-z
  annulus=cylinder(x,y,1,z,h).cut(cylinder(x,y,.85,z-.01,h+.02));v=volume(annulus,trays['tray-'+side])
  root=cylinder(x,y,1,.8,1.2);root_v=volume(root,trays['tray-'+side])
  row.update(thread_bearing_annulus_expected_mm3=annulus.volume,thread_bearing_annulus_actual_mm3=v,thread_bearing_material_fraction=v/annulus.volume,thread_bearing_annulus_intact=abs(v-annulus.volume)<1e-6,root_probe_volume_mm3=root_v,root_probe_expected_mm3=root.volume)
  row['passed']=abs(v-annulus.volume)<1e-6 and abs(root_v-root.volume)<1e-6 and h>=3 and row['root_material_mm']>=1.2
 hw.update(geometry_sha256=sha(out/'assembly-index.json'),all_E_replacements_passed=all(r['passed'] for r in hw['E_stack']),engagement_method='Exact Common of complete nominal M2 major-radius 1.00 / original pilot-radius 0.85 annulus across Z3.85..7.35; full annulus required, plus independent 1.20 mm root material probe. Threads remain nominal; physical retention untested.')
 save(out/'hardware-inventory.json',hw);m=read(out/'measurements.json');m['tuning_hardware']=hw['E_stack'];save(out/'measurements.json',m)
 print(pitch,'full thread-bearing annulus and root',hw['all_E_replacements_passed'],flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
