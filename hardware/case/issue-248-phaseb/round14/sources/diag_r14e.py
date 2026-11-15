import json, sys
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import tube
from audit_repair import load_round9, common_shape, shape_volume
from design_r14 import design_points
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

def bbox(s):
    b=Bnd_Box(); BRepBndLib.Add_s(getattr(s,'wrapped',s),b,True)
    return tuple(round(v,2) for v in (b.GetXMin(),b.GetXMax(),b.GetYMin(),b.GetYMax(),b.GetZMin(),b.GetZMax()))

HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
idx,by_name=load_round9('17')
tray=by_name['tray-right']
for i in (0,1,2,12):
    solid,_=tube([tuple(p) for p in design_points(B,A,i)],0.5)
    c=common_shape(solid,tray); v=shape_volume(c)
    print(f'wire {i+1} vs tray: {v:.4f} bounds(x0,x1,y0,y1,z0,z1) {bbox(c) if v>1e-9 else None}',flush=True)
