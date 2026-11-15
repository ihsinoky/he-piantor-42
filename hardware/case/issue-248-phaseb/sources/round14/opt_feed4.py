"""Body-aware feed optimisation (round 14, final form).
Same two-phase structure as opt_feed3 (taut, then stored at polyline
target taut+30.2), plus an exact fixed-body term: every fixed solid of
the round-9 assembly is surface-sampled once (triangulation nodes);
variable feed samples are penalised by their distance to the nearest
fixed surface sample (hinge at 1.05 mm: wire radius 0.5 + 0.55 margin).
Origins (rise tops) and targets (P on-axis) and the approach-angle
penalty are as in opt_feed3's final form."""
import json, sys
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14 as dz
from audit_repair import load_round9
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.Poly import Poly_Triangulation
from OCP.TopoDS import TopoDS
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
def surface_points(shape,defl=0.6):
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_FACE
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS
    w=shape.wrapped if hasattr(shape,'wrapped') else shape
    BRepMesh_IncrementalMesh(w,defl,False,0.4,True)
    pts=[]; exp=TopExp_Explorer(w,TopAbs_FACE)
    while exp.More():
        f=TopoDS.Face(exp.Current()); loc=TopLoc_Location()
        tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation()
            for k in range(1,tri.NbNodes()+1):
                p=tri.Node(k).Transformed(tr); pts.append((p.X(),p.Y(),p.Z()))
        exp.Next()
    return pts
idx,by_name=load_round9('17')
FIXPTS=[]
for n,s in by_name.items():
    if n.startswith('Wire'): continue
    FIXPTS+= surface_points(s)
FIXPTS=np.array(FIXPTS); FTREE=cKDTree(FIXPTS)
print('fixed surface samples:',len(FIXPTS),flush=True)
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
AXV=np.array([0.8660254,-0.5,0.0])
def var_samples(x,i,nseg=11):
    m1=x[i*6:i*6+3]; m2=x[i*6+3:i*6+6]
    pts=[]
    for a,b in ((ORG[i],m1),(m1,m2),(m2,TGT[i])):
        for tt in np.linspace(0,1,nseg)[:-1]: pts.append(a+(b-a)*tt)
    pts.append(TGT[i])
    return np.array(pts)
def plen(x,i):
    m1=x[i*6:i*6+3]; m2=x[i*6+3:i*6+6]
    ch=[ORG[i],m1,m2,TGT[i]]
    return sum(np.linalg.norm(b-a) for a,b in zip(ch,ch[1:]))
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
        dd,_=FTREE.query(allp,k=1)
        bad=dd<1.05
        if bad.any(): loss+=float((((1.05-dd[bad])/0.3)**2).sum())*3.0
        for p in allp:
            c=ceiling(p[1])
            if p[2]>c: loss+=((p[2]-c)/0.3)**2*2
        for i in range(14):
            m2=x[i*6+3:i*6+6]
            u=TGT[i]-m2; u=u/np.linalg.norm(u)
            c=float(np.dot(u,-AXV))
            if c<0.3: loss+=((0.3-c)/0.2)**2*6.0
        if tautlen is not None:
            for i in range(14):
                dl=plen(x,i)-tautlen[i]
                loss+=((dl-30.2)/1.5)**2*3.0
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
    dd,_=FTREE.query(allp,k=1)
    return best, round(float(dd.min()),3)
LAD=[1.35,0.45,-0.45,-1.35]
X0=[]; BND=[]
for i in range(14):
    t,p=ORG[i],TGT[i]
    m1=t+(p-t)*0.38; m1[2]+=LAD[i%4]*0.8
    m2=t+(p-t)*0.72; m2[2]+=LAD[i%4]*0.35
    X0+= list(m1)+list(m2)
    BND+= [(0,46),(-4,44),(8.6,21.8)]*2
X0=np.array(X0,float)
print('phase1 taut (body-aware)...',flush=True)
r1=minimize(make_obj(None),X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
tautlen={i:plen(r1.x,i) for i in range(14)}
print('taut loss',round(r1.fun,3),'min pair / fixed-dist',minpair(r1.x),flush=True)
json.dump({str(i+1):{'M1':[round(v,3) for v in r1.x[i*6:i*6+3]],'M2':[round(v,3) for v in r1.x[i*6+3:i*6+6]]} for i in range(14)},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/taut_opt.json','w'),indent=1)
X0=r1.x.copy()
for i in range(14):
    X0[i*6+1]+=6.0; X0[i*6+2]+=3.0
    X0[i*6+4]+=10.0; X0[i*6+5]+=5.0
print('phase2 stored (body-aware, target +30.2 polyline)...',flush=True)
r2=minimize(make_obj(tautlen),X0,method='L-BFGS-B',bounds=BND,options={'maxiter':250,'ftol':1e-10})
dl={i:round(plen(r2.x,i)-tautlen[i],2) for i in range(14)}
print('stored loss',round(r2.fun,3),'min pair / fixed-dist',minpair(r2.x),'added',dl,flush=True)
json.dump({str(i+1):{'M1':[round(v,3) for v in r2.x[i*6:i*6+3]],'M2':[round(v,3) for v in r2.x[i*6+3:i*6+6]]} for i in range(14)},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/feed_opt.json','w'),indent=1)
print('saved',flush=True)
