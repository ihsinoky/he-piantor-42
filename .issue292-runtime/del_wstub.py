import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in list(b.GetTracks()):
    if t.GetNetname() != 'GND' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    if all(106.9 < mm(q.x) < 108.0 and 96.4 < mm(q.y) < 97.3 for q in (s, e)):
        b.Remove(t); n += 1
print('deleted', n)
p.SaveBoard(WP, b)
