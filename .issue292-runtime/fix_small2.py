"""S3b round 2: additional nudges on the work board (current positions)."""
import pcbnew as p
DST = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(DST)
def mm(v): return v / 1e6
def iu(v): return int(round(v * 1e6))
FP_MOVES = {'CVS': (0.40, 0.45), 'CIN2': (0.22, 0.22), 'JPAD': (-0.35, 0.0),
            'RPD1': (-0.30, 0.0), 'CFC': (-0.10, 0.10)}
VIA_MOVES = {(85.128, 99.059): (0.32, 0.29)}
pad_pts = []
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref in FP_MOVES:
        dx, dy = FP_MOVES[ref]
        for pad in f.Pads():
            q = pad.GetPosition(); pad_pts.append((mm(q.x), mm(q.y), dx, dy))
        pos = f.GetPosition()
        f.SetPosition(p.VECTOR2I(iu(mm(pos.x) + dx), iu(mm(pos.y) + dy)))
        print('moved fp', ref, FP_MOVES[ref])
moves = [(x, y, x + dx, y + dy) for x, y, dx, dy in pad_pts]
moves += [(x, y, x + dx, y + dy) for (x, y), (dx, dy) in VIA_MOVES.items()]
def near(x, y, x0, y0, tol=0.02): return abs(x - x0) < tol and abs(y - y0) < tol
n = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); x, y = mm(q.x), mm(q.y)
        for (x0, y0), (dx, dy) in VIA_MOVES.items():
            if near(x, y, x0, y0):
                t.SetPosition(p.VECTOR2I(iu(x + dx), iu(y + dy))); n += 1
        continue
    for which in ('start', 'end'):
        q = t.GetStart() if which == 'start' else t.GetEnd()
        x, y = mm(q.x), mm(q.y)
        for x0, y0, nx, ny in moves:
            if near(x, y, x0, y0):
                (t.SetStart if which == 'start' else t.SetEnd)(p.VECTOR2I(iu(nx), iu(ny)))
                n += 1; break
print('endpoints adjusted:', n)
p.SaveBoard(DST, b)
print('saved')
