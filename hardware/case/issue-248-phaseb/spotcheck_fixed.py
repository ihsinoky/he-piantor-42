"""Round-10 spot check: does the Common blind spot also affect pairs
involving fixed bodies? For the round-9 assemblies, every zero-volume
exact pair that involves a wire or the Fly cable (the long swept solids
of the blind-spot class) is re-resolved with the distance fallback, and
so is a sample of fixed-fixed zero pairs (largest AABB overlaps first).
Usage: spotcheck_fixed.py <pitch>. Chunked like audit_repair.py;
progress in .issue248-runtime/round10/."""
from common import *
from audit_repair import solid_distance, clipped_common_volume, load_round9, DIST_CLEAR

R10 = ROOT / '.issue248-runtime' / 'round10'

def aabb_overlap_volume(ab, bb):
    v = 1.
    for d in range(3):
        o = min(ab[1][d], bb[1][d]) - max(ab[0][d], bb[0][d])
        if o <= 0: return 0.
        v *= o
    return v

def spotcheck(pitch):
    base = HERE / f'{pitch}mm'
    audit = read(base / 'audit.json')
    idx = read(base / 'assembly-index.json')
    names = {i: r['name'] for i, r in enumerate(idx)}
    bnds = {r['name']: r['bounds'] for r in idx}
    geo_hash = sha(base / 'assembly-index.json')
    assert audit['geometry_sha256'] == geo_hash
    sel = {}
    fixed_sample = []
    for r in audit['exact_results']:
        if r.get('volume_mm3', 0.) > 1e-6: continue
        a, b = names[r['i']], names[r['j']]
        wa, wb = a.startswith('Wire-'), b.startswith('Wire-')
        if wa != wb or a == 'Fly-170mm' or b == 'Fly-170mm':
            sel[(a, b)] = 'wire-or-fly'
        elif not wa and not wb:
            fixed_sample.append((aabb_overlap_volume(bnds[a], bnds[b]), a, b))
    fixed_sample.sort(reverse=True)
    for _, a, b in fixed_sample[:50]:
        sel[(a, b)] = 'fixed-sample'
    progress = R10 / f'spotcheck-{pitch}-progress.json'
    done = {}
    if progress.exists():
        p = read(progress)
        if p['geometry_sha256'] == geo_hash: done = p['results']
    todo = [(a, b) for (a, b) in sorted(sel) if f'{a}|{b}' not in done]
    print(pitch, 'spotcheck pairs:', len(sel), 'todo:', len(todo), flush=True)
    solids = None
    chunk = int(os.environ.get('REPAIR_CHUNK', '24'))
    ops = 0
    for a, b in todo:
        if ops >= chunk:
            save(progress, dict(geometry_sha256=geo_hash, results=done))
            print('bounded chunk checkpoint; restart to continue', flush=True)
            return 75
        if solids is None: _, solids = load_round9(pitch)
        ops += 1
        rec = {}
        try:
            d = solid_distance(solids[a], solids[b])
            rec['distance_mm'] = d
            if d <= DIST_CLEAR:
                rec['clipped_volume_mm3'] = clipped_common_volume(solids[a], solids[b])
        except Exception as e:
            rec['error'] = repr(e)
        done[f'{a}|{b}'] = rec
        if 'clipped_volume_mm3' in rec or 'error' in rec:
            print('FLAG', a, b, rec, flush=True)
        if ops % 6 == 0: save(progress, dict(geometry_sha256=geo_hash, results=done))
    save(progress, dict(geometry_sha256=geo_hash, results=done))
    flagged = {k: v for k, v in done.items() if v.get('clipped_volume_mm3', 0.) > 1e-6}
    errors = {k: v for k, v in done.items() if 'error' in v}
    result = dict(pitch_mm=pitch, geometry_sha256=geo_hash, checked=len(done),
                  by_class={c: sum(1 for (a, b), cc in sel.items() if cc == c) for c in ('wire-or-fly', 'fixed-sample')},
                  flagged_hits=flagged, errors=errors,
                  min_distance_mm=min((v['distance_mm'] for v in done.values() if 'distance_mm' in v), default=None))
    out = HERE / 'sources' / 'round10'; out.mkdir(parents=True, exist_ok=True)
    save(out / f'spotcheck-fixed-{pitch}mm.json', result)
    print('COMPLETE', pitch, 'checked:', len(done), 'flagged:', len(flagged), 'errors:', len(errors), flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(spotcheck(int(sys.argv[1])))
