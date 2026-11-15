import sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
from build123d import Box, Pos
idx,by_name=load_round9('17')
tray=by_name['tray-right']
def cell(x,y,zc,s=0.3):
    b=Pos(x,y,zc)*Box(s,s,1.0)
    return shape_volume(common_shape(b,tray))
print('rib scan X=17.5: rows Y, cols Z=3..12 (vol):')
for y in (-16.0,-15.5,-15.0,-14.5,-14.0,-13.5,-13.0):
    row=[]
    for z in range(3,13):
        row.append(f'{cell(17.5,y,z+0.5):.2f}')
    print(f'Y{y}: '+' '.join(row),flush=True)
print('rib scan Y=-14.5: rows X=16.5..18.5, cols Z=3..12:')
for x in (16.5,17.0,17.5,18.0,18.5):
    row=[]
    for z in range(3,13):
        row.append(f'{cell(x,-14.5,z+0.5):.2f}')
    print(f'X{x}: '+' '.join(row),flush=True)
