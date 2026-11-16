import json, sys, time
sys.path.insert(0, 'sources/frontier')
import fitlibF as FF

t0 = time.time()
# classification coverage at both pitches
for p in (17, 16):
    bl = FF.bodies_at(p, 0)
    print(p, 'bodies', len(bl), 'load+classify', round(time.time() - t0, 1))
# s=0 reproduction of round-18 final: gate1 96/98, WW 6
M = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round18/repair_state.json'))['M']
FF.set_height(0)
wires, lens, failed = {}, {}, []
import fitlib18 as F
for side in ('right', 'left'):
    for pin in range(1, 15):
        w, r = FF.build_wire(FF.points_of(M, pin - 1, side))
        assert w is not None, (side, pin, r)
        wires[f'Wire-{side}-{pin:02d}'] = w; lens[f'Wire-{side}-{pin:02d}'] = round(r + 7.30, 2)
bodies = {p: FF.bodies_at(p, 0) for p in (17, 16)}
sc = FF.Scorer(wires, bodies)
ww, wf = sc.full()
print('WW', len(ww), 'WF17', len(wf[17]), 'WF16', len(wf[16]),
      'gate1_17', len(ww) + len(wf[17]), 'gate1_16', len(ww) + len(wf[16]),
      'longest', max(lens.values()), 'elapsed', round(time.time() - t0, 1))
