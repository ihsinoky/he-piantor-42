import sys, json
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE); sys.path.insert(0,f'{HERE}/sources/round14')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
idx,by_name=load_round9(17)
from build123d import Solid
def col(x,y,z0,z1,w=0.8):
    return Solid.make_box(w,w,z1-z0,Plane(origin=Vector(x-w/2,y-w/2,z0)))
print('--- tray columns at Y=-11, Z0..14 (rise band) ---')
for X in range(6,24):
    c=common_shape(col(X,-11,0,14),by_name['tray-right']); v=shape_volume(c) if c is not None else 0.0
    print(f'X={X} tray vol {round(v,2)}',flush=True)
print('--- wing columns at Y=-11, Z7..9 (PCB slab) ---')
for X in range(14,26):
    c=common_shape(col(X,-11,7,9),by_name['wing_right']); v=shape_volume(c) if c is not None else 0.0
    print(f'X={X} wing vol {round(v,2)}',flush=True)
print('--- tray columns at Y=-19, Z3..7 (convergence band) ---')
for X in range(8,18):
    c=common_shape(col(X,-19,3,7),by_name['tray-right']); v=shape_volume(c) if c is not None else 0.0
    print(f'X={X} tray vol {round(v,2)}',flush=True)
