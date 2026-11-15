"""Manufacturing free-state split pegs; fitted assembly retains installed-state pegs."""
from common import *
from export import free_post,mesh_absolute
def run(pitch):
 out=HERE/f'{pitch}mm';m=read(out/'manufacturing.json')
 for p in m['parts']:
  if not p['name'].startswith('post-'):continue
  b=p['bounds_mm'];q=free_post((b[0][0]+b[1][0])/2,(b[0][1]+b[1][1])/2);q.label=p['name']+'-FREE-PEG-3.15-PROVISIONAL'
  base=out/'manufacturing'/p['filename'];export_step(q,base.with_suffix('.step'));mesh_absolute(import_step(base.with_suffix('.step')),base.with_suffix('.stl'))
  p.update(installed_volume_mm3=p.get('installed_volume_mm3',p['volume_mm3']),volume_mm3=q.volume,free_peg_od_mm=3.15,installed_peg_od_mm=3.10,step_sha256=sha(base.with_suffix('.step')),stl_sha256=sha(base.with_suffix('.stl')))
 save(out/'manufacturing.json',m)
if __name__=='__main__':run(int(sys.argv[1]))
