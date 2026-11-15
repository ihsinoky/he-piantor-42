import sys
sys.path.insert(0,'hardware/case/issue-248-phaseb')
from common import *
from scipy.spatial.transform import Rotation
from scipy.integrate import cumulative_trapezoid

def rounded_variable(points,radii):
 pts=np.array(points,float);corners={}
 for i in range(1,len(pts)-1):
  radius=radii[i];u=pts[i-1]-pts[i];u/=np.linalg.norm(u);v=pts[i+1]-pts[i];v/=np.linalg.norm(v)
  theta=math.acos(np.clip(float(np.dot(u,v)),-1,1));d=radius/math.tan(theta/2)
  if not math.isfinite(d) or d<1e-8:continue
  center=pts[i]+(u+v)/np.linalg.norm(u+v)*radius/math.sin(theta/2);a=pts[i]+u*d;b=pts[i]+v*d;mid=center+(pts[i]-center)/np.linalg.norm(pts[i]-center)*radius
  corners[i]=(a,mid,b,d)
 for i in range(len(pts)-1):
  need=(corners[i][3] if i in corners else 0)+(corners[i+1][3] if i+1 in corners else 0)
  assert need<np.linalg.norm(pts[i+1]-pts[i])-1e-6,('R straight too short',i,need,float(np.linalg.norm(pts[i+1]-pts[i])))
 edges=[];prev=pts[0]
 for i in range(1,len(pts)-1):
  if i not in corners:continue
  a,mid,b,d=corners[i];edges.extend([Edge.make_line(Vector(*prev),Vector(*a)),Edge.make_three_point_arc(Vector(*a),Vector(*mid),Vector(*b))]);prev=b
 edges.append(Edge.make_line(Vector(*prev),Vector(*pts[-1])))
 return Wire(edges)

