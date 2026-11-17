import pcbnew, collections
B = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-matrix4/hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
def mm(v): return v/1e6
hits = collections.defaultdict(list)
for t in B.GetTracks():
    if not isinstance(t, pcbnew.PCB_TRACK) or isinstance(t, pcbnew.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    x0, x1 = sorted([mm(s.x), mm(e.x)]); y0, y1 = sorted([mm(s.y), mm(e.y)])
    if x1 < 96.4 or x0 > 103.6 or y1 < 123.9 or y0 > 131.4: continue
    hits[t.GetNetname()].append((round(x0,2), round(x1,2), round(y0,2), round(y1,2), 'F' if t.GetLayer()==0 else 'B'))
for net, lst in sorted(hits.items()):
    print(net, len(lst))
    for r in lst[:14]: print('   ', r)
