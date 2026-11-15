"""Slack-reel geometry (round 14, Candidate A): each strand's +30.2 mm
slack is one horizontal turn around a shared vertical axis in the bay
centre C=(0,5), at its own Z (ladder 1.12 mm), radius ~8 mm.
Entry radial u = 225 deg, sweep 270 deg, exit radial w = u rotated by
-270 deg in the XY plane. Fans (optimised separately) connect
rise-top -> entry point E_i and exit point X_i -> P_i.
Stored = with arc; taut = same waypoints with the E->X chord."""
import numpy as np
C=np.array([0.0,5.0])
U=np.array([np.cos(np.radians(-45.0)),np.sin(np.radians(-45.0))])
def rot(v,deg):
    t=np.radians(deg); c,s=np.cos(t),np.sin(t)
    return np.array([c*v[0]-s*v[1],s*v[0]+c*v[1]])
W=rot(U,-270.0)  # exit radial at 45 deg
TMID=rot(U,-135.0)  # mid radial at 180 deg
def z_of(i): return 4.6+1.12*i
def entry(i,R=8.0):
    p=C+R*U; return np.array([p[0],p[1],z_of(i)])
def exitp(i,R=8.0):
    p=C+R*W; return np.array([p[0],p[1],z_of(i)])
def midp(i,R=8.0):
    p=C+R*TMID; return np.array([p[0],p[1],z_of(i)])
def arc_len(R=8.0,sweep=270.0): return R*np.radians(sweep)
def chord(i,R=8.0): return float(np.linalg.norm(exitp(i,R)-entry(i,R)))
if __name__=='__main__':
    print('U',U,'W',W,'TMID',TMID)
    print('entry',entry(0),'exit',exitp(0),'mid',midp(0))
    print('arc len R8',round(arc_len(),2),'chord',round(chord(0),2),'gain',round(arc_len()-chord(0),2))
    for R in (7.0,7.5,8.0,8.5,9.0):
        print('R',R,'gain',round(arc_len(R)-chord(0,R),2))
