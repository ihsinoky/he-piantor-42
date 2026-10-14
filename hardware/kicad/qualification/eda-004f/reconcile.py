"""Read-only independent oracle: stdlib KiCad XML + generic S-expression parser.

No kicad-sch-api imports or graph calculations are used. The geometry reader is
bounded to the predeclared unrotated, wire-stub/local-label fixture.
"""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sexpdata

ROOT = Path(__file__).resolve().parent


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and str(x[0]) == key]


def one(node, key):
    items = children(node, key)
    assert len(items) == 1, (key, len(items))
    return items[0]


def pins(node):
    result = children(node, 'pin')
    for sub in children(node, 'symbol'):
        result += pins(sub)
    return result


def point(x, y):
    return (round(float(x), 6), round(float(y), 6))


def reconcile(directory, case='normal'):
    contract = json.loads((ROOT / 'contract.json').read_text())
    expected = contract['components']
    xml = ET.parse(directory / 'fixture.xml').getroot()
    assert '9.0.9' in xml.findtext('design/tool')
    sx = sexpdata.loads((directory / 'fixture.kicad_sch').read_text())
    definitions = {x[1]: x for x in children(one(sx, 'lib_symbols'), 'symbol')}
    actual = {}
    endpoints = {}
    for symbol in children(sx, 'symbol'):
        props = {x[1]: x[2] for x in children(symbol, 'property')}
        ref = props['Reference']
        lib_id = one(symbol, 'lib_id')[1]
        at = one(symbol, 'at')
        assert at[3] == 0, 'Fixture reader supports only contracted rotation 0'
        pin_table = {}
        for pin in pins(definitions[lib_id]):
            num = one(pin, 'number')[1]
            name = one(pin, 'name')[1]
            pos = one(pin, 'at')
            pin_table[num] = [name, str(pin[1])]
            endpoints[ref + '.' + num] = point(at[1] + pos[1], at[2] - pos[2])
        actual[ref] = dict(lib_id=lib_id, value=props['Value'], pins=pin_table)
    failures = []
    def check(condition, category, detail):
        if not condition:
            failures.append(dict(category=category, detail=detail))
    check(set(actual) == set(expected), 'component-set', sorted(actual))
    for ref, exp in expected.items():
        value = '12k' if case == 'value' and ref == 'R1' else exp['value']
        got = actual.get(ref, {})
        check(got.get('lib_id') == exp['lib_id'], 'identity', ref)
        check(got.get('value') == value, 'value', ref)
        check(got.get('pins') == {k: v[:2] for k, v in exp['pins'].items()}, 'pin-role', ref)
    # Union wire endpoints and local labels; every source pin must be on an endpoint.
    parent = {}
    def find(p):
        parent.setdefault(p, p)
        if parent[p] != p:
            parent[p] = find(parent[p])
        return parent[p]
    def join(a, b):
        parent[find(a)] = find(b)
    for wire in children(sx, 'wire'):
        xy = children(one(wire, 'pts'), 'xy')
        assert len(xy) == 2
        join(point(*xy[0][1:]), point(*xy[1][1:]))
    labels = {}
    for label in children(sx, 'label'):
        pos = point(*one(label, 'at')[1:3])
        if label[1] in labels:
            join(pos, labels[label[1]])
        labels[label[1]] = pos
    nc_points = {point(*one(n, 'at')[1:3]) for n in children(sx, 'no_connect')}
    nets = {}
    for endpoint, pos in endpoints.items():
        names = sorted(n for n, p in labels.items() if find(pos) == find(p))
        check(len(names) <= 1, 'shorted-names', endpoint)
        nets[endpoint] = names[0] if len(names) == 1 else None
    for ref, exp in expected.items():
        for num, (_, _, net) in exp['pins'].items():
            endpoint = ref + '.' + num
            check(nets.get(endpoint) == net, 'source-net', endpoint)
            check((endpoints[endpoint] in nc_points) == (endpoint in contract['intentional_nc']), 'nc-marker', endpoint)
    # KiCad omits virtual power flags from PCB netlists. Check them above, and
    # independently check all four physical parts and all fourteen physical pins.
    physical = {r: e for r, e in expected.items() if not r.startswith('#')}
    xml_components = {x.attrib['ref']: x for x in xml.findall('components/comp')}
    check(set(xml_components) == set(physical), 'xml-component-set', sorted(xml_components))
    xml_pins = {}
    for part in xml.findall('libparts/libpart'):
        xml_pins[part.attrib['lib'] + ':' + part.attrib['part']] = {
            p.attrib['num']: [p.attrib.get('name') or '~', p.attrib['type']]
            for p in part.findall('pins/pin')}
    xml_nets = {}
    for net in xml.findall('nets/net'):
        name = net.attrib['name']
        nodes = net.findall('node')
        if name.startswith('unconnected-'):
            check(len(nodes) == 1, 'xml-nc-isolation', name)
            name = None
        elif name.startswith('/'):
            name = name[1:]
        for n in nodes:
            endpoint = n.attrib['ref'] + '.' + n.attrib['pin']
            check(endpoint not in xml_nets, 'xml-duplicate-pin', endpoint)
            xml_nets[endpoint] = name
            check(n.attrib['pintype'].split('+')[0] == physical[n.attrib['ref']]['pins'][n.attrib['pin']][1], 'xml-node-role', endpoint)
    for ref, exp in physical.items():
        c = xml_components.get(ref)
        if c is not None:
            source = c.find('libsource').attrib
            check(source['lib'] + ':' + source['part'] == exp['lib_id'], 'xml-identity', ref)
            check(c.findtext('value') == ('12k' if case == 'value' and ref == 'R1' else exp['value']), 'xml-value', ref)
        check(xml_pins.get(exp['lib_id']) == {k: v[:2] for k, v in exp['pins'].items()}, 'xml-pin-table', ref)
        for num, (_, _, net) in exp['pins'].items():
            endpoint = ref + '.' + num
            check(endpoint in xml_nets and xml_nets[endpoint] == net, 'xml-net', endpoint)
    expected_xml_endpoints = {r + '.' + n for r, e in physical.items() for n in e['pins']}
    check(set(xml_nets) == expected_xml_endpoints, 'xml-endpoint-set', sorted(xml_nets))
    erc = json.loads((directory / 'erc.json').read_text())
    violations = [v for s in erc['sheets'] for v in s['violations']]
    return dict(case=case, parity_pass=not failures, failures=failures,
                source_component_count=len(actual), source_pin_count=len(endpoints),
                xml_component_count=len(xml_components), xml_pin_count=len(xml_nets),
                normalized=dict(components=actual, nets=nets, intentional_nc=sorted(e for e,p in endpoints.items() if p in nc_points)),
                erc_version=erc['kicad_version'], erc_violations=violations)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('directory', type=Path)
    p.add_argument('--case', default='normal')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    result = reconcile(a.directory, a.case)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'normalized'}, indent=2))
