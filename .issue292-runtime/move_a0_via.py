import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in list(b.GetTracks()):
    if t.GetNetname() != 'MUX_A0': continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        if abs(mm(q.x) - 71.95) < 0.02 and abs(mm(q.y) - 125.65) < 0.02: b.Remove(t); n += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        pts = {(round(mm(s.x), 2), round(mm(s.y), 2)), (round(mm(e.x), 2), round(mm(e.y), 2))}
        if pts == {(72.11, 123.41), (72.06, 125.55)}: b.Remove(t); n += 1
print('removed', n)
p.SaveBoard(WP, b)
