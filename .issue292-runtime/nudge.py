"""Move one footprint by (dx, dy) and translate every track endpoint / via
centre that lies within any of its pads' bboxes expanded by 0.4mm.
Usage: kpy.sh nudge.py REF DX DY"""
import pcbnew as p, sys

DST = '.issue292-runtime/wmain-work.kicad_pcb'
REF, DX, DY = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
def mm(v): return v / 1e6
def iu(v): return int(round(v * 1e6))

b = p.LoadBoard(DST)
fp = None
for f in b.GetFootprints():
    if f.GetReference() == REF: fp = f
assert fp is not None, REF
boxes = []
for pad in fp.Pads():
    bb = pad.GetBoundingBox()
    boxes.append((mm(bb.GetLeft()) - 0.4, mm(bb.GetTop()) - 0.4,
                  mm(bb.GetRight()) + 0.4, mm(bb.GetBottom()) + 0.4))
def inside(x, y):
    return any(x0 <= x <= x1 and y0 <= y <= y1 for x0, y0, x1, y1 in boxes)
q = fp.GetPosition()
fp.SetPosition(p.VECTOR2I(q.x + iu(DX), q.y + iu(DY)))
moved = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition()
        if inside(mm(v.x), mm(v.y)):
            t.SetPosition(p.VECTOR2I(v.x + iu(DX), v.y + iu(DY))); moved += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        ns = (mm(s.x), mm(s.y)); ne = (mm(e.x), mm(e.y))
        ch = False
        if inside(*ns): s = p.VECTOR2I(s.x + iu(DX), s.y + iu(DY)); ch = True
        if inside(*ne): e = p.VECTOR2I(e.x + iu(DX), e.y + iu(DY)); ch = True
        if ch: t.SetStart(s); t.SetEnd(e); moved += 1
p.SaveBoard(DST, b)
print(f'{REF} moved by ({DX},{DY}); {moved} track/via items followed')
