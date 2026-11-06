"""Source-declared paste-only correction, applied identically to input and output.
No copper modification, no autorouter call, no rip-up. Frozen seed-a untouched.
"""
from common import *
import pcbnew as p,shutil
assert json.loads((E/'inspection/seed-a/assessment.json').read_text())['pass_acceptance']
source=p.LoadBoard(str(E/'inputs/seed-a/main.kicad_pcb'));fps={f.GetReference():f for f in source.GetFootprints()}
clones={'J3':'J2','R16':'R6','R17':'R6','R18':'R6','R19':'R6','C23':'C14','C24':'C14','C25':'C15','C26':'C14','C27':'C14','C28':'C14'}
changes=[];graphics=[]
for ref,original in clones.items():
 f=fps[original];target=fps[ref];delta=target.GetPosition()-f.GetPosition();selected=[]
 for g in source.GetDrawings():
  if g.GetLayer()!=p.F_Paste:continue
  shape=g.GetEffectiveShape(p.F_Paste)
  if any(a.GetEffectiveShape(p.F_Cu).Collide(shape) for a in f.Pads()):selected.append(g)
 assert len(selected)==len(list(f.Pads())),(ref,len(selected))
 for g in selected:
  new=g.Duplicate();new.Move(delta);graphics.append(new)
 changes.append(dict(ref=ref,template_ref=original,paste_openings=len(selected),delta_mm=[p.ToMM(delta.x),p.ToMM(delta.y)]))
import sexpdata as sx
inputdir=E/'inputs/final';outputdir=E/'runs/final'
inputdir.mkdir(parents=True,exist_ok=False);outputdir.mkdir(parents=True,exist_ok=False)
b=p.LoadBoard(str(E/'inputs/seed-a/main.kicad_pcb'))
oldids={g.m_Uuid.AsString() for g in b.GetDrawings()}
for g in graphics:b.Add(g.Duplicate())
assert p.SaveBoard(str(inputdir/'main.kicad_pcb'),b)
node=sx.loads((inputdir/'main.kicad_pcb').read_text());added=[]
for v in node:
 if not isinstance(v,list) or not v or not str(v[0]).startswith('gr_'):continue
 uid=next(str(x[1]) for x in v if isinstance(x,list) and x and str(x[0])=='uuid')
 if uid not in oldids:added.append(v)
assert len(added)==len(graphics)
out=sx.loads((E/'runs/seed-a/out.kicad_pcb').read_text());out.extend(added)
(outputdir/'out.kicad_pcb').write_text(sx.dumps(out)+'\n')
shutil.copyfile(E/'inputs/seed-a/main.kicad_pro',inputdir/'main.kicad_pro')
shutil.copyfile(E/'inputs/seed-a/main.kicad_pro',outputdir/'out.kicad_pro')
shutil.copyfile(E/'inputs/seed-a/fp-lib-table',inputdir/'fp-lib-table')
save(E/'paste-correction.json',dict(utc=now(),changes=changes,new_openings=len(graphics),copper_unchanged=True,additional_routing_attempts=0,method='Duplicate exact source board F.Paste graphics for source component; translation only, same UUIDs applied to source input and routed board.',original_qualified_board_sha256=digest(E/'inspection/seed-a/main.kicad_pcb'),final_input_sha256=digest(E/'inputs/final/main.kicad_pcb'),final_raw_sha256=digest(E/'runs/final/out.kicad_pcb')))
print('Paste correction only:',len(graphics),'openings; input/output mirrored; copper unchanged')
