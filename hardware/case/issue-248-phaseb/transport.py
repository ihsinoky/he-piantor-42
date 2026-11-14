"""Exact parallel transported offsets of a line/circular-arc spine."""
from common import *
def rot(v,k,a):return v*math.cos(a)+np.cross(k,v)*math.sin(a)+k*np.dot(k,v)*(1-math.cos(a))
def offset_path(points,dx,dz,r=7.1):
 p=[np.array(v,float) for v in points];t=(p[1]-p[0]);t/=np.linalg.norm(t)
 b=np.array([0.,0,1]);n=np.cross(b,t);prev=p[0];off=n*dx+b*dz;start=prev+off;edges=[];radii=[];minslack=1e9
 def line(a,b):
  if np.linalg.norm(b-a)>1e-8:edges.append(Edge.make_line(Vector(*a),Vector(*b)))
 for i in range(1,len(p)-1):
  incoming=p[i]-p[i-1];incoming/=np.linalg.norm(incoming);outgoing=p[i+1]-p[i];outgoing/=np.linalg.norm(outgoing)
  alpha=math.acos(float(np.clip(np.dot(incoming,outgoing),-1,1)));k=np.cross(incoming,outgoing);k/=np.linalg.norm(k)
  d=r*math.tan(alpha/2);a=p[i]-incoming*d;c=a+np.cross(k,incoming)*r;end=p[i]+outgoing*d
  slack=np.dot(a-prev,incoming);minslack=min(minslack,slack);assert slack>1e-6,(i,slack)
  line(prev+off,a+off)
  radial=a-c;axial=k*np.dot(k,off);arc_center=c+axial
  aa=a+off;mid=c+rot(radial,k,alpha/2)+rot(off,k,alpha/2);off2=rot(off,k,alpha);bb=end+off2
  radius=float(np.linalg.norm(aa-arc_center));assert radius>=5-1e-7,radius
  edges.append(Edge.make_three_point_arc(Vector(*aa),Vector(*mid),Vector(*bb)));radii.append(radius)
  prev=end;off=off2
 line(prev+off,p[-1]+off)
 return Wire(edges),start,p[-1]+off,radii,minslack
