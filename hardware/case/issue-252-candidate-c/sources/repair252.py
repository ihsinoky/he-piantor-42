"""Issue #252 per-SEGMENT fitted repair (frontier method adapted).
Unit = one segment (SegW or SegM) of one strand, both sides (2 wires).
Free points: W list (SegW) / N list (SegM), right-side design frame;
left mirrors. Acceptance: local fitted count (WW x2 + WF17 + WF16,
frontier convention) strictly down, else >=2% volume down."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-midconn/.issue252-runtime')
import fitlib252 as C
import fitlib18 as F
import repair18_lib as R
import routes_round17 as rr

# Speed: build123d's default bounding_box() is the OPTIMAL box
# (BRepBndLib.AddOptimal, ~33 ms/call) and common.volume() calls it
# twice per pair check. Switch this process to the fast tessellation
# box: it is conservative (never smaller), so every early-out and
# partition built on it stays sound; exact Common still decides.
from build123d import Shape as _Shape
_orig_bb = _Shape.bounding_box
def _fast_bb(self, mode=1):
    return _orig_bb(self, mode)
_Shape.bounding_box = _fast_bb

HIT = F.HIT

class SegRepair:
    def __init__(self, D, bodies):
        self.D = D
        self.bodies = bodies
        self.body_bnd = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
        self.wires = {}
        self.wb = {}
        self._build_all()
        self.locals = {}
        import time as _t
        for seg in ('SegW', 'SegM'):
            for i in range(14):
                _t0 = _t.time()
                self.locals[(seg, i)] = self.eval_unit(seg, i, self._cand_of(seg, i))
                print(f'init {seg} {i + 1}: {self.locals[(seg, i)]} in {_t.time() - _t0:.1f}s', flush=True)

    @staticmethod
    def _bw(pts):
        return R.build_s(rr.split_corners(pts))

    def _build_all(self):
        for side in ('right', 'left'):
            for i in range(14):
                wp, mp = C.seg_points(self.D, i, side)
                for seg, pts in (('SegW', wp), ('SegM', mp)):
                    nm = C.wire_name(seg, side, i)
                    r, why = self._bw(pts)
                    assert r is not None, (nm, why)
                    self.wires[nm] = r
                    self.wb[nm] = F.bounds(r[0])

    @staticmethod
    def _unit_names(seg, i):
        return [C.wire_name(seg, side, i) for side in ('right', 'left')]

    def _cand_of(self, seg, i):
        return {nm: self.wires[nm] for nm in self._unit_names(seg, i)}

    @staticmethod
    def _near(samples, bnd):
        A, h = samples
        lo = np.array(bnd[0]); hi = np.array(bnd[1])
        d = np.maximum(np.maximum(lo - A, A - hi), 0.0)
        return float(np.sqrt((d * d).sum(axis=1)).min()), h

    @staticmethod
    def _vol_fast(w, ow, wbnd, obnd, sm, osm):
        if sm is not None and osm is not None:
            if R.min_pp(sm[0], osm[0]) > 1.01: return 0.0
        return R.vol_pair(w, ow, wbnd, obnd, repair=True, sa=sm, sb=osm)

    def eval_unit(self, seg, i, cand):
        cnt, vol = 0, 0.0
        mine = set(self._unit_names(seg, i))
        for nm, (w, sm) in cand.items():
            wbnd = F.bounds(w)
            for oname, (ow, osm) in self.wires.items():
                if oname in mine: continue
                v = self._vol_fast(w, ow, wbnd, self.wb[oname], sm, osm)
                if v > HIT: cnt += 2; vol += 2 * v
            for p in (17, 16):
                for bn, bs in self.bodies[p]:
                    dmin, h = self._near(sm, self.body_bnd[p][bn])
                    if dmin > 1.0 + h / 2 * 1.05 + 0.05: continue
                    v = R.vol_pair(w, bs, wbnd, self.body_bnd[p][bn])
                    if v > HIT: cnt += 1; vol += v
        (wa, sa), (wb2, sb) = cand[self._unit_names(seg, i)[0]], cand[self._unit_names(seg, i)[1]]
        v = self._vol_fast(wa, wb2, F.bounds(wa), F.bounds(wb2), sa, sb)
        if v > HIT: cnt += 2; vol += 2 * v
        return cnt, vol

    @staticmethod
    def _closest_pt(sa, sb):
        A, B = sa[0], sb[0]
        d2 = ((A[:, None, :] - B[None, :, :]) ** 2).sum(axis=2)
        ia, ib = np.unravel_index(np.argmin(d2), d2.shape)
        return (A[ia] + B[ib]) / 2

    def hit_details(self, seg, i):
        det = []
        mine = set(self._unit_names(seg, i))
        for nm in self._unit_names(seg, i):
            w, sm = self.wires[nm]
            for oname, (ow, osm) in self.wires.items():
                if oname in mine: continue
                v = self._vol_fast(w, ow, self.wb[nm], self.wb[oname], sm, osm)
                if v > HIT: det.append(('WW', oname, v, self._closest_pt(sm, osm)))
            for bn, bs in self.bodies[17]:
                dmin, h = self._near(sm, self.body_bnd[17][bn])
                if dmin > 1.0 + h / 2 * 1.05 + 0.05: continue
                v = R.vol_pair(w, bs, self.wb[nm], self.body_bnd[17][bn])
                if v > HIT:
                    A = sm[0]
                    lo = np.array(self.body_bnd[17][bn][0]); hi = np.array(self.body_bnd[17][bn][1])
                    dd = np.maximum(np.maximum(lo - A, A - hi), 0.0)
                    det.append(('WF', bn, v, A[int(np.argmin((dd * dd).sum(axis=1)))]))
        return det

    # ---- design manipulation ----
    @staticmethod
    def free_pts(D, seg, i):
        key = 'W' if seg == 'SegW' else 'N'
        return [(j, np.array(p, float)) for j, p in enumerate(D[str(i + 1)][key])]

    @staticmethod
    def set_pts(D, seg, i, pts):
        D2 = json.loads(json.dumps(D))
        key = 'W' if seg == 'SegW' else 'N'
        D2[str(i + 1)][key] = [[round(float(x), 3) for x in p] for j, p in sorted(pts)]
        return D2

    def candidates(self, seg, i):
        D = self.D
        cur = self.free_pts(D, seg, i)
        dets = sorted(self.hit_details(seg, i), key=lambda d: -d[2])
        shift_dirs = []
        for kind, other, v, Cc in dets[:5]:
            if Cc is None: continue
            bb = self.body_bnd[17][other] if kind == 'WF' else self.wb[other]
            Bc = (np.array(bb[0]) + np.array(bb[1])) / 2
            u = Cc - Bc; n = float(np.linalg.norm(u))
            if n > 1e-6: shift_dirs.append(u / n)
        shift_dirs += [np.array([0., 0., 1.]), np.array([0., 0., -1.]),
                       np.array([0., 1., 0.]), np.array([0., -1., 0.]),
                       np.array([1., 0., 0.]), np.array([-1., 0., 0.])]
        seen = set()
        for u in shift_dirs:
            for dlt in (4.5, 6.0, 3.0, 7.5):
                key = (tuple(np.round(u, 2)), dlt)
                if key in seen: continue
                seen.add(key)
                yield (f'shift-{dlt}', self.set_pts(D, seg, i, [(j, p + dlt * u) for j, p in cur]))
        for kind, other, v, Cc in dets:
            if Cc is None: continue
            bb = self.body_bnd[17][other] if kind == 'WF' else self.wb[other]
            Bc = (np.array(bb[0]) + np.array(bb[1])) / 2
            j, P = min(cur, key=lambda jp: float(np.linalg.norm(jp[1] - Cc)))
            dirs = []
            u = Cc - Bc; n = float(np.linalg.norm(u))
            if n > 1e-6: dirs.append(u / n)
            dirs += [np.array([0., 0., 1.]), np.array([0., 0., -1.])]
            u2 = P - Bc; n2 = float(np.linalg.norm(u2))
            if n2 > 1e-6: dirs.append(u2 / n2)
            seen2 = set()
            for u in dirs:
                for dlt in (3.0, 1.5, 0.75):
                    key = (j, tuple(np.round(u, 2)), dlt)
                    if key in seen2: continue
                    seen2.add(key)
                    yield (f'dir-{other[:14]}-{j}-{dlt}',
                           self.set_pts(D, seg, i, [(jj, p + dlt * u if jj == j else p)
                                                    for jj, p in cur]))
        d = D[str(i + 1)]
        if seg == 'SegW' and len(d['W']) < 5:
            wp, _ = C.seg_points(D, i, 'right')
            apW = np.array(wp[-2], float)
            mid = (np.array(d['W'][-1], float) + apW) / 2
            yield ('wins-insert', self.set_pts(D, seg, i, cur + [(len(d['W']), mid)]))
        if seg == 'SegM' and len(d['N']) < 3:
            _, mp = C.seg_points(D, i, 'right')
            P = np.array(mp[-3], float)
            mid = (np.array(d['N'][-1], float) + P) / 2
            yield ('nins-insert', self.set_pts(D, seg, i, cur + [(len(d['N']), mid)]))
        for scale in (1.25, 0.5):
            for j, P in cur:
                for ax in range(3):
                    for sgn in (1, -1):
                        u = np.zeros(3); u[ax] = sgn * scale
                        yield (f'ax-{j}-{ax}{sgn}-{scale}',
                               self.set_pts(D, seg, i, [(jj, p + u if jj == j else p)
                                                        for jj, p in cur]))

    def build_unit(self, Dcand, seg, i):
        out = {}
        for side in ('right', 'left'):
            wp, mp = C.seg_points(Dcand, i, side)
            pts = wp if seg == 'SegW' else mp
            r, why = self._bw(pts)
            if r is None: return None
            out[C.wire_name(seg, side, i)] = r
        return out

    def run_pass(self, budget_s=900, eval_cap=40, log=print):
        T0 = time.time(); traj = []
        units = [(seg, i) for seg in ('SegW', 'SegM') for i in range(14)]
        order = sorted(units, key=lambda u: -self.locals[u][0])
        for seg, i in order:
            if time.time() - T0 > budget_s: break
            cur_cnt, cur_vol = self.locals[(seg, i)]
            if cur_cnt == 0: continue
            evals = 0; improved = False
            for tag, Dcand in self.candidates(seg, i):
                if evals >= eval_cap or time.time() - T0 > budget_s: break
                cand = self.build_unit(Dcand, seg, i)
                if cand is None: continue
                evals += 1
                cnt, vol = self.eval_unit(seg, i, cand)
                if cnt < cur_cnt or (cnt == cur_cnt and vol < 0.98 * cur_vol):
                    self.D = Dcand
                    for nm, r in cand.items():
                        self.wires[nm] = r; self.wb[nm] = F.bounds(r[0])
                    self.locals[(seg, i)] = (cnt, vol)
                    traj.append((seg, i + 1, tag, cur_cnt, cnt, round(cur_vol, 2), round(vol, 2)))
                    log(f'  {seg} {i + 1}: {tag} -> count {cnt} vol {vol:.2f}', flush=True)
                    cur_cnt, cur_vol = cnt, vol; improved = True
                    break
            if not improved:
                traj.append((seg, i + 1, 'no-improve', cur_cnt, cur_cnt, round(cur_vol, 2), round(cur_vol, 2)))
        return traj
