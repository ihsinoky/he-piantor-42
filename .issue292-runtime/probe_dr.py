import pcbnew as p
def mm(v): return v/1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname() == 'PAD_DR':
            bb = pad.GetBoundingBox()
            print('PAD', f.GetReference(), pad.GetNumber(), tuple(round(mm(v), 2) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())))
for t in b.GetTracks():
    if t.GetNetname() == 'PAD_DR':
        bb = t.GetBoundingBox()
        l, tp, r, bt = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
        if l > 111.5 and tp > 95.5 and r < 112.6 and bt < 98.2:
            print('TRK/VIA', type(t).__name__, 'layer', t.GetLayer(), tuple(round(v, 2) for v in (l, tp, r, bt)), 'w', round(mm(t.GetWidth()), 3))
