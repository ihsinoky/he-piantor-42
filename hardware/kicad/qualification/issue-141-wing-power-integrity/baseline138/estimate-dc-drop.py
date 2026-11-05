#!/usr/bin/env python3
"""Supplementary centerline resistor model; not a field solver or sign-off.

Inventory comes from inspect-boards.py. Use numpy and shapely. Track/pad
contacts are lumped at projected centerline positions, pad spreading is
approximated, and vias use an assumed 20um barrel. This estimates scale of
DC drop and must not be read as a guaranteed manufactured-board maximum.
"""
import collections
import json
import math
from pathlib import Path
import numpy as np
from shapely.geometry import Point, LineString, box
from shapely.affinity import rotate, translate

OUT = Path(__file__).resolve().parent
RHO = 1.7241e-8
THICK = 0.035


def pad_shape(p):
    w, h = p['size']
    if p['shape'] == 'circle':
        return Point(p['position']).buffer(w / 2, quad_segs=64)
    assert p['shape'] == 'rect', 'Add oval geometry before using on another board'
    shape = rotate(box(-w / 2, -h / 2, w / 2, h / 2), -p['angle'])
    return translate(shape, *p['position'])


def model(inv, net, sensor_current, mux_current, width, temp):
    ts = [t for t in inv['tracks'] if t['net'] == net]
    ps = [p for p in inv['pads'] if p['net'] == net]
    vs = [v for v in inv['vias'] if v['net'] == net]
    lines = [LineString([t['start'], t['end']]) for t in ts]
    cuts = [{0.0, l.length} for l in lines]
    contacts, junctions, object_links = [], [], []
    rho = RHO * (1 + 0.00393 * (temp - 20))
    # Same-layer centerline intersections, including T junctions.
    for i, a in enumerate(lines):
        for j in range(i):
            if ts[i]['layer'] != ts[j]['layer']:
                continue
            # Router joins can contact through end caps without exact centerline
            # intersection. Add their short transverse copper connection.
            for x, y in ((i, j), (j, i)):
                for d in (0.0, lines[x].length):
                    point = lines[x].interpolate(d)
                    distance = point.distance(lines[y])
                    if distance <= (ts[x]['width_mm'] + ts[y]['width_mm']) / 2 + 2e-6:
                        target = lines[y].project(point)
                        cuts[y].add(target)
                        junctions.append((x, d, y, target, max(distance, 1e-5)))
            intersection = a.intersection(lines[j])
            if intersection.is_empty:
                continue
            if intersection.geom_type == 'Point':
                points = [intersection]
            elif intersection.geom_type == 'MultiPoint':
                points = list(intersection.geoms)
            elif intersection.geom_type == 'LineString':
                points = [Point(intersection.coords[0]), Point(intersection.coords[-1])]
            else:
                raise AssertionError(intersection.geom_type)
            for point in points:
                cuts[i].add(a.project(point))
                cuts[j].add(lines[j].project(point))
    objects = [(p, 'pad') for p in ps] + [(v, 'via') for v in vs]
    shapes = [pad_shape(obj) if kind == 'pad' else Point(obj['position']).buffer(obj['diameter_mm'] / 2, quad_segs=64)
              for obj, kind in objects]
    for i, (obj, kind) in enumerate(objects):
        for j in range(i):
            other, other_kind = objects[j]
            if set(obj['layers']) & set(other['layers']) and shapes[i].distance(shapes[j]) < 2e-6:
                length = math.dist(obj['position'], other['position'])
                resistance = rho * max(length, 1e-5) * 1e-3 / (width * THICK * 1e-6)
                object_links.append((kind + ':' + obj['uuid'], other_kind + ':' + other['uuid'], resistance))
        shape = pad_shape(obj) if kind == 'pad' else Point(obj['position']).buffer(obj['diameter_mm'] / 2, quad_segs=64)
        center = Point(obj['position'])
        for i, line in enumerate(lines):
            if ts[i]['layer'] not in obj['layers']:
                continue
            if line.distance(shape) > ts[i]['width_mm'] / 2 + 2e-6:
                continue
            distance = line.project(center)
            cuts[i].add(distance)
            # Lumped spreading approximation, explicitly not a guaranteed bound.
            if kind == 'pad':
                length = center.distance(line.interpolate(distance))
                resistance = rho * (length * 1e-3) / (min(obj['size']) * THICK * 1e-6)
            else:
                # Half-barrel per attachment: a top-bottom traverse pays full R.
                resistance = rho * 1.2e-3 / (math.pi * obj['drill_mm'] * 1e-3 * 20e-6) / 2
            contacts.append((i, distance, kind + ':' + obj['uuid'], max(resistance, 1e-6)))
    edges, nodes = [], {}

    def node(key):
        if key not in nodes:
            nodes[key] = len(nodes)
        return nodes[key]

    def point_node(i, distance):
        point = lines[i].interpolate(distance)
        return node((ts[i]['layer'], round(point.x, 6), round(point.y, 6)))

    for i, line in enumerate(lines):
        positions = sorted(cuts[i])
        for a, b in zip(positions, positions[1:]):
            if b - a > 1e-6:
                resistance = rho * ((b - a) * 1e-3) / (width * THICK * 1e-6)
                edges.append((point_node(i, a), point_node(i, b), resistance))
    for i, distance, key, resistance in contacts:
        edges.append((point_node(i, distance), node(key), resistance))
    for i, di, j, dj, length in junctions:
        a, b = point_node(i, di), point_node(j, dj)
        if a != b:
            edges.append((a, b, rho * length * 1e-3 / (width * THICK * 1e-6)))
    for a, b, resistance in object_links:
        edges.append((node(a), node(b), resistance))
    pin_nodes = {p['ref'] + '.' + p['number']: node('pad:' + p['uuid']) for p in ps}
    sources = {pin_nodes[p['ref'] + '.' + p['number']] for p in ps if p['ref'] == 'J_WING'}
    assert sources
    adjacency = collections.defaultdict(list)
    for a, b, r in edges:
        adjacency[a].append((b, r))
        adjacency[b].append((a, r))
    reached, queue = set(sources), list(sources)
    while queue:
        a = queue.pop()
        for b, _ in adjacency[a]:
            if b not in reached:
                reached.add(b)
                queue.append(b)
    assert set(pin_nodes.values()) <= reached, ('Approximate graph did not connect all actual pads',
                                               [k for k, v in pin_nodes.items() if v not in reached])
    unknown = sorted(reached - sources)
    indices = {a: i for i, a in enumerate(unknown)}
    conductance, load = np.zeros((len(unknown), len(unknown))), np.zeros(len(unknown))
    for a, b, r in edges:
        if a not in reached:
            continue
        g = 1 / r
        for x, y in ((a, b), (b, a)):
            if x in indices:
                conductance[indices[x], indices[x]] += g
                if y in indices:
                    conductance[indices[x], indices[y]] -= g
    for p in ps:
        current = sensor_current if p['ref'].startswith('U_H') else mux_current if p['ref'].startswith('U_MUX_') else 0
        if current:
            load[indices[pin_nodes[p['ref'] + '.' + p['number']]]] += current
    voltage = np.linalg.solve(conductance, load)
    residual = float(np.max(np.abs(conductance @ voltage - load)))
    assert residual < 1e-7
    return dict(pins={key: float(voltage[indices[n]] if n in indices else 0) for key, n in pin_nodes.items()},
                load_A=float(sum(load)), max_drop_V=float(max(voltage)), nodes=len(reached),
                resistors=len(edges), kcl_residual_A=residual)


