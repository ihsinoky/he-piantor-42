import pcbnew as p
def mm(v): return v/1e6
for tag, path in [('REV10', 'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'),
                  ('WMAIN', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')]:
    try: b = p.LoadBoard(path)
    except Exception as e: print(tag, 'load fail', e); continue
    for f in b.GetFootprints():
        if f.GetReference() in ('J2', 'J3'):
            print(f"{tag} {f.GetReference()} at ({mm(f.GetPosition().x):.2f},{mm(f.GetPosition().y):.2f}) rot={f.GetOrientationDegrees():.1f}")
            ps = [(pad.GetNumber(), round(mm(pad.GetPosition().x),2), round(mm(pad.GetPosition().y),2),
                   round(mm(pad.GetSize().x),2), round(mm(pad.GetSize().y),2), round(pad.GetOrientationDegrees(),1)) for pad in f.Pads()]
            for row in ps[:6]: print('   ', row)
            print('    ... total pads', len(ps))
