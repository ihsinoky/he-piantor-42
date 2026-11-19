"""Delete GND tracks/vias whose exact shape overlaps another net's shape (per layer). Iterates."""
import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
LAYS = ('F', 'I2', 'B')
for it in range(3):
    obs = {}
    for L in LAYS:
        obs[L] = [(n2, s2) for n2, s2 in all_obs(L) if n2 != 'GND']
    bad = []
    for m in MODEL:
        if not m['alive'] or m['net'] != 'GND': continue
        hit = False
        for L, sh in m['shapes'].items():
            if L not in obs: continue
            for n2, s2 in obs[L]:
                if sh.intersection(s2).area > 1e-9:
                    hit = True; break
            if hit: break
        if hit: bad.append(m)
    print(f'pass {it}: deleting {len(bad)} shorted GND items')
    if not bad: break
    for m in bad:
        b.Remove(m['obj']); m['alive'] = False
    p.SaveBoard(DST, b)