def main():
    results = []
    for pitch in (16, 17):
        cell = f'KRT-{pitch}-2L-0100'
        inv = json.loads((OUT / (cell + '-inventory.json')).read_text())
        refs = sorted(c['ref'] for c in inv['components'] if c['value'] == 'DRV5055A3QDBZR')
        for label, current, width, temp in [
            ('datasheet-5mA-worst-width-20C', 0.005, 0.08, 20),
            ('datasheet-5mA-worst-width-125C', 0.005, 0.08, 125),
            ('envelope-11mA-nominal-width-20C', 0.011, 0.10, 20),
            ('envelope-11mA-worst-width-20C', 0.011, 0.08, 20),
            ('envelope-11mA-worst-width-125C', 0.011, 0.08, 125),
        ]:
            supply = model(inv, 'HALL_5V', current, 2.7e-6, width, temp)
            ground = model(inv, 'GND', current, 2.7e-6, width, temp)
            sensor_rows = []
            for ref in refs:
                high, low = supply['pins'][ref + '.1'], ground['pins'][ref + '.3']
                sensor_rows.append(dict(ref=ref, supply_drop_V=high, ground_rise_V=low,
                                        loop_drop_V=high + low, local_supply_at_5V_V=5 - high - low,
                                        local_supply_at_4V75_V=4.75 - high - low))
            results.append(dict(cell=cell, scenario=label, temperature_C=temp, width_mm=width,
                                sensor_current_A=current, supply=supply, ground=ground, sensors=sensor_rows,
                                max_sensor_loop_drop_V=max(s['loop_drop_V'] for s in sensor_rows),
                                min_local_supply_at_4V75_V=min(s['local_supply_at_4V75_V'] for s in sensor_rows)))
            print(cell, label, results[-1]['max_sensor_loop_drop_V'], results[-1]['min_local_supply_at_4V75_V'], flush=True)
    (OUT / 'dc-drop-estimate.json').write_text(json.dumps(dict(
        method='Centerline lumped resistor approximation, not guaranteed worst-case or manufacturing sign-off',
        assumptions=dict(copper_mm=THICK, rho20_ohm_m=RHO, alpha_per_K=0.00393, via_barrel_um=20,
                         connector_nodes_ideal=True, pad_spreading_approximate=True,
                         manufactured_junction_topology_assumed_preserved=True),
        limitations=['Does not establish analog accuracy or supply transient margins',
                     'Connector, cable, Main supply, contact constriction and etch profile omitted',
                     '125C is a resistivity sensitivity case; ambient125C plus self-heating is not approved'],
        results=results), indent=2) + '\n')


if __name__ == "__main__":
    main()
