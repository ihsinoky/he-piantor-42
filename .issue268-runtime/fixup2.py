"""Issue #268 stage 3e fixup2:
- shorten GND bus extension end 98.90 -> 98.78 (0.12 clearance to MUX_OUT_A jog),
- delete vestigial MUX_A2 via + diagonal (failed route tail),
- terminate the A2 branch on the nearby main-comp micro-segment chain."""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)

def segkey(t):
    s, e = t.GetStart(), t.GetEnd()
    return (t.GetNetname(), t.GetLayerName(), round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2))

for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA):
        s = t.GetStart()
        if t.GetNetname() == 'MUX_A2' and abs(mm(s.x) - 103.60) < 0.01 and abs(mm(s.y) - 128.40) < 0.01:
            b.RemoveNative(t); print('deleted A2 via (103.60,128.40)')
        continue
    k = segkey(t)
    if k == ('GND', 'B.Cu', 98.55, 130.20, 98.90, 130.20):
        t.SetEnd(p.VECTOR2I(p.FromMM(98.78), p.FromMM(130.20))); print('GND bus end -> 98.78')
    if k == ('MUX_A2', 'B.Cu', 100.50, 125.30, 103.60, 128.40):
        b.RemoveNative(t); print('deleted A2 diagonal')

t = p.PCB_TRACK(b)
t.SetStart(p.VECTOR2I(p.FromMM(100.50), p.FromMM(125.30)))
t.SetEnd(p.VECTOR2I(p.FromMM(100.79), p.FromMM(125.66)))
t.SetWidth(p.FromMM(0.10)); t.SetLayer(p.B_Cu); t.SetNet(b.GetNetInfo().GetNetItem('MUX_A2'))
b.Add(t); print('added A2 termination segment')
b.Save(SRC); print('saved')
