"""Read-only Stage 1 screening. No board/footprint/drill/routing output.

Hole offsets are a grid-derived hypothesis, not released manufacturing dimensions.
Run from any directory; emits deterministic JSON to stdout using stdlib only.
"""
from pathlib import Path
import hashlib
import itertools
import json
import math
import re

ROOT = Path(__file__).resolve().parents[4]
E = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path):
    stack = []
    root = None
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', path.read_text()):
        if token == '(':
            node = []
            if stack:
                stack[-1].append(node)
            else:
                root = node
            stack.append(node)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack
    return root


def children(node, name):
    return [n for n in node if isinstance(n, list) and n and n[0] == name]


def child(node, name):
    return children(node, name)[0]


def xy(node, name):
    return tuple(map(float, child(node, name)[1:3]))


def distance_to_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    den = dx*dx+dy*dy
    t = max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
    return math.dist(p, (a[0]+t*dx, a[1]+t*dy))


def screen(pitch):
    definition = ROOT / f'hardware/jitx/wing/generated/representative21-{pitch}mm/definition.json'
    pcb = ROOT / f'hardware/kicad/qualification/issue-141-wing-power-integrity/runs/KRT-{pitch}-2L-P0300/out.kicad_pcb'
    d, board = json.loads(definition.read_text()), parse(pcb)
    fps = {next(p[2] for p in children(f, 'property') if p[1] == 'Reference'): f
           for f in children(board, 'footprint')}
    keys = d['sensor_sites']
    assert len(keys) == 21 and len({s['source_key_id'] for s in keys}) == 21
    centers = [(100+s['x_mm'], 100-s['y_mm']) for s in keys]
    for s, center in zip(keys, centers):
        assert xy(fps[s['reference']], 'at') == center
        assert child(fps[s['reference']], 'layer')[1] == 'F.Cu'
    actual_mounts = []
    for f in fps.values():
        for pad in children(f, 'pad'):
            if pad[2] == 'np_thru_hole':
                assert xy(pad, 'at') == (0, 0)
                actual_mounts.append((*xy(f, 'at'), float(child(pad, 'drill')[1])))
    mounts = [(100+h['x_mm'],100-h['y_mm'],h['diameter_mm']) for h in d['mounting_holes']]
    assert sorted(actual_mounts) == sorted(mounts) and len(mounts) == 4
    assert float(child(child(board, 'general'), 'thickness')[1]) == 1.2
    edges = [e for e in children(board, 'gr_line') if child(e, 'layer')[1] == 'Edge.Cuts']
    points = [xy(e, name) for e in edges for name in ('start', 'end')]
    bounds = [min(p[0] for p in points), min(p[1] for p in points),
              max(p[0] for p in points), max(p[1] for p in points)]
    assert bounds == [100-d['width_mm']/2,100-d['height_mm']/2,
                      100+d['width_mm']/2,100+d['height_mm']/2]
    holes = [(x+offset,y) for x,y in centers for offset in (-5.08,5.08)]
    radius = 1.75/2  # maximum diameter in manufacturer drawing
    proposed_copper_gap = 0.25  # planning allocation; manufacturer confirmation required
    segments, vias = children(board, 'segment'), children(board, 'via')
    hole_hits, segments_hit, vias_hit = [], set(), set()
    for i, h in enumerate(holes):
        sh = [j for j,s in enumerate(segments)
              if distance_to_segment(h,xy(s,'start'),xy(s,'end'))
              < radius+proposed_copper_gap+float(child(s,'width')[1])/2]
        vh = [j for j,v in enumerate(vias)
              if math.dist(h,xy(v,'at')) < radius+proposed_copper_gap+float(child(v,'size')[1])/2]
        segments_hit.update(sh)
        vias_hit.update(vh)
        if sh or vh:
            hole_hits.append({'key':keys[i//2]['source_key_id'],'side':[-1,1][i%2],
                              'segment_count':len(sh),'via_count':len(vh)})
    min_edge = min(min(h[0]-bounds[0], bounds[2]-h[0], h[1]-bounds[1], bounds[3]-h[1])-radius for h in holes)
    min_mount = min(math.dist(h,m[:2])-radius-2.5 for h in holes for m in mounts)
    min_web = min(math.dist(a,b)-2*radius for a,b in itertools.combinations(holes,2))
    # Reflection is of key centers only. Components are re-instantiated with valid pin maps.
    mirror = [(-s['x_mm'],s['y_mm']) for s in keys]
    assert all((-x,y) == (s['x_mm'],s['y_mm']) for (x,y),s in zip(mirror,keys))
    connector = next(c for c in d['components'] if c['kind']=='connector')
    expected = ['HALL_5V','GND','MUX_A0','GND','MUX_A1','MUX_A2','WING_EN','GND',
                'MUX_OUT_A','GND','MUX_OUT_B','GND','MUX_OUT_C','GND']
    assert [connector['pins'][str(i)] for i in range(1,15)] == expected
    return {'definition':str(definition.relative_to(ROOT)), 'definition_sha256':sha(definition),
            'pcb':str(pcb.relative_to(ROOT)), 'pcb_sha256':sha(pcb),
            'bounds_mm':bounds,'mounts_xy_diameter_mm':sorted(mounts),
            'left_keys':21,'right_keys':len(mirror),'current_top_sensors':21,
            'proposed_holes_per_wing':len(holes),'proposed_holes_per_pair':2*len(holes),
            'hypothesis_hole_edge_to_outline_min_mm':round(min_edge,6),
            'hypothesis_hole_edge_to_mount_keepout_min_mm':round(min_mount,6),
            'hypothesis_hole_to_hole_min_web_mm':round(min_web,6),
            'existing_segment_count':len(segments),'existing_via_count':len(vias),
            'hypothesis_holes_with_segment_or_via_conflict':len(hole_hits),
            'hypothesis_unique_segments_conflicted':len(segments_hit),
            'hypothesis_unique_vias_conflicted':len(vias_hit),'conflicts':hole_hits,
            'not_screened':['pads','filled zones','3D bodies','courtyards','drill position tolerance'],
            'pin_map':dict(enumerate(expected,1)),
            'panel_side_by_side_core_mm':[2*d['width_mm']+2,d['height_mm']],
            'panel_with_5mm_outer_rails_example_mm':[2*d['width_mm']+12,d['height_mm']+10]}


if __name__ == '__main__':
    print(json.dumps({'scope':'read-only hypothetical geometry screening, not PCB qualification',
                      'hypothesis':{'grid_mm':1.27,'hole_offset_x_mm':[-5.08,5.08],
                                    'hole_offset_y_mm':0,'max_hole_diameter_mm':1.75,
                                    'proposed_copper_to_hole_edge_mm':0.25},
                      'wings':{str(p):screen(p) for p in (16,17)}},ensure_ascii=False,indent=2))
