"""Round 18 slack build: bight storage across the corridor corner on
the repaired feed. Detour leaves the B1->corridor host at 4.5 mm,
bulges by depth d along a chosen normal, rejoins the climb 2.5 mm
past the corridor point (corridor waypoint is bypassed, not moved).
Per-strand depth bisected for Delta = target (max 14.0); direction
chosen by fitted local score against the incrementally built stored
assembly. Usage: slack18.py [target] [budget_s]"""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import repair18_lib as R

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 13.8
BUDGET = float(sys.argv[2]) if len(sys.argv) > 2 else 1500
T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

state = json.load(open(f'{RT}/round18/repair_state.json'))
M = state['M']

def unit(v):
    v = np.array(v, float); return v / np.linalg.norm(v)

def stored_points(M, i, side, direction, d):
    pts = F.points_of(M, i, 'right')
    B0, B1, COR, RISE = [np.array(p, float) for p in pts[:4]]
    rest = pts[4:]
    t_in = unit(COR - B1); t_out = unit(RISE - COR)
    if direction == 'U':
        n = np.array([0., 0., 1.])
    else:
        n = np.array([t_in[1], -t_in[0], 0.]); n = unit(n)
        if direction == 'W' and n[0] > 0: n = -n
        if direction == 'E' and n[0] < 0: n = -n
    q0 = B1 + 4.5 * t_in
    q3 = COR + 2.5 * t_out
    q1 = q0 + d * n + 1.5 * t_in
    q2 = q3 + d * n - 1.5 * t_out
    out = [B0, B1, q0, q1, q2, q3, RISE] + [np.array(p, float) for p in rest]
    out = [list(map(float, p)) for p in out]
    if side == 'left':
        out = [[-p[0], p[1], p[2]] for p in out]
    return out

def build_len(pts):
    w, r = F.build_wire(pts)
    return (r if w is not None else None)

# taut lengths per design (right side; left identical by symmetry of construction)
taut_len = {}
for i in range(14):
    L = build_len(F.points_of(M, i, 'right'))
    assert L is not None
    taut_len[i] = L
log('taut lengths ok; max', round(max(taut_len.values()), 2))

def solve_d(i, direction, target):
    lo, hi = 0.0, 9.0
    Lhi = build_len(stored_points(M, i, 'right', direction, hi))
    if Lhi is None: return None, None
    if Lhi - taut_len[i] < target:
        return hi, Lhi - taut_len[i]
    for _ in range(7):
        mid = (lo + hi) / 2
        L = build_len(stored_points(M, i, 'right', direction, mid))
        if L is None: hi = mid; continue
        if L - taut_len[i] < target: lo = mid
        else: hi = mid
    d = (lo + hi) / 2
    L = build_len(stored_points(M, i, 'right', direction, d))
    return (d, L - taut_len[i]) if L is not None else (None, None)

plan = {}
for i in range(14):
    plan[i] = {}
    for dr in ('W', 'E', 'U'):
        d, dl = solve_d(i, dr, TARGET)
        plan[i][dr] = (d, None if dl is None else round(dl, 2))
    log('strand', i + 1, plan[i])
json.dump({str(i + 1): plan[i] for i in plan},
          open(f'{RT}/round18/slack_plan.json', 'w'), indent=1)
log('plan saved')

# ---------- stage B: assemble with fitted direction choice ----------
bodies, body_bnd = R.load_bodies()
wires, samp, wb = {}, {}, {}
for side in ('right', 'left'):
    for pin in range(1, 15):
        r, why = R.build_s(F.points_of(M, pin - 1, side))
        assert r is not None, (side, pin, why)
        nm = f'Wire-{side}-{pin:02d}'
        wires[nm] = r[0]; samp[nm] = r[1]; wb[nm] = F.bounds(r[0])
log('taut assembly built')

choices = {}
for i in range(14):
    best = None
    for dr in ('W', 'E', 'U'):
        d, dl = plan[i][dr]
        if d is None: continue
        cand = {}
        ok = True
        for side in ('right', 'left'):
            r, why = R.build_s(stored_points(M, i, side, dr, d))
            if r is None: ok = False; break
            cand[side] = r
        if not ok: continue
        tot_c, tot_v = 0, 0.0
        for side in ('right', 'left'):
            nm = f'Wire-{side}-{i + 1:02d}'
            c, v, _ = R.eval_wire(nm, cand[side][0], cand[side][1],
                                  wires, samp, wb, bodies, body_bnd)
            tot_c += c; tot_v += v
        if best is None or (tot_c, tot_v) < (best[0], best[1]):
            best = (tot_c, tot_v, dr, d, cand)
        log('strand', i + 1, dr, 'd', d, 'local', tot_c, round(tot_v, 1))
    assert best is not None, i
    tot_c, tot_v, dr, d, cand = best
    for side in ('right', 'left'):
        nm = f'Wire-{side}-{i + 1:02d}'
        wires[nm] = cand[side][0]; samp[nm] = cand[side][1]; wb[nm] = F.bounds(cand[side][0])
    choices[i] = {'dir': dr, 'd': d, 'local': [tot_c, round(tot_v, 2)]}
    log('CHOOSE strand', i + 1, dr, 'd', d, 'local', tot_c, round(tot_v, 1))

# ---------- accounting + save ----------
out = {'target': TARGET, 'M': M, 'strands': {}}
for i in range(14):
    dr, d = choices[i]['dir'], choices[i]['d']
    rec = {'dir': dr, 'd': d, 'local': choices[i]['local']}
    for side in ('right', 'left'):
        pts = stored_points(M, i, side, dr, d)
        w, L = F.build_wire(pts)
        rec[f'points_{side}'] = pts
        rec[f'len_{side}'] = round(L, 3)
    rec['delta_right'] = round(rec['len_right'] - taut_len[i], 3)
    rec['delta_left'] = rec['delta_right']
    rec['finished_right'] = round(rec['len_right'] + 7.30, 2)
    out['strands'][str(i + 1)] = rec
    log('strand', i + 1, 'delta', rec['delta_right'], 'finished', rec['finished_right'])
json.dump(out, open(f'{RT}/round18/stored.json', 'w'), indent=1)
log('stored.json saved')
