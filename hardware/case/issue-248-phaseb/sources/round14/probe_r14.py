import sys, json
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE)
from common import *
from audit_repair import load_round9, common_shape, shape_volume
D=read(HERE/'routes-round9.json'); B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])
def s_of(i):
    ep=np.array(A[i][6],float)
    s=float(np.linalg.norm(np.array(A[i][5],float)-ep-np.array([0,0,0.35])))
    if i>=10: s=4.75-0.9*(i-9)
    return s
def build(i):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    G=(ep+s_of(i)*AX+np.array([0,0,0.35])).tolist()
    pre=(np.array(G)+8.0*AX).tolist()
    return [B[i][0],B[i][1],B[i][2],B[i][3],[ox,0.0,5.1],[ox,10.0,10.5],pre,G,A[i][6]]
idx,by_name=load_round9(17)
fixed={n:s for n,s in by_name.items() if not n.startswith('Wire')}
wires={}
for i in range(14):
    pts=build(i)
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
json.dump({'wire_fixed':hits},open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/probe_r14.json','w'),indent=1)
