import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in list(b.GetTracks()):
    if t.GetNetname() != 'PAD_SCL' or isinstance(t, p.PCB_VIA) or t.GetLayer() != 6: continue
    s, e = t.GetStart(), t.GetEnd()
    a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
    if min(a[1], bb[1]) > 126.9 and 72.0 < min(a[0], bb[0]) and max(a[0], bb[0]) < 96.0:
        b.Remove(t); n += 1
print('cut', n)
p.SaveBoard(WP, b)
