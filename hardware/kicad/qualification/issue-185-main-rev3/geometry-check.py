from common import *
import pcbnew as p,math
sys.path.insert(0,str(E/'source183'))
from audit import polygons,pad_polygon,xy
from shapely.geometry import Point,LineString
from shapely.ops import unary_union
w=E/'inspection/final';b=p.LoadBoard(str(w/'main.kicad_pcb'));old=p.LoadBoard(str(E.parent/'issue-175-main-dual-wing-final2/inspection/final/main.kicad_pcb'));layers=list(b.GetEnabledLayers().CuStack())
def placements(board):return {f.m_Uuid.AsString():dict(ref=f.GetReference(),position_mm=xy(f.GetPosition()),angle=f.GetOrientationDegrees()) for f in board.GetFootprints()}
assert placements(b)==placements(old);assert b.GetCopperLayerCount()==4 and p.ToMM(b.GetDesignSettings().GetBoardThickness())==1.2
# Native filled copper and explicit tracks/vias/pads must respect inherited diameter5 mounting reservation.
copper={l:[] for l in layers}
for f in b.GetFootprints():
 for a in f.Pads():
  if a.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  for l in layers:
   if a.IsOnLayer(l):copper[l].append(pad_polygon(a,l))
for t in b.GetTracks():
 for l in layers:
  if not t.IsOnLayer(l):continue
  g=Point(xy(t.GetPosition())).buffer(p.ToMM(t.GetWidth())/2,quad_segs=128) if isinstance(t,p.PCB_VIA) else LineString([xy(t.GetStart()),xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth())/2,quad_segs=32)
  copper[l].append(g)
for z in b.Zones():
 if z.GetIsRuleArea():continue
 for l in layers:
  if z.IsOnLayer(l):copper[l].append(polygons(z.GetFilledPolysList(l)))
copper={l:unary_union(gs) for l,gs in copper.items()};holes=[]
for f in b.GetFootprints():
 if not f.GetReference().startswith('H'):continue
 center=xy(f.GetPosition());a=list(f.Pads())[0];assert a.GetAttribute()==p.PAD_ATTRIB_NPTH and xy(a.GetDrillSize())==[2.2,2.2]
 clear=min(Point(center).distance(g) for g in copper.values());assert clear>=2.5-2e-6
 holes.append(dict(ref=f.GetReference(),position_mm=center,drill_mm=2.2,min_center_to_copper_mm=clear))
assert len(holes)==4
save(E/'geometry-check.json',dict(board_sha256=digest(w/'main.kicad_pcb'),all_66_footprint_placements_identical=True,footprints=len(placements(b)),copper_layers=[b.GetLayerName(l) for l in layers],thickness_mm=1.2,holes=holes,reservation_diameter_mm=5,pass_check=True))
print('Fixed placements, four layers/1.2mm, all four diameter5 reservations PASS')
