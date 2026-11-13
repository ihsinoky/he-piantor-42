"""Independent exact protected-region comparison, reloading audit/source BReps."""
import sys,json,os
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
from build123d import Shape
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(path):
 s=TopoDS_Shape();BRepTools.Read_s(s,str(path),BRep_Builder());return Shape.cast(s)
def clip(a,b):return Compound(children=list(a.intersect(b)))
def main(pitch):
 delta=float(os.environ.get('HEIGHT_DELTA','6'));runtime=ROOT/'.issue244-runtime';src=runtime/f'cache{pitch}';audit=runtime/f'delta-{delta:g}'/f'audit{pitch}'
 sn=json.loads((src/'index.json').read_text())['names'];an=json.loads((audit/'index.json').read_text())
 # Compare the rigidly raised protected seat/opening, above the Z3 extension.
 region=prism(box(-13,-100,13,-39),3.001,39.999)
 low=prism(box(-200,-100,200,100),0,1.199)
 results={}
 for side in ('left','right'):
  name='tray-'+side;a=load(src/f'{sn.index(name)}.brep');indices=[i for i,r in enumerate(an) if r['name']==name]
  assert indices
  bg=Compound(children=[load(audit/f'{j}.brep') for j in indices])
  b=bg.translate((0,0,-delta))
  ar=clip(a,region);br=clip(b,region);common=volume(ar,br)
  results[side]=dict(fly_scope_added_mm3=max(0,br.volume-common),fly_scope_removed_mm3=max(0,ar.volume-common),lower_floor_delta_mm3=volume(bg,low)-volume(a,low),new_tray_valid=b.is_valid,new_tray_solids=len(b.solids()))
  print(pitch,side,results[side],flush=True)
 result=dict(volume_comparison_tolerance_mm3=1e-4,comparison_datum='raised assembly translated down by Delta; above extension',protected_Fly_box_xyz_mm=[[-13,-100,3.001],[13,-39,43]],parts=results,fly_scope_unchanged=all(max(r['fly_scope_added_mm3'],r['fly_scope_removed_mm3'])<1e-4 for r in results.values()),floor_below_Z1_199_unchanged=all(abs(r['lower_floor_delta_mm3'])<1e-4 for r in results.values()))
 save(HERE/f'delta-{delta:g}'/f'{pitch}mm/invariants.json',result)
if __name__=='__main__':main(int(sys.argv[1]))
