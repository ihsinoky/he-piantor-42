"""Read actual filled-zone outlines for independent Gerber polygon comparison."""
from common import *
import pcbnew as p
b=p.LoadBoard(str(E/'inspection/final/main.kicad_pcb'));rows=[]
def ring(line):return [[p.ToMM(line.CPoint(i).x),-p.ToMM(line.CPoint(i).y)] for i in range(line.PointCount())]
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for layer in b.GetEnabledLayers().CuStack():
  if not z.IsOnLayer(layer):continue
  poly=z.GetFilledPolysList(layer)
  for i in range(poly.OutlineCount()):rows.append(dict(layer=b.GetLayerName(layer),outer=ring(poly.Outline(i)),holes=[ring(poly.Hole(i,j)) for j in range(poly.HoleCount(i))]))
paste=[]
for d in b.GetDrawings():
 if d.GetLayer() not in [p.F_Paste,p.B_Paste]:continue
 kind={p.S_RECT:'rect',p.S_CIRCLE:'circle',p.S_SEGMENT:'line'}[d.GetShape()]
 paste.append(dict(layer=b.GetLayerName(d.GetLayer()),kind=kind,start=[p.ToMM(d.GetStart().x),-p.ToMM(d.GetStart().y)],end=[p.ToMM(d.GetEnd().x),-p.ToMM(d.GetEnd().y)],width=p.ToMM(d.GetWidth()),filled=d.IsFilled()))
save(E/'cam-native-zones.json',dict(board_sha256=digest(E/'inspection/final/main.kicad_pcb'),zones=rows,paste=paste))
