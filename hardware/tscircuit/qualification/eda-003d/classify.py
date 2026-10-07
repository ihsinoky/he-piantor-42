"""Classify accepted Main diagnostics using exact line/circle/rectangle geometry.

No router invocation, dependency install, generated-data write or rule change.
Only conflicts with an explicit common geometric witness on BOTH copper sides
are merged. Net names, checker types, proximity and shared object IDs alone
never merge faults. All below-rule primitive pairs, not only minima, are kept.
"""
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPS = 1e-8
MAX_FEASIBILITY_ITERATIONS = 800


def point(p):
    return (p['x'], p['y'])


def add(a, b):
    return (a[0]+b[0], a[1]+b[1])


def sub(a, b):
    return (a[0]-b[0], a[1]-b[1])


def mul(a, n):
    return (a[0]*n, a[1]*n)


def dot(a, b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a, b):
    return a[0]*b[1]-a[1]*b[0]


def norm(a):
    return math.hypot(*a)


def project(p, a, b):
    v = sub(b, a)
    t = max(0, min(1, dot(sub(p, a), v)/(dot(v, v) or 1)))
    return add(a, mul(v, t))


def closest_lines(a, b, c, d):
    ab, cd = sub(b, a), sub(d, c)
    den = cross(ab, cd)
    if abs(den) > 1e-14:
        t, u = cross(sub(c, a), cd)/den, cross(sub(c, a), ab)/den
        if 0 <= t <= 1 and 0 <= u <= 1:
            p = add(a, mul(ab, t))
            return (0, p, p)
    pairs = [(a, project(a, c, d)), (b, project(b, c, d)),
             (project(c, a, b), c), (project(d, a, b), d)]
    return min((norm(sub(p, q)), p, q) for p, q in pairs)


def contains(shape, p):
    if 'polygon' in shape:
        poly = shape['polygon']
        return all(cross(sub(poly[(i+1) % 4], a), sub(p, a)) >= -EPS
                   for i, a in enumerate(poly))
    return norm(sub(p, project(p, shape['a'], shape['b']))) <= shape['radius']+EPS


def spacing(a, b):
    """Signed capsule clearance; polygon penetration returns negative radius.

    For hole center inside a pad, penetration is at least the hole radius;
    do not claim a polygon signed-distance penetration depth.
    """
    if 'polygon' in a:
        assert 'polygon' not in b, 'Pad-pad geometry not present in accepted diagnostics'
        if contains(a, b['a']) or contains(a, b['b']):
            p = b['a'] if contains(a, b['a']) else b['b']
            return (-b['radius'], p, p)
        poly = a['polygon']
        dist, p, q = min(closest_lines(x, poly[(i+1) % 4], b['a'], b['b'])
                         for i, x in enumerate(poly))
        direction = mul(sub(p, q), 1/(dist or 1))
        return (dist-b['radius'], p, add(q, mul(direction, b['radius'])))
    if 'polygon' in b:
        dist, q, p = spacing(b, a)
        return (dist, p, q)
    dist, p, q = closest_lines(a['a'], a['b'], b['a'], b['b'])
    direction = mul(sub(q, p), 1/(dist or 1))
    return (dist-a['radius']-b['radius'], add(p, mul(direction, a['radius'])),
            sub(q, mul(direction, b['radius'])))


