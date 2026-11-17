import pcbnew as p
from collections import Counter
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for net in ['HALL_5V','GND','MUX_A0','MUX_A2','WING_EN','MUX_OUT_C']:
    c = Counter()
    for t in b.GetTracks():
        if t.GetNetname() != net or isinstance(t, p.PCB_VIA): continue
        s = t.GetStart()
        if 90 <= mm(s.x) <= 126 and 116 <= mm(s.y) <= 134: c[round(mm(t.GetWidth()),2)] += 1
    print(net, dict(c))
