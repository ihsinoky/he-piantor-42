import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in list(b.GetTracks()):
    if t.GetNetname() != 'PAD_SDA': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition()
        if abs(mm(v.x) - 111.75) < 0.01 and abs(mm(v.y) - 95.75) < 0.01: b.Remove(t); n += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        pts = {(round(mm(s.x), 2), round(mm(s.y), 2)), (round(mm(e.x), 2), round(mm(e.y), 2))}
        if pts == {(111.75, 96.80), (111.75, 95.75)}: b.Remove(t); n += 1
print('removed', n)
p.SaveBoard(WP, b)
