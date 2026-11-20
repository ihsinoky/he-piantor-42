"""Translate all track endpoints / via centres of NET inside a bbox by (dx,dy).
Usage: kpy.sh shift_run.py NET X0 Y0 X1 Y1 DX DY"""
import pcbnew as p, sys

DST = '.issue292-runtime/wmain-work.kicad_pcb'
NET = sys.argv[1]
X0, Y0, X1, Y1, DX, DY = [float(v) for v in sys.argv[2:8]]
def mm(v): return v / 1e6
def iu(v): return int(round(v * 1e6))

b = p.LoadBoard(DST)
netobj = b.FindNet(NET)
moved = 0
for t in b.GetTracks():
    if t.GetNetname() != NET: continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition()
        if X0 <= mm(v.x) <= X1 and Y0 <= mm(v.y) <= Y1:
            t.SetPosition(p.VECTOR2I(v.x + iu(DX), v.y + iu(DY))); moved += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        ch = False
        if X0 <= mm(s.x) <= X1 and Y0 <= mm(s.y) <= Y1:
            s = p.VECTOR2I(s.x + iu(DX), s.y + iu(DY)); ch = True
        if X0 <= mm(e.x) <= X1 and Y0 <= mm(e.y) <= Y1:
            e = p.VECTOR2I(e.x + iu(DX), e.y + iu(DY)); ch = True
        if ch: t.SetStart(s); t.SetEnd(e); moved += 1
p.SaveBoard(DST, b)
print(f'{NET}: shifted {moved} items by ({DX},{DY})')
