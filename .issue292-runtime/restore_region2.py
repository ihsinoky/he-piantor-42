"""Restore adopted items of NET whose endpoints all have x >= XMIN and centre x <= XMAX,
not already present. Usage: kpy.sh restore_region2.py NET XMIN XMAX"""
import pcbnew as p, sys
DST = '.issue292-runtime/wmain-work.kicad_pcb'
SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
NET, XMIN, XMAX = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
def mm(v): return v / 1e6
def key_track(t):
    s, e = t.GetStart(), t.GetEnd()
    return ('T', t.GetNetname(), t.GetLayer(), round(mm(s.x), 3), round(mm(s.y), 3),
            round(mm(e.x), 3), round(mm(e.y), 3), round(mm(t.GetWidth()), 3))
def key_via(t):
    v = t.GetPosition()
    return ('V', t.GetNetname(), round(mm(v.x), 3), round(mm(v.y), 3))
work = p.LoadBoard(DST)
have = {key_via(t) if isinstance(t, p.PCB_VIA) else key_track(t) for t in work.GetTracks()}
src = p.LoadBoard(SRC)
added = 0
for t in list(src.GetTracks()):
    if t.GetNetname() != NET: continue
    k = key_via(t) if isinstance(t, p.PCB_VIA) else key_track(t)
    if k in have: continue
    if isinstance(t, p.PCB_VIA):
        xs = [mm(t.GetPosition().x)]
    else:
        s, e = t.GetStart(), t.GetEnd()
        xs = [mm(s.x), mm(e.x)]
    if min(xs) < XMIN or sum(xs) / len(xs) > XMAX: continue
    src.Remove(t); work.Add(t); added += 1
p.SaveBoard(DST, work)
print(f'{NET}: restored {added} adopted items (endpoints x>={XMIN}, centre x<={XMAX})')
