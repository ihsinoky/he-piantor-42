import pcbnew as p, shutil
shutil.copy('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb', '.issue292-runtime/probe.kicad_pcb')
b = p.LoadBoard('.issue292-runtime/probe.kicad_pcb')
for f in b.GetFootprints():
    if f.GetReference() == 'CIN2':
        pos = f.GetPosition()
        print('before:', pos.x/1e6, pos.y/1e6)
        f.SetPosition(p.VECTOR2I(pos.x + 350000, pos.y + 350000))
        print('after set:', f.GetPosition().x/1e6, f.GetPosition().y/1e6)
        break
b.SaveBoard('.issue292-runtime/probe.kicad_pcb')
b2 = p.LoadBoard('.issue292-runtime/probe.kicad_pcb')
for f in b2.GetFootprints():
    if f.GetReference() == 'CIN2':
        print('reloaded:', f.GetPosition().x/1e6, f.GetPosition().y/1e6)
