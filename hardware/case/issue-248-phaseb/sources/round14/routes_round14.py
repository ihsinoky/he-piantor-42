"""Round 14 fitted wire builder (Candidate A, design v11).

Per strand (right side, design index i; left side mirrors with j=13-i):
waypoints from design_r14.design_points, with the hairpin arc built as a
true three-point arc (round 9 pattern). The loop parameter p is bisected
per strand so that (stored length) - (taut length, same route without the
loop points and with the feed run from the rise top) = +30.2 mm.
Returns {side: {pin: (solid, path_length)}} and the per-strand account.
"""
import json, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import *
import design_r14 as dz

HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']

def wire_from_points(pts, loop_idx=None):
    """pts: full waypoint list. loop_idx: index of H1 in pts (arc spans
    H1 -> Amid -> B1, i.e. pts[loop_idx..loop_idx+2])."""
    if loop_idx is None:
        path=rounded([tuple(p) for p in pts])
        segs=[path]
    else:
        pre=[tuple(p) for p in pts[:loop_idx+1]]
        post=[tuple(p) for p in pts[loop_idx+2:]]
        a=rounded(pre)
        arc=Edge.make_three_point_arc(Vector(*pts[loop_idx]),Vector(*pts[loop_idx+1]),Vector(*pts[loop_idx+2]))
        b=rounded(post)
        segs=[a,Wire([arc]),b]
        path=Wire([e for s in segs for e in s.edges()])
    d0=np.array(pts[1],float)-np.array(pts[0],float)
    q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pts[0]),z_dir=Vector(*map(float,d0))))),path=path)
    assert q.is_valid and len(q.solids())==1
    return q,path.length

def loop_index(pts):
    # pts layout: [B0,B1,corridor,RT,H1,Amid,B1d,D1,K',M1,M2,P,G,ep]
    return 4

def strand(i,p_loop):
    pts=dz.design_points(B,A,i,p_loop=p_loop,with_loop=True)
    return wire_from_points(pts,loop_idx=loop_index(pts))

def strand_taut(i):
    # same route without loop: RT -> M1 directly (feed origin = rise top)
    pts=dz.design_points(B,A,i,with_loop=False)
    # design_points(with_loop=False) yields [B0,B1,corr,RT,M1,M2,P,G,ep]
    return wire_from_points(pts,loop_idx=None)

def solve_p(i,target=30.2):
    taut_len=strand_taut(i)[1]
    lo,hi=2.0,20.0
    def add(p): return strand(i,p)[1]-taut_len
    flo,fhi=add(lo),add(hi)
    assert flo<target<fhi,(i,flo,fhi)
    for _ in range(14):
        mid=(lo+hi)/2
        if add(mid)<target: lo=mid
        else: hi=mid
    p=(lo+hi)/2
    return p,add(p),taut_len

def build_side(sgn):
    out={}
    for pin in range(1,15):
        i=pin-1 if sgn>0 else 14-pin
        j=i if sgn>0 else 13-i
        # design index j is defined in right-side convention; for the left
        # side the design strand j mirrors: use design strand j's points
        # with X negated (round 9 mirroring convention).
        p,added,taut=solve_p(j)
        pts=dz.design_points(B,A,j,p_loop=p,with_loop=True)
        if sgn<0:
            pts=[[-q[0],q[1],q[2]] for q in pts]
        q_solid,length=wire_from_points(pts,loop_idx=loop_index(pts))
        out[pin]={'solid':q_solid,'length':length,'p':p,'added':added,'taut':taut}
    return out

if __name__=='__main__':
    side=build_side(+1)
    for pin in range(1,15):
        r=side[pin]
        print(f"pin {pin}: len {r['length']:.2f} +tails {r['length']+7.3:.2f} p {r['p']:.2f} added {r['added']:.2f} taut {r['taut']:.2f}",flush=True)
