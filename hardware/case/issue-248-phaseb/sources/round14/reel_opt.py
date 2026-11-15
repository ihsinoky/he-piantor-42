"""Reel fans optimisation. Fan1: rise-top -> F1a -> F1b -> E_i (reel entry).
Fan2: Y_i (fixed exit-tangent point) -> F2a -> P_i. Fixed samples include
the reel arcs (R=9.2) and all other fixed chains."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14 as dz
import reel
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
R0=9.2
def ceiling(y):
    if y<1.935593: return 22.65-1.0
    t=min(max((y-1.935593)/36.578838,0),1)
    return 24.65-11.10*t-2.0-1.0
def arc_samples(i,R=R0):
    e=reel.entry(i,R); m=reel.midp(i,R); x=reel.exitp(i,R)
    # circle through e,m,x in plane z=z_i: sample by angle
    C=reel.C; z=reel.z_of(i)
    a0=np.arctan2(e[1]-C[1],e[0]-C[0])
    pts=[]
    for k in range(25):
        ang=a0-np.radians(270.0)*k/24.0
        pts.append(np.array([C[0]+R*np.cos(ang),C[1]+R*np.sin(ang),z]))
    return pts
def y_point(i,R=R0):
    x=reel.exitp(i,R)
    t=np.array([-0.70710678,-0.70710678,0.0])
    return x+8.0*t
def base_fixed(i):
    pts=[]
    ep,G,P=dz.stations(B,A,i)
    for a,b in ((np.array(B[i][0],float),np.array(B[i][1],float)),
                (np.array(B[i][1],float),dz.corridor(i)),
                (dz.corridor(i),dz.rise_top(B,A,i)),
                (P,G),(G,ep)):
        for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(b)
    pts+= arc_samples(i)
    return np.array(pts)
FIX={i:base_fixed(i) for i in range(14)}
def run_opt(origins,targets,nvar,fixed_extra,label):
    """origins/targets: per-strand arrays; nvar points per strand.
    fixed_extra: per-strand additional fixed sample arrays."""
    FIXL={i:np.vstack([FIX[i],fixed_extra[i]]) if fixed_extra[i] is not None else FIX[i] for i in range(14)}
    FIXALL=np.vstack([FIXL[i] for i in range(14)])
    FIXOWN=np.concatenate([[i]*len(FIXL[i]) for i in range(14)])
    def var_samples(x,i):
        ms=[x[i*3*nvar+k*3:i*3*nvar+k*3+3] for k in range(nvar)]
        ch=[origins[i]]+ms+[targets[i]]; pts=[]
        for a,b in zip(ch,ch[1:]):
            for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(targets[i]); return np.array(pts)
    X0=[]; BND=[]
    for i in range(14):
        for k in range(nvar):
            fr=(k+1)/(nvar+1)
            m=origins[i]+(targets[i]-origins[i])*fr
            X0+= list(m); BND+= [(-12,46),(-16,44),(3.4,21.8)]
    X0=np.array(X0,float)
    def objective(x):
        allp=[]; allo=[]
        for i in range(14):
            sp=var_samples(x,i); allp.append(sp); allo+=[i]*len(sp)
        allp=np.vstack(allp); allo=np.array(allo)
        comb=np.vstack([allp,FIXALL]); own=np.concatenate([allo,FIXOWN])
        tree=cKDTree(comb); loss=0.0
        for a,b in tree.query_pairs(1.6):
            if own[a]==own[b]: continue
            if a>=len(allp) and b>=len(allp): continue
            d=np.linalg.norm(comb[a]-comb[b])
            if d<1.3: loss+=((1.3-d)/0.3)**2
        for p in allp:
            c=ceiling(p[1])
            if p[2]>c: loss+=((p[2]-c)/0.3)**2*2
        for i in range(14):
            ms=[x[i*3*nvar+k*3:i*3*nvar+k*3+3] for k in range(nvar)]
            d1=np.linalg.norm(ms[-1]-targets[i]); d0=np.linalg.norm(ms[0]-origins[i])
            if d1<11.0: loss+=((11.0-d1)/1.5)**2*10.0
            if d0<9.0: loss+=((9.0-d0)/1.5)**2*10.0
            ch=[origins[i]]+ms+[targets[i]]
            for k in range(1,len(ch)-1):
                u=ch[k]-ch[k-1]; v=ch[k+1]-ch[k]
                c=float(np.dot(u,v)/(np.linalg.norm(u)*np.linalg.norm(v)+1e-9))
                if c<0.35: loss+=((0.35-c)/0.2)**2*6.0
        return loss+0.001*np.sum((x-X0)**2)
    def minpair(x):
        allp=[]; allo=[]
        for i in range(14):
            sp=var_samples(x,i); allp.append(sp); allo+=[i]*len(sp)
        allp=np.vstack(allp); allo=np.array(allo)
        comb=np.vstack([allp,FIXALL]); own=np.concatenate([allo,FIXOWN])
        tree=cKDTree(comb); best=(9,None)
        for a,b in tree.query_pairs(2.2):
            if own[a]==own[b]: continue
            if a>=len(allp) and b>=len(allp): continue
            d=np.linalg.norm(comb[a]-comb[b])
            if d<best[0]: best=(d,(own[a]+1,own[b]+1,tuple(np.round(comb[a],1))))
        return best
    print(label,'init min',minpair(X0),flush=True)
    res=minimize(objective,X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
    print(label,'loss',round(res.fun,3),'min',minpair(res.x),flush=True)
    return {i:[res.x[i*3*nvar+k*3:i*3*nvar+k*3+3] for k in range(nvar)] for i in range(14)}
ORG={i:dz.rise_top(B,A,i) for i in range(14)}
ENT={i:reel.entry(i,R0) for i in range(14)}
fan1=run_opt(ORG,ENT,2,{i:None for i in range(14)},'fan1')
# freeze fan1 samples as fixed for fan2
def fan1_samples(i):
    ch=[ORG[i]]+fan1[i]+[ENT[i]]; pts=[]
    for a,b in zip(ch,ch[1:]):
        for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
    pts.append(ENT[i]); return np.array(pts)
EXT={i:reel.exitp(i,R0) for i in range(14)}
TGT={i:dz.stations(B,A,i)[2] for i in range(14)}
fan2=run_opt(EXT,TGT,2,{i:fan1_samples(i) for i in range(14)},'fan2')
out={str(i+1):{'F1':[[round(v,3) for v in p] for p in fan1[i]],
               'F2':[[round(v,3) for v in p] for p in fan2[i]]} for i in range(14)}
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/reel_opt.json','w'),indent=1)
print('saved reel_opt.json',flush=True)
