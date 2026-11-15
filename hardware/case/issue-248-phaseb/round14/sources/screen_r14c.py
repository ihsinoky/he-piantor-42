import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])

def s_of(i):
    ep=np.array(A[i][6],float)
    s=float(np.linalg.norm(np.array(A[i][5],float)-ep-np.array([0,0,0.35])))
    if i>=10: s=4.75-0.9*(i-9)   # unfloored stagger continuation
    return s

def build(i,t):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    G=(ep+s_of(i)*AX+np.array([0,0,0.35])).tolist()
    pts=[B[i][0],B[i][1],B[i][2],B[i][3],[ox,0.0,5.1],[ox,10.0,10.5]]
    if t>0: pts.append((np.array(G)+t*AX).tolist())
    pts+=[G,A[i][6]]
    return pts

def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)

def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))

def ev2(tfun,sname):
    P={i:build(i,tfun(i)) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
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
    print(f'{sname} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:6]} inv {invs}',flush=True)
    return P

if __name__=='__main__':
    ev2(lambda i: 8.0 if i>=8 else 0.0,'mixed t8 i>=8 (pins9-14)')
    ev2(lambda i: 8.0 if i>=7 else 0.0,'mixed t8 i>=7 (pins8-14)')
    ev2(lambda i: 8.0,'all t8 unfloor (pin1 preG outside case - reference)')
