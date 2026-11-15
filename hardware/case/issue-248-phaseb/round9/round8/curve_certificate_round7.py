"""Independent non-rational Bezier convex-hull curvature bound and quadrature.

For each patch, bound |v×a| above by the largest Bernstein cross-product
control vector and |v| below by the smallest velocity-control projection onto
its midpoint tangent. Their quotient bounds curvature on the entire interval.
Subdivision tightens bounds; no finite curvature sampling establishes a PASS.
"""
from common import *
from OCP.GeomConvert import GeomConvert_BSplineCurveToBezierCurve
from scipy.integrate import quad

def split(p):
 work=np.array(p);left=[work[0]];right=[work[-1]]
 while len(work)>1:
  work=(work[:-1]+work[1:])/2;left.append(work[0]);right.append(work[-1])
 return np.array(left),np.array(right[::-1])
def evaluate(p,t):
 q=np.array(p)
 while len(q)>1:q=q[:-1]*(1-t)+q[1:]*t
 return q[0]
def radius_lower_bound(p):
 degree=len(p)-1;v=degree*np.diff(p,axis=0);a=(degree-1)*np.diff(v,axis=0);pdeg=len(v)-1;qdeg=len(a)-1
 mid=evaluate(v,.5);direction=mid/np.linalg.norm(mid);lower=float(np.min(v@direction))
 if lower<=0:return 0.
 cc=[]
 for k in range(pdeg+qdeg+1):
  c=np.zeros(3)
  for i in range(pdeg+1):
   j=k-i
   if 0<=j<=qdeg:c+=math.comb(pdeg,i)*math.comb(qdeg,j)/math.comb(pdeg+qdeg,k)*np.cross(v[i],a[j])
  cc.append(c)
 upper=max(np.linalg.norm(c) for c in cc)
 return lower**3/upper if upper>1e-20 else 1e15

def certify(edge,target=5,maxdepth=8):
 adaptor=edge.geom_adaptor();spline=adaptor.Curve().Curve().Copy();assert not spline.IsRational()
 spline.Transform(edge.location.wrapped.Transformation())
 converter=GeomConvert_BSplineCurveToBezierCurve(spline,adaptor.FirstParameter(),adaptor.LastParameter(),1e-12)
 radii=[];length=0.;err=0.;leaves=0;unproved=[]
 for i in range(1,converter.NbArcs()+1):
  bz=converter.Arc(i);p=np.array([[v.X(),v.Y(),v.Z()] for v in bz.Poles()]);v=(len(p)-1)*np.diff(p,axis=0)
  val,e=quad(lambda t:float(np.linalg.norm(evaluate(v,t))),0,1,epsabs=1e-11,epsrel=1e-11);length+=val;err+=e
  stack=[(p,0)]
  while stack:
   p,depth=stack.pop();r=radius_lower_bound(p)
   if r<target and depth<maxdepth:
    l,rr=split(p);stack.extend([(l,depth+1),(rr,depth+1)]);continue
   leaves+=1;radii.append(r)
   if r<target:unproved.append(dict(bezier_patch=i,subdivision_depth=depth,radius_lower_bound_mm=r))
 return dict(method='non-rational Bezier Bernstein velocity/acceleration cross-product convex-hull bound, adaptive dyadic subdivision',bezier_patches=converter.NbArcs(),bounded_subintervals=leaves,minimum_radius_lower_bound_mm=min(radii),target_radius_mm=target,passed=not unproved,unproved_intervals=unproved,independent_quadrature_length_mm=length,quadrature_error_estimate_mm=err,kernel_curve_length_mm=edge.length,length_delta_mm=length-edge.length)
if __name__=='__main__':
 from routes_round7 import components
 p=HERE/'routes-round7-prototype.json'
 assert p.exists()
 d=read(p);rows=[]
 for r in d['right']:
  c=components(r)[2];proof=certify(c);rows.append(dict(pin=r['pin'],**proof));print(r['pin'],proof['passed'],proof['minimum_radius_lower_bound_mm'],proof['length_delta_mm'],flush=True)
 save(HERE/'curve-certificates-round7.json',dict(prototype_sha256=sha(p),strands=rows,passed=all(r['passed'] and abs(r['length_delta_mm'])<1e-6 for r in rows)))
