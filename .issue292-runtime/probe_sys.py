import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v/1e6
targets = {'CVCC1': (75.7,118.3), 'CVCC2': (71.8,119.4), 'U1.26': (78.8,123.55)}
for t in b.GetTracks():
    if t.GetNetname() != 'SYS_3V3': continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    for name, (tx, ty) in targets.items():
        if any(abs(x-tx) < 3 and abs(y-ty) < 3 for x, y in pts):
            kind = 'VIA' if isinstance(t, p.PCB_VIA) else {0:'F',31:'I2',2:'B'}.get(t.GetLayer(), t.GetLayer())
            print(f'{name}: {kind} w={mm(t.GetWidth()):.2f} {pts}')
