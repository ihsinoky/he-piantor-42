"""Dump the FINISHED tree board (edges, footprints+pads, tracks, vias)
to board_dump_final.json for render_pngs_final.py."""
import pcbnew as p, json
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
LAY = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
out = {'edges': [], 'fps': [], 'tracks': [], 'vias': []}
for s in b.GetDrawings():
    if isinstance(s, p.PCB_SHAPE) and s.GetLayer() == p.Edge_Cuts:
        a, c = s.GetStart(), s.GetEnd()
        out['edges'].append((p.ToMM(a.x), p.ToMM(a.y), p.ToMM(c.x), p.ToMM(c.y)))
for f in b.GetFootprints():
    fp = {'ref': str(f.GetReference()), 'pads': []}
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        fp['pads'].append({'n': str(pad.GetNumber()), 'net': pad.GetNetname(),
                           'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                           'sx': p.ToMM(sz.x), 'sy': p.ToMM(sz.y)})
    out['fps'].append(fp)
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        out['vias'].append({'net': t.GetNetname(), 'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                            'd': p.ToMM(t.GetWidth(p.F_Cu))})
    else:
        s, e = t.GetStart(), t.GetEnd()
        out['tracks'].append({'net': t.GetNetname(), 'layer': LAY.get(t.GetLayer()),
                              'w': p.ToMM(t.GetWidth()),
                              'x1': p.ToMM(s.x), 'y1': p.ToMM(s.y),
                              'x2': p.ToMM(e.x), 'y2': p.ToMM(e.y)})
(E/'board_dump_final.json').write_text(json.dumps(out))
print('dumped:', {k: len(v) for k, v in out.items()})
