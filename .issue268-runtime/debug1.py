"""Debug: MUX_OUT_C components + target + goal extent near J_WING pad 13."""
import importlib.util, sys
spec = importlib.util.spec_from_file_location('b2', '.issue268-runtime/build2.py')
# Instead of importing (it executes), replicate minimal pieces:
import math
import numpy as np
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        for pad in fp.Pads():
            if pad.GetNetname() == 'MUX_OUT_C':
                q = pad.GetPosition(); print('JW pad13 at', mm(q.x), mm(q.y), 'layer', int(pad.GetLayer()))
print('--- MUX_OUT_C tracks:')
for t in b.GetTracks():
    if t.GetNetname() == 'MUX_OUT_C':
        s, e = t.GetStart(), t.GetEnd()
        print(' via' if isinstance(t, p.PCB_VIA) else f' L{int(t.GetLayer())}',
              (round(mm(s.x),2), round(mm(s.y),2)), (round(mm(e.x),2), round(mm(e.y),2)), 'w', round(mm(t.GetWidth()),2))
print('--- MUX_OUT_C pads:')
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() == 'MUX_OUT_C':
            q = pad.GetPosition(); print(' ', fp.GetReference(), pad.GetNumber(), (round(mm(q.x),2), round(mm(q.y),2)), 'L', int(pad.GetLayer()))
