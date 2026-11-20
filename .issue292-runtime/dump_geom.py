"""Dump board geometry (pads with rotation, tracks, vias, outline) to JSON
for the GND-tap planner."""
import pcbnew as p, json, sys
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/sys.argv[1]))
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
out = {'pads': [], 'tracks': [], 'vias': []}
for f in b.GetFootprints():
    ref = str(f.GetReference())
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        layers = []
        if pad.IsOnLayer(p.F_Cu): layers.append('F')
        if pad.IsOnLayer(p.B_Cu): layers.append('B')
        out['pads'].append({'ref': f"{ref}.{pad.GetNumber()}", 'net': pad.GetNetname(),
                            'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                            'sx': p.ToMM(sz.x), 'sy': p.ToMM(sz.y),
                            'rot': pad.GetOrientationDegrees(), 'layers': layers,
                            'pth': pad.GetAttribute() == p.PAD_ATTRIB_PTH})
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        out['vias'].append({'net': t.GetNetname(), 'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                            'd': p.ToMM(t.GetWidth(p.F_Cu))})
    else:
        s, e = t.GetStart(), t.GetEnd()
        out['tracks'].append({'net': t.GetNetname(), 'layer': LAY.get(t.GetLayer()),
                              'x1': p.ToMM(s.x), 'y1': p.ToMM(s.y),
                              'x2': p.ToMM(e.x), 'y2': p.ToMM(e.y),
                              'w': p.ToMM(t.GetWidth())})
Path('geom_now.json').write_text(json.dumps(out))
print('pads', len(out['pads']), 'tracks', len(out['tracks']), 'vias', len(out['vias']))
