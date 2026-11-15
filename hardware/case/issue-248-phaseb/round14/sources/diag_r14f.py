import sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
idx,by_name=load_round9('17')
tray=by_name['tray-right']
from build123d import Box, Pos
def col(x,y,z0,z1):
    b=Pos(x,y,(z0+z1)/2)*Box(0.8,0.8,z1-z0)
    return shape_volume(common_shape(b,tray))
print('tray Z-profile (0.8 col, vol per 1mm slice):')
for (x,y) in ((16,-15),(18,-13),(14,-13),(13,-8),(16,-18),(11.9,-18),(10,-15)):
    prof=[]
    for z in range(2,13):
        v=col(x,y,z,z+1)
        prof.append(f'{z}:{v:.2f}')
    print(f'X{x} Y{y}: '+' '.join(prof),flush=True)
