import pcbnew as p
mm = lambda v: v/1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
for fp in b.GetFootprints():
    if fp.GetReference() != 'J_WING': continue
    print('FPID:', fp.GetFPID().GetLibItemName(), 'layer', fp.GetLayerName(), 'rot', fp.GetOrientationDegrees(), 'flipped', fp.IsFlipped())
    for d in fp.GraphicalItems():
        bb = d.GetBoundingBox()
        print('  item layer', d.GetLayerName(), 'bbox x %.3f..%.3f y %.3f..%.3f' % (mm(bb.GetLeft()), mm(bb.GetRight()), mm(bb.GetTop()), mm(bb.GetBottom())))
