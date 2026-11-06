#!/usr/bin/env python3
"""Fixed-topology copper-conductance study, not a reroute or pour generator.

Capture the original #141 model's solved graph using Python's return profiler.
The original file/function is not edited. Scale ONLY track/junction/object-link
resistors; pad spreading and all half-via barrels remain fixed. An exact node
contraction computes the zero-track-resistance limit for this graph.
Requires numpy and shapely, with bytecode writes disabled by the runner.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import numpy as np

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
Q = E.parent
src = Q / 'issue-141-wing-power-integrity/dc-model.py'
spec = importlib.util.spec_from_file_location('original141', src)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
captured = {}


def capture(frame, event, arg):
    if event == 'return' and frame.f_code is m.model.__code__:
        captured.update(frame.f_locals)


def solve(g, factor):
    edges = g['edges']
    n = len(g['nodes'])
    # #141 appends tracks, contacts, junctions, object links in that order.
    nj = sum(g['point_node'](i, di) != g['point_node'](j, dj)
             for i, di, j, dj, _ in g['junctions'])
    nc, no = len(g['contacts']), len(g['object_links'])
    nt = len(edges) - nc - nj - no
    assert nt > 0
    variable = [i < nt or i >= nt + nc for i in range(len(edges))]
    parent = list(range(n))

    def root(a):
        while a != parent[a]:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    if factor is None:
        for (a, b, _), vary in zip(edges, variable):
            if vary:
                parent[root(a)] = root(b)
    sources = {root(a) for a in g['sources']}
    unknown = sorted({root(a) for a in g['reached']} - sources)
    index = {a: i for i, a in enumerate(unknown)}
    mat = np.zeros((len(unknown), len(unknown)))
    load = np.zeros(len(unknown))
    for a, old_index in g['indices'].items():
        if root(a) in index:
            load[index[root(a)]] += g['load'][old_index]
    for (a, b, r), vary in zip(edges, variable):
        a, b = root(a), root(b)
        if a == b:
            continue
        if vary and factor is not None:
            r /= factor
        conductance = 1 / r
        for x, y in [(a, b), (b, a)]:
            if x in index:
                mat[index[x], index[x]] += conductance
                if y in index:
                    mat[index[x], index[y]] -= conductance
    v = np.linalg.solve(mat, load)
    residual = float(np.max(np.abs(mat @ v - load))) if len(v) else 0.
    assert residual < 1e-7
    return dict(pins={k: float(v[index[root(a)]]) if root(a) in index else 0.
                      for k, a in g['pin_nodes'].items()}, residual_A=residual,
                variable_resistors=sum(variable), fixed_resistors=nc,
                nodes_after_contraction=len(unknown) + len(sources))


saved = json.loads((Q / 'issue-141-wing-power-integrity/dc-drop-estimate.json').read_text())
results = []
reproduction = []
for pitch in [16, 17]:
    inv = json.loads((Q / f'issue-141-wing-power-integrity/KRT-{pitch}-2L-P0300-inventory.json').read_text())
    solutions = {}
    for net in ['HALL_5V', 'GND']:
        captured.clear()
        sys.setprofile(capture)
        try:
            original = m.model(inv, net, .005, 2.7e-6, .24, 125)
        finally:
            sys.setprofile(None)
        g = captured.copy()
        solutions[net] = {str(f): solve(g, f) for f in [1., 2., 4., 10., None]}
        assert max(abs(original['pins'][p] - solutions[net]['1.0']['pins'][p])
                   for p in original['pins']) < 1e-9
    original_saved = next(s for s in saved['results'] if s['pitch_mm'] == pitch and
                          s['variant'] == 'after' and s['temperature_C'] == 125 and
                          s['width_factor'] == .8 and s['sensor_current_A'] == .005)
    scale = .127 / original_saved['supply']['load_A']
    for factor in [1., 2., 4., 10., None]:
        a, b = solutions['HALL_5V'][str(factor)], solutions['GND'][str(factor)]
        sensors = [dict(ref=p.rsplit('.', 1)[0],
                        loop_drop_V=(a['pins'][p] + b['pins'][p.rsplit('.', 1)[0] + '.3']) * scale)
                   for p in a['pins'] if p.startswith('U_H') and p.endswith('.1')]
        assert len(sensors) == 21
        worst = max(sensors, key=lambda s: s['loop_drop_V'])
        baseline = original_saved['max_sensor_loop_drop_V'] * scale
        if factor == 1:
            err = abs(worst['loop_drop_V'] - baseline)
            assert err < 1e-8
            reproduction.append(dict(pitch_mm=pitch, absolute_error_V=err))
        results.append(dict(pitch_mm=pitch, temperature_C=125, width_factor=.8,
                            planning_current_A=.127, conductance_multiplier=factor,
                            interpretation='zero variable-resistance limit; fixed pad/via retained' if factor is None
                            else 'conductance target, same contacts/topology; not physical widened traces',
                            worst_sensor=worst, wing_drop_ratio=worst['loop_drop_V']/baseline,
                            max_kcl_residual_A=max(a['residual_A'], b['residual_A']),
                            networks={k: {key: val for key, val in solutions[k][str(factor)].items() if key != 'pins'}
                                      for k in solutions}, sensors=sensors))
rho = 1.7241e-8 * (1 + .00393 * 105)
strips = []
for length, width, layers in [(50, 1, 1), (50, 3, 1), (50, 3, 2), (100, 1, 1)]:
    resistance = rho * length * 1e-3 / (width * .8 * 1e-3 * 35e-6 * layers)
    strips.append(dict(length_mm=length, nominal_width_mm=width, parallel_layers=layers,
                       temperature_C=125, width_factor=.8, resistance_ohm=resistance))
(E / 'copper-study.json').write_text(json.dumps(dict(
    status='RESISTANCE_TARGETS_AND_MATHEMATICAL_LIMIT_ONLY',
    source=str(src.relative_to(E.parents[3])), source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
    original_function_modified=False, reproduction=reproduction, results=results, ideal_strips=strips,
    limitations=['No layout changes, new copper geometry or parasitic/clearance proof.',
                 'Pad spreading and half-via barrels fixed; contacts, cable and switches outside graph.',
                 'Zero-variable-resistance limit only applies to this inherited topology/approximation.',
                 'Uniform factor0.5 in compare.py is more optimistic than doubling track conductance.']
), ensure_ascii=False, indent=2) + '\n')
for p in results:
    print(p['pitch_mm'], p['conductance_multiplier'], p['worst_sensor'], p['wing_drop_ratio'], flush=True)
