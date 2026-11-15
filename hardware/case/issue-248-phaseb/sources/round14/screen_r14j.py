import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])
def build(i, LF, mshift):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    rx=21.0-1.25*i
    zc=5.3 if i%2==0 else 4.2
    zf=10.5 if i%2==0 else 9.6
    bow=0.7 if i%2==0 else -0.7
    L=max(25.3-1.6*i, LF)
    J=(ep+L*AX+np.array([0,0,0.35]))
    N=np.array([rx,8.0,zf]); M=(N+J)/2.0+np.array([mshift[0],mshift[1],bow])
    B3=[ox,-24.3, 5.65 if i%2==0 else 4.55]
    return [B[i][0],B[i][1],B[i][2],B3,[rx,-16.0,zc],[rx,-7.0,zf],N.tolist(),M.tolist(),J.tolist(),A[i][6]]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);Ln=np.linalg.norm(b-a);n=max(2,int(Ln/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
def trim_need(pts):
    # replicate geometry.rounded trim check: max over segments of (d_i + d_{i+1}) - len
    pts=[np.array(p,float) for p in pts]; worst=-1e9
    corners={}
    for i in range(1,len(pts)-1):
        u=pts[i-1]-pts[i]; u/=np.linalg.norm(u); v=pts[i+1]-pts[i]; v/=np.linalg.norm(v)
        th=np.arccos(np.clip(float(np.dot(u,v)),-1,1)); d=5./np.tan(th/2)
        corners[i]=d if np.isfinite(d) else 0.0
    for i in range(len(pts)-1):
        need=(corners.get(i,0)+corners.get(i+1,0))
        worst=max(worst, need-np.linalg.norm(pts[i+1]-pts[i]))
    return worst
def ev(LF,mshift):
    P={i:build(i,LF,mshift) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.05])
    tw=max(trim_need(p) for p in P.values())
    print(f'LF={LF} mshift={mshift} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} trim_worst {round(tw,3)}',flush=True)
if __name__=='__main__':
    for LF in (5.5,6.5):
        for ms in ((2.5,-1.5),(1.5,-1.0),(0.0,0.0)):
            ev(LF,ms)
