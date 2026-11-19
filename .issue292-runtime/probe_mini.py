import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
keep = []
for f in list(b.GetFootprints()):
    if f.GetReference() != 'J2': b.Remove(f)
for t in list(b.GetTracks()):
    q = t.GetPosition() if isinstance(t, p.PCB_VIA) else t.GetStart()
    if not (isinstance(t, p.PCB_VIA) and abs(q.x / 1e6 - 76.29) < 0.3 and abs(q.y / 1e6 - 109.14) < 0.3):
        b.Remove(t)
for z in list(b.Zones()): b.Remove(z)
for d in list(b.GetDrawings()): b.Remove(d)
p.SaveBoard('.issue292-runtime/mini.kicad_pcb', b)
print('mini saved')
