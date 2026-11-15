"""Stage-2-only optimisation: W2 per strand (T, LB fixed). Fixed samples:
stage-1 lines and rises of all strands. Rib/block boxes penalised."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14 as dz
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
BUMP=[0.75,0.25,-0.25,-0.75]
def init_W2(i):
    T=np.array([dz.tx_of(i),dz.ty_of(i),dz.zc_of(i)])
    LB=np.array([dz.lane_x(i),-12.0,dz.zc_of(i)])
    if i==0: return np.array([19.5,-12.6,dz.zc_of(i)])
    if i in (1,2,3,4): return np.array([dz.tx_of(i)-2.5,-17.9+0.2*(i%3),dz.zc_of(i)])
    m=(T+LB)/2; m[2]+=BUMP[i%4]; return m
def fixed_samples(i):
    pts=[]
    B3=np.array([B[i][0][0],-24.3,dz.zc_of(i)+0.3])
    T=np.array([dz.tx_of(i),dz.ty_of(i),dz.zc_of(i)])
    LB=np.array([dz.lane_x(i),-12.0,dz.zc_of(i)])
    RT=dz.rise_top(i)
    for a,b in ((B3,T),(LB,RT)):
        for tt in np.linspace(0,1,11)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(b)
    return np.array(pts)
FIX={i:fixed_samples(i) for i in range(14)}
FIXALL=np.vstack([FIX[i] for i in range(14)])
FIXOWN=np.concatenate([[i]*len(FIX[i]) for i in range(14)])
RIB=(16.35-0.55,17.8+0.55,-15.15-0.55,-13.65+0.55,2.0,11.7+0.55)
BLK=(13.2-0.3,18.5+0.3,-12.3-0.3,-4.5+0.3,2.0,10.0+0.3)
def in_box(p,bx): return (bx[0]<p[0]<bx[1] and bx[2]<p[1]<bx[3] and bx[4]<p[2]<bx[5])
X0=[]; BND=[]
for i in range(14):
    X0+= list(init_W2(i)); BND+= [(5,26),(-20.5,-10.5),(3.0,6.5)]
X0=np.array(X0,float)
def var_samples(x,i):
    w2=x[i*3:i*3+3]
    T=np.array([dz.tx_of(i),dz.ty_of(i),dz.zc_of(i)])
    LB=np.array([dz.lane_x(i),-12.0,dz.zc_of(i)])
    pts=[]
    for a,b in ((T,w2),(w2,LB)):
        for tt in np.linspace(0,1,11)[:-1]: pts.append(a+(b-a)*tt)
    pts.append(LB)
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
        # skip fixed-fixed pairs (constant)
        if a>=len(allp) and b>=len(allp): continue
        d=np.linalg.norm(comb[a]-comb[b])
        if d<1.3: loss+=((1.3-d)/0.3)**2
    for p in allp:
        if in_box(p,RIB): loss+=25.0
        if in_box(p,BLK): loss+=25.0
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
print('init min:',minpair(X0),'loss',round(objective(X0),2),flush=True)
res=minimize(objective,X0,method='L-BFGS-B',bounds=BND,options={'maxiter':200,'ftol':1e-10})
print('opt loss',round(res.fun,3),'min:',minpair(res.x),flush=True)
out={str(i+1):{'W2':[round(v,3) for v in res.x[i*3:i*3+3]]} for i in range(14)}
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/stage2_opt.json','w'),indent=1)
print('saved stage2_opt.json',flush=True)
