import json, itertools, math
import numpy as np
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json'))
B,A=D['before'],D['after']
R=5.0; Y0=-4.0  # fold tangent centre Y; arcs share tangent point (fx,Y0,zf+2R), L2=0
def arc_pts(cy,cz,phase,n=25):
    # phase 'up': from (Y0, zf) heading +Y over bulge +Y to (Y0, zf+2R) heading -Y, centre (Y0,zf+R)... start rel (0,-R)
    out=[]
    for k in range(n+1):
        th=math.pi*k/n
        if phase=='up':  # centre (Y0, zf+R); start angle -90deg (rel (0,-R)) going through +Y bulge
            y=Y0+R*math.sin(th); z=cz-R*math.cos(th)
        else:            # centre (Y0, zf+R); from top rel (0,+R) through -Y bulge to bottom
            y=Y0-R*math.sin(th); z=cz+R*math.cos(th)
        out.append([None,y,z])
    return out
def build(i):
    zf=A[i][3][2]; G=A[i][5]; ep=A[i][6]; fx=28.85-1.25*i
    pts=[B[i][0],B[i][1],[fx,-18.0,5.1],[fx,-7.0,zf],[fx,Y0,zf]]
    up=arc_pts(Y0,zf+R,'up'); dn=arc_pts(Y0,zf+R,'dn')
    for p in up: p[0]=fx
    for p in dn: p[0]=fx
    pts+=up[1:]+dn[1:]  # ends at (fx,Y0,zf) heading +Y
    pts+=[[fx+10.0,8.0,zf],G,ep]
    return pts
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for t in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*t)
    out.append(np.array(pts[-1],float)); return np.array(out)
def plen(p): return sum(np.linalg.norm(np.array(b,float)-np.array(a,float)) for a,b in zip(p,p[1:]))
P={i:build(i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
pairs=[]
for i,j in itertools.combinations(range(14),2):
    d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2); pairs.append((round(float(d.min()),3),i+1,j+1))
below=sorted([p for p in pairs if p[0]<1.0])
# candidate A longest (polyline) for release arithmetic: A6 best longest 93.42+7.3=100.72 -> polyline longest excl tails:
res={'fold':'S-fold R5, tangent Y0=-4, upper leg zf+10','longest_polyline':round(max(plen(p) for p in P.values()),2),
 'longest+tails':round(max(plen(p) for p in P.values())+7.3,2),
 'release_vs_A (31.42 arc pair + legs)':None,'min_pair':min(pairs),'n_below':len(below),'below':below[:8],
 'crown_centreline_max_z':round(max(A[i][3][2] for i in range(14))+10.0,2)}
print(json.dumps(res,indent=1))
json.dump(res,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round13/screen_b.json','w'),indent=1)
