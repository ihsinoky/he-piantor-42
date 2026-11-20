import pcbnew as p
B = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
mm = p.ToMM
print('--- In2.Cu items X 113..120, Y 128..137 ---')
for t in B.GetTracks():
    if t.GetLayerName() != 'In2.Cu': continue
    s, e = t.GetStart(), t.GetEnd()
    x1,y1,x2,y2 = mm(s.x),mm(s.y),mm(e.x),mm(e.y)
    if 113 <= min(x1,x2) and max(x1,x2) <= 120 and 128 <= min(y1,y2) and max(y1,y2) <= 137:
        kind = 'VIA' if t.Type() == p.PCB_VIA_T else 'TRK'
        print('%s %-8s (%.2f,%.2f)->(%.2f,%.2f) w=%.2f' % (kind, t.GetNetname(), x1,y1,x2,y2, mm(t.GetWidth()) if kind=='TRK' else 0))
print('--- In2.Cu items X 99..118, Y 133..136 (SYS highway path) ---')
for t in B.GetTracks():
    if t.GetLayerName() != 'In2.Cu': continue
    s, e = t.GetStart(), t.GetEnd()
    x1,y1,x2,y2 = mm(s.x),mm(s.y),mm(e.x),mm(e.y)
    if 99 <= min(x1,x2) and max(x1,x2) <= 118 and 133 <= min(y1,y2) and max(y1,y2) <= 136:
        kind = 'VIA' if t.Type() == p.PCB_VIA_T else 'TRK'
        print('%s %-8s (%.2f,%.2f)->(%.2f,%.2f)' % (kind, t.GetNetname(), x1,y1,x2,y2))
