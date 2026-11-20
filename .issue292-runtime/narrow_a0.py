import pcbnew as p
WP = '.issue292-runtime/wmain-work.kicad_pcb'
b = p.LoadBoard(WP)
def mm(v): return v / 1e6
n = 0
for t in b.GetTracks():
    if t.GetNetname() != 'MUX_A0' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    pts = {(round(mm(s.x), 2), round(mm(s.y), 2)), (round(mm(e.x), 2), round(mm(e.y), 2))}
    if pts == {(72.10, 123.41), (72.05, 125.55)}:
        t.SetWidth(int(0.05 * 1e6)); n += 1
print('narrowed', n)
p.SaveBoard(WP, b)
