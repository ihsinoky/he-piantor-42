"""Move only C26 and its two paste apertures in the un-routed seed-b input."""
from common import *
import pcbnew as p,shutil,collections
old=R/'hardware/kicad/qualification/issue-169-main-dual-wing-followup'
w=E/'inputs/final';w.mkdir(parents=True,exist_ok=False)
src=old/'inputs/seed-b/main.kicad_pcb';b=p.LoadBoard(str(src))
fps={f.GetReference():f for f in b.GetFootprints()};f=fps['C26']
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
before=[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)]
selected=[g for g in b.GetDrawings() if g.GetLayer()==p.F_Paste and any(a.GetEffectiveShape(p.F_Cu).Collide(g.GetEffectiveShape(p.F_Paste)) for a in f.Pads())]
assert len(selected)==2
delta=V(94.5,77.2)-f.GetPosition();f.Move(delta)
for g in selected:g.Move(delta)
original=json.loads((E/'circuit-intent.json').read_text())['original']
for ref,a in original.items():
 q=fps[ref];assert [p.ToMM(q.GetPosition().x),p.ToMM(q.GetPosition().y),q.GetOrientationDegrees()]==[a['x'],a['y'],a['angle']],ref
lib=E/'Stage173.pretty';lib.mkdir();io=p.PCB_IO_KICAD_SEXPR()
for q in b.GetFootprints():
 q.SetFPID(p.LIB_ID('Stage173',q.GetReference()));io.FootprintSave(str(lib),q)
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
shutil.copyfile(old/'inputs/seed-b/main.kicad_pro',w/'main.kicad_pro')
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Stage173")(type "KiCad")(uri "${KIPRJMOD}/../../Stage173.pretty")(options "")(descr "Frozen Issue173 source footprints")))\n')
save(E/'preparation.json',dict(utc=now(),source=str(src.relative_to(R)),source_sha256=digest(src),source_is_unrouted_input=True,moved_footprints={'C26':dict(before=before,after=[94.5,77.2],angle=0)},moved_paste_apertures=[g.m_Uuid.AsString() for g in selected],original_53_positions_unchanged=True,other_footprint_positions_unchanged=True,seed_tracks_and_vias_unchanged=True))
save(E/'routing-scope.json',dict(utc=now(),max_global_attempts=1,max_local_repair_attempts=0,timeout_seconds=2400,condition_args=ARGS+['--keep-input-copper'],ordering='mps (default, successful seed-a policy)',direction='default',no_condition_relaxation=True,preflight_fail_stops_without_routing=True))
print('C26 moved',before,'->',[94.5,77.2],'; original 53 fixed')
