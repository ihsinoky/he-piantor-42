import json, math, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
# fan lane set from round 9 after[2]/after[3]; reassign monotonically by outlet X (idx0=pin1, X desc)
pairs=sorted(((A[i][2][0], A[i][3][2]) for i in range(14)), key=lambda t:-t[0])  # fx desc
lanes={i:pairs[i] for i in range(14)}  # idx asc (outlet X desc) -> fx desc: order-preserving fan
def pathA(i):
    x=B[i][0][0]; fx,zf=lanes[i]
    G=A[i][5]; ep=A[i][6]
    return [B[i][0],B[i][1],B[i][2],B[i][3],[fx,-18.0,5.1],[fx,-7.0,zf],[fx+12.0,8.0,zf],G,ep]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
paths={i:pathA(i) for i in range(14)}
S={i:sample(p) for i,p in paths.items()}
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
lens={i:plen(p) for i,p in paths.items()}
# stage orders at Y cuts: interpolate X per strand at given Y (use samples, nearest in Y on monotone-ish segments: use first crossing)
def order_at(Y):
    xs={}
    for i,s in S.items():
        # find sample segment crossing Y with strand generally northbound in corridor/rise; take median x of samples within 0.3 of Y
        cand=[p[0] for p in s if abs(p[1]-Y)<0.35]
        xs[i]=float(np.median(cand)) if cand else None
    seq=sorted((x,i) for i,x in xs.items() if x is not None)
    order=[i for x,i in seq]  # west->east
    inv=sum(1 for a,b in itertools.combinations(order,2) if a<b)  # pin idx asc should be west->east? outlet: idx0 eastmost
    return xs,order
res={'lengths':{str(i):round(lens[i],2) for i in lens},'longest':round(max(lens.values()),2),
     'longest_plus_tails_7.3':round(max(lens.values())+7.3,2)}
# inversions measured against traversal order: at outlet, west->east order is idx 13..0. Clean route keeps that relative order at every Y cut.
for Y in (-32,-27,-21,-12,0):
    xs,order=order_at(Y)
    base=[13-i for i in range(14)]  # west->east at outlet
    pos={v:k for k,v in enumerate(order)}
    inv=sum(1 for a,b in itertools.combinations(base,2) if pos[a]>pos[b])
    res[f'inv_at_Y{Y}']=inv
# all-pairs min distance, overall + zones by midpoint Y
zones={'corridor(Y<-24.3)':lambda y:y<-24.3,'fan(-24.3..-18)':lambda y:-24.3<=y<-18,'rise(-18..-7)':lambda y:-18<=y<-7,'bow(-7..15)':lambda y:-7<=y<15,'approach(Y>=15)':lambda y:y>=15}
close={z:[] for z in zones}; overall=[]
for i,j in itertools.combinations(range(14),2):
    a,b=S[i],S[j]
    d=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)
    k=np.unravel_index(np.argmin(d),d.shape); md=float(d[k]); mid=a[k[0]]
    overall.append((round(md,3),i+1,j+1))
    for z,f in zones.items():
        if f(mid[1]): close[z].append((round(md,3),i+1,j+1))
res['pairs_below_1.0_overall']=sorted([o for o in overall if o[0]<1.0])
res['min_overall']=min(overall)
res['zones']={z:{'n_below_1.0':len([c for c in v if c[0]<1.0]),'min':(min(v) if v else None),'below':sorted([c for c in v if c[0]<1.0])[:12]} for z,v in close.items()}
print(json.dumps(res,indent=1))
json.dump(res,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/screen_a.json','w'),indent=1)
