"""Reel candidate fitted builder + probe (right side, 17 mm). v2.

Slack accounting (documented): the taut reference is NOT built as a
wire (its E joint is a 115 deg corner that cannot fillet in the short
chord segment). Instead:
  slack_true(R) = stored_path_len(R)
                  - [pre_len(R) + chord(R) + post_len(R)]
                  + loss(phiE_taut) + loss(phiX_taut)
where pre/post are the fan chains built standalone (their internal
corner losses are identical in both states and cancel), chord is the
E->X straight, and loss(phi) = 10*tan(phi/2) - 5*phi is the standard
R5 fillet length loss at the two joints the chord state would have.
R is bisected so slack_true = +30.2 mm per strand.
"""
import json, sys
import numpy as np
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0,'/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
from common import *
import design_r14 as dz
import reel
from routes_round14 import split_corners
HERE='/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT='/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14'
D=json.load(open(f'{HERE}/routes-round9.json')); B,A=D['before'],D['after']
OPT=json.load(open(f'{RT}/reel_opt.json'))
def chains(i,R):
    ep,G,P=dz.stations(B,A,i)
    F1=[np.array(q) for q in OPT[str(i+1)]['F1']]
    F2=[np.array(q) for q in OPT[str(i+1)]['F2']]
    E=reel.entry(i,R); M=reel.midp(i,R); X=reel.exitp(i,R)
    pre=[list(B[i][0]),list(B[i][1]),dz.corridor(i).tolist(),dz.rise_top(B,A,i).tolist()]+[p.tolist() for p in F1]+[E.tolist()]
    post=[X.tolist()]+[p.tolist() for p in F2]+[P.tolist(),G.tolist(),list(A[i][6])]
    return pre,M,post,E,X,F1,F2
def path_len(pts):
    return rounded(split_corners(pts)).length
def loss(phi):
    return 10.0*np.tan(phi/2)-5.0*phi
def slack_true(i,R):
    pre,M,post,E,X,F1,F2=chains(i,R)
    stored=path_len(pre)+R*np.radians(270.0)+path_len(post)-0.0
    # stored path: pre (ends at E, no E corner counted) + arc + post;
    # the E/X joint losses in the real wire are inside neither term;
    # correct by subtracting stored joint losses:
    tE=np.array([-0.70710678,-0.70710678,0.0])  # arc entry tangent (CW at -45)
    arr=np.array(E)-np.array(F1[-1]); arr=arr/np.linalg.norm(arr)
    phiE_s=np.arccos(np.clip(np.dot(arr,tE),-1,1))
    tX=np.array([0.70710678,-0.70710678,0.0])   # arc exit tangent (CW at 45)
    dep=np.array(F2[0])-np.array(X); dep=dep/np.linalg.norm(dep)
    phiX_s=np.arccos(np.clip(np.dot(tX,dep),-1,1))
    stored-= (loss(phiE_s)+loss(phiX_s))
    chord=float(np.linalg.norm(np.array(X)-np.array(E)))
    cd=np.array(X)-np.array(E); cd=cd/np.linalg.norm(cd)
    phiE_t=np.arccos(np.clip(np.dot(arr,cd),-1,1))
    phiX_t=np.arccos(np.clip(np.dot(cd,dep),-1,1))
    taut=path_len(pre)+chord+path_len(post)-loss(phiE_t)-loss(phiX_t)
    return stored-taut, stored, taut
def solve_R(i,target=30.2):
    lo,hi=5.5,11.0
    flo,_ ,_=slack_true(i,lo); fhi,_,_=slack_true(i,hi)
    assert flo<target<fhi,(i,flo,fhi)
    for _ in range(10):
        mid=(lo+hi)/2
        if slack_true(i,mid)[0]<target: lo=mid
        else: hi=mid
    R=(lo+hi)/2
    s,st,tt=slack_true(i,R)
    return R,s,st,tt
def wire_stored(i,R):
    pre,M,post,E,X,F1,F2=chains(i,R)
    a=rounded(split_corners(pre))
    arc=Edge.make_three_point_arc(Vector(*pre[-1]),Vector(*M),Vector(*post[0]))
    b=rounded(split_corners(post))
    path=Wire([e for s in (a,Wire([arc]),b) for e in s.edges()])
    d0=np.array(pre[1],float)-np.array(pre[0],float)
    q=sweep(Face(Wire.make_circle(.5,Plane(origin=Vector(*pre[0]),z_dir=Vector(*map(float,d0))))),path=path)
    assert q.is_valid and len(q.solids())==1
    return q,path.length
if __name__=='__main__':
    from audit_repair import load_round9, common_shape, shape_volume
    idx,by_name=load_round9('17')
    fixed={n:s for n,s in by_name.items() if not n.startswith('Wire')}
    wires={}; report={}
    for pin in range(1,15):
        i=pin-1
        try:
            R,s,st,tt=solve_R(i)
            q,L=wire_stored(i,R)
            wires[pin]=q; report[pin]=dict(R=round(R,2),fitted=round(L,2),finished=round(L+7.3,2),slack=round(s,2),tautref=round(tt,2))
            print(f'pin {pin}: R {R:.2f} fitted stored {L:.2f} finished {L+7.3:.2f} slack {s:.2f} tautref {tt:.2f}',flush=True)
        except Exception as e:
            report[pin]=dict(error=str(e)[:120])
            print(f'pin {pin}: BUILD FAIL {str(e)[:120]}',flush=True)
    hits={}
    names=sorted(wires)
    for a_i in range(len(names)):
        for b_i in range(a_i+1,len(names)):
            a,b=names[a_i],names[b_i]
            c=common_shape(wires[a],wires[b]); v=shape_volume(c) if c is not None else 0.0
            if v and v>1e-6: hits[f'{a}x{b}']=round(v,4)
    print('WIRE-WIRE fitted overlaps:',json.dumps(hits),flush=True)
    fhits={}
    for pin,w in wires.items():
        for fn,f in fixed.items():
            try:
                c=common_shape(w,f); v=shape_volume(c) if c is not None else 0.0
            except Exception:
                v=-1
            if v and v>1e-6: fhits.setdefault(f'pin{pin}',{})[fn]=round(v,4)
    print('WIRE-FIXED hits:',json.dumps(fhits)[:2500],flush=True)
    report['_wire_wire']=hits; report['_wire_fixed']=fhits
    json.dump(report,open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14/reel_probe.json','w'),indent=1)
    print('saved reel_probe.json',flush=True)
