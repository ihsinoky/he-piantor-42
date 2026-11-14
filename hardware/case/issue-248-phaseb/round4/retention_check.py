"""Check the actual support load path and local removal relief, not intended metadata."""
from common import *
from build import shell_pillar
def run(pitch):
 out=HERE/f'{pitch}mm';idx,raw=cached(pitch);rows=[]
 shells=[q for n,k,q in raw if n=='shell-central']
 for i,(x,y) in enumerate(read(HERE/'routing-structure-round4.json')['shell_retainer_sites_mm']):
  n='tray-left' if x<0 else 'tray-right';tray=next(q for name,k,q in raw if name==n);insert=next(q for name,k,q in raw if name==f'shell-insert-{i}')
  samples=[dict(z_mm=z,material_present=tray.is_inside(Vector(x,y-2,z))) for z in (1.9,2.1,11.7,18,22)]
  pillar=shell_pillar(x,y)
  load=cylinder(x,y-2,.45,.8,TOP-2-.8);load_common=volume(load,tray)
  hit=sum(volume(pillar,q) for q in shells);fit=volume(insert,tray);expected=math.pi*(1.6**2-1.4**2)*4
  rows.append(dict(side='left' if x<0 else 'right',load_path_samples=samples,load_probe_expected_mm3=load.volume,load_probe_actual_mm3=load_common,missing_load_path_mm3=max(0,load.volume-load_common),pillar_shell_intersection_mm3=hit,insert_press_fit_intersection_mm3=fit,expected_press_fit_mm3=expected,screw_engagement_mm=3,passed=all(r['material_present'] for r in samples) and abs(load.volume-load_common)<1e-6 and hit<1e-6 and abs(fit-expected)<1e-6))
 save(out/'retention-check.json',dict(status=P['status'],geometry_sha256=sha(out/'assembly-index.json'),supports=rows,local_geometry_passed=all(r['passed'] for r in rows),physical_load_or_inversion_certified=False))
 print(pitch,'retention local geometry',all(r['passed'] for r in rows),flush=True)
if __name__=='__main__':run(int(sys.argv[1]))
