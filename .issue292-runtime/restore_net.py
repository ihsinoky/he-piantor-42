"""Restore ALL items of one net from the adopted board that are missing
in the work board (matched by geometry, since uuids differ after copies)."""
import pcbnew as p, sys

SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
DST = '.issue292-runtime/wmain-work.kicad_pcb'
NET = sys.argv[1]

def mm(v): return v / 1e6
def key(t):
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); return ('V', round(mm(q.x), 3), round(mm(q.y), 3))
    s, e = t.GetStart(), t.GetEnd()
    return ('T', t.GetLayer(), round(mm(s.x), 3), round(mm(s.y), 3),
            round(mm(e.x), 3), round(mm(e.y), 3), round(mm(t.GetWidth()), 3))

src = p.LoadBoard(SRC)
work = p.LoadBoard(DST)
have = {key(t) for t in work.GetTracks() if t.GetNetname() == NET}
netobj = work.FindNet(NET)
added = 0
for t in src.GetTracks():
    if t.GetNetname() != NET or key(t) in have: continue
    if isinstance(t, p.PCB_VIA):
        v = p.PCB_VIA(work)
        v.SetPosition(t.GetPosition())
        v.SetWidth(t.GetWidth(p.F_Cu)); v.SetDrill(t.GetDrill())
        v.SetNet(netobj); work.Add(v)
    else:
        nt = p.PCB_TRACK(work)
        nt.SetStart(t.GetStart()); nt.SetEnd(t.GetEnd())
        nt.SetWidth(t.GetWidth()); nt.SetLayer(t.GetLayer())
        nt.SetNet(netobj); work.Add(nt)
    added += 1
p.SaveBoard(DST, work)
print(f'{NET}: restored {added} missing items')
