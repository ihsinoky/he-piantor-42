"""Restore GND tracks/vias present in the tree board but missing from the work board (exact geometry key match)."""
import pcbnew as p
DST = '.issue292-runtime/wmain-work.kicad_pcb'
SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
def mm(v): return v / 1e6
def key(t):
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); return ('V', round(mm(v.x), 3), round(mm(v.y), 3))
    s, e = t.GetStart(), t.GetEnd()
    return ('T', t.GetLayer(), round(mm(s.x), 3), round(mm(s.y), 3), round(mm(e.x), 3), round(mm(e.y), 3), round(mm(t.GetWidth()), 3))
work = p.LoadBoard(DST)
wk = {key(t) for t in work.GetTracks() if t.GetNetname() == 'GND'}
src = p.LoadBoard(SRC)
n = 0
for t in list(src.GetTracks()):
    if t.GetNetname() != 'GND': continue
    if key(t) in wk: continue
    src.Remove(t); work.Add(t); n += 1
p.SaveBoard(DST, work)
print('restored GND items:', n)
