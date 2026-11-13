"""Connected cable/cover study. Uses immutable #232 assembly BReps."""
import sys,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
from build123d import Axis
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE=HERE.parent/'issue-232-final';OLD=HERE.parent/'issue-238-bay-study'
def read(p):return json.loads(p.read_text())
def bb(s):
 b=s.bounding_box();return [[getattr(b.min,k) for k in 'XYZ'],[getattr(b.max,k) for k in 'XYZ']]
def fly_path(d,south):
 cy=d['fly']['transform']['translation_mm'][1];start=d['fly']['cable']['waypoints_mm'][0];end=d['fly']['cable']['waypoints_mm'][-1]
 # Low connected storage above the Wing bundles, avoiding both splice rows.
 pts=[start,[0,-18,8.8],[-10,-3,8.8],[-10,south,8.8],[6,south,8.8],[6,-16,8.8],[-6,-16,14.6],[-6,-7,14.6],[0,-1,14.6],[0,7.9,14.6]]
 edges=list(rounded(pts).edges());dy=2.;t=math.acos(1-dy/10);length=10*math.sin(t)
 a=Vector(0,7.9,14.6);m=Vector(0,7.9+length/2,13.6);e=Vector(0,7.9+length,12.6)
 m1=Vector(0,7.9+5*math.sin(t/2),14.6-5*(1-math.cos(t/2)))
 m2=Vector(0,7.9+length-5*math.sin(t/2),12.6+5*(1-math.cos(t/2)))
 edges +=[Edge.make_three_point_arc(a,m1,m),Edge.make_three_point_arc(m,m2,e),Edge.make_line(e,Vector(*end))]
 return Wire(edges),pts

def wing_route(sgn,south):
 # Original #232 Wing fanout and passage are preserved.
 fan=[];fl=[]
 for i in range(14):
  pts=[[sgn*27+(i-6.5)*1.25,-35.45,8.4],[sgn*27+(i-6.5)*1.25,-31.5,8.4],[sgn*27,-24,5],[sgn*14,-18.8,5]]
  q,path=tube(pts,.5);fan.append(q);fl.append(path.length)
 lowerpts=[[sgn*27,-24,5],[sgn*7,-16,5],[sgn*7,south,5],[sgn*18,south,5],[sgn*18,-20,5]]
 lower,lp=tube(lowerpts,2.5)
 upperpts=[[sgn*18,-20,5],[sgn*7,-20,12.95],[sgn*7,-8,12.95],[sgn*20,12,12.95],[sgn*30,18,12.95]]
 upper=[];ul=[];last=[];ml=[]
 positions=[(i-2,-1) for i in range(5)]+[(i-2,0) for i in range(5)]+[(i-1.5,1) for i in range(4)]
 for i,(off,dz) in enumerate(positions):
  pts=[[x+off,y,z+dz] for x,y,z in upperpts];pts[0]=lowerpts[-1]
  q,path=tube(pts,.5);upper.append(q);ul.append(path.length)
  # Native stock pin order; longitudinal row coordinate and outward exit.
  u=(i-6.5)*1.25;theta=math.radians(120 if sgn==1 else -120)
  ep=[sgn*15.5+u*math.cos(theta)+7.4*math.sin(theta),43-u*math.sin(theta)+7.4*math.cos(theta),12.8]
  approach=[ep[0]+8*math.sin(theta),ep[1]+8*math.cos(theta),12.8]
  pts=[pts[-1],approach,ep];q,path=tube(pts,.5);last.append(q);ml.append(path.length)
 return dict(lower=lower,wing_fanout=Compound(children=fan),upper=Compound(children=upper),main_fanout=Compound(children=last)),dict(lower_waypoints_mm=lowerpts,upper_waypoints_mm=upperpts,longest_connected_conductor_mm=max(fl[i]+lp.length-math.dist([sgn*27,-24,5],[sgn*14,-18.8,5])+ul[i]+ml[i] for i in range(14)),main_outlets_mm=[bb(q) for q in last])

def checks(s,items,skip=()):
 out=[]
 for n,o in items.items():
  if n in skip:continue
  v=volume(s,o)
  if v>1e-6:out.append(dict(part=n,overlap_mm3=v))
 return out
