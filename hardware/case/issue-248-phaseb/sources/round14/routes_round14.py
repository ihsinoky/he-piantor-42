"""Round 14 fitted wire builder (Candidate A, design v13).

Route per strand (right-side design convention; left mirrors j=13-i):
B0,B1 (round 9 dress) -> corridor (fx,-18,5.1) -> rise top (fx,-7,zf9)
-> M1 -> M2 -> P -> G (round 9 station) -> ep.
TAUT family: M from taut_opt.json. STORED family: M(alpha) =
tautM + alpha*(storedM - tautM); alpha is bisected per strand so that
fitted_length(stored) - fitted_length(taut) = +30.2 mm (the service
slack, distributed as an optimiser-shaped detour in the bay).
Extraction states blend stored->taut (see audit_round14.py).
"""
import json, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import *
import design_r14 as dz

HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT='/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
TAUT=json.load(open(f'{RT}/taut_opt.json'))
STORED=json.load(open(f'{RT}/feed_opt.json'))

def feed_pts(i,kind,alpha=1.0):
    tm=[np.array(TAUT[str(i+1)]['M1']),np.array(TAUT[str(i+1)]['M2'])]
    if kind=='taut': return tm
    sm=[np.array(STORED[str(i+1)]['M1']),np.array(STORED[str(i+1)]['M2'])]
    return [t+alpha*(s-t) for t,s in zip(tm,sm)]

def points(i,kind='stored',alpha=1.0,blend=None):
    """blend t in [0,1]: stored->taut interpolation of the feed points
    (service extraction states)."""
    ep,G,P=dz.stations(B,A,i)
    if blend is None:
        ms=feed_pts(i,kind,alpha)
    else:
        sm=feed_pts(i,'stored',alpha); tm=feed_pts(i,'taut')
        ms=[s+(t-s)*blend for s,t in zip(sm,tm)]
    return [list(B[i][0]),list(B[i][1]),dz.corridor(i).tolist(),
            dz.rise_top(B,A,i).tolist()]+[m.tolist() for m in ms]+[
            P.tolist(),G.tolist(),list(A[i][6])]

def split_corners(pts):
    """Split only corners that bound a segment failing rounded()'s
    actual criterion (sum of adjacent trims >= segment length).
    One simultaneous pass, chamfer offset capped at 0.30*segmin."""
    pts=[np.array(p,float) for p in pts]
    n=len(pts)
    trims=[0.0]*n
    for k in range(1,n-1):
        u=(pts[k]-pts[k-1]); u=u/np.linalg.norm(u)
        v=(pts[k+1]-pts[k]); v=v/np.linalg.norm(v)
        phi=np.arccos(float(np.clip(np.dot(u,v),-1,1)))
        trims[k]=5.0*np.tan(phi/2) if phi<2.9 else 1e9
    bad=set()
    for k in range(n-1):
        L=np.linalg.norm(pts[k+1]-pts[k])
        if trims[k]+trims[k+1]>=L-1e-9:
            bad.add(k); bad.add(k+1)
    out=[pts[0]]
    for k in range(1,n-1):
        a,b,c=pts[k-1],pts[k],pts[k+1]
        if k in bad:
            segmin=min(np.linalg.norm(b-a),np.linalg.norm(c-b))
            u=(b-a)/np.linalg.norm(b-a); v=(c-b)/np.linalg.norm(c-b)
            d=min(trims[k]+1.0,0.30*segmin)
            out.append(b-d*u); out.append(b+d*v)
        else:
            out.append(b)
    out.append(pts[-1])
    return [tuple(p) for p in out]

def wire(pts):
    try:
        path=rounded(split_corners(pts))
    except AssertionError:
        path=None
        for drop in ((5,),(4,),(4,5)):
            cand=[q for k,q in enumerate(pts) if k not in drop]
            try:
                path=rounded(split_corners(cand)); pts=cand; break
            except AssertionError:
                continue
        if path is None: raise
    d0=np.array(pts[1],float)-np.array(pts[0],float)
    q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
    assert q.is_valid and len(q.solids())==1
    return q,path.length

def solve_alpha(i,target=30.2):
    taut_len=wire(points(i,'taut'))[1]
    def add(a): return wire(points(i,'stored',alpha=a))[1]-taut_len
    lo,hi=0.7,1.45
    flo,fhi=add(lo),add(hi)
    assert flo<target<fhi,(i,flo,fhi)
    for _ in range(12):
        mid=(lo+hi)/2
        if add(mid)<target: lo=mid
        else: hi=mid
    a=(lo+hi)/2
    return a,add(a),taut_len

def build_side(sgn,kind='stored'):
    out={}
    for pin in range(1,15):
        jj=(pin-1) if sgn>0 else (14-pin)
        if kind=='stored':
            a,added,taut=solve_alpha(jj)
            pts=points(jj,'stored',alpha=a)
        else:
            a,added,taut=1.0,0.0,wire(points(jj,'taut'))[1]
            pts=points(jj,'taut')
        if sgn<0: pts=[[-q[0],q[1],q[2]] for q in pts]
        q_solid,length=wire(pts)
        out[pin]={'solid':q_solid,'length':length,'alpha':a,'added':added,'taut':taut}
    return out

if __name__=='__main__':
    side=build_side(+1,'stored')
    mx=0
    for pin in range(1,15):
        r=side[pin]; fin=r['length']+7.3; mx=max(mx,fin)
        print(f"pin {pin}: fitted {r['length']:.2f} finished {fin:.2f} alpha {r['alpha']:.3f} added {r['added']:.2f}",flush=True)
    print('longest finished',round(mx,3),flush=True)
