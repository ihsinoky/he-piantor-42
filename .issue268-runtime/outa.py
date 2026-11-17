import pcbnew, collections
B = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-matrix4/hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
def mm(v): return v/1e6
# union-find over MUX_OUT_A items via board connectivity is complex; approximate:
# group by connected components using geometry touch on same net (pads+tracks+vias)
items = []
for fp in B.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() == 'MUX_OUT_A':
            q = pad.GetPosition(); items.append(('pad', fp.GetReference(), pad.GetNumber(), mm(q.x), mm(q.y)))
for t in B.GetTracks():
    if t.GetNetname() != 'MUX_OUT_A': continue
    s, e = t.GetStart(), t.GetEnd()
    kind = 'via' if isinstance(t, pcbnew.PCB_VIA) else 'seg'
    items.append((kind, 'F' if t.GetLayer() == 0 else 'B', '', round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2)))
print(len(items), 'items')
for it in items:
    x = it[3]; y = it[4]
    print(it)
