import pcbnew as p
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
segs = []
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_SCL' or isinstance(t, p.PCB_VIA): continue
    if t.GetLayer() != 6: continue
    s, e = t.GetStart(), t.GetEnd()
    a, bb = (round(mm(s.x), 2), round(mm(s.y), 2)), (round(mm(e.x), 2), round(mm(e.y), 2))
    if max(a[1], bb[1]) > 124.0 and min(a[0], bb[0]) > 72.0 and max(a[0], bb[0]) < 96.0:
        segs.append((a, bb))
print('I2 SCL segs in south box:', len(segs))
pts = {}
for a, bb in segs:
    pts[a] = pts.get(a, 0) + 1; pts[bb] = pts.get(bb, 0) + 1
ends = [q for q, n in pts.items() if n == 1]
print('endpoints (deg1):', ends)
