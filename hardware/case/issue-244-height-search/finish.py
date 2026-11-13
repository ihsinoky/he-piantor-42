"""Exact contact bounds, single-solid exports, and case/cover metrology after audit."""
import sys,json,math
import study as s
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from build123d import Shape

def main(pitch):
 out=s.HERE/f'{pitch}mm';cache=s.RUNTIME/f'audit{pitch}'
 idx=s.read(cache/'index.json');audit=s.read(out/'audit.json');d=s.read(out/'measurements.json')
 raw=[]
 for i,r in enumerate(idx):
  q=s.TopoDS_Shape();s.BRepTools.Read_s(q,str(cache/f'{i}.brep'),s.BRep_Builder());raw.append(Shape.cast(q))
 contacts=[]
 for r in audit['unexpected_interferences']:
  op=BRepAlgoAPI_Common(raw[r['i']].wrapped,raw[r['j']].wrapped);op.SetRunParallel(True);op.SetUseOBB(True);op.Build()
  assert op.IsDone() and not op.Shape().IsNull()
  q=Shape.cast(op.Shape());contacts.append(dict(**r,overlap_bounds_mm=s.bounds(q)))
 s.save(out/'collision-map.json',contacts)
 # Partition -> one machinable cover. Uniform translation leaves all pocket depths fixed.
 cp=s.shape(d['cover_outline']);cover=s.prism(cp,14.7,1.5);gs=[]
 for sgn,angle in [(-1,-120),(1,120)]:
  a=math.radians(angle);x=sgn*17.102146;y=42.075
  gs.append(s.Polygon([(x+u*math.cos(a)+v*math.sin(a),y-u*math.sin(a)+v*math.cos(a)) for u,v in [(-10.375,-1.6),(10.375,-1.6),(10.375,5.55),(-10.375,5.55)]]))
 fs=d['fly']['path_samples_mm']
 for g,z in [(s.unary_union(gs).buffer(.3),15.95),(s.LineString([(p[0],p[1]) for p in fs]).simplify(.02).buffer(1.22,quad_segs=8),15.8),(s.box(-5,-55,5,-45),15.2)]:
  cover=cover.cut(s.prism(cp.intersection(g),14.699,z-14.699))
 for x,y in d['retention_sites_mm']:
  cover=cover.cut(s.cylinder(x,y,1.1,14.699,1.502)).cut(s.Solid.make_cone(.8,2.1,1,s.Plane(origin=(x,y,15.2))))
 cover=cover.translate((0,0,s.DELTA))
 pv=sum(q.volume for r,q in zip(idx,raw) if r['name']=='Cover')
 assert cover.is_valid and len(cover.solids())==1 and abs(cover.volume-pv)<1e-3
 s.export_step(cover,out/'cover-study.step')
 met=dict(cover=dict(valid=True,solids=1,partition_volume_mm3=pv,volume_mm3=cover.volume,volume_difference_mm3=abs(cover.volume-pv),bounds_mm=s.bounds(cover)),wings={},printing={})
 for side in ('left','right'):
  parts=[q for r,q in zip(idx,raw) if r['name'].startswith('Wing-'+side)]
  # Conservative fanout constituents are audited separately; delivered cable is their union.
  cable=parts[0].fuse(*parts[1:])
  met['wings'][side]=dict(valid=cable.is_valid,solids=len(cable.solids()),volume_mm3=cable.volume)
  # A rejected candidate may also fail cable-union topology. Preserve that
  # diagnostic and the original audited envelope instead of losing metrology.
  if cable.is_valid and len(cable.solids())==1:
   s.export_step(cable,out/f'wing-{side}.step')
  tray=[q for r,q in zip(idx,raw) if r['name']=='tray-'+side]
  assert tray
  tray=s.Compound(children=tray)
  b=tray.bounding_box()
  met['printing'][side]=dict(with_5mm_brim_xy_mm=[b.size.X+10,b.size.Y+10],z_mm=b.size.Z,within_220x220x250=max(b.size.X+10,b.size.Y+10)<=220 and b.size.Z<=250,valid=tray.is_valid,solids=len(tray.solids()),constituents=[dict(volume_mm3=q.volume,bounds_mm=s.bounds(q)) for q in tray.solids()])
 s.save(out/'metrology.json',met)
 print('METROLOGY',s.DELTA,pitch,met,flush=True)
if __name__=='__main__':main(int(sys.argv[1]))
