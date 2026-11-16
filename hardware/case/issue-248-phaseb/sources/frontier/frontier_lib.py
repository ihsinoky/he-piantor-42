"""Frontier-study shared machinery: per-strand fitted repair
(round-18 method), bulge slack build (round-18 method + downward
direction), gate-3 Part A extraction arithmetic (round-18 method) -
all against height-parameterised bodies/points from fitlibF."""
import json, sys, time
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, PB)
sys.path.insert(0, f'{PB}/sources/round18')
sys.path.insert(0, f'{PB}/sources/frontier')
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R

build_s = R.build_s
vol_pair = R.vol_pair
eval_wire = R.eval_wire


def build_all_wires(M):
    wires, samp, wb, lens = {}, {}, {}, {}
    for side in ('right', 'left'):
        for pin in range(1, 15):
            r, why = build_s(FF.points_of(M, pin - 1, side))
            if r is None:
                return None, why
            nm = f'Wire-{side}-{pin:02d}'
            wires[nm] = r[0]; samp[nm] = r[1]; wb[nm] = F.bounds(r[0])
    return (wires, samp, wb), None


def full_score(M, bodies):
    """Gate-1 full score via fitlib18 Scorer. Returns dict or None."""
    wires, lens, failed = {}, {}, []
    for side in ('right', 'left'):
        for pin in range(1, 15):
            w, r = FF.build_wire(FF.points_of(M, pin - 1, side))
            if w is None:
                failed.append((side, pin, r)); continue
            nm = f'Wire-{side}-{pin:02d}'
            wires[nm] = w; lens[nm] = round(r + 7.30, 2)
    if failed:
        return {'failed': failed}
    sc = FF.Scorer(wires, bodies)
    ww, wf = sc.full()
    return {'ww': ww, 'wf': {str(p): wf[p] for p in wf}, 'lens': lens,
            'gate1_17': len(ww) + len(wf[17]), 'gate1_16': len(ww) + len(wf[16]),
            'ww_count': len(ww), 'wf_17': len(wf[17]), 'wf_16': len(wf[16]),
            'longest': max(lens.values()),
            'vol_sum': round(sum(ww.values()) + sum(sum(v.values()) for v in wf.values()), 2)}


