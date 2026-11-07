"""Analytic rectangular-sheet check of the same triangle stiffness kernel."""
from pathlib import Path
import importlib.util,json,sys
sys.path[:0]=['/home/hatch/workspace/projects/he-piantor-42/.issue175-runtime/python','/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/venv/lib/python3.12/site-packages']
import numpy as np
from scipy.sparse import coo_matrix
E=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('extract',E/'extract-resistance.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
checks=[]
for length,width,nx,ny in [(10.,1.,20,4),(3.,7.,6,14)]:
 vertices=np.array([(length*x/nx,width*y/ny) for y in range(ny+1) for x in range(nx+1)])
 triangles=[]
 for y in range(ny):
  for x in range(nx):
   a=y*(nx+1)+x;c=a+nx+1;triangles.extend([(a,a+1,c+1),(a,c+1,c)])
 tri=np.array(triangles);pts=vertices[tri];a2=np.abs((pts[:,1,0]-pts[:,0,0])*(pts[:,2,1]-pts[:,0,1])-(pts[:,1,1]-pts[:,0,1])*(pts[:,2,0]-pts[:,0,0]));local=m.sheet_elements(pts,a2);I=[];J=[];G=[]
 for a in range(3):
  for b in range(3):I.extend(tri[:,a]);J.extend(tri[:,b]);G.extend(local[:,a,b])
 K=coo_matrix((G,(I,J)),shape=(len(vertices),len(vertices))).tocsr();voltage=vertices[:,0]/length;currents=K@voltage
 left=np.isclose(vertices[:,0],0);right=np.isclose(vertices[:,0],length);inside=~(left|right)
 current=float(sum(currents[right]));resistance=1/current;analytic=1.7241e-8*length/(35e-6*width)
 assert abs(resistance/analytic-1)<1e-10 and np.max(np.abs(currents[inside]))<1e-9
 checks.append(dict(length_mm=length,width_mm=width,analytic_ohm=analytic,FEM_ohm=resistance,relative_error=abs(resistance/analytic-1),interior_KCL_A=float(np.max(np.abs(currents[inside])))))
(E/'fem-selfcheck.json').write_text(json.dumps(dict(pass_all=True,sheet_checks=checks),indent=2)+'\n');print(checks)
