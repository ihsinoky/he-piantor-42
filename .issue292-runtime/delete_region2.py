"""Delete WORK-board items of NET whose endpoints all have x >= XMIN and centre x <= XMAX
(mirror of restore_region2's filter). Usage: kpy.sh delete_region2.py NET XMIN XMAX"""
import pcbnew as p, sys
DST = '.issue292-runtime/wmain-work.kicad_pcb'
NET, XMIN, XMAX = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
def mm(v): return v / 1e6
work = p.LoadBoard(DST)
n = 0
for t in list(work.GetTracks()):
    if t.GetNetname() != NET: continue
    if isinstance(t, p.PCB_VIA):
        xs = [mm(t.GetPosition().x)]
    else:
        s, e = t.GetStart(), t.GetEnd()
        xs = [mm(s.x), mm(e.x)]
    if min(xs) < XMIN or sum(xs) / len(xs) > XMAX: continue
    work.Remove(t); n += 1
p.SaveBoard(DST, work)
print(f'{NET}: deleted {n} items (endpoints x>={XMIN}, centre x<={XMAX})')
