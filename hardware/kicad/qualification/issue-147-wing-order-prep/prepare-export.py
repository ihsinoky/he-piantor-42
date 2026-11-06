"""Preflight first, then export byte-identical copies of Issue 141 outputs."""
from collections import Counter
import json
import shutil
import pcbnew
from common import R, E, T, SOURCE, now, digest, save, run, environment

EXPECTED = {
    16: '3f29d24274c6e1834cf344c1c9c3bb234cd1aefa1e85d6eb3e8470eb5f2383f4',
    17: 'e7744a86e65459905b7629f2c8a13c60f1c0aa1d26c85139ac1c893d634e5939',
}


def xy(point):
    return [point.x / 1e6, point.y / 1e6]


def counts(items):
    return dict(Counter(items))


def inspect(pitch):
    cell = f'KRT-{pitch}-2L-P0300'
    src = SOURCE / 'runs' / cell / 'out.kicad_pcb'
    assert digest(src) == EXPECTED[pitch]
    assessment = json.loads((SOURCE / 'inspection' / cell / 'assessment.json').read_text())
    assert assessment['pass_acceptance'] and not any(assessment['metrics'].values())
    b = pcbnew.LoadBoard(str(src))
    ds = b.GetDesignSettings()
    edges = [dict(start=xy(d.GetStart()), end=xy(d.GetEnd()), width_mm=d.GetWidth()/1e6)
             for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
    assert len(edges) == 4
    vertices = Counter(tuple(p) for edge in edges for p in (edge['start'], edge['end']))
    assert len(vertices) == 4 and set(vertices.values()) == {2}
    xs = sorted(set(p[0] for p in vertices))
    ys = sorted(set(p[1] for p in vertices))
    assert len(xs) == len(ys) == 2
    assert all(e['start'][0] == e['end'][0] or e['start'][1] == e['end'][1] for e in edges)
    pads, npth, fields = [], [], []
    for f in b.GetFootprints():
        for field in (f.Reference(), f.Value()):
            fields.append(dict(text=field.GetText(), layer=b.GetLayerName(field.GetLayer()), visible=field.IsVisible()))
        for p in f.Pads():
            item = dict(ref=f.GetReference(), number=p.GetNumber(), pos=xy(p.GetPosition()),
                        size=xy(p.GetSize()), drill=xy(p.GetDrillSize()),
                        angle_deg=p.GetOrientationDegrees(), attribute=int(p.GetAttribute()),
                        shape=int(p.GetShape()), layers=[b.GetLayerName(i) for i in p.GetLayerSet().Seq()])
            pads.append(item)
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                npth.append(item)
    assert len(npth) == 4 and all(p['drill'] == [2.2, 2.2] for p in npth)
    tracks, vias = [], []
    for t in b.GetTracks():
        if isinstance(t, pcbnew.PCB_VIA):
            vias.append(dict(pos=xy(t.GetPosition()), diameter_mm=t.GetWidth(pcbnew.F_Cu)/1e6,
                             drill_mm=t.GetDrillValue()/1e6,
                             tented_front=t.IsTented(pcbnew.F_Mask), tented_back=t.IsTented(pcbnew.B_Mask)))
        else:
            tracks.append(dict(start=xy(t.GetStart()), end=xy(t.GetEnd()), width_mm=t.GetWidth()/1e6,
                               net=t.GetNetname(), layer=b.GetLayerName(t.GetLayer())))
    assert all(t['width_mm'] == (0.3 if t['net'] in ('GND', 'HALL_5V') else 0.1) for t in tracks)
    assert all(v['diameter_mm'] == 0.6 and v['drill_mm'] == 0.3 for v in vias)
    silk = [f for f in fields if f['visible'] and f['layer'] in ('F.Silkscreen', 'B.Silkscreen')]
    graphics = list(b.GetDrawings()) + [g for f in b.GetFootprints() for g in f.GraphicalItems()]
    silk_graphics = [g for g in graphics if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
    assert not silk and not silk_graphics
    assert b.GetCopperLayerCount() == 2 and ds.GetBoardThickness()/1e6 == 1.2
    assert ds.m_MinClearance/1e6 == 0.1
    assert all(z.GetIsRuleArea() for z in b.Zones())
    record = dict(pitch_mm=pitch, cell=cell, source=str(src.relative_to(R)), sha256=digest(src),
                  source_assessment_sha256=digest(SOURCE / 'inspection' / cell / 'assessment.json'),
                  kicad_version=pcbnew.GetBuildVersion(), inspected_utc=now(),
                  copper_layers=b.GetCopperLayerCount(), thickness_mm=ds.GetBoardThickness()/1e6,
                  min_clearance_mm=ds.m_MinClearance/1e6, edges=edges,
                  outline_bounds_mm=[xs[0], ys[0], xs[1], ys[1]],
                  outline_dimensions_mm=[xs[1]-xs[0], ys[1]-ys[0]],
                  npth=npth, pads=pads, tracks=tracks, vias=vias, fields=fields,
                  smd_pad_count=sum(p['attribute'] == pcbnew.PAD_ATTRIB_SMD for p in pads),
                  pth_pad_count=sum(p['attribute'] == pcbnew.PAD_ATTRIB_PTH for p in pads),
                  visible_silk_count=len(silk) + len(silk_graphics),
                  zones=dict(rule_areas=b.GetAreaCount(), copper_pours=0),
                  mask_expansion_mm=ds.m_SolderMaskExpansion/1e6,
                  soldermask_min_width_mm=ds.m_SolderMaskMinWidth/1e6,
                  tent_vias_front=ds.m_TentViasFront, tent_vias_back=ds.m_TentViasBack,
                  findings=[dict(id='SILK-ABSENT', origin='input-board',
                                 detail='No visible silkscreen graphics or text on either side; reference/value fields hidden. Export cannot restore absent legend.',
                                 action='PO accepts unmarked boards, or design owner adds legend and requalifies in a separate change. No design changes here.')],
                  copper_thickness_note='1oz required at order; not established by copper artwork or generic .gbrjob defaults.')
    save(E / f'{pitch}mm' / 'preflight.json', record)
    return record


preflights = [inspect(pitch) for pitch in (16, 17)]
save(E / 'preflight-summary.json', dict(utc=now(), completed_before_export=True,
     mandatory_geometry_present=True, silk_missing_both=True,
     disposition='Export faithful review candidates; no design edits. PO/design disposition for absent legend remains open.'))
cli = environment()['KICAD_CLI']
for pitch, preflight in zip((16, 17), preflights):
    cell = preflight['cell']
    work = T / f'{pitch}mm'
    work.mkdir(exist_ok=True)
    pcb = work / f'wing-{pitch}mm.kicad_pcb'
    shutil.copyfile(SOURCE / 'runs' / cell / 'out.kicad_pcb', pcb)
    shutil.copyfile(SOURCE / 'runs' / cell / 'out.kicad_pro', pcb.with_suffix('.kicad_pro'))
    # Library lookup belongs to the runtime configuration, not the board design.
    shutil.copyfile(SOURCE / 'inspection' / cell / 'fp-lib-table', work / 'fp-lib-table')
    assert digest(pcb) == preflight['sha256']
    dest = E / f'{pitch}mm'
    fab = dest / 'gerber'
    fab.mkdir(exist_ok=True)
    run(f'{pitch}mm-drc', [cli, 'pcb', 'drc', '--format', 'json', '--severity-all',
                          '--all-track-errors', '--exit-code-violations', '-o', dest / 'drc.json', pcb])
    run(f'{pitch}mm-gerbers', [cli, 'pcb', 'export', 'gerbers', '--layers',
        'F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts', '--precision', '6',
        '--subtract-soldermask', '-o', str(fab) + '/', pcb])
    run(f'{pitch}mm-drill', [cli, 'pcb', 'export', 'drill', '--format', 'excellon',
        '--drill-origin', 'absolute', '--excellon-units', 'mm', '--excellon-zeros-format', 'decimal',
        '--excellon-oval-format', 'alternate', '--excellon-separate-th', '--generate-report',
        '--report-path', dest / 'drill-report.txt', '-o', str(fab) + '/', pcb])
    paste = dest / 'paste-reference-not-for-order'
    run(f'{pitch}mm-paste-reference', [cli, 'pcb', 'export', 'gerbers', '--layers',
        'F.Paste,B.Paste', '-o', str(paste) + '/', pcb])
    assert digest(pcb) == preflight['sha256']
    save(dest / 'export-provenance.json', dict(utc=now(), source=preflight['source'],
         source_sha256=preflight['sha256'], runtime_copy_sha256=digest(pcb),
         project_source=str((SOURCE / 'runs' / cell / 'out.kicad_pro').relative_to(R)),
         project_sha256=digest(pcb.with_suffix('.kicad_pro')),
         design_modified=False, absolute_origin=True, gerber_precision='4.6 mm',
         drill_units='mm', drill_zeros='decimal', pth_npth_separated=True,
         paste_excluded_from_order=True, stencil=False, pcba=False))
print('Both preflights, DRCs, Gerber/Excellon exports completed.')
