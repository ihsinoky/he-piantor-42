import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
print('outlines:', po.OutlineCount())
for name in ('Polygon','Outline'):
    try:
        ch = getattr(po, name)(0)
        print(name, '->', type(ch).__name__, [m for m in dir(ch) if 'oint' in m or 'eg' in m][:8])
        try:
            print('  PointCount:', ch.PointCount())
        except Exception as e: print('  pc err', e)
        try:
            pts = ch.GetPoints(); print('  GetPoints n:', len(pts), pts[0])
        except Exception as e: print('  gp err', e)
    except Exception as e:
        print(name, 'err', e)
t = [x for x in b.GetTracks() if type(x).__name__=='PCB_TRACK'][0]
s = t.GetEffectiveShape(p.F_Cu)
print('track eff class:', s.GetClass())
print('shape methods:', [m for m in dir(s) if not m.startswith('_')])
