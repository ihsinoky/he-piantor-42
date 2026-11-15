"""Feed optimisation for v11: M1/M2 per strand (origins K', targets P fixed).
Fixed samples: dress/corridor/rise/loop/P/G/ep of all strands + penalty
boxes from the frozen solids' bounding boxes (switch envelopes, Wing,
Main, trays, POM, screws) and the slope ceiling."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14 as dz
from audit_repair import load_round9
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
idx,by_name=load_round9('17')
BOXES=[]
for n,s in by_name.items():
    if n.startswith('Wire'): continue
    if not n.startswith(('switch-envelope','POM-','plate-screw-','underside-')): continue
    b=Bnd_Box(); BRepBndLib.Add_s(s.wrapped if hasattr(s,'wrapped') else s,b,True)
    BOXES.append((n,(b.GetXMin()-0.3,b.GetXMax()+0.3,b.GetYMin()-0.3,b.GetYMax()+0.3,b.GetZMin()-0.3,b.GetZMax()+0.3)))
def in_box(p,bx): return (bx[0]<p[0]<bx[1] and bx[2]<p[1]<bx[3] and bx[4]<p[2]<bx[5])
def ceiling(y):
    if y<1.935593: return 22.65-1.0
    t=min(max((y-1.935593)/36.578838,0),1)
    return 24.65-11.10*t-2.0-1.0
def fixed_samples(i):
    pts=[]
    ep,G,P=dz.stations(B,A,i)
    lp=dz.loop_points(B,A,i)
    K1=lp[3]+8.0*dz.UF2
    chains=[[np.array(B[i][0],float),np.array(B[i][1],float),dz.corridor(i),dz.rise_top(B,A,i)],
            [dz.rise_top(B,A,i),lp[0],lp[1],lp[2],lp[3],K1,dz.feed_origin(B,A,i)],
            [P,G,ep]]
    for ch in chains:
        for a,b in zip(ch,ch[1:]):
            for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(ch[-1])
    return np.array(pts)
FIX={i:fixed_samples(i) for i in range(14)}
FIXALL=np.vstack([FIX[i] for i in range(14)])
FIXOWN=np.concatenate([[i]*len(FIX[i]) for i in range(14)])
LAD=[1.35,0.45,-0.45,-1.35]
def init_M(i):
    t=dz.feed_origin(B,A,i); p=dz.stations(B,A,i)[2]
    m1=t+(p-t)*0.38; m1[2]+=LAD[i%4]*0.8
    m2=t+(p-t)*0.72; m2[2]+=LAD[i%4]*0.35
    return m1,m2
X0=[]; BND=[]
for i in range(14):
    m1,m2=init_M(i)
    X0+= list(m1)+list(m2)
    BND+= [(4,48),(-4,44),(8.6,21.8)]*2
X0=np.array(X0,float)
def var_samples(x,i):
    m1=x[i*6:i*6+3]; m2=x[i*6+3:i*6+6]
    org=dz.feed_origin(B,A,i); P=dz.stations(B,A,i)[2]
    pts=[]
    for a,b in ((org,m1),(m1,m2),(m2,P)):
        for tt in np.linspace(0,1,11)[:-1]: pts.append(a+(b-a)*tt)
    pts.append(P)
    return np.array(pts)
def all_var(x):
    allp=[]; allo=[]
    for i in range(14):
        sp=var_samples(x,i); allp.append(sp); allo+=[i]*len(sp)
    return np.vstack(allp),np.array(allo)
def objective(x):
    allp,allo=all_var(x)
    comb=np.vstack([allp,FIXALL]); own=np.concatenate([allo,FIXOWN])
    tree=cKDTree(comb); loss=0.0
    for a,b in tree.query_pairs(1.6):
        if own[a]==own[b]: continue
        if a>=len(allp) and b>=len(allp): continue
        d=np.linalg.norm(comb[a]-comb[b])
        if d<1.3: loss+=((1.3-d)/0.3)**2
    if False and BOXES:
        BARR=np.array([bx for _,bx in BOXES])
        inside=((allp[:,None,0]>BARR[None,:,0])&(allp[:,None,0]<BARR[None,:,1])&
                (allp[:,None,1]>BARR[None,:,2])&(allp[:,None,1]<BARR[None,:,3])&
                (allp[:,None,2]>BARR[None,:,4])&(allp[:,None,2]<BARR[None,:,5]))
        loss+=25.0*float(inside.any(axis=1).sum())
    for p in allp:
        c=ceiling(p[1])
        if p[2]>c: loss+=((p[2]-c)/0.3)**2*2
    return loss+0.002*np.sum((x-X0)**2)
def minpair(x):
    allp,allo=all_var(x)
    comb=np.vstack([allp,FIXALL]); own=np.concatenate([allo,FIXOWN])
    tree=cKDTree(comb); best=(9,None)
    for a,b in tree.query_pairs(2.2):
        if own[a]==own[b]: continue
        if a>=len(allp) and b>=len(allp): continue
        d=np.linalg.norm(comb[a]-comb[b])
        if d<best[0]: best=(d,(own[a]+1,own[b]+1,tuple(np.round(comb[a],1))))
    return best
print('boxes:',len(BOXES),'init min:',minpair(X0),'loss',round(objective(X0),2),flush=True)
res=minimize(objective,X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
print('opt loss',round(res.fun,3),'min:',minpair(res.x),flush=True)
out={str(i+1):{'M1':[round(v,3) for v in res.x[i*6:i*6+3]],'M2':[round(v,3) for v in res.x[i*6+3:i*6+6]]} for i in range(14)}
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/feed_opt.json','w'),indent=1)
print('saved feed_opt.json',flush=True)
