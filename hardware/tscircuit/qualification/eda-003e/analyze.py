"""Deterministic read-only signature extraction from accepted EDA-003D geometry."""
import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
HERE = Path(__file__).resolve().parent
Q = HERE.parent

def load(p):
    return json.loads(p.read_text())

def distance_point_segment(p, a, b):
    v = [b[i]-a[i] for i in range(2)]
    length2 = sum(x*x for x in v)
    t = max(0, min(1, sum((p[i]-a[i])*v[i] for i in range(2))/length2)) if length2 else 0
    return math.dist(p, [a[i]+t*v[i] for i in range(2)])

def extract(records):
    result = []
    for r in records:
        if r['type'] != 'pcb_via_trace_clearance_error' or abs(r['actual_minimum_spacing_mm']-.115) > .0003:
            continue
        via = next(o for o in r['objects'] if o['kind']=='pcb_via')
        trace = next(o for o in r['objects'] if o['kind']=='pcb_trace')
        pair = min(r['violating_primitive_pairs'], key=lambda p:p['gap_mm'])
        segment = next(g for g in pair['geometry'] if g['object_id']==trace['id'])
        center = [via['x'], via['y']]
        spacing = distance_point_segment(center,segment['a'],segment['b'])-via['outer_diameter']/2-segment['radius']
        assert abs(spacing-r['actual_minimum_spacing_mm']) < 1e-10
        result.append(dict(record_id=r['record_id'],physical_cluster_ids=r['cluster_ids'],via_id=via['id'],
            pcb_trace_id=trace['id'],source_trace_id=trace['source_trace_id'],source_ports=trace['source_ports'],
            via_owner_pcb_trace_id=via['pcb_trace_id'],via_net=via['nets'],trace_net=trace['nets'],
            via_center_mm=center,via_copper_diameter_mm=via['outer_diameter'],via_copper_radius_mm=via['outer_diameter']/2,
            via_drill_diameter_mm=via['hole_diameter'],via_drill_radius_mm=via['hole_diameter']/2,
            trace_width_mm=2*segment['radius'],trace_half_width_mm=segment['radius'],
            closest_trace_segment=segment,layer=pair['layer'],material_spacing_mm=spacing,
            center_to_segment_distance_mm=spacing+via['outer_diameter']/2+segment['radius'],
            required_clearance_mm=r['required_clearance_mm'],via_stock_generated=via['stock_autorouted'],trace_stock_generated=trace['stock_autorouted']))
    vc=collections.Counter(r['via_id'] for r in result);tc=collections.Counter(r['pcb_trace_id'] for r in result)
    for r in result:
        r.update(same_via_signature_records=vc[r['via_id']],same_trace_signature_records=tc[r['pcb_trace_id']])
    return {'target_mm':.115,'band_mm':.0003,'selection':'via-trace records by accepted minimum material spacing; not checker message rounding',
        'records':result,'summary':{'raw_records':len(result),'distinct_vias':len(vc),'distinct_traces':len(tc),
        'distinct_net_pairs':len({tuple(sorted(r['via_net']+r['trace_net'])) for r in result}),
        'physical_clusters':len({c for r in result for c in r['physical_cluster_ids']}),
        'via_center_bounds_mm':{axis:[min(r['via_center_mm'][i] for r in result),max(r['via_center_mm'][i] for r in result)] for i,axis in enumerate(['x','y'])},
        'layers':dict(collections.Counter(r['layer'] for r in result)),
        'spacing_range_mm':[min(r['material_spacing_mm'] for r in result),max(r['material_spacing_mm'] for r in result)]}}

def main():
    records=load(Q/'eda-003d/evidence/error-records-normalized.json')
    result=extract(records)
    expected=load(Q/'eda-003d/evidence/root-cause-families.json')['recurring_signature']['record_ids']
    assert [r['record_id'] for r in result['records']]==expected
    raw=gzip.decompress((Q/'eda-003c/evidence/raw/latest-main.circuit.json.gz').read_bytes())
    assert hashlib.sha256(raw).hexdigest()=='97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131'
    circuit= json.loads(raw)
    ids={x.get('pcb_via_id',x.get('pcb_trace_id')):x for x in circuit if x['type'] in ['pcb_via','pcb_trace']}
    for r in result['records']:
        via=ids[r['via_id']];assert [via['x'],via['y']]==r['via_center_mm']
        assert via['outer_diameter']==r['via_copper_diameter_mm']
        trace=ids[r['pcb_trace_id']]
        assert trace['source_trace_id']==r['source_trace_id']
    (HERE/'evidence/signature-population.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['summary'],indent=2))

if __name__=='__main__':main()
