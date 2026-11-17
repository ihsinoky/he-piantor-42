"""17R via repair on routed.kicad_pcb: move the HALL_5V via that sits on
U_HC4.1 south along its own B.Cu track to (116.9, 97.62) (pad-edge gap
0.14), and add an F.Cu segment joining the old tap stub end (116.9, 97.0)
to the moved via. The B.Cu track still starts inside pad 1, so the pad
keeps its direct B connection."""
import pcbnew as p
from pathlib import Path
w = Path('/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-right')
b = p.LoadBoard(str(w / 'routed.kicad_pcb'))
V = lambda x, y: p.VECTOR2I(p.FromMM(x), p.FromMM(y))
moved = 0
for t in b.GetTracks():
    if t.Type() == p.PCB_VIA_T and t.m_Uuid.AsString().startswith('e8e3234d'):
        t.SetPosition(V(116.9, 97.62)); moved += 1
print('vias moved:', moved)
net = None
for t in b.GetTracks():
    if t.GetNetname() == 'HALL_5V':
        net = t.GetNetCode(); break
seg = p.PCB_TRACK(b)
seg.SetStart(V(116.9, 97.0)); seg.SetEnd(V(116.9, 97.62))
seg.SetWidth(p.FromMM(0.6)); seg.SetLayer(p.F_Cu); seg.SetNetCode(net)
b.Add(seg)
p.SaveBoard(str(w / 'routed.kicad_pcb'), b)
print('segment added, net code', net)
print('done')
