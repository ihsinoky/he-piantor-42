import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
print('tracks:', len(b.GetTracks()), 'fps:', len(b.GetFootprints()), 'zones:', b.GetAreaCount())
print('board methods:', [m for m in dir(b) if 'utline' in m or 'dge' in m][:10])
t = b.GetTracks()[0]
print('track type:', type(t).__name__, 'has GetEffectiveShape:', hasattr(t,'GetEffectiveShape'))
fp = b.GetFootprints()[0]
pad = list(fp.Pads())[0]
print('pad has GetEffectiveShape:', hasattr(pad,'GetEffectiveShape'))
try:
    s = pad.GetEffectiveShape(p.F_Cu)
    print('eff shape class:', s.GetClass() if hasattr(s,'GetClass') else type(s))
except Exception as e:
    print('eff err:', e)
z = b.Zones()[0] if len(b.Zones()) else None
print('zone0:', z.GetNetname() if z else None, 'filled polys F:', len(z.GetFilledPolysList(p.F_Cu).Polygons()) if z else 0)
print('drawings:', len(b.GetDrawings()))
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        print('edge shape class:', d.GetShape() if hasattr(d,'GetShape') else type(d).__name__)
        break
