import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
a=np.array([0.866025,-0.5,0.0])
def build(i,fx0,ext):
    zf=A[i][3][2]; G=np.array(A[i][5],float); ep=A[i][6]; fx=fx0-1.25*i
    E=G+a*ext; E[2]=zf
    return [B[i][0],B[i][1],[fx,-18.0,5.1],[fx,-7.0,zf],list(E),A[i][5],ep]
def sample(pts,step=0.2):
    out=[]
    for p,q in zip(pts,pts[1:]):
        p=np.array(p,float);q=np.array(q,float);L=np.linalg.norm(q-p);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(p+(q-p)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(x,float)) for x,b in zip(p,p[1:]))
for fx0,ext in ((28.85,9.0),(28.85,13.0),(27.6,9.0)):
    P={i:build(i,fx0,ext) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); pairs.append((round(float(d.min()),3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.0])
    inv=0
    print(f'A7 fx0={fx0} ext={ext} min',min(pairs),'n_below',len(below),'below',below[:8],'longest+tails',round(max(plen(p) for p in P.values())+7.3,2),flush=True)
