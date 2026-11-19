import pcbnew as p
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
def mm(v): return v / 1e6
kill = []
for t in list(b.GetTracks()):
    if t.GetNetname() != 'SYS_3V3': continue
    bb = t.GetBoundingBox()
    if mm(bb.GetLeft()) < 84.5: kill.append(t)
print('kill count:', len(kill))
for t in kill: b.Remove(t)
bad = [(i, type(f).__name__) for i, f in enumerate(b.GetFootprints()) if not hasattr(f, 'Pads')]
print('bad footprints after mass Remove:', bad)
print('total footprints:', len(b.GetFootprints()))
