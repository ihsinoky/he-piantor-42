"""Millimetres, assembly X right/Y south/Z up. No writes to source trees."""
from pathlib import Path
import os,sys,json,csv,math,hashlib
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'issue-228-final'
STUDY=HERE.parent/'issue-230-mount-study'
REV4=ROOT/'hardware/kicad/qualification/issue-235-wing-round2'
sys.path.insert(0,str(BASE))
from base import prism,cylinder,polygons,coords,rows,save,sha,rect_key
from build123d import Face,Wire,Edge,Vector,Plane,Solid,Compound,extrude,sweep,import_step,export_step,export_stl
from shapely.geometry import Polygon,Point,LineString,box,mapping,shape
from shapely.affinity import affine_transform
from shapely.ops import unary_union
import numpy as np

def transform(g,t):
 m=t['matrix'];return affine_transform(g,[m[0][0],m[0][1],m[1][0],m[1][1],*t['translation']])

def leaves(s,owner=None):
 n=s.label
 if not n or n.lower() in ('solid','compound','assembly','part'):n=owner
 cs=list(s.children)
 if cs:
  return [p for c in cs for p in leaves(c,n)]
 return [(n,s)]

def volume(a,b):
 aa=a.bounding_box();bb=b.bounding_box()
 if any(min(getattr(aa.max,k),getattr(bb.max,k))-max(getattr(aa.min,k),getattr(bb.min,k))<1e-7 for k in ('X','Y','Z')):return 0.
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 from OCP.BRepGProp import BRepGProp
 from OCP.GProp import GProp_GProps
 operation=BRepAlgoAPI_Common(a.wrapped,b.wrapped);operation.Build()
 if not operation.IsDone():raise RuntimeError('OCP intersection failed')
 common=operation.Shape()
 if common.IsNull():return 0.
 props=GProp_GProps();BRepGProp.VolumeProperties_s(common,props,True,False,False)
 return abs(props.Mass())

def rounded(points,radius=5.):
 pts=[np.array(p,float) for p in points];corners={}
 for i in range(1,len(pts)-1):
  u=pts[i-1]-pts[i];u/=np.linalg.norm(u);v=pts[i+1]-pts[i];v/=np.linalg.norm(v)
  theta=math.acos(np.clip(float(np.dot(u,v)),-1,1));d=radius/math.tan(theta/2)
  if not math.isfinite(d) or d<1e-8:continue
  center=pts[i]+(u+v)/np.linalg.norm(u+v)*radius/math.sin(theta/2)
  a=pts[i]+u*d;b=pts[i]+v*d;mid=center+(pts[i]-center)/np.linalg.norm(pts[i]-center)*radius
  corners[i]=(a,mid,b,d)
 for i in range(len(pts)-1):
  need=(corners[i][3] if i in corners else 0)+(corners[i+1][3] if i+1 in corners else 0)
  assert need<np.linalg.norm(pts[i+1]-pts[i])-1e-6,('R5 straight too short',i,need,points)
 edges=[];prev=pts[0]
 for i in range(1,len(pts)-1):
  if i not in corners:continue
  a,mid,b,d=corners[i];edges.extend([Edge.make_line(Vector(*prev),Vector(*a)),Edge.make_three_point_arc(Vector(*a),Vector(*mid),Vector(*b))]);prev=b
 edges.append(Edge.make_line(Vector(*prev),Vector(*pts[-1])))
 return Wire(edges)

def tube(points,radius,bend=5):
 path=rounded(points,bend);direction=np.array(points[1])-np.array(points[0])
 return sweep(Face(Wire.make_circle(radius,Plane(origin=Vector(*points[0]),z_dir=Vector(*map(float,direction))))),path=path),path

def export(s,p,stl=False):
 s.parent=None
 s.label=p.stem
 export_step(s,p.with_suffix('.step'))
 if stl:
  reloaded=import_step(p.with_suffix('.step'))
  export_stl(reloaded,p.with_suffix('.stl'),tolerance=.005,angular_tolerance=.025)

def local_round_square(x,y,angle,w=14.02,r=.2):
 from shapely.affinity import rotate,translate
 return translate(rotate(box(-w/2+r,-w/2+r,w/2-r,w/2-r).buffer(r,quad_segs=8),angle),x,y)

def dxf(path,g):
 import ezdxf
 doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace()
 for layer in ('OUTLINE','APERTURES','TIE_HOLES'):doc.layers.new(layer)
 m.add_lwpolyline(list(g.exterior.coords)[:-1],close=True,dxfattribs={'layer':'OUTLINE'})
 for ring in g.interiors:
  poly=Polygon(ring);layer='APERTURES' if poly.area>100 else 'TIE_HOLES'
  m.add_lwpolyline(list(ring.coords)[:-1],close=True,dxfattribs={'layer':layer})
 doc.saveas(path)
