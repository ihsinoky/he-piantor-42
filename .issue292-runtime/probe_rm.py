import pcbnew as p
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
n0 = sum(1 for f in b.GetFootprints() if hasattr(f, 'Pads'))
print('footprints with Pads before:', n0, 'total:', len(b.GetFootprints()))
t = [t for t in b.GetTracks() if t.GetNetname() == 'SYS_3V3'][0]
b.Remove(t)
bad = [type(f).__name__ for f in b.GetFootprints() if not hasattr(f, 'Pads')]
print('after Remove: bad entries:', bad)
