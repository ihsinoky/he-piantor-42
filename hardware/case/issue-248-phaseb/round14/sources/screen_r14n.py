import json, itertools, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from design_r14 import design_points
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
def sample(pts,step=0.15):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
P={i:design_points(B,A,i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
for (i,j) in ((7,9),(2,4),(3,8),(1,5)):
    d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
    k=np.unravel_index(np.argmin(d),d.shape)
    print(f'pair {i+1}-{j+1} min {d[k]:.3f} at {np.round(S[i][k[0]],2)} vs {np.round(S[j][k[1]],2)}',flush=True)
