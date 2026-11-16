"""Gate-8 evidence for the frontier study: fitted preview STEP of the
highest sub-22.2 height (plate 20.5, 17 mm) - height-model bodies +
stored (slack-dressed) wires from the finish run."""
import json, sys
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier'
sys.path.insert(0, PB); sys.path.insert(0, f'{PB}/sources/frontier')
import fitlibF as FF
import frontier_lib as FL
from build123d import export_step, Compound

s = 6.95
FF.set_height(s)
bodies = dict(FF.bodies_at(17, s))
stored = json.load(open(f'{RT}/stored_z205b.json'))
parts = [b for b in bodies.values()]
for k, r in stored['strands'].items():
    for side in ('right', 'left'):
        w, why = FL.build_s(r[f'points_{side}'])
        assert w is not None, (k, side, why)
        parts.append(w[0])
out = f'{PB}/sources/frontier/preview-plate20.5-17mm.step'
export_step(Compound(children=parts), out)
print('wrote', out, 'parts', len(parts))
