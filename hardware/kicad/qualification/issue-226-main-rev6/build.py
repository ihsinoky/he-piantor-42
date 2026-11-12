"""Rev.5 plus 4mm equal-leg vertex chamfers and local GND plane setback only."""
from common import *
import pcbnew as p,shutil,math,uuid
from shapely.geometry import Polygon,Point
from shapely.ops import split
from shapely.geometry import LineString
V=E.parent/'issue-221-main-rev5';W=E/'inspection/final';W.mkdir(parents=True,exist_ok=True)
for name in ['main.kicad_pro']:shutil.copyfile(V/'inspection/final'/name,W/name)
(W/'fp-lib-table').write_text((V/'inspection/final/fp-lib-table').read_text().replace('${KIPRJMOD}/../../Rev5.pretty','${KIPRJMOD}/../../../issue-221-main-rev5/Rev5.pretty'))
b=p.LoadBoard(str(V/'inspection/final/main.kicad_pcb'))

vertices=[(62.107317,137.9),(100.,72.267949),(137.892682,137.9)]
old=Polygon(vertices);center=old.centroid;new=[];rows=[];clips=[];clip_equations=[]
for i,v in enumerate(vertices):
 units=[]
 for d in [-1,1]:
  q=vertices[(i+d)%3];dx,dy=q[0]-v[0],q[1]-v[1];length=math.hypot(dx,dy);units.append((dx/length,dy/length))
 ends=[]
 for ux,uy in units:
  q=[round(v[0]+4*ux,6),round(v[1]+4*uy,6)]
  # KiCad 1nm grid: round toward the interior if nearest-grid lies outside.
  for _ in range(4):
   if old.covers(Point(q)):break
   q=[round(q[j]+math.copysign(.000001,[center.x,center.y][j]-q[j]),6) for j in [0,1]]
  assert old.covers(Point(q));ends.append(q)
 new.extend(ends)
 angle=math.degrees(math.acos(sum(a*c for a,c in zip(*units))))
 edge=LineString(ends);mid=edge.interpolate(.5,normalized=True);dx=center.x-mid.x;dy=center.y-mid.y
 # Select inward normal to face; clip zone boundary 0.55mm behind it.
 a,c=ends;tx,ty=c[0]-a[0],c[1]-a[1];length=math.hypot(tx,ty);nx,ny=-ty/length,tx/length
 if nx*dx+ny*dy<0:nx,ny=-nx,-ny
 clip_equations.append((nx,ny,nx*a[0]+ny*a[1]+.55))
 shift=[(q[0]+nx*.55,q[1]+ny*.55) for q in ends];sx,sy=shift[0]
 line=LineString([(sx-tx*100,sy-ty*100),(sx+tx*100,sy+ty*100)])
 half=next(g for g in split(Polygon([(0,0),(200,0),(200,200),(0,200)]),line).geoms if g.covers(center));clips.append(half)
 rows.append(dict(vertex=i+1,original_xy_mm=v,interior_angle_deg=angle,nominal_leg_mm=[4,4],actual_leg_mm=[math.dist(v,q) for q in ends],face_endpoints_mm=ends,face_length_mm=length,normal_tip_removed_mm=edge.distance(Point(v)),new_angles_nominal_deg=[120,120],zone_setback_mm=.55))
outline=Polygon(new);assert outline.is_valid and outline.difference(old).area==0
# Replace only root edge blocks in source text; preserve every other object.
import re
raw=(V/'inspection/final/main.kicad_pcb').read_text()
pattern=r'\t\(gr_line\n.*?\n\t\)'
removed=[]
def remove_edge(match):
 block=match.group()
 if '(layer "Edge.Cuts")' in block:removed.append(block);return ''
 return block
raw=re.sub(pattern,remove_edge,raw,flags=re.S);assert len(removed)==3
blocks=[]
for a,c in zip(new,new[1:]+new[:1]):
 blocks.append(f' (gr_line (start {a[0]:.6f} {a[1]:.6f}) (end {c[0]:.6f} {c[1]:.6f}) (stroke (width 0.05) (type default)) (layer "Edge.Cuts") (uuid "{uuid.uuid4()}"))')
