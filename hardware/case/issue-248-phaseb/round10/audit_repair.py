"""Round-10 repaired strand-strand audit.

The pipeline audit's per-pair BRepAlgoAPI_Common silently returns zero
volume for some long swept wire solids (proven round 9: pair
Wire-right-01/05 round 8, audit 0.0 mm3 vs box-clipped Common 2.456 mm3).
This repair keeps the audit's full-Common volumes (same geometry, reused
from the round's audit.json) and adds a solid-level fallback for every
wire-wire pair the full Common reported as zero:

  1. exact minimum distance between the two solids
     (BRepExtrema_DistShapeShape). Distance > 0 proves the solids are
     disjoint - an overlapping pair has distance exactly 0 - so a pair
     with distance > DIST_CLEAR is CLEAR at solid level.
  2. if distance <= DIST_CLEAR, a partitioned clipped Common: the AABB
     intersection box is partitioned into <=CELL mm cells and the Common
     volume is summed cell by cell (Common distributes over a partition
     of one operand, so the sum is the exact overlap volume; the short
     clipped operands avoid the long-solid failure mode).

A pair is a HIT iff its resolved volume (full or clipped) exceeds 1e-6
mm3, matching the pipeline threshold. Zero-volume tangential touches
(distance ~0, clipped volume 0) are recorded separately.

Usage: audit_repair.py <round8|round9> <pitch>
Chunked: env REPAIR_CHUNK limits new fallback operations per invocation;
exit code 75 means "checkpoint saved, restart to continue" (audit.py
pattern). Progress in .issue248-runtime/round10/.
"""
from common import *
from build123d import import_step, Solid, Pos

DIST_CLEAR = 1e-3   # mm; above this the solids are provably disjoint
CELL = 4.0          # mm; clipped-Common partition cell size
R10 = ROOT / '.issue248-runtime' / 'round10'; R10.mkdir(parents=True, exist_ok=True)

def common_shape(a, b):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    op = BRepAlgoAPI_Common(a.wrapped, b.wrapped)
    op.SetRunParallel(True); op.SetUseOBB(True); op.Build()
    if not op.IsDone(): raise RuntimeError('OCCT Common failed')
    return op.Shape()

def shape_volume(shape):
    if shape.IsNull(): return 0.
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    props = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, props, True, False, False)
    return abs(props.Mass())

def solid_distance(a, b):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); d.Perform()
    if not d.IsDone(): raise RuntimeError('DistShapeShape failed')
    return d.Value()

def clipped_common_volume(a, b):
    """Exact overlap volume via AABB-intersection partition."""
    ab, bb = bounds(a), bounds(b)
    lo = [max(ab[0][d], bb[0][d]) for d in range(3)]
    hi = [min(ab[1][d], bb[1][d]) for d in range(3)]
    if any(hi[d] - lo[d] <= 0 for d in range(3)): return 0.
    # pad by one wire radius so a tangential overlap region is fully inside
    lo = [lo[d] - 0.6 for d in range(3)]; hi = [hi[d] + 0.6 for d in range(3)]
    total = 0.
    xs = [lo[0]]; 
    while xs[-1] < hi[0] - 1e-9: xs.append(min(xs[-1] + CELL, hi[0]))
    ys = [lo[1]]
    while ys[-1] < hi[1] - 1e-9: ys.append(min(ys[-1] + CELL, hi[1]))
    zs = [lo[2]]
    while zs[-1] < hi[2] - 1e-9: zs.append(min(zs[-1] + CELL, hi[2]))
    for xi in range(len(xs) - 1):
        for yi in range(len(ys) - 1):
            for zi in range(len(zs) - 1):
                cell = Pos(xs[xi], ys[yi], zs[zi]) * Solid.make_box(
                    xs[xi+1]-xs[xi], ys[yi+1]-ys[yi], zs[zi+1]-zs[zi])
                ac = common_shape(a, cell)
                if ac.IsNull(): continue
                total += shape_volume(common_shape(Shape.cast(ac), b))
    return total

def load_round8(pitch):
    """Solids for the frozen round-8 assembly, matched to its index by
    volume+bounds (the fitted STEP omits only the 3 USB-reference rows,
    which the audit excludes anyway)."""
    asm = import_step(HERE / f'round8/{pitch}mm/fitted-assembly-PROVISIONAL.step')
    solids = asm.solids()
    idx = read(HERE / f'round8/{pitch}mm/assembly-index.json')
    used = {}
    by_name = {}
    for k, r in enumerate(idx):
        for n, s in enumerate(solids):
            if n in used: continue
            if abs(s.volume - r['volume_mm3']) <= max(1e-6, abs(r['volume_mm3']) * 1e-9):
                sb = bounds(s)
                if all(abs(sb[0][d]-r['bounds'][0][d]) < 1e-6 and abs(sb[1][d]-r['bounds'][1][d]) < 1e-6 for d in range(3)):
                    used[n] = k; by_name[r['name']] = s; break
    return idx, by_name

