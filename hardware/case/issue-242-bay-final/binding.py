"""Extract exact PCB/cable intersection and true Y=constant BRep sections."""
import sys,json
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
def main(pitch):
 out=HERE/f'{pitch}mm';a=json.loads((out/'audit.json').read_text());rows=[]
 for side in ('left','right'):
  hs=[r for r in a['unexpected_interferences'] if {r['a'],r['b']}=={'wing_'+side,'Wing-'+side+'-upper'}];r=max(hs,key=lambda r:r['volume_mm3'])
  cache=ROOT/f'.issue242-runtime/audit{pitch}';board=load(cache/f"{r['i']}.brep");wire=load(cache/f"{r['j']}.brep")
  common=Compound(children=list(board.intersect(wire)));assert abs(common.volume-r['volume_mm3'])<1e-5
  b=common.bounding_box();c=common.center();x,y=c.X,c.Y
  plane=Face(Wire.make_polygon([Vector(x-8,y,8),Vector(x+8,y,8),Vector(x+8,y,14.5),Vector(x-8,y,14.5)],close=True))
  sections={}
  for name,s in [('Wing PCB',board),('Rising conductor',wire)]:
   curves=[]
   for face in s.intersect(plane):
    for edge in face.edges():curves.append([[v.X,v.Z] for v in edge.positions([j/40 for j in range(41)])])
   sections[name]=curves
  export_step(common,out/f'binding-{side}-intersection-REJECTED.step')
  rows.append(dict(side=side,pitch_mm=pitch,source_pair=r,overlap_mm3=common.volume,overlap_bounds_mm=[[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']],section_Y_mm=y,section_center_X_mm=x,section_edges_XZ_mm=sections))
 save(out/'binding-sections.json',rows)
if __name__=='__main__':main(int(sys.argv[1]))
