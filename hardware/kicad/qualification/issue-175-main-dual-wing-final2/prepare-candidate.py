"""Generate one pre-route candidate, retaining all existing components and copper."""
from common import *
import pcbnew as p,shutil,collections,sexpdata as sx
label=sys.argv[1];x,y=map(float,sys.argv[2:4]);assert label in ['candidate-1','candidate-2','candidate-3']
w=E/'inputs'/label;w.mkdir(parents=True,exist_ok=True);assert not (w/"main.kicad_pcb").exists()
old=R/'hardware/kicad/qualification/issue-173-main-dual-wing-final/inputs/final';src=old/'main.kicad_pcb';b=p.LoadBoard(str(src));fps={f.GetReference():f for f in b.GetFootprints()};f=fps['C26']
pose=lambda f:[p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y),f.GetOrientationDegrees()]
before={r:pose(q) for r,q in fps.items()}
ids=json.loads((old.parent.parent/'preparation.json').read_text())['moved_paste_apertures']
selected=[g for g in b.GetDrawings() if g.m_Uuid.AsString() in ids];assert len(selected)==2
delta=p.VECTOR2I(p.FromMM(x),p.FromMM(y))-f.GetPosition();f.Move(delta)
for g in selected:g.Move(delta)
assert all(pose(q)==before[r] for r,q in fps.items() if r!='C26')
lib=E/'Stage175.pretty';lib.mkdir(exist_ok=True);io=p.PCB_IO_KICAD_SEXPR()
for q in b.GetFootprints():q.SetFPID(p.LIB_ID('Stage175',q.GetReference()));io.FootprintSave(str(lib),q)
assert p.SaveBoard(str(w/'main.kicad_pcb'),b)
shutil.copyfile(old/'main.kicad_pro',w/'main.kicad_pro')
(w/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "Stage175")(type "KiCad")(uri "${KIPRJMOD}/../../Stage175.pretty")(options "")(descr "Frozen Issue175 footprints")))\n')
def copper(path):return collections.Counter(sx.dumps(a) for a in sx.loads(path.read_text()) if isinstance(a,list) and a and str(a[0]) in ['segment','via'])
assert copper(src)==copper(w/'main.kicad_pcb')
save(w/'preparation.json',dict(utc=now(),source=str(src.relative_to(R)),source_sha256=digest(src),board_sha256=digest(w/'main.kicad_pcb'),C26_before=before['C26'],C26_after=pose(f),other_65_positions_and_angles_unchanged=True,seed_copper_canonical_identical=True,paste_apertures_moved=[g.m_Uuid.AsString() for g in selected]))
