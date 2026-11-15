import sys, json
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0,HERE)
from common import *
from audit_repair import load_round9, common_shape, shape_volume
exec(open(f'{HERE}/sources/round14/probe_r14.py').read().split('idx,by_name')[0].split('from audit_repair')[0])
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
def mkwire(i):
    pts=build(i); path=rounded(pts)
    d0=np.array(pts[1],float)-np.array(pts[0],float)
    return sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
idx,by_name=load_round9(17)
for wi,targets in ((0,['wing_right','underside-right-U_HC1','switch-envelope-R_R1_C5','switch-envelope-R_R0_C5']),(13,['wing_right','tray-right']),(5,['wing_right'])):
    w=mkwire(wi)
    for tn in targets:
        c=common_shape(w,by_name[tn]); v=shape_volume(c) if c is not None else 0.0
        print(f'wire{wi+1} x {tn}: vol {round(v,4)} bounds {bounds(Shape.cast(c)) if v>1e-6 else None}',flush=True)
# round 9's own wire 1 vs wing_right for reference
w9=by_name['Wire-right-01']
for tn in ('wing_right','switch-envelope-R_R1_C5','underside-right-U_HC1'):
    c=common_shape(w9,by_name[tn]); v=shape_volume(c) if c is not None else 0.0
    print(f'R9 wire1 x {tn}: vol {round(v,4)}',flush=True)
print('env R1_C5 bounds',bounds(by_name['switch-envelope-R_R1_C5']))
print('env R0_C5 bounds',bounds(by_name['switch-envelope-R_R0_C5']))
print('U_HC1 bounds',bounds(by_name['underside-right-U_HC1']))
print('C_HC1 bounds',bounds(by_name['underside-right-C_HC1']))
print('wing_right bounds',bounds(by_name['wing_right']))
