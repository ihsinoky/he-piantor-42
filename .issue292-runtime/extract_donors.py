"""Extract donor geometry/footprints from Rev.10 board + ISP1807 from jrwatch."""
import pcbnew as p, json
def S(x):
    return str(x)
from pathlib import Path
E = Path(__file__).resolve().parent
W = E.parent
REV10 = W/'hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'
out = {}

b = p.LoadBoard(str(REV10))
# outline drawings on Edge.Cuts
edges = []
for d in b.GetDrawings():
    if d.GetLayerName() == 'Edge.Cuts':
        s = {'shape': d.GetShapeStr() if hasattr(d,'GetShapeStr') else str(d.GetShape())}
        try:
            s['start'] = [p.ToMM(d.GetStart().x), p.ToMM(d.GetStart().y)]
            s['end'] = [p.ToMM(d.GetEnd().x), p.ToMM(d.GetEnd().y)]
        except Exception:
            pass
        try:
            s['center'] = [p.ToMM(d.GetCenter().x), p.ToMM(d.GetCenter().y)]
            s['radius'] = p.ToMM(d.GetRadius())
        except Exception:
            pass
        edges.append(s)
out['edges'] = edges
# footprints inventory
fps = []
for f in b.GetFootprints():
    pos = f.GetPosition()
    pads = []
    for a in f.Pads():
        pads.append({'num': a.GetNumber(), 'net': S(a.GetNetname()),
                     'pos': [round(p.ToMM(a.GetPosition().x),4), round(p.ToMM(a.GetPosition().y),4)],
                     'size': [round(p.ToMM(a.GetSize().x),3), round(p.ToMM(a.GetSize().y),3)],
                     'shape': str(a.GetShape()), 'type': str(a.GetAttribute())})
    fps.append({'ref': S(f.GetReference()), 'value': S(f.GetValue()),
                'fp': S(f.GetFPID().GetLibItemName()) if f.GetFPID() else '',
                'pos': [round(p.ToMM(pos.x),4), round(p.ToMM(pos.y),4)],
                'rot': f.GetOrientationDegrees(), 'layer': f.GetLayerName(),
                'pads': pads})
out['rev10_footprints'] = fps
out['rev10_nets'] = sorted([S(n.GetNetname()) for n in b.GetNetsByName().values()] if hasattr(b,'GetNetsByName') else [])
(E/'rev10-donor.json').write_text(json.dumps(out, indent=1))
print('edges', len(edges), 'fps', len(fps))

# jrwatch: find ISP1807-ish footprint
j = p.LoadBoard(str(E/'sources/jrwatch.kicad_pcb'))
cands = []
for f in j.GetFootprints():
    cands.append({'ref': S(f.GetReference()), 'value': S(f.GetValue()),
                  'fp': S(f.GetFPID().GetLibItemName()) if f.GetFPID() else '',
                  'npads': len(list(f.Pads()))})
(E/'jrwatch-fps.json').write_text(json.dumps(cands, indent=1))
print('jrwatch fps', len(cands))
for c in cands:
    if 'ISP' in (c['value']+c['fp']+c['ref']).upper() or '1807' in (c['value']+c['fp']):
        print('ISP candidate:', c)
