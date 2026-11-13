"""Reconstruct one cover solid; verify equality with the audited tile partition."""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'issue-232-final'))
from geometry import *
from build123d import Shape
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main(pitch):
 out=HERE/f'{pitch}mm';d=json.loads((out/'measurements.json').read_text());cp=shape(d['cover_outline']);assert cp.geom_type=='Polygon'
 cover=prism(cp,14.7,1.5);gs=[]
 for sgn,angle in [(-1,-120),(1,120)]:
  a=math.radians(angle);x=sgn*17.102146;y=42.075
  gs.append(Polygon([(x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]]))
 fs=d['fly']['path_samples_mm']
 for g,z in [(unary_union(gs).buffer(.3),15.95),(LineString([(p[0],p[1]) for p in fs]).simplify(.02).buffer(1.22,quad_segs=8),15.8),(box(-5,-55,5,-45),15.2)]:
  cover=cover.cut(prism(cp.intersection(g),14.699,z-14.699))
 for x,y in d['retention_sites_mm']:
  cover=cover.cut(cylinder(x,y,1.1,14.699,1.502)).cut(Solid.make_cone(.8,2.1,1,Plane(origin=(x,y,15.2))))
 cache=ROOT/f'.issue242-runtime/audit{pitch}';index=json.loads((cache/'index.json').read_text());partition=0
 for i,r in enumerate(index):
  if r['name']!='Cover':continue
  s=TopoDS_Shape();BRepTools.Read_s(s,str(cache/f'{i}.brep'),BRep_Builder());partition+=Shape.cast(s).volume
 assert cover.is_valid and len(cover.solids())==1
 assert abs(cover.volume-partition)<1e-3,(cover.volume,partition)
 export_step(cover,out/'cover-study.step')
 save(out/'cover-metrology.json',dict(valid=cover.is_valid,solid_count=len(cover.solids()),volume_mm3=cover.volume,audited_partition_volume_mm3=partition,volume_agreement_mm3=abs(cover.volume-partition),top_Z_mm=cover.bounding_box().max.Z,outline_connected=cp.geom_type=='Polygon'))
 print(pitch,'single-solid cover / tile volume agreement',abs(cover.volume-partition),flush=True)
if __name__=='__main__':main(int(sys.argv[1]))
