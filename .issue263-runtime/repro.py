from pathlib import Path
import pcbnew as p, json
E=Path('hardware/kicad/qualification/issue-263-implementation').resolve(); BASE=E.parent/'issue-235-wing-round2'
src=BASE/'wing-rev4-16mm-left'
b=p.LoadBoard(str(src/'routed.kicad_pcb'))
old=[f for f in b.GetFootprints() if f.GetReference()=='J_WING'][0]
nets={a.GetNumber():a.GetNetCode() for a in old.Pads() if a.GetNumber()!='MP'}
pos=old.GetPosition(); cx,cy=p.ToMM(pos.x),p.ToMM(pos.y)
removed=0
for t in list(b.GetTracks()):
 if t.GetNetCode() not in nets.values(): continue
 s,e=t.GetStart(),t.GetEnd()
 if max(abs(p.ToMM(s.x)-cx),abs(p.ToMM(s.y)-cy),abs(p.ToMM(e.x)-cx),abs(p.ToMM(e.y)-cy))<18.0:
  b.Remove(t); removed+=1
print('removed',removed)
b.Remove(old)
f=p.FootprintLoad(str(E/'connector'),'Hirose_FH12-14S-0.5SH_1x14-1MP_P0.50mm_Horizontal')
print('loaded',bool(f))
