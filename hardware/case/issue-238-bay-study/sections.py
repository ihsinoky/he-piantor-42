"""Extract exact X=0 BRep section edges of the retained assembly for SVG review."""
import sys,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import leaves,import_step,save
from build123d import Plane

def extract():
 data=[]
 for n,s in leaves(import_step(HERE.parent/'issue-232-final/17mm/assembly.step')):
  if n not in ('tray-left','tray-right','main','cable-rack','EZmate-Fly-plug','EZmate-Main-plug') and not n.startswith('Fly-official-'):continue
  if not s.is_valid:continue # D-037 invalid USB shell explicitly disclosed; use its measured external bbox separately.
  b=s.bounding_box()
  if b.min.X>0 or b.max.X<0:continue
  for face in s.intersect(Plane.YZ) or []:
   for e in face.edges():
    count=max(2,math.ceil(e.length/.1));p=e.positions([i/count for i in range(count+1)])
    data.append(dict(part=n,yz_mm=[[v.Y,v.Z] for v in p]))
 save(HERE/'section-x0.json',data)
if __name__=='__main__':extract()
