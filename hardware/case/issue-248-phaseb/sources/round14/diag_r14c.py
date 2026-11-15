import sys, json
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE); sys.path.insert(0,f'{HERE}/sources/round14')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
from design_r14 import design_points
D=read(HERE/'routes-round9.json'); B,A=D['before'],D['after']
idx,by_name=load_round9(17)
def mkwire(i):
    pts=design_points(B,A,i); path=rounded(pts)
    d0=np.array(pts[1],float)-np.array(pts[0],float)
    return sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
CASES=[(0,'wing_right'),(0,'switch-envelope-R_R2_C5'),(0,'switch-envelope-R_R1_C5'),(0,'underside-right-U_MUX_B'),
       (3,'tray-right'),(5,'tray-right'),(6,'tray-right'),(2,'underside-right-U_MUX_B'),
       (12,'POM-right-H2'),(13,'POM-right-H2'),(12,'tray-right'),(10,'tray-right'),(12,'plate-screw-right-H2')]
cache={}
for wi,tn in CASES:
    if wi not in cache: cache[wi]=mkwire(wi)
    c=common_shape(cache[wi],by_name[tn]); v=shape_volume(c) if c is not None else 0.0
    print(f'wire{wi+1} x {tn}: {round(v,4)} bounds {[[round(x,2) for x in row] for row in bounds(Shape.cast(c))] if v>1e-6 else None}',flush=True)
for tn in ('POM-right-H2','plate-screw-right-H2','tray-right','underside-right-U_MUX_B','underside-right-U_MUX_C'):
    print(tn,'bounds',[[round(x,2) for x in row] for row in bounds(by_name[tn])],flush=True)
