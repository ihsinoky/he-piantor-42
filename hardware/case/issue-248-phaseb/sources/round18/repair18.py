"""Round 18 per-strand Gauss-Seidel fitted repair (first-improvement).
Acceptance: candidate design-strand local fitted count (both sides,
both pitches, gate-1 convention: WW repaired-standard, WF plain
Common, threshold 0.005 mm3) must not regress; prefer strict count
improvement, then >=2% volume improvement at equal count.
WW zero-Common pairs are prefiltered by exact centreline samples:
samples at <=0.25 mm arc spacing give curve_min >= d_points - 0.25,
so d_points > 1.28 proves solid distance > 0.03 (disjoint).
State: .issue248-runtime/round18/repair_state.json; resumable."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import audit_repair as ar
from geometry import rounded
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformAbscissa  # unused, kept for reference
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
BUDGET = float(sys.argv[1]) if len(sys.argv) > 1 else 1200
T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

def path_samples(path, step=0.2):
    """(samples, h): samples along the rounded path at <=step spacing;
    h = max consecutive gap. curve_min >= d_points - (hA + hB)/2."""
    out = []
    for e in path.edges():
        ad = BRepAdaptor_Curve(e.wrapped)
        n = max(2, int(np.ceil(e.length / step)) + 1)
        for u in np.linspace(ad.FirstParameter(), ad.LastParameter(), n):
            p = ad.Value(float(u)); out.append([p.X(), p.Y(), p.Z()])
    A = np.array(out)
    gaps = np.sqrt(((A[1:] - A[:-1]) ** 2).sum(-1))
    return A, float(gaps.max())

def build_s(pts):
    """Strict build + centreline samples. (solid, samples) or (None, why)."""
    try:
        path = rounded(F.rr.split_corners(pts))
    except AssertionError as e:
        return None, f'rounded: {str(e)[:50]}'
    from build123d import sweep, Face, Wire, Plane, Vector
    d0 = np.array(pts[1], float) - np.array(pts[0], float)
    try:
        w = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*pts[0]),
                  z_dir=Vector(*map(float, d0))))), path=path)
    except Exception as e:
        return None, f'sweep: {str(e)[:50]}'
    if not (w.is_valid and len(w.solids()) == 1):
        return None, 'invalid'
    return (w, path_samples(path)), None

def min_pp(A, B):
    best = 1e9
    for s in range(0, len(A), 256):
        d = np.sqrt(((A[s:s + 256, None, :] - B[None, :, :]) ** 2).sum(-1))
        best = min(best, float(d.min()))
    return best

# ---------- state ----------
state_p = f'{RT}/round18/repair_state.json'
try:
    state = json.load(open(state_p)); M = state['M']
    log('resumed: pass', state['pass'], 'accepted', len(state['trajectory']))
except FileNotFoundError:
    M = json.load(open(f'{RT}/round14/taut_opt.json'))
    state = {'M': M, 'trajectory': [], 'pass': 0, 'done_this_pass': []}
    log('fresh state from taut_opt')
BND = json.load(open(f'{RT}/round17/feed_state_bnd.json'))
bodies = {p: F.bodies_of(p) for p in (17, 16)}
body_bnd = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
body_shape = {p: dict(bl) for p, bl in bodies.items()}

wires, samp = {}, {}
for side in ('right', 'left'):
    for pin in range(1, 15):
        r, why = build_s(F.points_of(M, pin - 1, side))
        assert r is not None, (side, pin, why)
        wires[f'Wire-{side}-{pin:02d}'] = r[0]; samp[f'Wire-{side}-{pin:02d}'] = r[1]
wb = {n: F.bounds(s) for n, s in wires.items()}
log('built all wires + samples')

def vol_pair(a, b, ab, bb, repair=False, sa=None, sb=None):
    if F._gap(ab, bb) > 0: return 0.0
    if repair and sa is not None and sb is not None:
        thr = 1.0 + (sa[1] + sb[1]) / 2 * 1.05 + 0.05
        if min_pp(sa[0], sb[0]) > thr: return 0.0
    v = F.volume(a, b)
    if v > 0 or not repair: return v
    d = ar.solid_distance(a, b)
    if d > ar.DIST_CLEAR: return 0.0
    return ar.clipped_common_volume(a, b)

def eval_design(i, cand):
    """cand: {side: (solid, samples)}. (count, vol) vs other wires + bodies."""
    cnt, vol = 0, 0.0
    for side in ('right', 'left'):
        name = f'Wire-{side}-{i + 1:02d}'
        w, sm = cand[side]; wbnd = F.bounds(w)
        for oname, ow in wires.items():
            if oname == name: continue
            v = vol_pair(w, ow, wbnd, wb[oname], repair=True, sa=sm, sb=samp[oname])
            if v > F.HIT: cnt += 2; vol += 2 * v
        for p in (17, 16):
            for bn, bs in bodies[p]:
                v = vol_pair(w, bs, wbnd, body_bnd[p][bn])
                if v > F.HIT: cnt += 1; vol += v
    return cnt, vol

def centroid(shape):
    props = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, props, True, False, False)
    c = props.CentreOfMass(); return np.array([c.X(), c.Y(), c.Z()])

def hit_details(i):
    det = []
    for side in ('right', 'left'):
        name = f'Wire-{side}-{i + 1:02d}'
        w = wires[name]
        for oname, ow in wires.items():
            if oname == name: continue
            v = vol_pair(w, ow, wb[name], wb[oname], repair=True, sa=samp[name], sb=samp[oname])
            if v > F.HIT:
                cs = ar.common_shape(w, ow)
                det.append(('WW', oname, v, centroid(cs) if not cs.IsNull() else None))
        for bn, bs in bodies[17]:
            v = vol_pair(w, bs, wb[name], body_bnd[17][bn])
            if v > F.HIT:
                cs = ar.common_shape(w, bs)
                det.append(('WF', bn, v, centroid(cs) if not cs.IsNull() else None))
    return det

# ---------- candidates ----------
def chain_pts(Md, i):
    d = Md[str(i + 1)]
    return [(k, np.array(d[k], float)) for k in ('M1', 'M2', 'M3') if k in d]

def set_chain(Md, i, pts):
    M2 = json.loads(json.dumps(Md))
    M2[str(i + 1)] = {k: [round(float(x), 3) for x in p] for k, p in pts}
    return M2

def candidates(i):
    cur = chain_pts(M, i)
    b = BND.get(str(i + 1))
    if b:
        yield ('bnd-seed', set_chain(M, i, [(k, np.array(b[k], float))
                                            for k in ('M1', 'M2', 'M3') if k in b]))
    dets = sorted(hit_details(i), key=lambda d: -d[2])
    # coordinated shift moves (whole chain translated) from top hits
    shift_dirs = []
    for kind, other, v, C in dets[:5]:
        if C is None: continue
        bb = body_bnd[17][other] if kind == 'WF' else wb[other]
        Bc = (np.array(bb[0]) + np.array(bb[1])) / 2
        u = C - Bc; n = float(np.linalg.norm(u))
        if n > 1e-6: shift_dirs.append(u / n)
    shift_dirs += [np.array([0., 0., 1.]), np.array([0., 0., -1.]),
                   np.array([0., 1., 0.]), np.array([0., -1., 0.])]
    seen_s = set()
    for u in shift_dirs:
        for dlt in (4.5, 6.0, 3.0, 7.5):
            key = (tuple(np.round(u, 2)), dlt)
            if key in seen_s: continue
            seen_s.add(key)
            yield (f'shift-{dlt}-' + ','.join(str(round(x, 1)) for x in u),
                   set_chain(M, i, [(kk, pp + dlt * u) for kk, pp in cur]))
    for kind, other, v, C in dets:
        if C is None: continue
        bb = body_bnd[17][other] if kind == 'WF' else wb[other]
        Bc = (np.array(bb[0]) + np.array(bb[1])) / 2
        k, P = min(cur, key=lambda kp: float(np.linalg.norm(kp[1] - C)))
        dirs = []
        u = C - Bc; n = float(np.linalg.norm(u))
        if n > 1e-6: dirs.append(u / n)
        dirs += [np.array([0., 0., 1.]), np.array([0., 0., -1.])]
        u2 = P - Bc; n2 = float(np.linalg.norm(u2))
        if n2 > 1e-6: dirs.append(u2 / n2)
        seen = set()
        for u in dirs:
            for dlt in (3.0, 1.5, 0.75):
                key = (k, tuple(np.round(u, 2)), dlt)
                if key in seen: continue
                seen.add(key)
                yield (f'dir-{other[:16]}-{k}-{dlt}',
                       set_chain(M, i, [(kk, pp + dlt * u if kk == k else pp)
                                        for kk, pp in cur]))
    if len(cur) == 2:
        ptsR = F.points_of(M, i, 'right')
        P = np.array(ptsR[-3], float)
        M3 = (cur[1][1] + P) / 2
        yield ('m3-insert', set_chain(M, i, cur + [('M3', M3)]))
        for ax in range(3):
            for dlt in (2.0, -2.0):
                u = np.zeros(3); u[ax] = dlt
                yield (f'm3-pert-{ax}-{dlt}', set_chain(M, i, cur + [('M3', M3 + u)]))
    for scale in (1.25, 0.5):
        for k, P in cur:
            for ax in range(3):
                for sgn in (1, -1):
                    u = np.zeros(3); u[ax] = sgn * scale
                    yield (f'ax-{k}-{ax}{sgn}-{scale}',
                           set_chain(M, i, [(kk, pp + u if kk == k else pp)
                                            for kk, pp in cur]))

def build_design(Mcand, i):
    out = {}
    for side in ('right', 'left'):
        r, why = build_s(F.points_of(Mcand, i, side))
        if r is None: return None
        out[side] = r
    return out

def save():
    state['M'] = M
    json.dump(state, open(state_p, 'w'), indent=1)

# ---------- main (first-improvement) ----------
locals_cache = {}
for i in range(14):
    cw = {s: (wires[f'Wire-{s}-{i + 1:02d}'], samp[f'Wire-{s}-{i + 1:02d}'])
          for s in ('right', 'left')}
    locals_cache[i] = eval_design(i, cw)
log('locals', {i + 1: v[0] for i, v in locals_cache.items()},
    'total', sum(v[0] for v in locals_cache.values()))
order = sorted(range(14), key=lambda i: -locals_cache[i][0])
for i in order:
    if i in state['done_this_pass']: continue
    if time.time() - T0 > BUDGET:
        save(); log('budget exit mid-pass'); sys.exit(0)
    cur_cnt, cur_vol = locals_cache[i]
    if cur_cnt == 0:
        state['done_this_pass'].append(i); save(); continue
    accepted = None; evals = 0
    for label, Mcand in candidates(i):
        if evals >= 48 or time.time() - T0 > BUDGET: break
        cw = build_design(Mcand, i)
        if cw is None: continue
        evals += 1
        c, v = eval_design(i, cw)
        if (c < cur_cnt) or (c == cur_cnt and v < cur_vol * 0.98):
            accepted = (c, v, label, Mcand, cw); break
    if accepted:
        c, v, label, Mcand, cw = accepted
        M = Mcand
        for side in ('right', 'left'):
            nm = f'Wire-{side}-{i + 1:02d}'
            wires[nm] = cw[side][0]; samp[nm] = cw[side][1]; wb[nm] = F.bounds(cw[side][0])
        state['trajectory'].append({'pass': state['pass'], 'design': i + 1,
                                    'from': [cur_cnt, round(cur_vol, 2)],
                                    'to': [c, round(v, 2)], 'move': label,
                                    'evals': evals})
        locals_cache[i] = (c, v)
        log('ACCEPT design', i + 1, label, cur_cnt, '->', c,
            'vol', round(cur_vol, 1), '->', round(v, 1), 'evals', evals)
    else:
        log('no-improve design', i + 1, 'count', cur_cnt, 'evals', evals)
    state['done_this_pass'].append(i)
    save()
if len(state['done_this_pass']) >= 14:
    state['pass'] += 1; state['done_this_pass'] = []
    save(); log('PASS', state['pass'] - 1, 'COMPLETE')
log('done chunk')
