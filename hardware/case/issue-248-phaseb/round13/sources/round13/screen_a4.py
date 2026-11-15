import json, itertools
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
def build(i,fx0,boff,ybow,shift_from_p2):
    x=B[i][0][0]; zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=fx0-1.25*i
    pts=[B[i][0],B[i][1]]
    if shift_from_p2: pts.append([fx,-28.8,5.1])
    else: pts.append(B[i][2])
    pts.append(B[i][3] if not shift_from_p2 else [fx,-24.3,5.1])
    pts += [[fx,-18.0,5.1],[fx,-7.0,zf],[fx+boff,ybow,zf],G,ep]
    return pts
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
out={}
for fx0 in (26.35,27.6):
 for boff in (10.0,12.0):
  for ybow in (14.0,20.0):
   for sfp in (True,False):
    P={i:build(i,fx0,boff,ybow,sfp) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    pairs=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); pairs.append((round(float(d.min()),3),i+1,j+1))
    below=[p for p in pairs if p[0]<1.0]
    key=f'fx0={fx0} boff={boff} ybow={ybow} shiftP2={sfp}'
    out[key]={'min':min(pairs),'n_below':len(below),'below':sorted(below)[:6],'longest+tails':round(max(plen(p) for p in P.values())+7.3,2)}
    print(key,'min',min(pairs),'n_below',len(below),'longest+tails',out[key]['longest+tails'],flush=True)
json.dump(out,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/screen_a4.json','w'),indent=1)
