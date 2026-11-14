"""Independent analytic sheet benchmark, reciprocity and load superposition checks."""
from common import *
sys.path[:0]=[str(BASE/'.issue175-runtime/python'),str(B/'venv/lib/python3.12/site-packages')]
import numpy as np,triangle
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
verts=np.array([[0.,0.],[10.,0.],[10.,5.],[0.,5.]])
a=triangle.triangulate(dict(vertices=verts,segments=np.array([[0,1],[1,2],[2,3],[3,0]])),'pq20a.03Q');v=a['vertices'];tr=a['triangles'];sigma=35e-6/1.7241e-8
I=[];J=[];G=[]
for ids in tr:
 x=v[ids];twice_area=abs(np.linalg.det(np.array([[1,*p] for p in x])));Bmat=np.linalg.inv(np.array([[1,*p] for p in x]))[1:,:];local=sigma*twice_area/2*(Bmat.T@Bmat)
 for i in range(3):
  for j in range(3):I.append(ids[i]);J.append(ids[j]);G.append(local[i,j])
K=coo_matrix((G,(I,J)),shape=(len(v),len(v))).tocsc();left=np.flatnonzero(abs(v[:,0])<1e-10);right=np.flatnonzero(abs(v[:,0]-10)<1e-10);fixed=np.r_[left,right];unknown=np.setdiff1d(np.arange(len(v)),fixed);u=np.zeros(len(v));u[right]=1;u[unknown]=spsolve(K[unknown,:][:,unknown],-(K[unknown,:]@u));current=(K@u)[right].sum();r=1/current;analytic=1.7241e-8/35e-6*10/5;assert abs(r/analytic-1)<1e-8
checks=[]
def av(result,ref):return sum(x for k,x in result['terminal_voltage_V'].items() if k.startswith(ref+'.'))/6
for label in ['final']:
 s=json.loads((E/('ground-extraction-'+label+'.json')).read_text());rows=s['rows']
 for row in rows:
  one,two,both=row['results_at_20C']['output_returns'];recip=abs(av(one,'J3')-av(two,'J2'));superpos=max(abs(av(both,ref)-.127*(av(one,ref)+av(two,ref))) for ref in ['J2','J3']);assert recip<1e-7 and superpos<1e-7
  assert max(x['kcl_residual_A'] for x in [one,two,both,row['results_at_20C']['input_return']])<1e-6
  checks.append(dict(label=label,mesh_area=row['max_triangle_area_mm2'],width_factor=row['track_width_factor'],reciprocity_error_V=recip,superposition_error_V=superpos))
save(E/'ground-model-verification.json',dict(utc=now(),pass_numerics=True,rectangle_dimensions_mm=[10,5],rectangle_expected_ohm=analytic,rectangle_extracted_ohm=r,relative_error=abs(r/analytic-1),checks=checks,manufacturing_bound=False,limitation='Convergence and algebra do not prove actual material minima or return-current contact distribution'))
print('Ground solver: analytic rectangle, reciprocity, superposition and KCL PASS')