class Repair:
    """Round-18 per-strand Gauss-Seidel fitted repair, parameterised
    by bodies (both pitches) and the height-set fitlibF points."""

    def __init__(self, M, bodies):
        self.M = M
        self.bodies = bodies
        self.body_bnd = {p: {n: F.bounds(s) for n, s in bl}
                         for p, bl in bodies.items()}
        res, why = build_all_wires(M)
        assert res is not None, why
        self.wires, self.samp, self.wb = res
        self.locals = {}
        for i in range(14):
            self.locals[i] = self.eval_design(i, self._cand_of(i))

    def _cand_of(self, i):
        return {s: (self.wires[f'Wire-{s}-{i + 1:02d}'],
                    self.samp[f'Wire-{s}-{i + 1:02d}'])
                for s in ('right', 'left')}

    def eval_design(self, i, cand):
        cnt, vol = 0, 0.0
        for side in ('right', 'left'):
            name = f'Wire-{side}-{i + 1:02d}'
            w, sm = cand[side]; wbnd = F.bounds(w)
            for oname, ow in self.wires.items():
                if oname == name: continue
                v = vol_pair(w, ow, wbnd, self.wb[oname], repair=True,
                             sa=sm, sb=self.samp[oname])
                if v > F.HIT: cnt += 2; vol += 2 * v
            for p in (17, 16):
                for bn, bs in self.bodies[p]:
                    v = vol_pair(w, bs, wbnd, self.body_bnd[p][bn])
                    if v > F.HIT: cnt += 1; vol += v
        return cnt, vol

    def hit_details(self, i):
        from OCP.BRepGProp import BRepGProp
        from OCP.GProp import GProp_GProps
        import audit_repair as ar
        def centroid(shape):
            props = GProp_GProps()
            BRepGProp.VolumeProperties_s(shape, props, True, False, False)
            c = props.CentreOfMass(); return np.array([c.X(), c.Y(), c.Z()])
        det = []
        for side in ('right', 'left'):
            name = f'Wire-{side}-{i + 1:02d}'
            w = self.wires[name]
            for oname, ow in self.wires.items():
                if oname == name: continue
                v = vol_pair(w, ow, self.wb[name], self.wb[oname],
                             repair=True, sa=self.samp[name], sb=self.samp[oname])
                if v > F.HIT:
                    cs = ar.common_shape(w, ow)
                    det.append(('WW', oname, v,
                                centroid(cs) if not cs.IsNull() else None))
            for bn, bs in self.bodies[17]:
                v = vol_pair(w, bs, self.wb[name], self.body_bnd[17][bn])
                if v > F.HIT:
                    cs = ar.common_shape(w, bs)
                    det.append(('WF', bn, v,
                                centroid(cs) if not cs.IsNull() else None))
        return det

    @staticmethod
    def chain_pts(Md, i):
        d = Md[str(i + 1)]
        return [(k, np.array(d[k], float)) for k in ('M1', 'M2', 'M3') if k in d]

    @staticmethod
    def set_chain(Md, i, pts):
        M2 = json.loads(json.dumps(Md))
        M2[str(i + 1)] = {k: [round(float(x), 3) for x in p] for k, p in pts}
        return M2

    def candidates(self, i):
        M = self.M
        cur = self.chain_pts(M, i)
        dets = sorted(self.hit_details(i), key=lambda d: -d[2])
        shift_dirs = []
        for kind, other, v, C in dets[:5]:
            if C is None: continue
            bb = self.body_bnd[17][other] if kind == 'WF' else self.wb[other]
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
                       self.set_chain(M, i, [(kk, pp + dlt * u) for kk, pp in cur]))
        for kind, other, v, C in dets:
            if C is None: continue
            bb = self.body_bnd[17][other] if kind == 'WF' else self.wb[other]
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
                           self.set_chain(M, i, [(kk, pp + dlt * u if kk == k else pp)
                                                 for kk, pp in cur]))
        if len(cur) == 2:
            ptsR = FF.points_of(M, i, 'right')
            P = np.array(ptsR[-3], float)
            M3 = (cur[1][1] + P) / 2
            yield ('m3-insert', self.set_chain(M, i, cur + [('M3', M3)]))
            for ax in range(3):
                for dlt in (2.0, -2.0):
                    u = np.zeros(3); u[ax] = dlt
                    yield (f'm3-pert-{ax}-{dlt}',
                           self.set_chain(M, i, cur + [('M3', M3 + u)]))
        for scale in (1.25, 0.5):
            for k, P in cur:
                for ax in range(3):
                    for sgn in (1, -1):
                        u = np.zeros(3); u[ax] = sgn * scale
                        yield (f'ax-{k}-{ax}{sgn}-{scale}',
                               self.set_chain(M, i, [(kk, pp + u if kk == k else pp)
                                                     for kk, pp in cur]))

    def build_design(self, Mcand, i):
        out = {}
        for side in ('right', 'left'):
            r, why = build_s(FF.points_of(Mcand, i, side))
            if r is None: return None
            out[side] = r
        return out

    def run_pass(self, budget_s=900, eval_cap=40, log=print):
        T0 = time.time()
        traj = []
        order = sorted(range(14), key=lambda i: -self.locals[i][0])
        for i in order:
            if time.time() - T0 > budget_s:
                log('pass budget exit at design', i + 1); break
            cur_cnt, cur_vol = self.locals[i]
            if cur_cnt == 0: continue
            accepted = None; evals = 0
            for label, Mcand in self.candidates(i):
                if evals >= eval_cap or time.time() - T0 > budget_s: break
                cw = self.build_design(Mcand, i)
                if cw is None: continue
                evals += 1
                c, v = self.eval_design(i, cw)
                if (c < cur_cnt) or (c == cur_cnt and v < cur_vol * 0.98):
                    accepted = (c, v, label, Mcand, cw); break
            if accepted:
                c, v, label, Mcand, cw = accepted
                self.M = Mcand
                for side in ('right', 'left'):
                    nm = f'Wire-{side}-{i + 1:02d}'
                    self.wires[nm] = cw[side][0]; self.samp[nm] = cw[side][1]
                    self.wb[nm] = F.bounds(cw[side][0])
                self.locals[i] = (c, v)
                traj.append({'design': i + 1, 'from': cur_cnt, 'to': c,
                             'move': label, 'evals': evals})
                log('ACCEPT', i + 1, label, cur_cnt, '->', c)
            else:
                log('no-improve', i + 1, 'count', cur_cnt, 'evals', evals)
        return traj


# ---------------- slack (round-18 bulge + downward direction) ---------------

def _unit(v):
    v = np.array(v, float); return v / np.linalg.norm(v)


