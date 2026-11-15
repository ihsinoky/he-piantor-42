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
    N=np.array([rx,8.0,zf])
    M=(N+J)/2.0+np.array([0,0,bow])
    return [B[i][0],B[i][1],B[i][2],B[i][3],[rx,-16.0,zc],[rx,-7.0,zf],N.tolist(),M.tolist(),J.tolist(),A[i][6]]

def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)

def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))

def ev(rx0,L1,lam,bowamp):
    P={i:build(i,rx0,L1,lam,bowamp) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]; zones={}
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape); md=float(d[k]); mid=S[i][k[0]]
        pairs.append((round(md,3),i+1,j+1,round(float(mid[1]),1)))
        z='run' if mid[1]<-24.3 else ('conv' if mid[1]<-16 else ('west' if mid[1]<8 else 'feed'))
        zones.setdefault(z,[]).append((round(md,3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.05])
    invs={}
    for Y in (-30,-20,-10,0,10,20,30):
        xs={}
        for i,s in S.items():
            cand=[p[0] for p in s if abs(p[1]-Y)<0.35]
            if cand: xs[i]=float(np.median(cand))
        base=[13-i for i in range(14)]
        order=[i for x,i in sorted((x,i) for i,x in xs.items())]
        pos={v:k for k,v in enumerate(order)}
        invs[Y]=sum(1 for a,b in itertools.combinations(base,2) if a in pos and b in pos and pos[a]>pos[b])
    print(f'rx0={rx0} L1={L1} lam={lam} bow={bowamp} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:6]} zones { {z:min(v) for z,v in zones.items()} } inv {invs}',flush=True)

if __name__=='__main__':
    for rx0 in (20.0,21.0):
        for bowamp in (0.5,0.7,0.9):
            ev(rx0,16.15,0.9,bowamp)
