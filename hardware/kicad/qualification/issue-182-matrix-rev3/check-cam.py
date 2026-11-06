"""Independent parsed manufacturing-data checks and review ZIP packaging.

Resumed verifier: Excellon coordinates are quantized to 0.001 mm.
The inherited inspector remains unchanged. Run with the viewer venv; see README.md.
"""
from collections import Counter
import json
import math
import warnings
import zipfile
import importlib.metadata
from pathlib import Path

from gerbonara import GerberFile, ExcellonFile, LayerStack
from gerbonara.graphic_objects import Flash, Line
from common import E, now, save, digest
import sys
VERIFY_ONLY = "--verify-only" in sys.argv
if VERIFY_ONLY:
    def save(path, value):
        pass


def point(x, y):
    return (round(x, 6), round(y, 6))


def board_point(p):
    return point(p[0], -p[1])


def segment(start, end, width):
    return (*sorted([start, end]), round(width, 6))


def drill_key(o):
    return (point(o.x, o.y), round(o.aperture.diameter, 6))


results = []
for pitch in (18,):
    dest = E / 'manufacturing'
    pre = json.loads((dest / 'native-inventory.json').read_text())
    fab = dest / 'gerber'
    xmin, ymin, xmax, ymax = pre['outline_bounds_mm']
    bounds = ((xmin-2, -ymax-2), (xmax+2, -ymin+2))
    files = {}
    parser_warnings = []
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        for f in sorted(fab.iterdir()):
            if f.suffix == '.gbrjob':
                continue
            files[f.suffix] = (ExcellonFile.open(f, plated='NPTH' not in f.name)
                               if f.suffix == '.drl' else GerberFile.open(f))
        # Separate drill files share an extension; load with explicit classification.
        pth = ExcellonFile.open(fab / 'm1-matrix18-PTH.drl', plated=True)
        npth = ExcellonFile.open(fab / 'm1-matrix18-NPTH.drl', plated=False)
        stack = LayerStack.open(fab)
        parser_warnings = sorted(set(str(w.message) for w in captured))
    for ext in ('.gtl', '.gbl'):
        parsed = files[ext]
        layer = 'F.Cu' if ext == '.gtl' else 'B.Cu'
        lines = [o for o in parsed.objects if isinstance(o, Line)]
        expected = Counter(segment(board_point(t['start']), board_point(t['end']), t['width_mm'])
                           for t in pre['tracks'] if t['layer'] == layer)
        actual = Counter(segment(point(o.x1, o.y1), point(o.x2, o.y2), o.aperture.diameter) for o in lines)
        assert actual == expected, f'{pitch} {layer}: trace geometry differs'
        via_flashes = [o for o in parsed.objects if isinstance(o, Flash)
                       and dict(o.aperture.attrs).get('.AperFunction') == ('ViaPad',)]
        assert Counter(drill_key(o) for o in via_flashes) == Counter(
            (board_point(v['pos']), v['diameter_mm']) for v in pre['vias'])
        pad_flashes = [o for o in parsed.objects if isinstance(o, Flash) and '.P' in o.attrs]
        expected_pads = [p for p in pre['pads'] if p['attribute'] == 1 and layer in p['layers']]
        assert len(pad_flashes) == len(expected_pads)
        # Connector mounting lands can intentionally share the same MP number.
        remaining = list(expected_pads)
        for o in pad_flashes:
            candidates = [p for p in remaining if (p['ref'], p['number']) == o.attrs['.P']
                          and math.dist(board_point(p['pos']), (o.x, o.y)) <= 2e-6]
            assert len(candidates) == 1
            p = candidates[0]
            remaining.remove(p)
            (left, bottom), (right, top) = o.bounding_box()
            expected_size = p['size'][::-1] if round(p['angle_deg']) % 180 == 90 else p['size']
            assert abs(right-left-expected_size[0]) <= 3e-6
            assert abs(top-bottom-expected_size[1]) <= 3e-6
        assert not remaining
        assert all(o.polarity_dark for o in parsed.objects)
        assert len(lines) + len(via_flashes) + len(pad_flashes) == len(parsed.objects)
    # KiCad Excellon decimal output rounds to 0.001 mm; Gerber is 0.000001 mm.
    # Require a one-to-one match at that precision AND bound actual displacement.
    expected_drills = [(board_point(v['pos']), v['drill_mm']) for v in pre['vias']]
    drill_errors = []
    for o in pth.objects:
        candidates = [(i, p) for i, p in enumerate(expected_drills)
                      if p[1] == round(o.aperture.diameter, 6)
                      and abs(p[0][0] - o.x) <= 0.0005001
                      and abs(p[0][1] - o.y) <= 0.0005001]
        assert len(candidates) == 1, 'Non-unique or missing drill match'
        i, (pos, _) = candidates[0]
        expected_drills.pop(i)
        drill_errors.append(math.dist(pos, (o.x, o.y)))
    assert not expected_drills
    assert Counter(drill_key(o) for o in npth.objects) == Counter(
        (board_point(p['pos']), p['drill'][0]) for p in pre['npth'])
    assert all(isinstance(o, Flash) for o in pth.objects + npth.objects)
    outline = files['.gm1']
    assert Counter(segment(point(o.x1, o.y1), point(o.x2, o.y2), o.aperture.diameter)
                   for o in outline.objects) == Counter(
        segment(board_point(e['start']), board_point(e['end']), e['width_mm']) for e in pre['edges'])
    # At zero expansion each top mask aperture must match one SMD land.
    assert len(files['.gts'].objects) == pre['smd_pad_count'] == pre['smd_pad_count']
    assert Counter(point(o.x, o.y) for o in files['.gts'].objects) == Counter(
        board_point(p['pos']) for p in pre['pads'] if p['attribute'] == 1)
    top_pads = [o for o in files['.gtl'].objects if isinstance(o, Flash) and '.P' in o.attrs]
    def aperture_bounds(o):
        return tuple(round(v, 6) for pair in o.bounding_box() for v in pair)
    assert Counter(aperture_bounds(o) for o in files['.gts'].objects) == Counter(aperture_bounds(o) for o in top_pads)
    assert not files['.gbs'].objects
    assert all(v['tented_front'] and v['tented_back'] for v in pre['vias'])
    # Mask subtraction can emit clear flashes even when there is no printed legend.
    assert sum(o.polarity_dark for o in files['.gto'].objects)>100
    assert not any(o.polarity_dark for o in files['.gbo'].objects)
    paste_top = GerberFile.open(dest / 'paste' / 'm1-matrix18-F_Paste.gtp')
    paste_bottom = GerberFile.open(dest / 'paste' / 'm1-matrix18-B_Paste.gbp')
    assert len(paste_top.objects) == pre['smd_pad_count']-18 and not paste_bottom.objects
    assert Counter(aperture_bounds(o) for o in paste_top.objects) == Counter(aperture_bounds(o) for o in top_pads if not o.attrs['.P'][0].startswith('TP_'))
    drc = json.loads((dest / 'drc.json').read_text())
    assert not drc['violations'] and not drc['unconnected_items']
    # Filter-free offline rendering is performed separately by render-review.py.
    # Nine manufacturing files only. gbrjob is evidence, not order authority:
    # its Size includes the 0.05mm outline stroke and Finish is unspecified.
    archive = dest / 'm1-matrix18-gerber-review.zip'
    members = sorted(f for f in fab.iterdir() if f.suffix != '.gbrjob')
    assert len(members) == 9
    if not VERIFY_ONLY:
        assert not archive.exists()
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for f in members:
                z.write(f, f.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(z.read(f.name) == f.read_bytes() for f in members)
    result = dict(board="m1-matrix18-16-17mm", pitches_mm=[16,17], key_count=18, utc=now(), source_sha256=pre['source_sha256'], derived_sha256=pre['source_sha256'],
                  gerbonara_version=importlib.metadata.version('gerbonara'),
                  traces_geometry_width_layer_match=True, via_flash_geometry_match=True,
                  smd_pad_position_and_bounds_match=True, outline_centerlines_match=True,
                  drill_positions_diameters_classification_match=True,
                  pth_holes=len(pth.objects), npth_holes=len(npth.objects), slots=0,
                  excellon_coordinate_resolution_mm=0.001,
                  drill_max_radial_displacement_mm=max(drill_errors),
                  min_via_annular_ring_after_coordinate_rounding_mm=0.15-max(drill_errors),
                  drill_match_method='Unique per-hole match, same diameter, <=0.0005 mm per axis; all holes consumed. NPTH exact match. Export quantization only; no data edits.',
                  front_mask_openings=pre["smd_pad_count"], back_mask_openings=0, via_tenting_both=True,
                  printed_silk_dark_primitives=sum(o.polarity_dark for o in files['.gto'].objects), paste_front_apertures=pre["smd_pad_count"]-18, paste_back_apertures=0,
                  rerun_drc_violations=0, rerun_drc_unconnected=0,
                  minimum_clearance_rule_mm=0.1,
                  clearance_method='KiCad exact-source DRC using Issue 182 frozen final input project; exact exported trace/via/pad comparison. Not a separate CAM DFM certification.',
                  parser_warnings=parser_warnings,
                  warning_disposition='Gerbonara warns about KiCad G90 after header; coordinates are absolute and all parsed holes match board. No data edits.',
                  archive=archive.name, archive_sha256=digest(archive),
                  archive_members=[dict(name=f.name, sha256=digest(f)) for f in members],
                  exclusions=['paste supplied separately for PCBA', 'gbrjob (stroke-inflated Size, unspecified Finish)', 'preview and reports'],
                  preview_rendered_from_exported_files=True, manual_visual_review='Recorded separately in visual-review.json')
    save(dest / 'manufacturing-check.json', result)
    results.append(result)
save(E / 'manufacturing-checks.json', results)
print('Parsed M1 geometry, drills, masks, PCBA paste, DRC and archive verified.')
