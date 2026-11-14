"""Independent reload of shipped manufacturing STEP/STL, including rejected parts."""
from common import *
import importlib.util
spec=importlib.util.spec_from_file_location('verify232',HERE.parent/'issue-232-final/verify.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def run(pitch):
 out=HERE/f'{pitch}mm';m=read(out/'manufacturing.json');checks=[]
 for p in m['parts']:
  n=p['name'];base=out/'manufacturing'/p['filename'];q=import_step(base.with_suffix('.step'));b=q.bounding_box();mesh=old.meshcheck(base.with_suffix('.stl'),q)
  row=dict(part=n,valid=q.is_valid,solids=len(q.solids()),step_volume_delta_mm3=abs(q.volume-p['volume_mm3']),brim_xy_mm=[b.size.X+10,b.size.Y+10],mesh=mesh,step_sha256=sha(base.with_suffix('.step')),stl_sha256=sha(base.with_suffix('.stl')))
  row['passed']=q.is_valid and len(q.solids())==1 and max(row['brim_xy_mm'])<=220 and b.size.Z<=250 and row['step_volume_delta_mm3']<1e-4 and mesh['nonmanifold_edges']==0 and mesh['degenerate_triangles']==0 and mesh['volume_relative_error']<.001 and row['step_sha256']==p['step_sha256'] and row['stl_sha256']==p['stl_sha256']
  checks.append(row);print(pitch,n,row['passed'],flush=True)
 preview=out/'fitted-assembly-PROVISIONAL.step';ass=import_step(preview)
 count=sum(len(q.solids()) for n,q in leaves(ass));expected=sum(not r['name'].startswith('USB-reference-') for r in read(out/'assembly-index.json'))
 save(out/'export-verification.json',dict(status=P['status'],checks=checks,passed=all(r['passed'] for r in checks),preview_exists=preview.exists(),preview_reloaded_solids=count,preview_expected_solids=expected,preview_inventory_passed=count==expected,preview_sha256=sha(preview),geometry_sha256=sha(out/'assembly-index.json')))
if __name__=='__main__':run(int(sys.argv[1]))
