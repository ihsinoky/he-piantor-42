import sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
from build123d import Box, Pos
idx,by_name=load_round9('17')
tray=by_name['tray-right']
def cell(x,y,zc):
    b=Pos(x,y,zc)*Box(0.9,0.9,1.0)
    return shape_volume(common_shape(b,tray))
for zc in (5.0,9.0):
    print(f'--- tray occupancy at Z {zc} (X=9..21 across, Y rows) ---',flush=True)
    print('Y\\X '+' '.join(f'{x:4d}' for x in range(9,22)),flush=True)
    for y in range(-18,-4):
        row=[]
        for x in range(9,22):
            v=cell(x,y,zc)
            row.append('####' if v>0.4 else ('....' if v<0.02 else f'{v:.2f}'))
        print(f'{y:3d} '+' '.join(row),flush=True)
