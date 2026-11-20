#!/usr/bin/env python3
"""Pad-by-pad diff: official (Eagle, Insight SiP) vs derived footprint.
Tries all 8 dihedral transforms of the centered official frame against
the derived frame; reports the best and the full per-pad table."""
import json, math, itertools

off = json.load(open('official-pads.json'))
der = json.load(open('../isp1807-derived-pads.json'))

# center official on its pad-center bbox
xs = [v[0] for v in off.values()]; ys = [v[1] for v in off.values()]
cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
offc = {k: [v[0]-cx, v[1]-cy, v[2], v[3]] for k, v in off.items()}

def transforms(p):
    x, y = p
    return {
        'id': (x, y), 'rot90': (-y, x), 'rot180': (-x, -y), 'rot270': (y, -x),
        'flipx': (-x, y), 'flipy': (x, -y), 'flipxy': (y, x), 'flipx_rot90': (-y, -x),
    }

common = [k for k in der if k in offc]
best = None
for name in ['id', 'rot90', 'rot180', 'rot270', 'flipx', 'flipy', 'flipxy', 'flipx_rot90']:
    errs = []
    for k in common:
        tx, ty = transforms(offc[k][:2])[name]
        errs.append(math.hypot(tx-der[k][0], ty-der[k][1]))
    m = max(errs); mean = sum(errs)/len(errs)
    if best is None or m < best[1]:
        best = (name, m, mean)
print('best transform:', best)

name = best[0]
rows = []
moved = added = removed = resized = same = 0
for k in sorted(set(offc) | set(der), key=lambda z: int(z)):
    o = offc.get(k); d = der.get(k)
    if o:
        tx, ty = transforms(o[:2])[name]
        o = [round(tx, 4), round(ty, 4), o[2], o[3]]
    if o and d:
        dp = math.hypot(o[0]-d[0], o[1]-d[1])
        ds = (o[2]-d[2], o[3]-d[3])
        status = []
        if dp > 0.005: status.append(f'MOVED {dp:.3f}'); moved += 1
        if abs(ds[0]) > 0.005 or abs(ds[1]) > 0.005: status.append(f'RESIZED {ds[0]:+.2f}/{ds[1]:+.2f}'); resized += 1
        if not status: status.append('SAME'); same += 1
        rows.append((k, o, d, ' '.join(status)))
    elif o:
        rows.append((k, o, None, 'ADDED (official only)')); added += 1
    else:
        rows.append((k, None, d, 'REMOVED (derived only)')); removed += 1

print(f'same={same} moved={moved} resized={resized} added={added} removed={removed}')
with open('isp1807-pad-diff.md', 'w') as f:
    f.write('# ISP1807-LR pad diff — official (Insight SiP Eagle lib) vs derived\n\n')
    f.write(f'Transform applied to official frame: {name} (after bbox centering). ')
    f.write(f'same={same} moved={moved} resized={resized} added={added} removed={removed}\n\n')
    f.write('| pad | official x | official y | official size | derived x | derived y | derived size | status |\n')
    f.write('|---|---|---|---|---|---|---|---|\n')
    for k, o, d, s in rows:
        f.write('| {} | {} | {} | {} | {} | {} | {} | {} |\n'.format(
            k,
            o[0] if o else '-', o[1] if o else '-', f'{o[2]}x{o[3]}' if o else '-',
            d[0] if d else '-', d[1] if d else '-', f'{d[2]}x{d[3]}' if d else '-', s))
json.dump({'transform': name, 'rows': [(k, o, d, s) for k, o, d, s in rows]},
          open('isp1807-pad-diff.json', 'w'), indent=1)
for k, o, d, s in rows:
    if s != 'SAME':
        print(k, o, d, s)
