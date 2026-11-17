"""Issue #268 stage 3f fixup3: restore the MUX_A2 via + diagonal (they carried
the east B.Cu chain's only link to main); remove fixup2's termination segment."""
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)
nc = b.GetNetInfo().GetNetItem('MUX_A2')
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    if (t.GetNetname() == 'MUX_A2' and abs(mm(s.x) - 100.50) < 0.01 and abs(mm(s.y) - 125.30) < 0.01
            and abs(mm(e.x) - 100.79) < 0.01 and abs(mm(e.y) - 125.66) < 0.01):
        b.RemoveNative(t); print('removed fixup2 termination segment')
v = p.PCB_VIA(b); v.SetPosition(p.VECTOR2I(p.FromMM(103.60), p.FromMM(128.40)))
v.SetWidth(p.FromMM(0.6)); v.SetDrill(p.FromMM(0.3)); v.SetNet(nc)
v.SetLayerPair(p.F_Cu, p.B_Cu); b.Add(v); print('restored A2 via')
t = p.PCB_TRACK(b)
t.SetStart(p.VECTOR2I(p.FromMM(100.50), p.FromMM(125.30)))
t.SetEnd(p.VECTOR2I(p.FromMM(103.60), p.FromMM(128.40)))
t.SetWidth(p.FromMM(0.10)); t.SetLayer(p.B_Cu); t.SetNet(nc)
b.Add(t); print('restored A2 diagonal')
b.Save(SRC); print('saved')
