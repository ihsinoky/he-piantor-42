"""Issue #252 gate 3: carrier service qualification.
Steps (both pitches where bodies differ; wires are pitch-independent):
 1 shells-off: shells translated +Z {2,5,10,25} vs wires + envelopes
 2 unplug W pair: SegW tail points (AP,TW) translated -X*s (right) /
   +X*s (left), s in {3,6}: rebuild, length must not grow >0.05,
   contacts vs all fixed bodies + other wires (fitted state)
 3 unplug M pair: SegM tail points (TM, AP_M) translated +Y*s,
   s in {3,6}: same checks
 4 Wing lift-out (W unplugged): Wing group bodies + SegW wires
   translated +Z {5,20} vs remaining assembly
 5 Main segment removal: SegM wires translated +Z {5,20} after
   step 3 state vs remaining assembly
Contacts counted with the repaired audit standard (vol_pair)."""
import json, sys, time
import numpy as np
sys.path.insert(0, '.')
import fitlib252 as C
import fitlib18 as F
import repair18_lib as R
import routes_round17 as rr
import repair252 as RP  # applies the fast-bounds patch

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'design_state.json'))
bodies = C.all_bodies()
wires, lens, failed = C.build_all(D)
assert not failed, failed
solids = {n: r[0] for n, r in wires.items()}
samp = {n: r[1] for n, r in wires.items()}
wb = {n: F.bounds(s) for n, s in solids.items()}
bb = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
log('wires built', len(solids))

def vol(a, b, ab, bbnd, sa=None, sb=None):
    return RP.SegRepair._vol_fast(a, b, ab, bbnd, sa, sb) if sa is not None else \
        R.vol_pair(a, b, ab, bbnd)

def hits_moved(moved, fixed_solids, fixed_samp, pitch_bodies):
    """moved: {name: (solid, samp)}; returns hit list."""
    hits = []
    for nm, (s, sm) in moved.items():
        sb_ = F.bounds(s)
        for onm, os_ in fixed_solids.items():
            if onm in moved: continue
            v = vol(s, os_, sb_, wb.get(onm, F.bounds(os_)), sm, fixed_samp.get(onm))
            if v > F.HIT: hits.append((nm, onm, round(v, 3)))
        for bn, bs in pitch_bodies:
            dmin, h = RP.SegRepair._near(sm, bb[17][bn] if bn in bb[17] else F.bounds(bs))
            if dmin > 1.0 + h / 2 * 1.05 + 0.05: continue
            v = R.vol_pair(s, bs, sb_, F.bounds(bs))
            if v > F.HIT: hits.append((nm, bn, round(v, 3)))
    return hits

def translate_solid(s, dx, dy, dz):
    from build123d import Pos
    return Pos(dx, dy, dz) * s

res = {}
# ---- step 1: shells off ----
shell_names = {'shell-central', 'strip-left', 'strip-right'}
for p in (17, 16):
    bl = dict(bodies[p])
    bad = []
    for dz in (2, 5, 10, 25):
        moved = {n: (translate_solid(bl[n], 0, 0, dz), None) for n in shell_names if n in bl}
        # shells vs wires + switch envelopes (bodies that stay)
        stay = {n: s for n, s in bl.items() if n not in shell_names}
        hits = []
        for nm, (s, _) in moved.items():
            for wn, ws in solids.items():
                v = R.vol_pair(s, ws, F.bounds(s), wb[wn])
                if v > F.HIT: hits.append((nm, wn, round(v, 3)))
            for bn, bs in stay.items():
                if not bn.startswith('switch-envelope'): continue
                v = R.vol_pair(s, bs, F.bounds(s), F.bounds(bs))
                if v > F.HIT: hits.append((nm, bn, round(v, 3)))
        bad.append((dz, len(hits), hits[:4]))
    res[f'shells_off_{p}'] = bad
    log('shells off', p, bad)

