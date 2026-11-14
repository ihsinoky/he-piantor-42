"""Regenerate absolute-tolerance STL from final STEP, never alter CAD or relax tests."""
from common import *
from export import mesh_absolute
def run(pitch):
 out=HERE/f'{pitch}mm';m=read(out/'manufacturing.json')
 for p in m['parts']:
  base=out/'manufacturing'/p['filename'];q=import_step(base.with_suffix('.step'))
  mesh_absolute(q,base.with_suffix('.stl'));p['stl_sha256']=sha(base.with_suffix('.stl'))
  print(pitch,p['name'],'absolute mesh exported',flush=True)
 m['stl_absolute_deflection_mm']=.005;m['stl_angular_deflection_radians']=.025
 save(out/'manufacturing.json',m)
if __name__=='__main__':run(int(sys.argv[1]))
