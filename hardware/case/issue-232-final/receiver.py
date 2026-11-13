"""Receiving tray; exact D-037 BRep silhouette is authoritative at raised joins."""
from geometry import *

def make(original,outer,cavity,deck,clip,flybay,d,pitch,side,channel):
 # A sampled/projected curve can differ by microns at a clipped Fly boundary.
 # Extend construction material then trim with the original exact outer wire,
 # avoiding coincident near-duplicate exterior surfaces at that junction.
 faces=[]
 for f in original.faces():
  try:
   if abs(f.center().Z)<1e-7 and f.normal_at().Z<-.99:faces.append(f)
  except Exception:pass
 floor=max(faces,key=lambda f:f.area)
 footprint=extrude(Face(floor.outer_wire()),amount=30,dir=(0,0,1))
 band=outer.buffer(.02,join_style=2).difference(outer.buffer(-.02,join_style=2))
 tray=original.cut(channel).cut(prism(box(-300,-200,300,200).difference(flybay),14.7,30))
 ring=outer.difference(cavity)
 rim=outer.difference(outer.buffer(-1,join_style=2))
 pocket=deck.buffer(-1,join_style=2)
 ledge=deck.difference(Polygon(d['boards']['wing_'+side]).buffer(.502,join_style=2))
 inner_rim=deck.difference(pocket)
 for g,z,h in [(ring,11.2,3.5),(rim,14.7,1.5),(ledge,11.2,3.5),(inner_rim,14.7,1.5)]:
  g=g.union(band).difference(flybay).intersection(clip).simplify(.003,preserve_topology=True)
  if g.is_empty:continue
  material=prism(g,z,h);material=Compound(children=list(material.intersect(footprint)))
  tray=tray.fuse(material)
 for r in rows(STUDY/f'{pitch}mm-{side}/supports.csv'):
  tray=tray.cut(cylinder(float(r['assembly_x_mm']),float(r['assembly_y_mm']),1.55,1.2,.8))
 assert tray.is_valid and len(tray.solids())==1
 return tray
