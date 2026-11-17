import pcbnew as p
mm = lambda v: v/1e6
def segs(path, net, box):
    b = p.LoadBoard(path)
    out = set()
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        bb = t.GetBoundingBox()
        if mm(bb.GetRight()) < box[0] or mm(bb.GetLeft()) > box[1] or mm(bb.GetBottom()) < box[2] or mm(bb.GetTop()) > box[3]: continue
        s, e = t.GetStart(), t.GetEnd()
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else t.GetLayerName()
        out.add((kind, round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2)))
    return out
box = (99, 113.5, 119, 133)
a = segs('hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb', 'HALL_5V', box)
c = segs('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb', 'HALL_5V', box)
print('only in Rev.3:')
for s in sorted(a - c): print(' ', s)
print('only in Rev.4:')
for s in sorted(c - a): print(' ', s)
