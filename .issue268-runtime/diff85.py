import pcbnew as p
mm = lambda v: v/1e6
def segs(path):
    b = p.LoadBoard(path)
    out = set()
    for t in b.GetTracks():
        if t.GetNetname() != 'GND': continue
        bb = t.GetBoundingBox()
        if mm(bb.GetRight()) < 82 or mm(bb.GetLeft()) > 95 or mm(bb.GetBottom()) < 123 or mm(bb.GetTop()) > 131: continue
        s, e = t.GetStart(), t.GetEnd()
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else t.GetLayerName()
        out.add((kind, round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2)))
    return out
a = segs('.issue268-runtime/stage1/board.kicad_pcb')
c = segs('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
print('only in stage1:')
for s in sorted(a - c): print(' ', s)
print('only in current:')
for s in sorted(c - a): print(' ', s)
