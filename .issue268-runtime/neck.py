"""Issue #268 stage 3a: GND necks. Five J_WING GND stubs (pads 2,4,10,12,14)
are trapped south of the signal-escape via wall (vias at y=130.75, 0.5mm from
each GND lane): a 0.30 track cannot pass (needs 0.55, has 0.50). A 0.15 neck
passes with 0.125mm clearance. Draw 0.15 B.Cu necks in-lane y 131.00 -> 129.90,
then the 0.30 A* bridge takes over north of the wall."""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
b = p.LoadBoard(SRC)
netcode = b.GetNetInfo().GetNetItem('GND')
for x in (96.75, 97.75, 98.75, 101.75, 102.75):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(p.FromMM(x), p.FromMM(131.00)))
    t.SetEnd(p.VECTOR2I(p.FromMM(x), p.FromMM(129.90)))
    t.SetWidth(p.FromMM(0.15)); t.SetLayer(p.B_Cu); t.SetNet(netcode)
    b.Add(t)
    print('neck at x=%.2f' % x)
b.Save(SRC)
print('saved')