def load_round9(pitch):
    idx, raw = cached(pitch)
    return idx, {r['name']: s for r, (n, k, s) in zip(idx, raw)}

def repair(source, pitch):
    base = HERE / (f'round8/{pitch}mm' if source == 'round8' else f'{pitch}mm')
    audit = read(base / 'audit.json')
    idx = read(base / 'assembly-index.json')
    names = {i: r['name'] for i, r in enumerate(idx)}
    geo_hash = sha(base / 'assembly-index.json')
    assert audit['geometry_sha256'] == geo_hash, 'audit/geometry mismatch'
    # wire-wire pairs and their full-Common volumes from the round's audit
    pairs = {}
    for r in audit['exact_results']:
        a, b = names[r['i']], names[r['j']]
        if a.startswith('Wire-') and b.startswith('Wire-'):
            pairs[(a, b)] = r.get('volume_mm3', 0.)
    # any wire-wire pair not an exact candidate was AABB-rejected: verify
    wires = sorted({n for n in names.values() if n.startswith('Wire-')})
    bnds = {r['name']: r['bounds'] for r in idx}
    for x in range(len(wires)):
        for y in range(x + 1, len(wires)):
            a, b = wires[x], wires[y]
            if (a, b) in pairs or (b, a) in pairs: continue
            ab, bb = bnds[a], bnds[b]
            gap = max(ab[0][d] - bb[1][d] if ab[0][d] > bb[1][d] else bb[0][d] - ab[1][d] for d in range(3))
            assert gap > 1e-7, f'wire pair neither exact nor AABB-clear: {a} {b}'
            pairs[(a, b)] = None  # AABB-clear
    progress = R10 / f'repair-{source}-{pitch}-progress.json'
    done = {}
    if progress.exists():
        p = read(progress)
        if p['geometry_sha256'] == geo_hash: done = p['results']
    todo = [(a, b) for (a, b), v in sorted(pairs.items()) if v == 0. and f'{a}|{b}' not in done]
    print(source, pitch, 'wire pairs:', len(pairs), 'audit hits:', sum(1 for v in pairs.values() if v and v > 1e-6),
          'fallback todo:', len(todo), flush=True)
    solids = None
    chunk = int(os.environ.get('REPAIR_CHUNK', '24'))
    ops = 0
    for a, b in todo:
        if ops >= chunk:
            save(progress, dict(geometry_sha256=geo_hash, results=done))
            print('bounded chunk checkpoint; restart to continue', flush=True)
            return 75
        if solids is None:
            _, solids = (load_round8(pitch) if source == 'round8' else load_round9(pitch))
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
        print('RESOLVED', a, b, rec, flush=True)
        if ops % 6 == 0: save(progress, dict(geometry_sha256=geo_hash, results=done))
    save(progress, dict(geometry_sha256=geo_hash, results=done))
    # assemble final result
    hits, touches, clears, errors = [], [], [], []
    for (a, b), v in sorted(pairs.items()):
        if v is None: clears.append(dict(a=a, b=b, method='aabb')); continue
        if v > 1e-6: hits.append(dict(a=a, b=b, volume_mm3=v, method='full-common')); continue
        rec = done[f'{a}|{b}']
        if 'error' in rec: errors.append(dict(a=a, b=b, **rec)); continue
        cv = rec.get('clipped_volume_mm3', 0.)
        if cv > 1e-6: hits.append(dict(a=a, b=b, volume_mm3=cv, method='clipped-common', distance_mm=rec['distance_mm']))
        elif rec['distance_mm'] <= DIST_CLEAR: touches.append(dict(a=a, b=b, distance_mm=rec['distance_mm'], clipped_volume_mm3=cv))
        else: clears.append(dict(a=a, b=b, method='distance', distance_mm=rec['distance_mm']))
    result = dict(source=source, pitch_mm=pitch, geometry_sha256=geo_hash,
                  wire_pairs_total=len(pairs), audit_full_common_hits=sum(1 for v in pairs.values() if v and v > 1e-6),
                  true_hits=len(hits), hits=hits, zero_volume_touches=touches, clears=len(clears),
                  errors=errors, threshold_mm3=1e-6, dist_clear_mm=DIST_CLEAR, cell_mm=CELL)
    out = HERE / 'sources' / 'round10'; out.mkdir(parents=True, exist_ok=True)
    save(out / f'repaired-audit-{source}-{pitch}mm.json', result)
    print('COMPLETE', source, pitch, 'true hits:', len(hits), 'touches:', len(touches), 'errors:', len(errors), flush=True)
    return 0

if __name__ == '__main__':
    sys.exit(repair(sys.argv[1], int(sys.argv[2])))
