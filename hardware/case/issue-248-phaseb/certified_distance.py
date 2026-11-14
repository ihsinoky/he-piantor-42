"""Minimum over trimmed boundary faces, bypassing whole-solid inside shortcut."""
from common import *
def box_lower(a,b):return math.sqrt(sum(max(a[0][i]-b[1][i],b[0][i]-a[1][i],0)**2 for i in range(3)))
def boundary_distance(a,b):
 aa=[(f,bounds(f)) for f in a.faces()];bb=[(f,bounds(f)) for f in b.faces()]
 pairs=sorted([(box_lower(x,y),i,j) for i,(f,x) in enumerate(aa) for j,(g,y) in enumerate(bb)])
 best=float('inf');witness=None;count=0
 for lower,i,j in pairs:
  if lower>best+1e-7:break
  gap,pa,pb=aa[i][0].distance_to_with_closest_points(bb[j][0]);count+=1
  pa=list(pa);pb=list(pb)
  # Witnesses must be finite and within the actual trimmed-face bounds.
  for point,bound in [(pa,aa[i][1]),(pb,bb[j][1])]:
   assert all(math.isfinite(p) and bound[0][k]-1e-5<=p<=bound[1][k]+1e-5 for k,p in enumerate(point)),(gap,point,bound)
  assert abs(math.dist(pa,pb)-gap)<1e-5
  if gap<best:best=gap;witness=dict(a_face=i,b_face=j,a_point_mm=pa,b_point_mm=pb)
 return best,dict(**witness,exact_face_pairs=count,all_face_pairs=len(pairs),method='minimum exact distance over actual trimmed boundary faces; all other pairs excluded only by Euclidean AABB lower bound')
