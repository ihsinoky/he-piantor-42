"""Measure Wing Rev.5 J_WING escape tracks: segments touching each pad."""
import json, sys
import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
jw = None
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        jw = fp
pads = {p.GetNumber(): p for p in jw.Pads() if p.GetNumber().isdigit()}
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA):
        continue
    s, e = t.GetStart(), t.GetEnd()
    for n, p in pads.items():
        pc = p.GetPosition()
        for q in (s, e):
            if abs(q.x-pc.x) < 650000 and abs(q.y-pc.y) < 650000:
                print(n, p.GetNetname(), 'L', int(t.GetLayer()), 'w', round(t.GetWidth()/1e6, 3),
                      'from', (round(s.x/1e6, 3), round(s.y/1e6, 3)), 'to', (round(e.x/1e6, 3), round(e.y/1e6, 3)))
