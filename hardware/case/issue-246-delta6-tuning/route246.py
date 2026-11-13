"""Continuous R5 conductor centerlines and the nominal OD5 lower bundle.
All coordinates precede the common final Delta translation.
"""
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'issue-232-final'))
from geometry import tube,rounded,Compound

def wing(sgn,south,delta=6):
 low=7-delta
 lowpts=[[sgn*27,-24,low],[sgn*7,-16,low],[sgn*7,south,low],[sgn*19,south,low],[sgn*19,0,low]]
 lower,lp=tube(lowpts,2.5)
 # A 4/3/4/3 hex pack has 2.5042 mm maximum material radius;
 # the full strands plus nominal OD5 bundle are audited. 1.01 mm centers avoid
 # coincident/tangent OD1 faces. All fourteen curves continue through the U.
 pack=[]
 for row,count in enumerate((4,3,4,3)):
  for col in range(count):pack.append(((col-(count-1)/2)*1.01,(row-1.5)*math.sqrt(3)/2*1.01))
 upperpack=[((i-2)*1.05,-1.05) for i in range(5)]+[((i-2)*1.05,0) for i in range(5)]+[((i-1.5)*1.05,1.05) for i in range(4)]
 wires=[];lengths=[];samples=[];waypoints=[];eps=[];upper_samples=[]
 for i,((dx,dzlow),(off,dz)) in enumerate(zip(pack,upperpack)):
  a=math.radians(120 if sgn==1 else -120);u=(i-6.5)*1.25
  ep=[sgn*15.5+u*math.cos(a)+7.4*math.sin(a),43-u*math.sin(a)+7.4*math.cos(a),12.8]
  ap=[ep[0]+9*math.sin(a),ep[1]+9*math.cos(a),12.8]
  lpts=[[p[0]+sgn*dx,p[1],p[2]+dzlow] for p in lowpts]
  pts=[[sgn*27+(i-6.5)*1.25,-35.45,8.4],[sgn*27+(i-6.5)*1.25,-31.5,8.4]]+lpts+[[sgn*(5+off),-18,low],[sgn*(5+off),-7,12.8+dz],[sgn*(23+off),8,12.8+dz],ap,ep]
  q,p=tube(pts,.5)
  assert q.is_valid and len(q.solids())==1
  wires.append(q);lengths.append(p.length);waypoints.append(pts);eps.append(ep)
  samples.append([[v.X,v.Y,v.Z] for v in p.positions([j/800 for j in range(801)])])
  up=rounded(pts[6:]);upper_samples.append([[v.X,v.Y,v.Z] for v in up.positions([j/320 for j in range(321)])])
 return {'conductors':Compound(children=wires),'lower':lower},dict(longest_conductor_mm=max(lengths),conductor_lengths_mm=lengths,conductor_waypoints_mm=waypoints,conductor_samples_mm=samples,lower_waypoints_mm=lowpts,lower_length_mm=lp.length,upper_samples_mm=upper_samples,main_exits_mm=eps,lower_pack_offsets_mm=pack,upper_pack_offsets_mm=upperpack)