def shared_conflict(a, b):
    """Prove an overlapping clearance witness; preserve layer and net pair."""
    if a['layer'] != b['layer'] or a['nets'] != b['nets']:
        return False
    for s, t in zip(a['shapes'], b['shapes']):
        if 'polygon' in s and 'polygon' in t:
            # Accepted records can share the same pad; distinct pads never
            # occur on the same net side in this diagnostic set.
            if s['object_id'] != t['object_id']:
                return False
        elif spacing(s, t)[0] > EPS:
            return False
    for event in (a, b):
        p, q = event['witness']
        if all(contains(e['shapes'][0], p) and contains(e['shapes'][1], q) for e in (a, b)):
            return {'points': [p, q], 'method': 'minimum witness'}
    # Prove continuity across shared joints using additional edge witnesses.
    # Convex primitives contain the straight interpolation to each minimum;
    # Euclidean distance is convex, so these below-rule witnesses connect the
    # two conflict regions. No arbitrary spatial merge radius is used.
    for side in (0, 1):
        for shape in (a['shapes'][side], b['shapes'][side]):
            probes = ([dict(a=p, b=p, radius=0) for p in shape['polygon']]
                      if 'polygon' in shape else
                      [dict(a=shape[k], b=shape[k], radius=shape['radius']) for k in ('a', 'b')])
            for probe in probes:
                for other in (a['shapes'][1-side], b['shapes'][1-side]):
                    gap, p, q = spacing(probe, other)
                    if gap >= min(a['required_mm'], b['required_mm'])-EPS:
                        continue
                    if all(contains(e['shapes'][side], p) and contains(e['shapes'][1-side], q)
                           for e in (a, b)):
                        return {'points': [p, q] if side == 0 else [q, p], 'method': 'joint witness'}
    # Intersection feasibility for the four convex copper primitives and the
    # below-rule spacing ball. Dykstra projections find a common witness even
    # when it is not one of the primitive minima or route joints. Accept only
    # after checking every original geometric constraint.
    def projection(shape, p):
        if contains(shape, p):
            return p
        if 'polygon' in shape:
            poly = shape['polygon']
            return min((project(p, x, poly[(i+1) % 4]) for i, x in enumerate(poly)),
                       key=lambda q: norm(sub(p, q)))
        q = project(p, shape['a'], shape['b'])
        v = sub(p, q)
        return add(q, mul(v, shape['radius']/(norm(v) or 1)))
    limit = min(a['required_mm'], b['required_mm'])-1e-7
    if limit <= 0:
        return False
    x = tuple((p[k]+q[k])/2 for p, q in zip(a['witness'], b['witness']) for k in (0, 1))
    corrections = [[0.0]*4 for _ in range(5)]
    for _ in range(MAX_FEASIBILITY_ITERATIONS):
        for i in range(5):
            y = tuple(x[k]+corrections[i][k] for k in range(4))
            if i < 4:
                side, which = i % 2, i // 2
                shape = (a, b)[which]['shapes'][side]
                p = projection(shape, y[side*2:side*2+2])
                z = list(y)
                z[side*2:side*2+2] = p
            else:
                p, q = y[:2], y[2:]
                v = sub(q, p)
                delta = mul(v, max(0, norm(v)-limit)/(2*(norm(v) or 1)))
                z = (*add(p, delta), *sub(q, delta))
            corrections[i] = [y[k]-z[k] for k in range(4)]
            x = tuple(z)
        if norm(sub(x[:2], x[2:])) < min(a['required_mm'], b['required_mm'])-EPS and all(
            contains(e['shapes'][0], x[:2]) and contains(e['shapes'][1], x[2:]) for e in (a, b)):
            return {'points': [x[:2], x[2:]], 'method': 'convex intersection witness'}
    return False


def group_events(events):
    parent = list(range(len(events)))
    proofs = []

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i, a in enumerate(events):
        for j, b in enumerate(events[:i]):
            if find(i) == find(j):
                continue
            proof = shared_conflict(a, b)
            if proof:
                proofs.append(dict(proof, event_indices=[i, j]))
                parent[find(i)] = find(j)
    groups = {}
    for i, e in enumerate(events):
        groups.setdefault(find(i), []).append(e)
    return list(groups.values()), proofs


def machine_json(value):
    """Keep bulky machine evidence to one observation per line."""
    def array(items):
        return '[\n'+',\n'.join(json.dumps(item, separators=(',', ':')) for item in items)+'\n]'
    if isinstance(value, list):
        return array(value)+'\n'
    fields = []
    for key, item in value.items():
        rendered = array(item) if isinstance(item, list) else json.dumps(item, separators=(',', ':'))
        fields.append(json.dumps(key)+':'+rendered)
    return '{\n'+',\n'.join(fields)+'\n}\n'


