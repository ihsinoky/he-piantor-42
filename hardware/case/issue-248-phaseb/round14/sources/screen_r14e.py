import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])
def build(i, rx0, L1, lam, feedy):
    ox=B[i][0][0]; ep=np.array(A[i][6],float); zf=A[i][3][2]
    rx=rx0-1.25*i
    J=(ep+(L1-lam*i)*AX+np.array([0,0,0.35])).tolist()
    pts=[B[i][0],B[i][1],B[i][2],B[i][3],[rx,-13.5,5.1],[rx,-7.0,zf]]
    if feedy>-7: pts.append([rx,8.0,zf])
    pts+=[J,A[i][6]]
    return pts
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
def ev(rx0,L1,lam,feedy):
    P={i:build(i,rx0,L1,lam,feedy) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
    below=sorted([p for p in pairs if p[0]<1.05])
    print(f'rx0={rx0} L1={L1} lam={lam} feedy={feedy} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:5]}',flush=True)
if __name__=='__main__':
    for feedy in (8,-7):
        for rx0 in (19.0,20.0,21.0):
            for L1 in (15.5,16.15,17.0):
                ev(rx0,L1,0.9,feedy)
