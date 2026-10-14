"""Read-only corroboration of the frozen partial transcription, after STOP.

Consumes only logical source records, component anchors and board fields from
retained routed evidence. Never reads/reuses its tracks/vias as a new input.
This is not a Main shape/copper verifier or an executed Main negative-test suite.
"""
import gzip
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT.parents[2] / 'tscircuit/qualification/eda-003c/evidence/raw/latest-main.circuit.json.gz'


def compare():
    intent = json.loads((ROOT/'source-intent.partial.json').read_text())
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == '0fbf192de02584520b9b53ac505ab0987d784eb0b0139077971901ab3c389ef2'
    raw = gzip.decompress(RAW.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == '97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131'
    data = json.loads(raw)
    def rows(kind):
        return [r for r in data if r['type'] == kind]
    components = {c['source_component_id']:c for c in rows('source_component')}
    ports = {p['source_port_id']:p for p in rows('source_port')}
    nets = {n['source_net_id']:n['name'] for n in rows('source_net')}
    parent = {p:p for p in ports}
    def find(p):
        while parent[p] != p:
            p = parent[p]
        return p
    def join(a,b):
        parent[find(b)] = find(a)
    for item in rows('source_component_internal_connection'):
        ids = item['source_port_ids']
        for p in ids[1:]:
            join(ids[0],p)
    for trace in rows('source_trace'):
        ids = trace['connected_source_port_ids']
        for p in ids[1:]:
            join(ids[0],p)
    names = {}
    for trace in rows('source_trace'):
        for p in trace['connected_source_port_ids']:
            names.setdefault(find(p),set()).update(nets[n] for n in trace['connected_source_net_ids'])
    assert all(len(n) == 1 for n in names.values())
    expected = {c['reference']:c for c in intent['components']}
    assert set(expected) == {c['name'] for c in components.values()}
    anchors = {p['source_component_id']:p for p in rows('pcb_component')}
    details = []
    def value_number(value):
        m = re.fullmatch(r'([\d.]+)([kmunp]?)(?:F)?',value)
        return float(m[1]) * {'':1,'k':1e3,'m':1e-3,'u':1e-6,'n':1e-9,'p':1e-12}[m[2]]
    for sid, actual in components.items():
        exp = expected[actual['name']]
        if actual['ftype'] == 'simple_resistor':
            assert math.isclose(actual['resistance'],value_number(exp['value']),rel_tol=1e-10)
        elif actual['ftype'] == 'simple_capacitor':
            assert math.isclose(actual['capacitance'],value_number(exp['value']),rel_tol=1e-10)
        elif actual['ftype'] == 'simple_chip':
            assert actual['manufacturer_part_number'] == exp['value']
        else:
            assert actual['ftype'] == 'simple_test_point' and exp['value'] is None
        a = anchors[sid]
        assert all(abs(a[k]-v)<1e-6 for k,v in zip(['display_offset_x','display_offset_y'],exp['source_position_mm']))
        assert a['rotation'] == exp['source_ccw_rotation_deg']
        got = {}
        logical = {}
        for p in ports.values():
            if p['source_component_id'] != sid:
                continue
            n = str(p['pin_number']) if 'pin_number' in p else next(h[3:] for h in p['port_hints'] if re.fullmatch(r'pin\d+',h))
            actual_names = names.get(find(p['source_port_id']),set())
            net = next(iter(actual_names)) if actual_names else None
            got.setdefault(n,[]).append(net)
            if 'pin_number' in p:
                logical[n] = dict(alias=p['name'], net=net, nc=p.get('do_not_connect',False))
        assert set(logical) == set(exp['pins'])
        for n,pin in exp['pins'].items():
            assert logical[n] == dict(alias=pin['alias'],net=pin['named_net'],nc=pin['intentional_nc'])
            lands = [e for e in intent['physical_endpoint_intent'] if e['reference']==actual['name'] and e['source_pin']==n]
            assert len(got[n]) == len(lands)
            assert all(net == pin['named_net'] for net in got[n])
        details.append(dict(reference=actual['name'], identity_value=True, logical_pins_alias_net_nc=True,
                            source_position_rotation=True, expanded_port_count=sum(map(len,got.values()))))
    assert set(nets.values()) == set(intent['named_nets'])
    board = rows('pcb_board')[0]
    for key,value in [('width',48),('height',44),('num_layers',2),('thickness',1.2)]:
        assert board[key] == value
    return dict(status='PASS_WITH_LIMITS', comparison_only=True, fresh_generation=False,
        historical_path=str(RAW.relative_to(ROOT.parents[3])),
        compressed_sha256=hashlib.sha256(RAW.read_bytes()).hexdigest(),
        raw_sha256=hashlib.sha256(gzip.decompress(RAW.read_bytes())).hexdigest(),
        components=details, runtime_source_ports=len(ports),
        logical_pin_numbers=sum(len(c['pins']) for c in expected.values()),
        required_physical_endpoint_intents=167, intentional_nc_physical_endpoint_intents=30,
        copper_reused=False, shape_parity=False, complete_role_parity=False,
        limitation='Only retained logical graph, duplicate expansion counts, identities/values and component anchors corroborated. No physical pad shapes/drills/land attachment, route copper, effective rules, Main generation or required Main fault test qualified.')


if __name__ == '__main__':
    result = compare()
    (ROOT/'evidence/retained-intent-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
    print('read-only retained source-intent corroboration PASS_WITH_LIMITS; no Main qualification')
