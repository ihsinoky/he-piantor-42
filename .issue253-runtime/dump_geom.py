import pcbnew, json
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-north/hardware/kicad/qualification/issue-235-wing-round2/wing-rev4-17mm-left/input.kicad_pcb')
fp = b.FindFootprintByReference('J_WING')
print('JWING pos', fp.GetPosition().x/1e6, fp.GetPosition().y/1e6, 'orient', fp.GetOrientationDegrees(), 'flip', fp.IsFlipped())
for p in fp.Pads():
    c = p.GetCenter()
    print('pad', p.GetNumber(), p.GetNetname(), round(c.x/1e6,3), round(c.y/1e6,3))
pts = []
for d in b.GetDrawings():
    if d.GetLayerName() == 'Edge.Cuts':
        bb = d.GetBoundingBox()
        pts.append((d.Type(), round(bb.GetLeft()/1e6,2), round(bb.GetTop()/1e6,2), round(bb.GetRight()/1e6,2), round(bb.GetBottom()/1e6,2)))
pts.sort(key=lambda r: r[2])
print('edge items by top Y:')
for r in pts[:14]: print(r)
