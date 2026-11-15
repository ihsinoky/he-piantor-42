import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
def build(i,bowstag,fanstag):
    x=B[i][0][0]; zf=A[i][3][2]+(1.15 if (bowstag and i%2) else 0.0); G=A[i][5]; ep=A[i][6]; fx=25.1-1.25*i
    zfan=5.1+(1.15 if (fanstag and i%2) else 0.0)
    return [B[i][0],B[i][1],B[i][2],B[i][3],[fx,-18.0,zfan],[fx,-7.0,zf],[fx+12.0,8.0,zf],G,ep]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
for name,bs,fs in (('V1 bow stagger',True,False),('V2 bow+fan stagger',True,True)):
    P={i:build(i,bs,fs) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); pairs.append((round(float(d.min()),3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.0])
    print(name,'min',min(pairs),'n_below',len(below),'below',below[:8],'longest+tails',round(max(plen(p) for p in P.values())+7.3,2),flush=True)
