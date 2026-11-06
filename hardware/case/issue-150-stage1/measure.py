"""Read-only mechanical inventory; stdlib only, run at repository root.
Outputs deterministic JSON to stdout. No CAD generation or design modification.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re

ROOT = Path(__file__).resolve().parents[3]

def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

def parse(p):
    stack = []
    root = None
    for t in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', (ROOT / p).read_text()):
        if t == '(':
            a = []
            if stack:
                stack[-1].append(a)
            else:
                root = a
            stack.append(a)
        elif t == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack
    return root

def children(a, k):
    return [b for b in a if isinstance(b, list) and b and b[0] == k]

def child(a, k):
    return children(a, k)[0]

def inventory(p):
    b = parse(p)
    fps = []
    holes = []
    for f in children(b, 'footprint'):
        props = {x[1]: x[2] for x in children(f, 'property')}
        at = [float(x) for x in child(f, 'at')[1:]]
        ref = props['Reference']
        fps.append(dict(ref=ref, value=props.get('Value'), at=at, layer=child(f, 'layer')[1]))
        angle = math.radians(at[2] if len(at) > 2 else 0)
        for pad in children(f, 'pad'):
            if pad[2] == 'np_thru_hole':
                x, y = map(float, child(pad, 'at')[1:3])
                holes.append(dict(ref=ref, x=round(at[0] + x*math.cos(angle) + y*math.sin(angle), 6),
                                  y=round(at[1] - x*math.sin(angle) + y*math.cos(angle), 6),
                                  drill=child(pad, 'drill')[1:]))
    edges = []
    for f in children(b, 'gr_line'):
        if child(f, 'layer')[1] == 'Edge.Cuts':
            edges.append([list(map(float, child(f, k)[1:3])) for k in ('start', 'end')])
    pts = [p for e in edges for p in e]
    bounds = [min(p[0] for p in pts), min(p[1] for p in pts),
              max(p[0] for p in pts), max(p[1] for p in pts)]
    return dict(path=p, sha256=sha(p), thickness_mm=float(child(child(b, 'general'), 'thickness')[1]),
                bounds_xy_mm=bounds, edges=edges, holes=holes, components=fps)

result = {'units': 'mm', 'frame': 'KiCad absolute; top view; X right, Y down', 'wings': {}}
for pitch in (16, 17):
    base = f'hardware/jitx/wing/generated/representative21-{pitch}mm/'
    d = json.loads((ROOT / (base+'definition.json')).read_text())
    native = inventory(f'hardware/kicad/qualification/issue-141-wing-power-integrity/runs/KRT-{pitch}-2L-P0300/out.kicad_pcb')
    frozen = json.loads((ROOT / 'hardware/case/issue-150-stage1/inputs/issue149-interface.json').read_text())[str(pitch)]
    silk = frozen
    for k in ('thickness_mm', 'bounds_xy_mm', 'holes', 'components'):
        assert native[k] == frozen['geometry'][k], k
    expected = sorted((100+h['x_mm'], 100-h['y_mm']) for h in d['mounting_holes'])
    assert expected == sorted((h['x'], h['y']) for h in native['holes'])
    assert len(native['holes']) == 4
    assert all(h['drill'] == ['2.2'] for h in native['holes'])
    assert native['thickness_mm'] == d['thickness_mm'] == 1.2
    keys = [dict(ref=s['reference'], key=s['source_key_id'], x=100+s['x_mm'], y=100-s['y_mm']) for s in d['sensor_sites']]
    byref = {c['ref']: c for c in native['components']}
    assert len(keys) == 21
    for s in keys:
        c = byref[s['ref']]
        assert c['at'][:2] == [s['x'], s['y']] and c['layer'] == 'F.Cu'
    pairs = []
    for a,b in itertools.combinations(keys, 2):
        dx,dy = abs(a['x']-b['x']), abs(a['y']-b['y'])
        pairs.append(dict(a=a['key'],b=b['key'],dx=dx,dy=dy,
                          axis_gap_switch_15_8=max(dx,dy)-15.8,
                          axis_gap_dsa_18_415=max(dx,dy)-18.415))
    summary = {}
    for name,w in [('switch_conservative',15.8),('dsa_nominal',18.415),('custom_cap_max',15.0)]:
        summary[name] = dict(square_width=w, pair_count=len(pairs),
            minimum_separating_axis_gap=min(max(p['dx'],p['dy'])-w for p in pairs),
            overlap_pairs=[{'a':p['a'],'b':p['b'],'dx':p['dx'],'dy':p['dy']} for p in pairs if p['dx'] < w and p['dy'] < w])
    result['wings'][str(pitch)] = dict(definition_path=base+'definition.json',definition_sha256=sha(base+'definition.json'),
        native=native,silk_path=silk['path'],silk_sha256=silk['sha256'], keys=keys,
        connector_cable_access_definition_mm=d['connector_cable_access_mm'],
        fit=summary, source_pairs=pairs)
main = inventory('hardware/kicad/qualification/issue-121-full-auto-conditions/evidence/inspection/main-cell1/krt/main.kicad_pcb')
assert len(main['holes']) == 2 and all(h['ref'] == 'J1' for h in main['holes'])
assert main['bounds_xy_mm'] == [76,78,124,122]
result['main'] = main
result['calculations'] = dict(dsa_width=0.725*25.4, dsa_height=0.291*25.4,
    switch_square_max=15.4+0.4, raised_fixture_minimum_H=5.05+2.8+1.12+0.10+0.30,
    raised_fixture_clearance_min=9.85-5.05-2.8-1.12-0.10,
    proposed_plate_opening=[14.15,0.05], nominal_web_16=16-14.15,nominal_web_17=17-14.15,
    top_sensor_chain_known_worst_case=0.15+0.05+0.08+0.05+0.10,
    underside_sensor_chain_known_worst_case=0.15+0.05+0.08+0.05+0.10+0.12,
    note='H is PCB top to plate top. Proposed tolerances are engineering allocations, not measured acceptance. Magnet datum unknown.')
print(json.dumps(result,ensure_ascii=False,indent=2))
