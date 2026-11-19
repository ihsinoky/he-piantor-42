import pcbnew as p
def mm(v): return v/1e6
for tag, path in [('ADOPTED', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'),
                  ('WORK', '.issue292-runtime/wmain-work.kicad_pcb')]:
    b = p.LoadBoard(path)
    for t in b.GetTracks():
        if t.GetNetname() in ('PAD_SCL', 'PAD_DR'):
            s, e = t.GetStart(), t.GetEnd()
            cx, cy = mm(s.x), mm(s.y)
            if 110 < cx < 114 and 94 < cy < 100:
                print(tag, t.GetNetname(), type(t).__name__, 'layer', t.GetLayer(),
                      (round(cx,2), round(cy,2)), (round(mm(e.x),2), round(mm(e.y),2)), 'w', round(mm(t.GetWidth()),3))
