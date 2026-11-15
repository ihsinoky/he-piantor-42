import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])
def build(i):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    rx=20.0-1.25*i
    zc=5.3 if i%2==0 else 4.2
    zf=10.5 if i%2==0 else 9.6
    bow=0.7 if i%2==0 else -0.7
    J=(ep+(16.15-0.9*i)*AX+np.array([0,0,0.35]))
    N=np.array([rx,8.0,zf]); M=(N+J)/2.0+np.array([0,0,bow])
    pts=[B[i][0],B[i][1],B[i][2],B[i][3],[ox-2.0,-21.0,zc],[rx,-16.0,zc],[rx,-7.0,zf],N.tolist(),M.tolist(),J.tolist(),A[i][6]]
    return pts
def sample_seg(pts,step=0.1):
    # returns samples with segment index
    out=[]
    for si,(a,b) in enumerate(zip(pts,pts[1:])):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append((si,a+(b-a)*tt))
    out.append((len(pts)-2,np.array(pts[-1],float)))
    return out
P={i:build(i) for i in range(14)}
S={i:sample_seg(p) for i,p in P.items()}
names=['B0-1','B1-2','B2-3','B3-dive','dive-C','C-R','R-N','N-M','M-J','J-ep']
for i,j in ((12,13),(11,12),(0,1)):
    a=[s for s in S[i]]; b=[s for s in S[j]]
    A_ = np.array([s[1] for s in a]); B_=np.array([s[1] for s in b])
    d=np.linalg.norm(A_[:,None,:]-B_[None,:,:],axis=2)
    k=np.unravel_index(np.argmin(d),d.shape)
    print(f'pair pins {i+1}-{j+1}: min {d[k]:.3f} seg {names[a[k[0]][0]]} pt {np.round(A_[k[0]],2)} x seg {names[b[k[1]][0]]} pt {np.round(B_[k[1]],2)}',flush=True)
    # also per-segment-pair minima summary for this pair
    seen={}
    for si in range(10):
        for sj in range(10):
            ia=[n for n,s in enumerate(a) if s[0]==si]; ib=[n for n,s in enumerate(b) if s[0]==sj]
            if ia and ib:
                dd=d[np.ix_(ia,ib)]; seen[(names[si],names[sj])]=round(float(dd.min()),3)
    close={k:v for k,v in seen.items() if v<1.3}
    print('  seg-pair mins <1.3:',close,flush=True)
