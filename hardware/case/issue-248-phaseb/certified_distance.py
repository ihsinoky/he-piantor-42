"""Minimum over trimmed boundary faces, bypassing whole-solid inside shortcut."""
from common import *
def box_lower(a,b):return math.sqrt(sum(max(a[0][i]-b[1][i],b[0][i]-a[1][i],0)**2 for i in range(3)))
def boundary_distance(a,b,zero_precision_mm=0.):
 aa=[(f,bounds(f)) for f in a.faces()];bb=[(f,bounds(f)) for f in b.faces()]
 pairs=sorted([(box_lower(x,y),i,j) for i,(f,x) in enumerate(aa) for j,(g,y) in enumerate(bb)])
 best=float('inf');witness=None;count=0
 if zero_precision_mm:
  # A distance between actual BRep vertices is a valid upper bound. This seed
  # is used only for seam reporting; clearance-gate face searches are unchanged.
  def vertices(faces):
   result={}
   for i,(face,bound) in enumerate(faces):
    for v in face.vertices():result.setdefault(tuple(v.center()),i)
   return result
  av=vertices(aa);bv=vertices(bb);ax=np.array(list(av));bx=np.array(list(bv))
  for start in range(0,len(ax),128):
   squared=np.sum((ax[start:start+128,None,:]-bx[None,:,:])**2,axis=2)
   i,j=np.unravel_index(squared.argmin(),squared.shape);value=math.sqrt(float(squared[i,j]));i+=start
   if value<best:
    best=value;pa=tuple(ax[i]);pb=tuple(bx[j]);witness=dict(a_face=av[pa],b_face=bv[pb],a_point_mm=list(pa),b_point_mm=list(pb),seed='actual BRep vertex distance upper bound')
 for lower,i,j in pairs:
  # Euclidean boundary distance has a global lower bound of zero.
  # Default callers require an exact zero. Seam reporting alone may request
  # an explicit [0,best] bracket; this does not certify a positive clearance.
  if best<=zero_precision_mm:break
  if lower>best+1e-7:break
  gap,pa,pb=aa[i][0].distance_to_with_closest_points(bb[j][0]);count+=1
  pa=list(pa);pb=list(pb)
  # Witnesses must be finite and within the actual trimmed-face bounds.
  for point,bound in [(pa,aa[i][1]),(pb,bb[j][1])]:
   assert all(math.isfinite(p) and bound[0][k]-1e-5<=p<=bound[1][k]+1e-5 for k,p in enumerate(point)),(gap,point,bound)
  assert abs(math.dist(pa,pb)-gap)<1e-5
  if gap<best:best=gap;witness=dict(a_face=i,b_face=j,a_point_mm=pa,b_point_mm=pb)
 return best,dict(**witness,exact_face_pairs=count,all_face_pairs=len(pairs),method='certified near-zero boundary-distance interval using a true BRep witness and global zero lower bound' if zero_precision_mm and best<=zero_precision_mm else 'minimum exact distance over actual trimmed boundary faces; other pairs excluded by Euclidean AABB lower bounds or exact zero lower bound',global_zero_lower_bound_used=best<=zero_precision_mm,minimum_distance_interval_mm=[0.,best] if best<=zero_precision_mm else [best,best],requested_zero_bracket_mm=zero_precision_mm)
