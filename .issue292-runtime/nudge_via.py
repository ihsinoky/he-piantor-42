"""Move the PAD_EN via (84.35,119.05) -> (84.30,119.10) and retarget
the two track endpoints that terminate at the old centre."""
import pcbnew as p
from pathlib import Path
E = Path('.').resolve()
path = str(E.parent/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
b = p.LoadBoard(path)
def mm(v): return p.ToMM(v)
OLD = (84.35, 119.05); NEW = (84.30, 119.10)
moved_via = None
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'PAD_EN':
        pos = t.GetPosition()
        if abs(mm(pos.x) - OLD[0]) < 0.01 and abs(mm(pos.y) - OLD[1]) < 0.01:
            t.SetPosition(p.VECTOR2I(p.FromMM(NEW[0]), p.FromMM(NEW[1])))
            moved_via = t
assert moved_via is not None
n = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or t.GetNetname() != 'PAD_EN': continue
    s, e = t.GetStart(), t.GetEnd()
    if abs(mm(s.x) - OLD[0]) < 0.01 and abs(mm(s.y) - OLD[1]) < 0.01:
        t.SetStart(p.VECTOR2I(p.FromMM(NEW[0]), p.FromMM(NEW[1]))); n += 1
    if abs(mm(e.x) - OLD[0]) < 0.01 and abs(mm(e.y) - OLD[1]) < 0.01:
        t.SetEnd(p.VECTOR2I(p.FromMM(NEW[0]), p.FromMM(NEW[1]))); n += 1
print('endpoints retargeted:', n)
assert n == 2
b.Save(path)
print('saved')
