import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-north/hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-left/input.kicad_pcb')
for d in b.GetDrawings():
    if d.GetLayerName() != 'Edge.Cuts': continue
    bb = d.GetBoundingBox()
    if bb.GetTop()/1e6 <= 16.0:
        print('type', d.Type(), 'SHAPE_T names:', d.GetShape())
        for attr in ('GetStart','GetEnd','GetMid','GetCenter','GetControlPoint1','GetControlPoint2','GetPointCount'):
            if hasattr(d, attr):
                try:
                    r = getattr(d, attr)()
                    print('  ', attr, (round(r.x/1e6,2), round(r.y/1e6,2)) if hasattr(r,'x') else r)
                except Exception as e: print('  ', attr, 'ERR', str(e)[:60])
