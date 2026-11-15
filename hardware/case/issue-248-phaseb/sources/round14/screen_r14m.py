import json, itertools, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from design_r14 import design_points
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
def trim_need(pts):
    pts=[np.array(p,float) for p in pts]; worst=-1e9; corners={}
    for i in range(1,len(pts)-1):
        u=pts[i-1]-pts[i]; u/=np.linalg.norm(u); v=pts[i+1]-pts[i]; v/=np.linalg.norm(v)
        th=np.arccos(np.clip(float(np.dot(u,v)),-1,1)); d=5./np.tan(th/2)
        corners[i]=d if np.isfinite(d) else 0.0
    for i in range(len(pts)-1):
        worst=max(worst, corners.get(i,0)+corners.get(i+1,0)-np.linalg.norm(pts[i+1]-pts[i]))
    return worst
P={i:design_points(B,A,i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
pairs=[]; zones={}
for i,j in itertools.combinations(range(14),2):
    d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
    k=np.unravel_index(np.argmin(d),d.shape); md=float(d[k]); mid=S[i][k[0]]
    pairs.append((round(md,3),i+1,j+1,round(float(mid[1]),1)))
    z='run' if mid[1]<-24.3 else ('conv' if mid[1]<-12 else ('west' if mid[1]<8 else 'feed'))
    zones.setdefault(z,[]).append((round(md,3),i+1,j+1))
below=sorted([p for p in pairs if p[0]<1.05])
print(f'v5 longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)}')
print('below:',below[:8])
print('zones:',{z:min(v) for z,v in zones.items()})
print('trim worst:',round(max(trim_need(p) for p in P.values()),3))
