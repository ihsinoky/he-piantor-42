"""Second independent source seed: larger derated output caps; alternate rail seed.
Prepared from seed-a INPUT, never from its routed result. Existing 53 refs fixed.
"""
from common import *
import pcbnew as p,shutil
w=E/'inputs/seed-b';assert not (E/'runs/seed-b').exists();w.mkdir(parents=True,exist_ok=True)
b=p.LoadBoard(str(E/'inputs/seed-a/main.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()};V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
positions={'C26':(91.8,77.5),'C27':(93.5,81),'C28':(98,81)}
for ref,(x,y) in positions.items():
 f=fps[ref];f.SetPosition(V(x,y));f.SetValue('22uF 16V X7R 1210');f.GetFieldByName('MPN').SetText('C3225X7R1C226K250AC')
 for a in f.Pads():
  a.SetSize(V(1.15,2.9));a.SetPosition(V(x+(-1.4 if a.GetNumber()=='1' else 1.4),y))
# A different source rail seed improves escape while keeping all power/QSPI nets.
# Endpoints remain the same; shorten the narrow U6 escape and use .4mm.
changed=[]
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 if t.GetNetname()=='V5V2' and t.GetLayer()==p.F_Cu and abs(p.ToMM(t.GetWidth())-.25)<1e-8:
  t.SetWidth(p.FromMM(.4));changed.append(t.m_Uuid.AsString())
assert len(changed)==1
# Add all missing new-component paste apertures on the source, before routing.
clones={'J3':'J2','R16':'R6','R17':'R6','R18':'R6','R19':'R6','C23':'C14','C24':'C14','C25':'C15'}
original_drawings=list(b.GetDrawings());new=[]
for ref,orig in clones.items():
 delta=fps[ref].GetPosition()-fps[orig].GetPosition();selected=[]
 for g in original_drawings:
  if g.GetLayer()==p.F_Paste and any(a.GetEffectiveShape(p.F_Cu).Collide(g.GetEffectiveShape(p.F_Paste)) for a in fps[orig].Pads()):selected.append(g)
 assert len(selected)==len(list(fps[orig].Pads()))
 for g in selected:d=g.Duplicate();d.Move(delta);b.Add(d);new.append(d.m_Uuid.AsString())
for ref in positions:
 for a in fps[ref].Pads():
  d=p.PCB_SHAPE(b);d.SetShape(p.S_RECT);d.SetLayer(p.F_Paste);d.SetWidth(0);d.SetFilled(True);pos=a.GetPosition();size=a.GetSize();d.SetStart(pos-V(.575,1.45));d.SetEnd(pos+V(.575,1.45));b.Add(d);new.append(d.m_Uuid.AsString())
assert len(new)==36
lib=E/'Stage169B.pretty';lib.mkdir(exist_ok=True);io=p.PCB_IO_KICAD_SEXPR()
for f in b.GetFootprints():
 f.SetFPID(p.LIB_ID('Stage169B',f.GetReference()));io.FootprintSave(str(lib),f)
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
shutil.copyfile(E/'inputs/seed-a/main.kicad_pro',w/'main.kicad_pro')
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Stage169B")(type "KiCad")(uri "${KIPRJMOD}/../../Stage169B.pretty")(options "")(descr "Frozen seed-b source footprints")))\n')
save(E/'seed-b-preparation.json',dict(utc=now(),source='inputs/seed-a/main.kicad_pcb',source_sha256=digest(E/'inputs/seed-a/main.kicad_pcb'),source_is_routing_input_not_output=True,output_cap_MPN='C3225X7R1C226K250AC',new_cap_pad_size_mm=[1.15,2.9],new_cap_pad_centers_mm=2.8,new_positions=positions,original_53_positions_unchanged=True,changed_source_seed_tracks=changed,new_paste_openings=len(new),whole_board_attempt_limit=2,local_ripup=False))
print('Seed-b prepared, output X7R1210 and alternate power escape seed')
