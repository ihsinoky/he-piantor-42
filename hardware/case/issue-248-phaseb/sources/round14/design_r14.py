"""Round 14 route design v11 (Candidate A). Right-side design convention
(left mirrors with j=13-i, as routes_round9).

Skeleton = round 13 variant A6 (screen-clean except the feed family) with
round 9's proven stations, and the feed/loop closed here:
outlet dress B0,B1 -> corridor point (fx,-18,5.1), fx = 28.85-1.25i
  (uniform row translation: parallel segments, spacing 1.25 preserved)
-> rise (fx,-7,zf9) with round 9's zf ladder
-> SLACK LOOP: vertical R5 hairpin on the uniform first feed segment
  (direction UF2, same for all strands; legs separated 10 mm along W2,
  the up direction perpendicular to UF2; hairpins tile like the segment
  family): RT -> H1 = RT + p*UF2 -> arc -> B1 = H1 + 10*W2 ->
  C1 = RT + 10*W2 -> K' = C1 + 8*UF2. p is tuned per strand in the
  builder so stored-minus-taut = +30.2 mm.
-> feed K' -> M1 -> M2 (numerically optimised, opt_feed2.py; fixed-sample
  obstacles incl. switch-envelope / Wing / Main boxes, slope ceiling)
-> P = G + 6a - 1.6z (dipped on-axis pre-station) -> G = round 9's station
  (A[i][5] verbatim) -> ep = A[i][6].
"""
import json
import numpy as np
AX=np.array([0.8660254,-0.5,0.0])
UF2=np.array([0.72,0.69,-0.06]); UF2=UF2/np.linalg.norm(UF2)
W2=np.array([0,0,1.0])-UF2*UF2[2]; W2=W2/np.linalg.norm(W2)
RT='/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14'
try:
    _OPT=json.load(open(f'{RT}/feed_opt.json'))
except FileNotFoundError:
    _OPT=None

def fx_of(i): return 28.85-1.25*i
def corridor(i): return np.array([fx_of(i),-18.0,5.1])
def rise_top(B,A,i): return np.array([fx_of(i),-7.0,A[i][3][2]])
def stations(B,A,i):
    ep=np.array(A[i][6],float)
    G=np.array(A[i][5],float)
    P=G+6.0*AX+np.array([0,0,-1.6])
    return ep,G,P
def feed_M(i):
    o=_OPT[str(i+1)]
    return np.array(o['M1']),np.array(o['M2'])
def loop_points(B,A,i,p_loop=9.0):
    RTp=rise_top(B,A,i)
    H1=RTp+UF2*p_loop
    Amid=H1+5.0*UF2+5.0*W2
    B1=H1+10.0*W2
    C1=RTp+10.0*W2
    return H1,Amid,B1,C1
def feed_origin(B,A,i,p_loop=9.0):
    return loop_points(B,A,i,p_loop)[3]+8.0*UF2
def design_points(B,A,i,p_loop=9.0,with_loop=True):
    ep,G,P=stations(B,A,i)
    M1,M2=feed_M(i)
    RTp=rise_top(B,A,i)
    pts=[list(B[i][0]),list(B[i][1]),corridor(i).tolist(),RTp.tolist()]
    if with_loop:
        H1,Amid,B1,C1=loop_points(B,A,i,p_loop)
        pts+= [H1.tolist(),Amid.tolist(),B1.tolist(),C1.tolist(),
               feed_origin(B,A,i,p_loop).tolist()]
    pts+= [M1.tolist(),M2.tolist(),P.tolist(),G.tolist(),list(A[i][6])]
    return pts