def _perp_h(t, direction):
    n = np.array([t[1], -t[0], 0.]); n = n / np.linalg.norm(n)
    if direction == 'W' and n[0] > 0: n = -n
    if direction == 'E' and n[0] < 0: n = -n
    return n


def stored_points(M, i, side, direction, d_host, d_climb=0.0):
    pts = FF.points_of(M, i, 'right')
    B0, B1, COR, RISE = [np.array(p, float) for p in pts[:4]]
    rest = pts[4:]
    t_in = _unit(COR - B1); t_out = _unit(RISE - COR)
    if direction == 'U':
        n = np.array([0., 0., 1.]); n2 = n
    elif direction == 'D':
        n = np.array([0., 0., -1.]); n2 = n
    else:
        n = _perp_h(t_in, direction); n2 = _perp_h(t_out, direction)
    Pa = B1 + 0.25 * (COR - B1) + d_host * n
    Pb = B1 + 0.75 * (COR - B1) + d_host * n
    out = [B0, B1, Pa, Pb, COR]
    if d_climb > 0:
        out.append(COR + 0.5 * (RISE - COR) + d_climb * n2)
    out.append(RISE)
    out += [np.array(p, float) for p in rest]
    out = [list(map(float, p)) for p in out]
    if side == 'left':
        out = [[-p[0], p[1], p[2]] for p in out]
    return out


def _build_len(pts):
    w, r = FF.build_wire(pts)
    return r if w is not None else None


def solve_d(M, i, taut_len, direction, target, depths=(20., 16., 13., 10.5, 9., 7.5, 6., 4.5, 3., 1.5)):
    def delta(dh, dc):
        L = _build_len(stored_points(M, i, 'right', direction, dh, dc))
        return None if L is None else L - taut_len
    dh_max = None
    for cand in depths:
        if delta(cand, 0.0) is not None:
            dh_max = cand; break
    if dh_max is None: return None, None, None
    top = delta(dh_max, 0.0)
    if top >= target:
        lo, hi = 0.0, dh_max
        for _ in range(7):
            mid = (lo + hi) / 2
            dl = delta(mid, 0.0)
            if dl is None: hi = mid; continue
            if dl < target: lo = mid
            else: hi = mid
        dh = (lo + hi) / 2
        return dh, 0.0, delta(dh, 0.0)
    dh = dh_max
    top2 = delta(dh, 3.0)
    if top2 is None or top2 <= top:
        return dh, 0.0, top
    if top2 >= target:
        lo, hi = 0.0, 3.0
        for _ in range(6):
            mid = (lo + hi) / 2
            dl = delta(dh, mid)
            if dl is None: hi = mid; continue
            if dl < target: lo = mid
            else: hi = mid
        dc = (lo + hi) / 2
        return dh, dc, delta(dh, dc)
    return dh, 3.0, top2