raw=raw.rstrip()[:-1]+'\n'+'\n'.join(blocks)+'\n)\n'
local=T/'outline-candidate.kicad_pcb';local.write_text(raw);shutil.copyfile(V/'inspection/final/main.kicad_pro',local.with_suffix('.kicad_pro'));b=p.LoadBoard(str(local))
zone_changes=[]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 poly=z.Outline();assert poly.OutlineCount()==1 and poly.HoleCount(0)==0
 ring=poly.Outline(0);geom=Polygon([(p.ToMM(ring.CPoint(i).x),p.ToMM(ring.CPoint(i).y)) for i in range(ring.PointCount())]);initial=geom
 for clip in clips:geom=geom.intersection(clip)
 assert geom.geom_type=='Polygon' and not geom.interiors
 poly.RemoveAllContours();poly.NewOutline()
 for x,y in list(geom.exterior.coords)[:-1]:poly.Append(round(x*1e6),round(y*1e6))
 zone_changes.append(dict(uuid=z.m_Uuid.AsString(),net=z.GetNetname(),layer=b.GetLayerName(z.GetLayer()),boundary_removed_area_mm2=initial.difference(geom).area))
# Boolean-clip the inherited actual fill as well as its boundary. A global
# refill perturbs remote oblique edges by a grid unit; exact clipping keeps
# every copper point outside the three corner regions unchanged.
from shapely.ops import unary_union
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for layer in b.GetEnabledLayers().CuStack():
  if not z.IsOnLayer(layer):continue
  source=z.GetFilledPolysList(layer)
  def ring(q):return [(p.ToMM(q.CPoint(i).x),p.ToMM(q.CPoint(i).y)) for i in range(q.PointCount())]
  dest=p.SHAPE_POLY_SET()
  for oi in range(source.OutlineCount()):
   assert source.HoleCount(oi)==0, 'Native fill is already fractured'
   points=ring(source.Outline(oi))
   # Half-plane polygon clipping preserves the inherited hole bridges and
   # all remote vertices exactly; do not union/re-fracture the original ring.
   for nx,ny,offset in clip_equations:
    result=[]
    for a,c in zip(points,points[1:]+points[:1]):
     da=nx*a[0]+ny*a[1]-offset;dc=nx*c[0]+ny*c[1]-offset
     if da>=0:result.append(a)
     if (da>=0)!=(dc>=0):
      fraction=da/(da-dc);result.append((a[0]+fraction*(c[0]-a[0]),a[1]+fraction*(c[1]-a[1])))
    points=result
   index=dest.NewOutline()
   for x,y in points:dest.Append(round(x*1e6),round(y*1e6),index)
  z.SetFilledPolysList(layer,dest)
 z.SetNeedRefill(False)
b.BuildConnectivity();p.SaveBoard(str(W/'main.kicad_pcb'),b)
save(E/'geometry-plan.json',dict(source_board_sha256=digest(V/'inspection/final/main.kicad_pcb'),board_sha256=digest(W/'main.kicad_pcb'),vertices=rows,rev5_polygon_mm=vertices,rev6_polygon_mm=new,rev5_area_mm2=old.area,rev6_area_mm2=outline.area,material_removed_mm2=old.area-outline.area,outside_rev5_area_mm2=outline.difference(old).area,zone_changes=zone_changes,reason='4mm equal legs make 4mm faces / 3.464mm tip removal. Preserves full diameter5mm mounting support with >=0.946mm perimeter margin; 5mm legs would leave only about0.12mm. Copper setback0.55mm provides50um margin above required0.5mm. No footprint or route moves.'))
shutil.copyfile(V/'inspection/final/main.kicad_pro',W/'main.kicad_pro')
print('Built Rev6',digest(W/'main.kicad_pcb'))
