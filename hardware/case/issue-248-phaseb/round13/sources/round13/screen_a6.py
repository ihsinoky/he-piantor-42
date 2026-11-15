import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
def build(i,fx0,boff):
    zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=fx0-1.25*i
    return [B[i][0],B[i][1],[fx,-18.0,5.1],[fx,-7.0,zf],[fx+boff,8.0,zf],G,ep]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
for fx0,boff in ((27.6,12.0),(28.85,10.0),(27.6,10.0)):
    P={i:build(i,fx0,boff) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); pairs.append((round(float(d.min()),3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.0])
    print(f'A6 fx0={fx0} boff={boff} min',min(pairs),'n_below',len(below),'below',below[:8],'longest+tails',round(max(plen(p) for p in P.values())+7.3,2),flush=True)
