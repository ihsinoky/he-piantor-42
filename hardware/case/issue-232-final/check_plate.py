"""Independent DXF metrology and STEP underside lead-in probes at all apertures."""
from geometry import *
import ezdxf

def run(pitch):
 out=HERE/f'{pitch}mm';d=json.loads((out/'dimensions.json').read_text());result=[]
 for side in ('left','right'):
  print(pitch,side,'plate metrology',flush=True)
  entities=list(ezdxf.readfile(out/f'plate-package/plate-{side}.dxf').modelspace())
  holes=[Polygon([(p[0],p[1]) for p in e.get_points()]) for e in entities if e.dxf.layer=='APERTURES']
  tieholes=[Polygon([(p[0],p[1]) for p in e.get_points()]) for e in entities if e.dxf.layer=='TIE_HOLES']
  plate=import_step(out/f'plate-package/plate-{side}.step');solid=plate.solids()[0];bb=plate.bounding_box()
  t=d['wing_transforms'][side];m=np.array(t['matrix']);trans=np.array(t['translation']);perkey=[]
  for r in rows(STUDY/f'{pitch}mm-{side}/cutouts.csv'):
   c=m@np.array([float(r['x_mm']),float(r['y_mm'])])+trans
   h=min(holes,key=lambda h:math.dist([h.centroid.x,h.centroid.y],c))
   verts=list(h.minimum_rotated_rectangle.exterior.coords);edges=[math.dist(a,b) for a,b in zip(verts,verts[1:])]
   theta=math.radians(float(r['rotation_ccw_deg']));u=m@np.array([math.cos(theta),math.sin(theta)])
   def inside(offset,z):return solid.is_inside(Vector(*(c+u*offset),z))
   probes=dict(upper_nominal_open=not inside(7.,16.1),upper_clip_flat_material=inside(7.11,16.1),underside_leadin_open=not inside(7.11,14.75),leadin_upper_material=inside(7.11,14.95))
   vs=list(h.exterior.coords)[:-1];radii=[]
   for i in range(len(vs)):
    a,b,e=map(np.array,[vs[i-2],vs[i-1],vs[i]])
    ab=np.linalg.norm(a-b);be=np.linalg.norm(b-e)
    if ab<.05 and be<.05:
     cross=abs(float((b[0]-a[0])*(e[1]-a[1])-(b[1]-a[1])*(e[0]-a[0])))
     if cross>1e-12:radii.append(float(ab*be*np.linalg.norm(e-a)/(2*cross)))
   row=dict(key=r['key'],centre_error_mm=math.dist([h.centroid.x,h.centroid.y],c),flat_min_mm=min(edges),flat_max_mm=max(edges),corner_radius_min_mm=min(radii),corner_radius_max_mm=max(radii),lead_in_probes=probes)
   row['passed']=row['centre_error_mm']<1e-7 and max(abs(e-14.02) for e in edges)<1e-7 and max(abs(v-.2) for v in radii)<1e-7 and all(probes.values())
   perkey.append(row)
  ties=[]
  for r in rows(STUDY/f'{pitch}mm-{side}/tie-holes.csv'):
   c=[float(r['assembly_x_mm']),float(r['assembly_y_mm'])];h=min(tieholes,key=lambda h:math.dist([h.centroid.x,h.centroid.y],c));ce=math.dist([h.centroid.x,h.centroid.y],c)
   radii=[math.dist(p,c) for p in h.exterior.coords];ties.append(dict(id=r['id'],centre_error_mm=ce,diameter_min_mm=min(radii)*2,diameter_max_mm=max(radii)*2,passed=ce<1e-7 and max(abs(2*r-2.2) for r in radii)<1e-7))
  result.append(dict(side=side,thickness_mm=bb.size.Z,bottom_z_mm=bb.min.Z,top_z_mm=bb.max.Z,keys=perkey,ties=ties,passed=all(r['passed'] for r in perkey+ties) and abs(bb.min.Z-14.7)<1e-6 and abs(bb.max.Z-16.2)<1e-6))
 save(out/'plate-metrology.json',dict(plates=result,passed=all(r['passed'] for r in result)))
 print(pitch,'plate checks',all(r['passed'] for r in result),flush=True)
if __name__=='__main__':
 import sys
 run(int(sys.argv[1]))