# ---- steps 2/3: unplug motions ----
def seg_pts_moved(seg, side, i, ds):
    wp, mp = C.seg_points(D, i, side)
    pts = [list(p) for p in (wp if seg == 'SegW' else mp)]
    if seg == 'SegW':
        sgn = -1.0 if side == 'right' else 1.0
        for j in (-2, -1): pts[j][0] += sgn * ds
    else:
        for j in (0, 1): pts[j][1] += ds
    return pts

for seg, tag in (('SegW', 'unplugW'), ('SegM', 'unplugM')):
    for ds in (3.0, 6.0):
        allhits = []; lenok = True; builds = True
        for side in ('right', 'left'):
            for i in range(14):
                nm = C.wire_name(seg, side, i)
                pts = seg_pts_moved(seg, side, i, ds)
                r, why = R.build_s(rr.split_corners(pts))
                if r is None: builds = False; continue
                w2, L2 = F.build_wire(pts)
                orig = lens[nm] - (7.30 if seg == 'SegW' else 6.80)
                if L2 > orig + 0.05: lenok = False
                moved = {nm: (r[0], r[1])}
                hits = hits_moved(moved, solids, samp, bodies[17])
                allhits += [(nm, h) for h in hits if h[1] != nm]
        res[f'{tag}_{ds}'] = {'hits': len(allhits), 'lenok': lenok, 'builds': builds,
                              'sample': allhits[:5]}
        log(tag, ds, res[f'{tag}_{ds}'])

# ---- step 4: Wing lift-out (right + left), W unplugged state ----
for side in ('right', 'left'):
    wing_bodies = {n: s for n, s in dict(bodies[17]).items()
                   if n in (f'wing_{side}', f'plate-{side}') or n.startswith(f'switch-envelope-{"R" if side == "right" else "L"}_')}
    segw = {C.wire_name('SegW', side, i): (solids[C.wire_name('SegW', side, i)], samp[C.wire_name('SegW', side, i)]) for i in range(14)}
    for dz in (5, 20):
        moved = {n: (translate_solid(s, 0, 0, dz), sm) for n, (s, sm) in
                 list(segw.items())}
        moved_b = {n: translate_solid(s, 0, 0, dz) for n, s in wing_bodies.items()}
        hits = []
        for nm, (s, sm) in moved.items():
            for onm, os_ in solids.items():
                if onm in moved: continue
                v = vol(s, os_, F.bounds(s), wb[onm], sm, samp[onm])
                if v > F.HIT: hits.append((nm, onm, round(v, 3)))
        for nm, s in moved_b.items():
            for bn, bs in bodies[17]:
                if bn in moved_b: continue
                v = R.vol_pair(s, bs, F.bounds(s), F.bounds(bs))
                if v > F.HIT: hits.append((nm, bn, round(v, 3)))
        res[f'liftout_{side}_{dz}'] = len(hits)
        log('liftout', side, dz, len(hits), hits[:3])

# ---- step 5: Main segment removal (+Z after unplug) ----
for side in ('right', 'left'):
    for dz in (5, 20):
        hits = []
        for i in range(14):
            nm = C.wire_name('SegM', side, i)
            s = translate_solid(solids[nm], 0, 0, dz)
            for onm, os_ in solids.items():
                if onm == nm: continue
                v = vol(s, os_, F.bounds(s), wb[onm], samp[nm], samp[onm])
                if v > F.HIT: hits.append((nm, onm, round(v, 3)))
            for bn, bs in bodies[17]:
                v = R.vol_pair(s, bs, F.bounds(s), bb[17][bn])
                if v > F.HIT: hits.append((nm, bn, round(v, 3)))
        res[f'segm_remove_{side}_{dz}'] = len(hits)
        log('segm remove', side, dz, len(hits), hits[:3])

json.dump(res, open('gate3_results.json', 'w'), indent=1, default=str)
log('DONE')
