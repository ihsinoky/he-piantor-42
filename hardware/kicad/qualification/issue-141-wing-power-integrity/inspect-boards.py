#!/usr/bin/env python3
"""Read #131 routed outputs with KiCad; cross-check native objects against AST.

No PCB or project is saved. Run with pcbnew and sexpdata on PYTHONPATH.
"""
import collections
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import pcbnew as p
POWER_WIDTH=float(sys.argv[1])
WIDTH_CODE=f"{round(POWER_WIDTH*1000):04d}"
import sexpdata as sx

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]
PREV = OUT


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def children(node, key):
    return [x for x in node if isinstance(x, list) and x and str(x[0]) == key]


def one(node, key):
    return children(node, key)[0]


def xy(v):
    return [p.ToMM(v.x), p.ToMM(v.y)]


summaries, allnets, provenance = [], [], []
for pitch in (16, 17):
    cell = f'KRT-{pitch}-2L-P{WIDTH_CODE}'
    source = PREV / 'runs' / cell / 'out.kicad_pcb'
    assessment = PREV / 'inspection' / cell / 'assessment.json'
    assert json.loads(assessment.read_text())['pass_acceptance']
    before = digest(source)
    tree = sx.loads(source.read_text())
    board = p.LoadBoard(str(source))
    nets = {int(x[1]): str(x[2]) for x in children(tree, 'net')}
    tracks, vias, pads, components, edges = [], [], [], [], []
    for obj in board.GetTracks():
        row = dict(uuid=obj.m_Uuid.AsString(), net=obj.GetNetname())
        if isinstance(obj, p.PCB_VIA):
            row.update(position=xy(obj.GetPosition()), diameter_mm=p.ToMM(obj.GetWidth(p.F_Cu)),
                       drill_mm=p.ToMM(obj.GetDrillValue()), layers=[board.GetLayerName(i) for i in (p.F_Cu, p.B_Cu)])
            vias.append(row)
        else:
            assert type(obj) == p.PCB_TRACK, 'Arc requires explicit length handling'
            row.update(start=xy(obj.GetStart()), end=xy(obj.GetEnd()), width_mm=p.ToMM(obj.GetWidth()),
                       layer=board.GetLayerName(obj.GetLayer()))
            row['length_mm'] = math.dist(row['start'], row['end'])
            tracks.append(row)
    for fp in board.GetFootprints():
        components.append(dict(ref=fp.GetReference(), value=fp.GetValue()))
        for pad in fp.Pads():
            pads.append(dict(ref=fp.GetReference(), number=pad.GetNumber(), net=pad.GetNetname(),
                             uuid=pad.m_Uuid.AsString(), position=xy(pad.GetPosition()), size=xy(pad.GetSize()),
                             angle=pad.GetOrientationDegrees(), drill=xy(pad.GetDrillSize()),
                             attribute={p.PAD_ATTRIB_NPTH: 'NPTH', p.PAD_ATTRIB_PTH: 'PTH', p.PAD_ATTRIB_SMD: 'SMD'}[pad.GetAttribute()],
                             shape={p.PAD_SHAPE_CIRCLE: 'circle', p.PAD_SHAPE_RECT: 'rect', p.PAD_SHAPE_OVAL: 'oval'}[pad.GetShape()],
                             layers=[board.GetLayerName(i) for i in (p.F_Cu, p.B_Cu) if pad.IsOnLayer(i)]))
    drawings = list(board.GetDrawings()) + [g for f in board.GetFootprints() for g in f.GraphicalItems()]
    for obj in drawings:
        if obj.GetLayer() == p.Edge_Cuts:
            assert obj.GetShape() == p.S_SEGMENT, 'Non-line edge requires explicit handling'
            edges.append(dict(start=xy(obj.GetStart()), end=xy(obj.GetEnd())))
    # Independent direct text measurement; UUID ties each result to its source.
    asttracks = {str(one(n, 'uuid')[1]): n for n in children(tree, 'segment')}
    assert len(asttracks) == len(tracks)
    for t in tracks:
        n = asttracks[t['uuid']]
        assert abs(float(one(n, 'width')[1]) - t['width_mm']) < 1e-9
        assert nets[int(one(n, 'net')[1])] == t['net']
        assert str(one(n, 'layer')[1]) == t['layer']
        for key in ('start', 'end'):
            assert math.dist(list(map(float, one(n, key)[1:3])), t[key]) < 2e-6
    assert len(children(tree, 'via')) == len(vias)
    assert sum(len(children(f, 'pad')) for f in children(tree, 'footprint')) == len(pads)
    assert len(edges) == 4
    xs = sorted({e[k][0] for e in edges for k in ('start', 'end')})
    ys = sorted({e[k][1] for e in edges for k in ('start', 'end')})
    assert len(xs) == len(ys) == 2
    expected = {frozenset(((xs[i], ys[0]), (xs[i], ys[1]))) for i in (0, 1)}
    expected |= {frozenset(((xs[0], ys[i]), (xs[1], ys[i]))) for i in (0, 1)}
    assert {frozenset((tuple(e['start']), tuple(e['end']))) for e in edges} == expected
    npth = [q for q in pads if q['attribute'] == 'NPTH']
    drilled = [q for q in pads if max(q['drill']) > 0]
    slots = [q for q in drilled if abs(q['drill'][0] - q['drill'][1]) > 1e-6]
    keepouts = [z.GetIsRuleArea() for z in board.Zones()]
    assert all(keepouts), 'Copper zones require separate current model'
    sensor_refs = sorted(c['ref'] for c in components if c['value'] == 'DRV5055A3QDBZR')
    mux_refs = sorted(c['ref'] for c in components if c['value'].startswith('TMUX1208'))
    assert len(sensor_refs) == 21 and len(mux_refs) == 3
    rows = []
    for net in sorted(set(t['net'] for t in tracks)):
        ts, vs, ps = ([t for t in tracks if t['net'] == net], [v for v in vias if v['net'] == net],
                      [q for q in pads if q['net'] == net])
        role = 'power' if net == 'HALL_5V' else 'GND' if net == 'GND' else 'signal'
        row = dict(cell=cell, net=net, role=role, segments=len(ts), vias=len(vs),
                   width_histogram_mm=dict(collections.Counter(str(t['width_mm']) for t in ts)),
                   min_width_mm=min(t['width_mm'] for t in ts), max_width_mm=max(t['width_mm'] for t in ts),
                   worst_width_mm=round(0.8 * min(t['width_mm'] for t in ts), 9),
                   length_mm=sum(t['length_mm'] for t in ts),
                   layers=dict(collections.Counter(t['layer'] for t in ts)),
                   pins=sorted(q['ref'] + '.' + q['number'] for q in ps))
        rows.append(row)
    assert len(rows) == 30
    assert all(abs(r['min_width_mm'] - (POWER_WIDTH if r['net'] in ['GND','HALL_5V'] else .1)) < 1e-9 for r in rows)
    allnets.extend(rows)
    summary = dict(cell=cell, source=str(source.relative_to(ROOT)), sha256=before,
                   original_acceptance=json.loads(assessment.read_text()),
                   dimensions_mm=[xs[1] - xs[0], ys[1] - ys[0]], external_edges=edges,
                   internal_edge_cuts=0, milled_slots=0, slotted_drills=slots,
                   npth=npth, drilled_pad_count=len(drilled), pth_pad_count=sum(q['attribute'] == 'PTH' for q in pads),
                   edge_scope='Board drawings and footprint graphics; exact single rectangular loop asserted',
                   track_count=len(tracks), via_count=len(vias),
                   via_dimensions=dict(collections.Counter(f"{v['diameter_mm']}/{v['drill_mm']}" for v in vias)),
                   copper_layers=board.GetCopperLayerCount(), thickness_mm=p.ToMM(board.GetDesignSettings().GetBoardThickness()),
                   zones=len(keepouts), all_zones_are_keepout_rule_areas=all(keepouts),
                   sensor_refs=sensor_refs, mux_refs=mux_refs, ast_native_crosscheck=True)
    summaries.append(summary)
    save(cell + '-inventory.json', dict(tracks=tracks, vias=vias, pads=pads, components=components))
    assert digest(source) == before
    provenance.extend([dict(path=str(q.relative_to(ROOT)), sha256=digest(q)) for q in
                       (source, assessment, PREV / 'inspection' / cell / 'snapshot.json')])
save('geometry-and-board-evidence.json', summaries)
save('net-widths.json', allnets)
save('board-read-provenance.json', dict(utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                                      kicad_version=p.GetBuildVersion(), sources=provenance,
                                      no_save_or_project_load=True))
with (OUT / 'net-widths.csv').open('w', newline='') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerow(['cell', 'net', 'role', 'segments', 'vias', 'min_width_mm', 'max_width_mm', 'worst_width_mm', 'length_mm', 'pins'])
    for row in allnets:
        writer.writerow([row[k] for k in ('cell', 'net', 'role', 'segments', 'vias', 'min_width_mm', 'max_width_mm', 'worst_width_mm', 'length_mm')] + [';'.join(row['pins'])])
print(json.dumps([{k: s[k] for k in ('cell', 'sha256', 'track_count', 'via_count', 'dimensions_mm', 'internal_edge_cuts', 'milled_slots')} for s in summaries], indent=2))
