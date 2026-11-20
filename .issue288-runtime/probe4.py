import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix/wmatrix.kicad_pcb')
for ref in ('R_SHUNT', 'J_USB', 'U_HA0'):
    fp = b.FindFootprintByReference(ref)
    print(ref, 'fp rot:', fp.GetOrientationDegrees())
    for p in fp.Pads()[:3]:
        print('   pad', p.GetNumber(), 'orient:', p.GetOrientationDegrees(), 'size:', p.GetSize().x/1e6, p.GetSize().y/1e6)
