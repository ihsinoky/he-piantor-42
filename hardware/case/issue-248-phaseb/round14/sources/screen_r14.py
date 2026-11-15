import json, itertools, sys
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']

def build(i, yr0, riselen, stagger, use_mid):
    ox=B[i][0][0]; G=A[i][5]; ep=A[i][6]
    y0=yr0+stagger*i; y1=y0+riselen
    pts=[B[i][0],B[i][1],B[i][2],B[i][3],[ox,y0,5.1],[ox,y1,10.5]]
    if use_mid:
        mx=(ox+G[0])/2.0; my=(y1+G[1])/2.0
        pts.append([mx,my,10.8])
    pts += [G,ep]
    return pts

def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)

def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))

def order_inv(S,Y):
    xs={}
    for i,s in S.items():
        cand=[p[0] for p in s if abs(p[1]-Y)<0.35]
        if cand: xs[i]=float(np.median(cand))
    base=[13-i for i in range(14)]  # west->east at outlet (idx13 westmost)
    order=[i for x,i in sorted((x,i) for i,x in xs.items())]
    pos={v:k for k,v in enumerate(order)}
    return sum(1 for a,b in itertools.combinations(base,2) if a in pos and b in pos and pos[a]>pos[b])

def evaluate(yr0,riselen,stagger,use_mid):
    P={i:build(i,yr0,riselen,stagger,use_mid) for i in range(14)}
    S={i:sample(p) for i,p in P.items()}
    pairs=[]; zones={}
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        k=np.unravel_index(np.argmin(d),d.shape); md=float(d[k]); mid=S[i][k[0]]
        pairs.append((round(md,3),i+1,j+1,round(float(mid[1]),1)))
        z='run' if mid[1]<-24.3 else ('north' if mid[1]<2 else ('rise/feed' if mid[1]<20 else 'approach'))
        zones.setdefault(z,[]).append((round(md,3),i+1,j+1))
    below=sorted([p for p in pairs if p[0]<1.05])
    invs={Y:order_inv(S,Y) for Y in (-30,-20,-10,0,10,20,30)}
    return dict(yr0=yr0,riselen=riselen,stagger=stagger,mid=use_mid,
        longest=round(max(plen(p) for p in P.values())+7.3,2),
        n_below=len(below),below=below[:10],min_pair=min(pairs),
        zone_min={z:min(v) for z,v in zones.items()},invs=invs)

if __name__=='__main__':
    results=[]
    for yr0 in (0.0,2.0,4.0):
        for riselen in (10.0,13.0):
            for stagger in (0.0,0.4):
                for use_mid in (False,True):
                    r=evaluate(yr0,riselen,stagger,use_mid)
                    results.append(r)
                    print({k:r[k] for k in ('yr0','riselen','stagger','mid','longest','n_below','min_pair')},'inv',r['invs'],flush=True)
    json.dump(results,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/screen_r14.json','w'),indent=1)
