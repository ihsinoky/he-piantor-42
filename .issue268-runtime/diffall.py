import pcbnew as p
mm = lambda v: v/1e6
def segs(path, net):
    b = p.LoadBoard(path)
    out = {}
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        s, e = t.GetStart(), t.GetEnd()
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else t.GetLayerName()
        key = (kind, round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2))
        out[key] = out.get(key, 0) + 1
    return out
import sys
net = sys.argv[1]
a = segs('.issue268-runtime/stage1/board2.kicad_pcb', net)
c = segs('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb', net)
lost = {k: v - c.get(k, 0) for k, v in a.items() if v - c.get(k, 0) > 0}
print(net, 'segments lost vs stage1:', lost)
