import json, itertools, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
import design_r14
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
def sample(pts,step=0.2):
    out=[]
    for a,b in zip(pts,pts[1:]):
        a=np.array(a,float);b=np.array(b,float);L=np.linalg.norm(b-a);n=max(2,int(L/step)+1)
        for tt in np.linspace(0,1,n)[:-1]: out.append(a+(b-a)*tt)
    out.append(np.array(pts[-1],float)); return np.array(out)
def zone(y):
    return 'run' if y<-24.3 else ('conv' if y<-12 else ('west' if y<8 else 'feed'))
def run(label):
    P={i:design_r14.design_points(B,A,i) for i in range(14)}; S={i:sample(p) for i,p in P.items()}
    zm={}; worst=[]
    for i,j in itertools.combinations(range(14),2):
        d=np.linalg.norm(S[i][:,None,:]-S[j][None,:,:],axis=2)
        for zi in range(S[i].shape[0]):
            row=d[zi]; k=int(np.argmin(row))
            z=zone(S[i][zi][1]); v=float(row[k])
            if z not in zm or v<zm[z][0]: zm[z]=(round(v,3),i+1,j+1)
            if v<1.05: worst.append((round(v,3),i+1,j+1,z))
    print(label,'zone minima:',zm,flush=True)
    print(label,'n sample-pairs <1.05:',len(worst),'worst:',sorted(worst)[:6],flush=True)
if __name__=='__main__':
    run('v9 current')
