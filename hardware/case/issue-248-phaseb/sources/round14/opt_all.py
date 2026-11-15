"""Joint optimisation of stage-2 point W2 and feed points M1/M2 per strand.
Fixed samples (dress, stage 1, rise, loop at p=9.2, P/G/ep) act as obstacles;
rib and tray-block boxes penalise variable-segment samples."""
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
def init_M(i):
    t=dz.feed_origin(i); p=dz.stations(B,A,i)[2]
    LAD=[1.35,0.45,-0.45,-1.35]
    m1=t+(p-t)*0.38; m1[2]+=LAD[i%4]*0.8
    m2=t+(p-t)*0.72; m2[2]+=LAD[i%4]*0.35
    return m1,m2
# fixed samples per strand: dress B0..B2, B3->T (stage1), LB->RT (rise),
# loop polyline (RT,H1,Amid,B1,D1), P->G->ep
def fixed_samples(i):
    pts=[]
    chain=[np.array(B[i][0],float),np.array(B[i][1],float),np.array(B[i][2],float),
           np.array([B[i][0][0],-24.3,dz.zc_of(i)+0.3]),
           np.array([dz.tx_of(i),dz.ty_of(i),dz.zc_of(i)])]
    ep,G,P=dz.stations(B,A,i)
    lp=dz.loop_points(i)
    chain2=[np.array([dz.lane_x(i),-12.0,dz.zc_of(i)]),dz.rise_top(i),lp[0],lp[1],lp[2],lp[3]]
    chain3=[P,G,ep]
    for ch in (chain,chain2,chain3):
        for a,b in zip(ch,ch[1:]):
            for tt in np.linspace(0,1,9)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(ch[-1])
    return np.array(pts)
FIX={i:fixed_samples(i) for i in range(14)}
FIXALL=np.vstack([FIX[i] for i in range(14)])
FIXOWN=np.concatenate([[i]*len(FIX[i]) for i in range(14)])
RIB=(16.35-0.6,17.8+0.6,-15.15-0.6,-13.65+0.6,2.0,11.7+0.6)
BLK=(13.2-0.6,18.5+0.6,-12.3-0.6,-4.5+0.6,2.0,10.0+0.6)
def in_box(p,bx):
    return (bx[0]<p[0]<bx[1] and bx[2]<p[1]<bx[3] and bx[4]<p[2]<bx[5])
def ceiling(y):
    if y<1.935593: return 22.65-1.0
    t=min(max((y-1.935593)/36.578838,0),1)
    return 24.65-11.10*t-2.0-1.0
X0=[]; BND=[]
for i in range(14):
    w2=init_W2(i); m1,m2=init_M(i)
    X0+= list(w2)+list(m1)+list(m2)
    BND+= [(5,26),(-20.5,-10.5),(3.0,6.5)]+[(4,44),(-4,40),(8.6,21.5)]*2
X0=np.array(X0,float)
def var_samples(x,i):
    w2=x[i*9:i*9+3]; m1=x[i*9+3:i*9+6]; m2=x[i*9+6:i*9+9]
    T=np.array([dz.tx_of(i),dz.ty_of(i),dz.zc_of(i)])
    LB=np.array([dz.lane_x(i),-12.0,dz.zc_of(i)])
    D1=dz.feed_origin(i)
    ep,G,P=dz.stations(B,A,i)
    pts=[]
    for ch in ([T,w2,LB],[D1,m1,m2,P]):
        for a,b in zip(ch,ch[1:]):
            for tt in np.linspace(0,1,11)[:-1]: pts.append(a+(b-a)*tt)
        pts.append(ch[-1])
    return np.array(pts)
def objective(x):
    loss=0.0
    allp=[]; allo=[]
    for i in range(14):
        sp=var_samples(x,i); allp.append(sp); allo+=[i]*len(sp)
    allp=np.vstack(allp); allo=np.array(allo)
    tree=cKDTree(allp)
    for a,b in tree.query_pairs(1.6):
        if allo[a]==allo[b]: continue
        d=np.linalg.norm(allp[a]-allp[b])
        if d<1.3: loss+=((1.3-d)/0.3)**2
    # variable vs fixed (other strands)
    treeF=cKDTree(FIXALL)
    for k,p in enumerate(allp):
        for j in treeF.query_ball_point(p,1.3):
            if FIXOWN[j]==allo[k]: continue
            d=np.linalg.norm(p-FIXALL[j])
            if d<1.3: loss+=((1.3-d)/0.3)**2
    for p in allp:
        if in_box(p,RIB): loss+=25.0
        if in_box(p,BLK): loss+=25.0
        c=ceiling(p[1])
        if p[2]>c: loss+=((p[2]-c)/0.3)**2*2
        if p[1]>12 and p[2]<9.2: loss+=((9.2-p[2])/0.3)**2
    return loss+0.002*np.sum((x-X0)**2)
def minpair(x):
    allp=[]; allo=[]
    for i in range(14):
        sp=var_samples(x,i); allp.append(sp); allo+=[i]*len(sp)
    allp=np.vstack(allp); allo=np.array(allo)
    tree=cKDTree(allp); best=(9,None)
    for a,b in tree.query_pairs(2.2):
        if allo[a]==allo[b]: continue
        d=np.linalg.norm(allp[a]-allp[b])
        if d<best[0]: best=(d,(allo[a]+1,allo[b]+1,tuple(np.round(allp[a],1))))
    treeF=cKDTree(FIXALL)
    for k,p in enumerate(allp):
        for j in treeF.query_ball_point(p,best[0]):
            if FIXOWN[j]==allo[k]: continue
            d=np.linalg.norm(p-FIXALL[j])
            if d<best[0]: best=(d,(allo[k]+1,FIXOWN[j]+1,'fixed',tuple(np.round(p,1))))
    return best
print('init min:',minpair(X0),'loss',round(objective(X0),2),flush=True)
res=minimize(objective,X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-9})
print('opt loss',round(res.fun,3),'min:',minpair(res.x),flush=True)
out={}
for i in range(14):
    out[str(i+1)]={'W2':[round(v,3) for v in res.x[i*9:i*9+3]],
                   'M1':[round(v,3) for v in res.x[i*9+3:i*9+6]],
                   'M2':[round(v,3) for v in res.x[i*9+6:i*9+9]]}
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/feed_opt.json','w'),indent=1)
print('saved',flush=True)