def slack_build(M, bodies, target=30.2, budget_s=900, log=print):
    """Round-18 stage A+B: per-strand direction/depth plan toward
    `target`, then incremental fitted assembly. Returns (rec, wires)
    with rec[strand] = {dir, d, delta_right, len_right, points_*}."""
    T0 = time.time()
    body_bnd = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
    taut_len = {}
    for i in range(14):
        L = _build_len(FF.points_of(M, i, 'right'))
        assert L is not None
        taut_len[i] = L
    plan = {}
    for i in range(14):
        plan[i] = {}
        for dr in ('W', 'E', 'U', 'D'):
            dh, dc, dl = solve_d(M, i, taut_len[i], dr, target)
            plan[i][dr] = (dh, dc, None if dl is None else round(dl, 2))
        log('slack plan strand', i + 1, plan[i])
        if time.time() - T0 > budget_s:
            log('slack budget exit in plan'); break
    wires, samp, wb = {}, {}, {}
    for side in ('right', 'left'):
        for pin in range(1, 15):
            r, why = build_s(FF.points_of(M, pin - 1, side))
            assert r is not None, (side, pin, why)
            nm = f'Wire-{side}-{pin:02d}'
            wires[nm] = r[0]; samp[nm] = r[1]; wb[nm] = F.bounds(r[0])
    rec = {}
    chosen = {}
    for i in range(14):
        best = None
        order = sorted(('W', 'E', 'U', 'D'),
                       key=lambda dr: -(plan[i][dr][2] if plan[i][dr][2] is not None else -1))
        for dr in order:
            dh0, dc0, dl0 = plan[i][dr]
            if dh0 is None: continue
            cand = {}; ok = True
            for side in ('right', 'left'):
                r, why = build_s(stored_points(M, i, side, dr, dh0, dc0))
                if r is None: ok = False; break
                cand[side] = r
            if not ok: continue
            tot_c, tot_v = 0, 0.0
            for side in ('right', 'left'):
                nm = f'Wire-{side}-{i + 1:02d}'
                c, v, _ = eval_wire(nm, cand[side][0], cand[side][1],
                                    wires, samp, wb, bodies, body_bnd)
                tot_c += c; tot_v += v
            dlv = dl0 if dl0 is not None else -1
            if best is None or (tot_c, tot_v) < (best[0], best[1]):
                best = (tot_c, tot_v, dr, (dh0, dc0), cand, dlv)
        if best is None:
            chosen[i] = ('TAUT', 0.0, 0.0)
            continue
        tot_c, tot_v, dr, (dh, dc), cand, dlv = best
        for side in ('right', 'left'):
            nm = f'Wire-{side}-{i + 1:02d}'
            wires[nm] = cand[side][0]; samp[nm] = cand[side][1]
            wb[nm] = F.bounds(cand[side][0])
        chosen[i] = (dr, dh, dc)
        log('slack strand', i + 1, dr, dh, dc, 'delta', dlv, 'local', tot_c)
        if time.time() - T0 > budget_s:
            log('slack budget exit in assembly'); break
    for i in range(14):
        if i not in chosen:
            chosen[i] = ('TAUT', 0.0, 0.0)
        dr, dh, dc = chosen[i]
        r = {'dir': dr, 'd': [dh, dc]}
        for side in ('right', 'left'):
            pts = (FF.points_of(M, i, side) if dr == 'TAUT'
                   else stored_points(M, i, side, dr, dh, dc))
            w, L = FF.build_wire(pts)
            r[f'points_{side}'] = pts
            r[f'len_{side}'] = round(L, 3)
        r['delta_right'] = round(r['len_right'] - taut_len[i], 3)
        r['finished_right'] = round(r['len_right'] + 7.30, 2)
        rec[str(i + 1)] = r
    return rec, wires


# ---------------- gate 3 Part A (round-18 arithmetic) ----------------------

def _state_points(M, i, direction, dh, dc, s):
    pts = FF.points_of(M, i, 'right')
    B0, B1, COR, RISE = [np.array(p, float) for p in pts[:4]]
    rest = pts[4:]
    B0 = B0 + np.array([0., -s, 0.]); B1 = B1 + np.array([0., -s, 0.])
    t_in = _unit(COR - B1); t_out = _unit(RISE - COR)
    if direction == 'U':
        n = np.array([0., 0., 1.]); n2 = n
    elif direction == 'D':
        n = np.array([0., 0., -1.]); n2 = n
    elif direction == 'TAUT':
        n = np.zeros(3); n2 = n
    else:
        n = _perp_h(t_in, direction); n2 = _perp_h(t_out, direction)
    if dh > 0.05:
        Pa = B1 + 0.25 * (COR - B1) + dh * n
        Pb = B1 + 0.75 * (COR - B1) + dh * n
        out = [B0, B1, Pa, Pb, COR]
    else:
        out = [B0, B1, COR]
    if dc > 0:
        out.append(COR + 0.5 * (RISE - COR) + dc * n2)
    out.append(RISE)
    out += [np.array(p, float) for p in rest]
    return [list(map(float, p)) for p in out]


def extraction_partA(M, rec):
    out = {}
    for k, r in rec.items():
        i = int(k) - 1
        dr = r['dir']; dh0, dc = r['d']
        L_st = r['len_right']  # path length without tails (round-18 convention)
        def plen(dh_, s_):
            try:
                w, L = FF.build_wire(_state_points(M, i, dr, dh_, dc, s_))
            except Exception:
                return None
            return None if w is None else L
        L60 = plen(0.0, 6.0)
        shortfall = None if L60 is None else round(max(0.0, L60 - L_st), 2)
        def feas(s_):
            L = plen(0.0, s_)
            return L is not None and L <= L_st + 1e-9
        if feas(6.0):
            s_max = 6.0
        elif not feas(0.0):
            s_max = 0.0
        else:
            lo, hi = 0.0, 6.0
            for _ in range(6):
                mid = (lo + hi) / 2
                if feas(mid): lo = mid
                else: hi = mid
            s_max = round(lo, 2)
        out[k] = {'dir': dr, 'delta': r['delta_right'], 's_max': s_max,
                  'shortfall_at_6mm': shortfall}
    return out
