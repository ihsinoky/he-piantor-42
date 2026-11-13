import os
os.environ['MPLCONFIGDIR']=os.path.abspath('.issue230-runtime/mplconfig')
from pathlib import Path
import json,math,csv,struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
from shapely.geometry import shape,Point
from shapely.geometry.polygon import orient
from shapely import constrained_delaunay_triangles
P=Path(__file__).resolve().parent
def stl(path,g,z0,z1):
 g=orient(g,sign=1.0)
 triangles=[]
 for t in constrained_delaunay_triangles(g).geoms:
  pts=list(t.exterior.coords)[:3]
  v=np.array(pts[1])-pts[0];w=np.array(pts[2])-pts[0];cross=v[0]*w[1]-v[1]*w[0]
  if cross<0:pts=pts[::-1]
  triangles.append([(x,y,z1) for x,y in pts]);triangles.append([(x,y,z0) for x,y in pts[::-1]])
 for r in [g.exterior,*g.interiors]:
  pts=list(r.coords)
  for a,b in zip(pts,pts[1:]):triangles.extend([[(a[0],a[1],z0),(b[0],b[1],z0),(b[0],b[1],z1)],[(a[0],a[1],z0),(b[0],b[1],z1),(a[0],a[1],z1)]])
 with path.open('wb') as f:
  f.write(b'Issue 230 study mesh, millimetres'.ljust(80,b' '));f.write(struct.pack('<I',len(triangles)))
  for t in triangles:
   n=np.cross(np.array(t[1])-t[0],np.array(t[2])-t[0]);n=n/np.linalg.norm(n)
   f.write(struct.pack('<12fH',*n,*t[0],*t[1],*t[2],0))
# Assembly elevations in plate STL; generic post STL origin local XY.
for d in sorted(P.glob('*mm-*')):
 g=shape(json.load(open(d/'plate.geojson')));stl(d/'plate-study.stl',g,14.7,16.2)
stl(P/'support-shaft.stl',Point(0,0).buffer(1.5,quad_segs=32),2.5,10)
stl(P/'support-collar.stl',Point(0,0).buffer(2.25,quad_segs=32),2,2.5)
stl(P/'support-peg.stl',Point(0,0).buffer(1.575,quad_segs=32),1.2,2)
# Main review diagram uses real generated plate, actual key coordinates and mount supports.
d=P/'17mm-left';g=shape(json.load(open(d/'plate.geojson')))
fig,ax=plt.subplots(figsize=(10,9));ax.add_patch(Patch(g.exterior.coords,facecolor='#adcce0',edgecolor='#172e42',lw=.8))
for r in g.interiors:ax.add_patch(Patch(r.coords,facecolor='white',edgecolor='#172e42',lw=.5))
for r in csv.DictReader(open(d/'cutouts.csv')):ax.text(float(r['x_mm']),float(r['y_mm']),r['key'].removeprefix('L_'),ha='center',va='center',fontsize=7)
for r in csv.DictReader(open(d/'supports.csv')):
 x,y=float(r['x_mm']),float(r['y_mm']);ax.add_patch(plt.Circle((x,y),1.5,color='#d44b13'));ax.text(x+2,y,r['id'],color='#a32b00',fontsize=9)
for r in csv.DictReader(open(d/'tie-holes.csv')):ax.text(float(r['x_mm'])+2,float(r['y_mm']),r['id'],fontsize=9)
ax.set_aspect('equal');ax.autoscale();ax.set_xlabel('Wing local X (mm)');ax.set_ylabel('Wing local Y north (mm)');ax.set_title('Recommended E-R: 1.5 mm aluminium plate + six underside supports\n17 mm left Wing; blue plate, orange PCB support contacts');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(P/'recommendation.png',dpi=170);plt.close(fig)
s=json.load(open(P/'summary.json'));s=[x for x in s if x['variant']=='17mm-left'];opts=['baseline','A_ribs_plateless','B_six_point_al_plate','C_pcb_tadpole_rev4six','D_legal_added_bosses_al_plate','E_float_with_screw_fallback','E_tray_ribs_al_plate'];labels=['Current tray','A: ribs only','B: 6 Tadpoles + Al','C: 6 PCB Tadpoles','D: added screws + Al','E-F: float/fallback','E-R: tray/ribs + Al']
fig,ax=plt.subplots(figsize=(10,5))
for i,(opt,label) in enumerate(zip(opts,labels)):
 a=next(x for x in s if x['option']==opt);ax.barh(i,a['bend_upper_mm']['max'],color='#387596');ax.plot([a['bend_lower_mm']['max'],a['bend_upper_mm']['max']],[i,i],color='black',lw=2)
ax.set_yticks(range(len(labels)),labels);ax.invert_yaxis();ax.set_xlabel('Worst-key bending proxy at 1 N (mm); black = strip-model bracket');ax.set_title('Mount layout dominates the stiffness benefit of a thin perforated plate');ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(P/'comparison.png',dpi=170)
