import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in list(b.GetTracks()):
    if t.GetNetname() != 'HALL_3V3' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    cx, cy = (mm(s.x) + mm(e.x)) / 2, (mm(s.y) + mm(e.y)) / 2
    if 128.35 < cx < 128.70 and 128.85 < cy < 129.40:
        b.Remove(t); n += 1
print('cut', n)
p.SaveBoard(WP, b)
