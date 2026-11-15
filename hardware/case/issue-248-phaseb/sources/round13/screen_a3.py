import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
def pathA(i):
    x=B[i][0][0]; zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=25.1-1.25*i
    return [B[i][0],B[i][1],B[i][2],B[i][3],[fx,-18.0,5.1],[fx,-7.0,zf],[fx+12.0,8.0,zf],G,ep]
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
paths={i:pathA(i) for i in range(14)}; S={i:sample(p) for i,p in paths.items()}
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
lens={i:plen(p) for i,p in paths.items()}
res={'variant':'A3 fan fx ladder 1.25','lengths':{str(i+1):round(lens[i],2) for i in lens},
 'longest':round(max(lens.values()),2),'longest_plus_tails_7.3':round(max(lens.values())+7.3,2),
 'harness_with_+30.2_slack':round(max(lens.values())+7.3+30.2,2)}
def order_at(Y):
    xs={}
    for i,s in S.items():
        cand=[p[0] for p in s if abs(p[1]-Y)<0.35]
        xs[i]=float(np.median(cand)) if cand else None
    order=[i for x,i in sorted((x,i) for i,x in xs.items() if x is not None)]
    base=list(range(13,-1,-1)); pos={v:k for k,v in enumerate(order)}
    return sum(1 for a,b in itertools.combinations(base,2) if pos[a]>pos[b])
for Y in (-32,-27,-21,-12,0): res[f'inv_at_Y{Y}']=order_at(Y)
zones={'corridor(Y<-24.3)':lambda y:y<-24.3,'fan(-24.3..-18)':lambda y:-24.3<=y<-18,'rise(-18..-7)':lambda y:-18<=y<-7,'bow(-7..15)':lambda y:-7<=y<15,'approach(Y>=15)':lambda y:y>=15}
close={z:[] for z in zones}; overall=[]
for i,j in itertools.combinations(range(14),2):
    a,b=S[i],S[j]; d=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2)
    k=np.unravel_index(np.argmin(d),d.shape); md=float(d[k]); mid=a[k[0]]
    overall.append((round(md,3),i+1,j+1))
    for z,f in zones.items():
        if f(mid[1]): close[z].append((round(md,3),i+1,j+1))
res['min_overall']=min(overall); res['pairs_below_1.0']=sorted([o for o in overall if o[0]<1.0])
res['zones']={z:{'n_below':len([c for c in v if c[0]<1.0]),'min':(min(v) if v else None),'below':sorted([c for c in v if c[0]<1.0])[:10]} for z,v in close.items()}
print(json.dumps(res,indent=1))
json.dump(res,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/screen_a3.json','w'),indent=1)
