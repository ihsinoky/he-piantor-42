import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
def build(i):
    fan=A[i][2]  # round 9 fan point (fx,-18,pz)
    return [B[i][0],B[i][1],B[i][2],B[i][3],fan,A[i][3],A[i][4],A[i][5],A[i][6]]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
P={i:build(i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
pairs=[]
for i,j in itertools.combinations(range(14),2):
    d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); k=np.unravel_index(np.argmin(d),d.shape)
    pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
below=sorted([p for p in pairs if p[0]<1.0])
print('A8 min',min(pairs),'n_below',len(below))
print('below (dist,pinA,pinB,atY):',below[:20])
print('longest+tails',round(max(plen(p) for p in P.values())+7.3,2))
json.dump({'below':below,'longest+tails':round(max(plen(p) for p in P.values())+7.3,2)},open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/screen_a8.json','w'),indent=1)
