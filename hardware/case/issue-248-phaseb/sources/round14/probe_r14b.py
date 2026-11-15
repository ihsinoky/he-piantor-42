import sys, json
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE); sys.path.insert(0,f'{HERE}/sources/round14')
from common import *
from audit_repair import load_round9, common_shape, shape_volume
from design_r14 import design_points
D=read(HERE/'routes-round9.json'); B,A=D['before'],D['after']
idx,by_name=load_round9(17)
fixed={n:s for n,s in by_name.items() if not n.startswith('Wire')}
wires={}
for i in range(14):
    pts=design_points(B,A,i)
    path=rounded(pts)
    d0=np.array(pts[1],float)-np.array(pts[0],float)
    q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
    wires[f'A-right-{i+1:02d}']=q
    print('built',i+1,'len',round(path.length,2),flush=True)
_c=common_shape(wires['A-right-01'],wires['A-right-01']); print('CONTROL',round(shape_volume(_c),2),flush=True)
hits={}
for wn,w in wires.items():
    for fn,f in fixed.items():
        try:
            c=common_shape(w,f); v=shape_volume(c) if c is not None else 0.0
        except Exception as e:
            v=-1; print('ERR',wn,fn,e,flush=True)
        if v and v>1e-6: hits.setdefault(wn,{})[fn]=round(v,4)
print('WIRE-FIXED HITS:',json.dumps(hits),flush=True)
json.dump({'wire_fixed':hits},open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/probe_r14b.json','w'),indent=1)
