"""Optimise feed intermediate points M1/M2 per strand (origins K' fixed,
P,G,ep fixed) for cross-strand centreline clearance, with slope-ceiling
and Main-floor penalties on samples."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from design_r14 import stations, feed_origin
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
ORG={}; P={}
for i in range(14):
    ep,G,PP=stations(B,A,i); P[i]=PP
    ORG[i]=feed_origin(i)
def ceiling(y):
    if y<1.935593: return 22.65-1.0
    t=min(max((y-1.935593)/36.578838,0),1)
    return 24.65-11.10*t-2.0-1.0
LAD=[1.35,0.45,-0.45,-1.35]
def init_M(i):
    t,p=ORG[i],P[i]
    m1=t+(p-t)*0.38; m1[2]+=LAD[i%4]*0.8
    m2=t+(p-t)*0.72; m2[2]+=LAD[i%4]*0.35
    return m1,m2
X0=[]; BND=[]
for i in range(14):
    m1,m2=init_M(i)
    X0+= list(m1)+list(m2)
    BND+= [(4,44),(-4,40),(8.6,21.5)]*2
X0=np.array(X0,float)
def samples(x):
    pts=[]; own=[]
    for i in range(14):
        m1=x[i*6:i*6+3]; m2=x[i*6+3:i*6+6]
        chain=[ORG[i],m1,m2,P[i]]
        sp=[]
        for a,b in zip(chain,chain[1:]):
            for tt in np.linspace(0,1,13)[:-1]: sp.append(a+(b-a)*tt)
        sp.append(P[i])
        pts+=sp; own+=[i]*len(sp)
    return np.array(pts),np.array(own)
def objective(x):
    pts,own=samples(x)
    tree=cKDTree(pts)
    loss=0.0
    for a,b in tree.query_pairs(1.6):
        if own[a]==own[b]: continue
        d=np.linalg.norm(pts[a]-pts[b])
        if d<1.3: loss+=((1.3-d)/0.3)**2
    for p in pts:
        c=ceiling(p[1])
        if p[2]>c: loss+=((p[2]-c)/0.3)**2*2
        if p[1]>12 and p[2]<9.2: loss+=((9.2-p[2])/0.3)**2
    reg=0.002*np.sum((x-X0)**2)
    return loss+reg
def minpair(x):
    pts,own=samples(x)
    tree=cKDTree(pts); best=(9,None)
    for a,b in tree.query_pairs(2.0):
        if own[a]==own[b]: continue
        d=np.linalg.norm(pts[a]-pts[b])
        if d<best[0]: best=(d,(own[a]+1,own[b]+1,tuple(np.round(pts[a],1))))
    return best
print('init min pair:',minpair(X0),'loss',round(objective(X0),2),flush=True)
res=minimize(objective,X0,method='L-BFGS-B',bounds=BND,options={'maxiter':300,'ftol':1e-9})
print('opt loss',round(res.fun,3),'min pair:',minpair(res.x),flush=True)
out={}
for i in range(14):
    out[str(i+1)]={'M1':[round(v,3) for v in res.x[i*6:i*6+3]],'M2':[round(v,3) for v in res.x[i*6+3:i*6+6]]}
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/feed_opt.json','w'),indent=1)
print('saved feed_opt.json',flush=True)
