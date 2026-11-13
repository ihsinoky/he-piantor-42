"""Replace the two headers; outward mating reverses the physical signal row."""
from common import *
import pcbnew as p,shutil,math
src=E.parent/'issue-226-main-rev6/inspection/final/main.kicad_pcb'
b=p.LoadBoard(str(src));changes=[]
for old in list(b.GetFootprints()):
 if old.GetReference() not in ['J2','J3']:continue
 ref=old.GetReference();angle=old.GetOrientationDegrees();pos=old.GetPosition()
 f=p.FootprintLoad(str(E/'connector'),'JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal');b.Add(f)
 f.SetReference(ref);f.SetValue('SM14B-GHS-TB(LF)(SN)');f.SetOrientationDegrees(angle)
 # Origin shift aligns the row geometrically; numbered signals need local rerouting.
 theta=math.radians(angle);f.SetPosition(p.VECTOR2I(pos.x+p.FromMM(1.85*math.sin(theta)),pos.y+p.FromMM(1.85*math.cos(theta))))
 oldpads={a.GetNumber():a for a in old.Pads() if a.GetNumber()!='15'}
 for a in f.Pads():
  if a.GetNumber()=='MP':a.SetNumber('15')
  else:
   o=oldpads[a.GetNumber()];a.SetNet(o.GetNet())
 f.SetPath(old.GetPath());changes.append(dict(ref=ref,angle_deg=angle,origin_mm=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)],exit_unit_xy=[math.sin(theta),math.cos(theta)],signal_row_reversed=True))
 b.Remove(old)
p.SaveBoard(str(E/'inspection/final/main.kicad_pcb'),b)
# Component identity only; logical pin netlist unchanged.
s=E/'schematic/main.kicad_sch';s.write_text(s.read_text().replace('BM14B-GHS-TBT(LF)(SN)','SM14B-GHS-TB(LF)(SN)'))
save(E/'replacement.json',dict(source_sha256=digest(src),board_sha256=digest(E/'inspection/final/main.kicad_pcb'),changes=changes,route_changes=0,phase="before-local-routing",reason="Same signal pitch/row geometry, but physical pad order reverses for outward mating. D-024 net numbers are retained and rerouted. Reinforcement lands are mechanical NC."))
