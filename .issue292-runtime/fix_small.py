"""S3b: pull-in edits for clusters N/T/E/S on a work copy.
Footprint moves + attached track-endpoint translation + via moves +
two free-track vertex moves. Verify afterwards with enumerate_edge.py."""
import pcbnew as p, shutil
SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
DST = '.issue292-runtime/wmain-work.kicad_pcb'
shutil.copy(SRC, DST)
b = p.LoadBoard(DST)
def mm(v): return v / 1e6
def iu(v): return int(round(v * 1e6))

FP_MOVES = {  # ref: (dx, dy) mm, +x east, +y south (KiCad)
    'CIN1': (0.40, 0.30), 'CIN2': (0.35, 0.35), 'CVS': (0.35, 0.30),
    'RRST': (0.30, 0.0), 'RPD1': (-0.70, 0.0), 'RPD3': (0.0, -0.15),
    'CFC': (-0.20, 0.30), 'JPAD': (-0.80, 0.0), 'TP1': (0.45, 0.10),
}
VIA_MOVES = {  # (x, y): (dx, dy)
    (93.28, 84.796): (0.35, 0.30),      # follows CVS
    (115.75, 100.475): (-0.45, 0.0),
    (132.071, 128.918): (-0.67, 0.28),
    (128.675, 122.998): (-0.38, 0.40),
}
PT_MOVES = {  # free track endpoints/vertices (x, y): (nx, ny)
    (117.4, 103.5): (117.4, 103.78), (119.3, 103.5): (119.3, 103.78),
    (94.5, 84.2): (94.78, 84.2), (94.5, 82.5): (94.78, 82.5),
    (94.9, 82.1): (95.6, 82.1),
}
# collect pad centers of moved footprints BEFORE moving
pad_pts = []  # (x, y, dx, dy)
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref in FP_MOVES:
        dx, dy = FP_MOVES[ref]
        for pad in f.Pads():
            q = pad.GetPosition()
            pad_pts.append((mm(q.x), mm(q.y), dx, dy))
        pos = f.GetPosition()
        f.SetPosition(p.VECTOR2I(iu(mm(pos.x) + dx), iu(mm(pos.y) + dy)))
        print('moved fp', ref, FP_MOVES[ref])

def near(pt, x, y, tol=0.02): return abs(pt[0] - x) < tol and abs(pt[1] - y) < tol

moves = [(x, y, x + dx, y + dy) for x, y, dx, dy in pad_pts]
moves += [(x, y, x + dx, y + dy) for (x, y), (dx, dy) in VIA_MOVES.items()]
moves += [(x, y, nx, ny) for (x, y), (nx, ny) in PT_MOVES.items()]

n_trk = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); x, y = mm(q.x), mm(q.y)
        for (x0, y0), (dx, dy) in VIA_MOVES.items():
            if near((x, y), x0, y0):
                t.SetPosition(p.VECTOR2I(iu(x + dx), iu(y + dy))); n_trk += 1
        continue
    for which in ('start', 'end'):
        q = t.GetStart() if which == 'start' else t.GetEnd()
        x, y = mm(q.x), mm(q.y)
        for x0, y0, nx, ny in moves:
            if near((x, y), x0, y0):
                v = p.VECTOR2I(iu(nx), iu(ny))
                (t.SetStart if which == 'start' else t.SetEnd)(v)
                n_trk += 1
                break
print('track/via endpoints adjusted:', n_trk)
p.SaveBoard(DST, b)
print('saved', DST)
