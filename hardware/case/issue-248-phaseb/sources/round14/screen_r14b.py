import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
AX=np.array([0.8660254,-0.5,0.0])  # connector axis unit, G = ep + s*AX + 0.35z

def build(i, t, smod):
    ox=B[i][0][0]; ep=np.array(A[i][6],float)
    s=np.linalg.norm(np.array(A[i][5],float)-ep-np.array([0,0,0.35]))
    if smod is not None: s=smod(i,s)
    G=ep+s*AX+np.array([0,0,0.35]); G=G.tolist()
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

def ev(t,smod=None,sname='r9s'):
    P={i:build(i,t,smod) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
    below=sorted([p for p in pairs if p[0]<1.05])
    print(f't={t} s={sname} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:8]}',flush=True)
    return below

if __name__=='__main__':
    for t in (0,4,6,8,10,12):
        ev(t)
    # unfloor pins 11-14: continue the -0.9 slope from pin10 s=4.75 down to 2.0 min
    ev(8, smod=lambda i,s: (4.75-0.9*(i-9)) if i>=10 else s, sname='unfloor')
    ev(8, smod=lambda i,s: max(4.75-0.9*(i-9),2.6) if i>=10 else s, sname='unfloor26')

def ev2(tfun,sname):
    def build2(i):
        ox=B[i][0][0]; ep=np.array(A[i][6],float)
        s=np.linalg.norm(np.array(A[i][5],float)-ep-np.array([0,0,0.35]))
        if i>=10: s=4.75-0.9*(i-9)
        G=(ep+s*AX+np.array([0,0,0.35])).tolist()
        pts=[B[i][0],B[i][1],B[i][2],B[i][3],[ox,0.0,5.1],[ox,10.0,10.5]]
        t=tfun(i)
        if t>0: pts.append((np.array(G)+t*AX).tolist())
        pts+=[G,A[i][6]]
        return pts
    P={i:build2(i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape)
        pairs.append((round(float(d[k]),3),i+1,j+1,round(float(S[i][k[0]][1]),1)))
    below=sorted([p for p in pairs if p[0]<1.05])
    print(f'{sname} longest {round(max(plen(p) for p in P.values())+7.3,2)} n_below {len(below)} min {min(pairs)} below {below[:6]}',flush=True)

if __name__=='__main__' and len(sys.argv)>1:
    pass
