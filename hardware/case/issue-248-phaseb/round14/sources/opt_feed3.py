"""Feed optimisation v13, two phases (origins = A6 rise tops, targets P).
Phase 1 (taut): pair-clearance only -> the natural-length clean family.
Phase 2 (stored): pair-clearance + per-strand length target taut+30.2
(the +30.2 mm service slack as a distributed, optimiser-shaped detour
dressed in the bay; builder later tunes amplitude per strand exactly).
Fixed samples: west transit (dress/corridor/rise) and P/G/ep of all strands.
Slope-ceiling penalty on variable samples."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14 as dz
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
def ceiling(y):
    if y<1.935593: return 22.65-1.0
    t=min(max((y-1.935593)/36.578838,0),1)
    return 24.65-11.10*t-2.0-1.0
def fixed_samples(i):
    pts=[]
    ep,G,P=dz.stations(B,A,i)
    chains=[[np.array(B[i][0],float),np.array(B[i][1],float),dz.corridor(i),dz.rise_top(B,A,i)],
            [P,G,ep]]
    for ch in chains:
        for a,b in zip(ch,ch[1:]):
            for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(ch[-1])
    return np.array(pts)
FIX={i:fixed_samples(i) for i in range(14)}
FIXALL=np.vstack([FIX[i] for i in range(14)])
FIXOWN=np.concatenate([[i]*len(FIX[i]) for i in range(14)])
ORG={i:dz.rise_top(B,A,i) for i in range(14)}
TGT={i:dz.stations(B,A,i)[2] for i in range(14)}
NV=6
def chain(x,i):
    return [ORG[i]]+[x[i*6+k*3:i*6+k*3+3] for k in range(2)]+[TGT[i]]
def var_samples(x,i,nseg=11):
    ch=chain(x,i); pts=[]
    for a,b in zip(ch,ch[1:]):
        for tt in np.linspace(0,1,nseg)[:-1]: pts.append(a+(b-a)*tt)
    pts.append(TGT[i])
    return np.array(pts)
def plen(x,i):
    ch=chain(x,i)
    return sum(np.linalg.norm(b-a) for a,b in zip(ch,ch[1:]))
def turn_pen(x):
    pen=0.0
    for i in range(14):
        ch=chain(x,i)
        for k in range(1,3):
            u=ch[k]-ch[k-1]; v=ch[k+1]-ch[k]
            lu=np.linalg.norm(u); lv=np.linalg.norm(v)
            if lu<9.0: pen+=((9.0-lu)/2.0)**2*2.0
            if lv<9.0: pen+=((9.0-lv)/2.0)**2*2.0
            c=float(np.dot(u,v)/(lu*lv+1e-9))
            if c<0.2: pen+=((0.2-c)/0.2)**2*8.0
    return pen
from audit_repair import load_round9
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
_idx,_bn=load_round9('17')
ENV=[]
for n,sh in _bn.items():
    if n.startswith('switch-envelope'):
        b=Bnd_Box(); BRepBndLib.Add_s(sh.wrapped if hasattr(sh,'wrapped') else sh,b,True)
        ENV.append((b.GetXMin()-0.55,b.GetXMax()+0.55,b.GetYMin()-0.55,b.GetYMax()+0.55,b.GetZMin()-0.55,b.GetZMax()+0.55))
ENV=np.array(ENV)
def env_pen(allp):
    inside=((allp[:,None,0]>ENV[None,:,0])&(allp[:,None,0]<ENV[None,:,1])&
            (allp[:,None,1]>ENV[None,:,2])&(allp[:,None,1]<ENV[None,:,3])&
            (allp[:,None,2]>ENV[None,:,4])&(allp[:,None,2]<ENV[None,:,5]))
    return 100.0*float(inside.any(axis=1).sum())
def make_obj(tautlen=None):
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
        AXV=np.array([0.8660254,-0.5,0.0])
        for i in range(14):
            m2=x[i*6+3:i*6+6]
            u=TGT[i]-m2; u=u/np.linalg.norm(u)
            c=float(np.dot(u,-AXV))
            if c<0.3: loss+=((0.3-c)/0.2)**2*6.0
        if tautlen is not None:
            for i in range(14):
                dl=plen(x,i)-tautlen[i]
                loss+=((dl-44.2)/1.5)**2*3.0
        return loss+0.001*np.sum((x-X0)**2)
    return objective
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
LAD=[1.35,0.45,-0.45,-1.35]
X0=[]; BND=[]
for i in range(14):
    t,p=ORG[i],TGT[i]
    for fr in (0.38,0.72):
        m=t+(p-t)*fr; m[2]+=LAD[i%4]*0.6
        X0+= list(m)
    BND+= [(0,46),(-4,44),(8.6,21.8)]*2
X0=np.array(X0,float)
print('phase1 taut...',flush=True)
r1=minimize(make_obj(None),X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
tautlen={i:plen(r1.x,i) for i in range(14)}
print('taut loss',round(r1.fun,3),'min',minpair(r1.x),'lens',round(min(tautlen.values()),1),round(max(tautlen.values()),1),flush=True)
json.dump({str(i+1):{'M1':[round(v,3) for v in r1.x[i*6:i*6+3]],'M2':[round(v,3) for v in r1.x[i*6+3:i*6+6]]} for i in range(14)},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/taut_opt.json','w'),indent=1)
X0=r1.x.copy()
for i in range(14):
    X0[i*6+1]+=6.0; X0[i*6+2]+=3.0
    X0[i*6+4]+=10.0; X0[i*6+5]+=5.0
print('phase2 stored...',flush=True)
r2=minimize(make_obj(tautlen),X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
dl={i:round(plen(r2.x,i)-tautlen[i],2) for i in range(14)}
print('stored loss',round(r2.fun,3),'min',minpair(r2.x),'added lens',dl,flush=True)
json.dump({str(i+1):{'M1':[round(v,3) for v in r2.x[i*6:i*6+3]],'M2':[round(v,3) for v in r2.x[i*6+3:i*6+6]]} for i in range(14)},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/feed_opt.json','w'),indent=1)
print('saved taut_opt.json + feed_opt.json (stored)',flush=True)
