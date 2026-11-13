"""Continuous planar envelope of the OD5 U as its turn retracts 22.1 -> 7.
The two R5 quarter arcs plus the 2 mm straight cap are graphs Y=f(X).
Translating the cap continuously in Y fills the strip between its end graphs.
The two legs and fixed entry corner are contained by the longest U curve.
A 0.152 mm XY allowance bounds all sampling/simplification errors (<0.01 mm).
The vertical slab Z4.5..9.5 conservatively contains the circular OD5 section.
"""
import math
from geometry import rounded,LineString,Polygon,unary_union

def footprint(sgn):
 cap=[]
 for j in range(33):
  a=math.pi-j*math.pi/64;cap.append((12+5*math.cos(a),2+5*math.sin(a)))
 for j in range(33):
  a=math.pi/2-j*math.pi/64;cap.append((14+5*math.cos(a),2+5*math.sin(a)))
 strip=Polygon([(sgn*x,y) for x,y in cap]+[(sgn*x,y+15.1) for x,y in reversed(cap)])
 pts=[[sgn*27,-24,7],[sgn*7,-16,7],[sgn*7,22.1,7],[sgn*19,22.1,7],[sgn*19,0,7]]
 p=rounded(pts);xy=[(v.X,v.Y) for v in p.positions([j/400 for j in range(401)])]
 g=unary_union([strip,LineString(xy).simplify(.003)]).buffer(2.65,quad_segs=32)
 return g.simplify(.002).buffer(.002,quad_segs=16)
