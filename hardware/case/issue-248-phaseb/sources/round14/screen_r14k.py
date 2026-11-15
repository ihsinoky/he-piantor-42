import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])

def build(i, lx0, lxstep, L1, lam, bowamp):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    lx=lx0+lxstep*(13-i)
    zc=4.9 if i%2==0 else 3.8
    zf=10.5 if i%2==0 else 9.6
    bow=bowamp if i%2==0 else -bowamp
    J=(ep+(L1-lam*i)*AX+np.array([0,0,0.35]))
    S=np.array([lx+12.0,8.0,zf]); M=(S+J)/2.0+np.array([3.5,-2.0,bow])
    B3=[ox,-24.3, 5.25 if i%2==0 else 4.15]
    return [B[i][0],B[i][1],B[i][2],B3,[lx,-16.0,zc],[lx,-7.0,zf],S.tolist(),M.tolist(),J.tolist(),A[i][6]]

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

def ev(lx0,lxstep,L1,lam,bowamp):
    P={i:build(i,lx0,lxstep,L1,lam,bowamp) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
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
    tw=max(trim_need(p) for p in P.values())
    print(f'lx0={lx0} step={lxstep} L1={L1} lam={lam} bow={bowamp} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:5]} zones { {z:min(v) for z,v in zones.items()} } inv {invs} trim {round(tw,3)}',flush=True)

if __name__=='__main__':
    for lxstep in (0.75,0.85):
        ev(3.0,lxstep,25.3,1.6,0.7)