def classify():
    accepted = HERE.parent/'eda-003c/evidence'
    raw = gzip.decompress((accepted/'raw/latest-main.circuit.json.gz').read_bytes())
    data = json.loads(raw)
    captured = json.loads((HERE/'evidence/stock-check-records.json').read_text())
    assert hashlib.sha256(raw).hexdigest() == captured['input_sha256']
    records = captured['records']
    byid = {e[e['type']+'_id']: e for e in data if e['type']+'_id' in e}
    traces = [e for e in data if e['type'] == 'pcb_trace']
    board = next(e for e in data if e['type'] == 'pcb_board')
    source_nets = {e['source_net_id']: e['name'] for e in data if e['type'] == 'source_net'}
    membership = {}
    for e in data:
        if e['type'] == 'source_trace':
            names = [source_nets[n] for n in e['connected_source_net_ids']]
            membership[e['source_trace_id']] = names
            for p in e['connected_source_port_ids']:
                membership[p] = names

    def identity(e):
        kind = e['type']
        eid = e[kind+'_id']
        if kind == 'pcb_via':
            net = identity(byid[e['pcb_trace_id']])['nets']
        elif kind == 'pcb_trace':
            net = membership.get(e.get('source_trace_id'), [])
        else:
            port = byid[e['pcb_port_id']]
            net = membership.get(port['source_port_id'], [])
        result = {'id': eid, 'kind': kind, 'nets': net,
                  'stock_autorouted': kind in ('pcb_via', 'pcb_trace') and eid != 'pcb_trace_0'}
        if kind == 'pcb_trace':
            result['source_trace_id'] = e.get('source_trace_id')
            result['source_trace_name'] = byid[e['source_trace_id']].get('display_name')
            result['source_ports'] = [dict(source_port_id=p, component=byid[byid[p]['source_component_id']]['name'],
                                           port=byid[p]['name']) for p in byid[e['source_trace_id']]['connected_source_port_ids']]
        if kind == 'pcb_via':
            result.update({k: e[k] for k in ('pcb_trace_id', 'x', 'y', 'hole_diameter', 'outer_diameter', 'layers')})
        if kind in ('pcb_smtpad', 'pcb_plated_hole'):
            port = byid[e['pcb_port_id']]
            sp = byid[port['source_port_id']]
            comp = byid[sp['source_component_id']]
            result.update(component=comp['name'], port=sp['name'], pcb_port_id=e['pcb_port_id'],
                          source_port_id=sp['source_port_id'], do_not_connect=sp.get('do_not_connect', False))
            result['geometry'] = {k: e[k] for k in ('x', 'y', 'shape', 'width', 'height', 'radius', 'layer', 'layers', 'ccw_rotation') if k in e}
        return result

    def shapes(e, hole=False):
        eid = e[e['type']+'_id']
        info = identity(e)
        # NC copper remains material; use unique NC identity instead of inventing a net.
        net = '|'.join(info['nets']) or 'NC:'+info.get('component', '')+'.'+info.get('port', eid)
        common = {'object_id': eid, 'net': net}
        if e['type'] == 'pcb_trace':
            out = []
            for i, (a, b) in enumerate(zip(e['route'], e['route'][1:])):
                # Same wire-wire coverage as stock checks. Via-adjacent geometry is
                # retained by the accepted connectivity verifier, not these checks.
                if a['route_type'] != 'wire' or b['route_type'] != 'wire' or a['layer'] != b['layer']:
                    continue
                out.append(dict(common, primitive_id=f'{eid}:{i}', layer=a['layer'],
                                a=point(a), b=point(b), radius=a.get('width', b.get('width', .1))/2))
            return out
        if e['type'] == 'pcb_via':
            return [dict(common, primitive_id=eid+(':hole' if hole else ''), layer=l,
                         a=point(e), b=point(e), radius=e['hole_diameter' if hole else 'outer_diameter']/2)
                    for l in e['layers']]
        assert e['shape'] in ('rect', 'circle'), e
        if e['shape'] == 'circle':
            return [dict(common, primitive_id=eid, layer=e['layer'], a=point(e), b=point(e), radius=e['radius'])]
        angle = math.radians(e.get('ccw_rotation', 0))
        poly = [(e['x']+x*math.cos(angle)-y*math.sin(angle), e['y']+x*math.sin(angle)+y*math.cos(angle))
                for x, y in [(-e['width']/2, -e['height']/2), (e['width']/2, -e['height']/2),
                             (e['width']/2, e['height']/2), (-e['width']/2, e['height']/2)]]
        return [dict(common, primitive_id=eid, layer=e['layer'], polygon=poly)]

    normalized, events = [], []
    for n, r in enumerate(records, 1):
        rid = f'R{n:03}'
        if r['type'] == 'pcb_placement_error':
            ids = r['pcb_placement_error_id'].removeprefix('via_in_pad_').split('_pcb_smtpad_')
            ids = [ids[0], 'pcb_smtpad_'+ids[1]]
            hole, required = True, 0.0
        elif r['type'] == 'pcb_trace_error':
            first = r['pcb_trace_id']
            second = r['pcb_trace_error_id'].removeprefix('overlap_'+first+'_')
            ids, hole, required = [first, second], False, board['min_trace_to_pad_edge_clearance']
        else:
            ids = r.get('pcb_pad_ids') or [r.get('pcb_pad_id') or r['pcb_via_id'], r['pcb_trace_id']]
            hole, required = False, r['minimum_clearance']
        objects = [byid[i] for i in ids]
        pairs = []
        for a in shapes(objects[0], hole=hole):
            for b in shapes(objects[1]):
                if a['layer'] != b['layer']:
                    continue
                gap, p, q = spacing(a, b)
                if gap >= required-1e-9:
                    continue
                # Deterministically align net sides, independent of checker direction.
                if a['net'] > b['net']:
                    a0, b0, p0, q0 = b, a, q, p
                else:
                    a0, b0, p0, q0 = a, b, p, q
                e = {'record_id': rid, 'type': r['type'], 'shapes': [a0, b0],
                     'nets': [a0['net'], b0['net']], 'layer': a['layer'],
                     'required_mm': required, 'gap_mm': gap, 'witness': [p0, q0], 'hole_conflict': hole}
                pairs.append(e)
        assert pairs, (rid, r)
        minimum = min(e['gap_mm'] for e in pairs)
        if 'actual_clearance' in r:
            assert abs(minimum-r['actual_clearance']) < 1e-7, (rid, minimum, r['actual_clearance'])
        events.extend(pairs)
        normalized.append({'record_id': rid, 'type': r['type'], 'diagnostic': r,
                           'objects': [identity(e) for e in objects],
                           'required_clearance_mm': required, 'actual_minimum_spacing_mm': minimum,
                           'material_geometric_distance_mm': max(0, minimum),
                           'signed_penetration_depth_exact': not hole or minimum > -.15+EPS,
                           'metric': 'hole intrusion (0 means no overlap)' if hole else 'copper edge clearance',
                           'violating_primitive_pairs': [{'objects': [e['shapes'][0]['primitive_id'], e['shapes'][1]['primitive_id']],
                               'layer': e['layer'], 'gap_mm': e['gap_mm'], 'geometry': e['shapes'],
                               'witness_copper_edge_points': e['witness']}
                               for e in pairs]})
    clusters = []
    groups, proofs = group_events(events)
    for i, group in enumerate(groups, 1):
        rawids = sorted({e['record_id'] for e in group})
        minimum = min(group, key=lambda e: e['gap_mm'])
        hole = any(e['hole_conflict'] for e in group)
        kinds = sorted({s['object_id'] for e in group for s in e['shapes']})
        clusters.append({'cluster_id': f'C{i:03}', 'record_ids': rawids, 'raw_records_explained': len(rawids),
                         'nets': group[0]['nets'], 'layer': group[0]['layer'], 'object_ids': kinds,
                         'primitive_ids': sorted({s['primitive_id'] for e in group for s in e['shapes']}),
                         'error_types': sorted({e['type'] for e in group}), 'smallest_spacing_mm': minimum['gap_mm'],
                         'location': [sum(p[k] for p in minimum['witness'])/2 for k in (0, 1)],
                         'witness': minimum['witness'],
                         'risk_priority': 1 if hole or minimum['gap_mm'] <= 0 else 2 if minimum['gap_mm'] < .1 else
                             3 if any(byid[k]['type'] == 'pcb_via' for k in kinds) else 5,
                         'responsibility': 'stock-generated via drill placement; internal phase unknown' if hole else
                             'stock-generated route/via clearance; internal phase unknown',
                         'merge_basis': 'shared geometric clearance witness or continuous below-rule corridor on both net sides; no proximity-only merge'})
    for r in normalized:
        r['cluster_ids'] = [c['cluster_id'] for c in clusters if r['record_id'] in c['record_ids']]
        r['same_conflict_other_record_ids'] = sorted({rid for c in clusters if r['record_id'] in c['record_ids']
                                                    for rid in c['record_ids'] if rid != r['record_id']})
    output = {'input_sha256': captured['input_sha256'], 'raw_error_record_count': len(records),
              'independent_physical_fault_count': len(clusters),
              'method': __doc__, 'numeric_tolerance_mm': EPS,
              'count_interpretation': 'Conservative local conflict components with proved merges; finite convex feasibility search can leave an unresolved merge. The 37 distinct net/NC pairs are an independent lower bound regardless of such merges.',
              'scope': 'All below-rule wire-wire primitive pairs covered by the 71 accepted records. Not a new board-wide DRC.',
              'merge_proofs': [dict(proof, primitive_pairs=[[s['primitive_id'] for s in events[i]['shapes']]
                                    for i in proof['event_indices']]) for proof in proofs],
              'clusters': clusters, 'risk_order': [c['cluster_id'] for c in sorted(clusters,
                  key=lambda c: (c['risk_priority'], c['smallest_spacing_mm'], -c['raw_records_explained'], c['cluster_id']))]}
    (HERE/'evidence/error-records-normalized.json').write_text(machine_json(normalized))
    (HERE/'evidence/physical-fault-clusters.json').write_text(machine_json(output))
    print(json.dumps({k: output[k] for k in ('raw_error_record_count', 'independent_physical_fault_count')}))
    for c in clusters:
        print(c['cluster_id'], c['record_ids'], c['nets'], round(c['smallest_spacing_mm'], 6), c['location'])


if __name__ == '__main__':
    classify()
