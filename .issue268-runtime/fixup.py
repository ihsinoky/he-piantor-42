"""Issue #268 stage 3c fixup:
- delete duplicate MUX_A2 micro-stubs at the island gap (router artefacts),
- delete zero-length tracks on link nets,
- bridge MUX_A2 island: (111.10,125.40)->(111.25,125.35) B.Cu 0.10,
- bridge GND west gap: (85.30,126.70)->(85.75,127.65) F.Cu 0.30."""
import math
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)
removed = 0
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    L = math.hypot(mm(e.x-s.x), mm(e.y-s.y))
    net = t.GetNetname()
    kill = False
    if net in LINK and L < 0.011: kill = True
    if net == 'MUX_A2' and L <= 0.06 and 111.05 <= mm(s.x) <= 111.20 and 125.35 <= mm(s.y) <= 125.45: kill = True
    if kill:
        b.RemoveNative(t); removed += 1
print('removed', removed, 'artefact tracks')

def add(net, x1, y1, x2, y2, layer, w):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(p.FromMM(x1), p.FromMM(y1)))
    t.SetEnd(p.VECTOR2I(p.FromMM(x2), p.FromMM(y2)))
    t.SetWidth(p.FromMM(w)); t.SetLayer(layer); t.SetNet(b.GetNetInfo().GetNetItem(net))
    b.Add(t)
    print('added', net, (x1, y1), (x2, y2))

add('MUX_A2', 111.10, 125.40, 111.25, 125.35, p.B_Cu, 0.10)
add('GND', 85.30, 126.70, 85.75, 127.65, p.F_Cu, 0.30)
b.Save(SRC)
print('saved')
