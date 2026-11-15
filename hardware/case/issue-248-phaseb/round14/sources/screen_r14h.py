import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])
def build(i, rx0, L1, lam, bowamp):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    rx=rx0-1.25*i
    zc=5.3 if i%2==0 else 4.2
    zf=10.5 if i%2==0 else 9.6
    bow=bowamp if i%2==0 else -bowamp
    J=(ep+(L1-lam*i)*AX+np.array([0,0,0.35]))
    N=np.array([rx,8.0,zf]); M=(N+J)/2.0+np.array([0,0,bow])
    return [B[i][0],B[i][1],B[i][2],B[i][3],[ox-2.0,-21.0,zc],[rx,-16.0,zc],[rx,-7.0,zf],N.tolist(),M.tolist(),J.tolist(),A[i][6]]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
def ev(rx0,L1,lam,bowamp):
    P={i:build(i,rx0,L1,lam,bowamp) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
    below=sorted([p for p in pairs if p[0]<1.05])
    print(f'rx0={rx0} L1={L1} lam={lam} bow={bowamp} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:6]}',flush=True)
if __name__=='__main__':
    for L1,lam in ((21.4,1.3),(25.3,1.6),(23.0,1.45),(25.3,1.3)):
        ev(20.0,L1,lam,0.7)
