import pcbnew as p, math
mm = lambda v: v/1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
for t in b.GetTracks():
    if t.GetNetname() != 'HALL_5V': continue
    s = t.GetStart()
    if abs(mm(s.x) - 98.1) < 1.6 and abs(mm(s.y) - 122.6) < 1.6:
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK ' + t.GetLayerName()
        e = t.GetEnd()
        print(kind, (round(mm(s.x), 3), round(mm(s.y), 3)), (round(mm(e.x), 3), round(mm(e.y), 3)))
src = open('.issue268-runtime/extract268.py').read()
exec(src.split("res = {}")[0])
adj = build('HALL_5V')
for n in sorted(adj):
    if abs(n[0] - 98.1) < 0.35 and abs(n[1] - 122.6) < 0.35:
        print('node', n, 'degree', len(adj[n]))
