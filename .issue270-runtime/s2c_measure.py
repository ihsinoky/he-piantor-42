"""Issue #270 stage 2c: MEASURE connector + tab geometry from Rev.9 board.

Loads the Rev.9 Main board with pcbnew, extracts for J2/J3:
- footprint position / orientation
- pad centres + sizes (signal pads 1..14 and MP pads)
- pad-row direction (PCA over the 14 signal-pad centres) = connector long axis
- footprint drawing shapes on F.Fab / F.CrtYd (body outline) in board coords
- Edge.Cuts outline polygon (board coords)
All converted to the harness case frame: case = board_mm - (100, 70).
Writes stage2c-measure.json.
"""
import json, math
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOARD = ROOT / 'hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb'
MM = 1e6
OFF = (100.0, 70.0)


def cv(x, y):
    return (x / MM - OFF[0], y / MM - OFF[1])


b = p.LoadBoard(str(BOARD))
out = {}

# Edge.Cuts outline
shapes = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        t = d.Type()
        if t == p.S_SEGMENT:
            s, e = d.GetStart(), d.GetEnd()
            shapes.append(('seg', [cv(s.x, s.y), cv(e.x, e.y)]))
        elif t == p.S_ARC:
            pts = [cv(q.x, q.y) for q in d.GetArcPoints()] if hasattr(d, 'GetArcPoints') else []
            shapes.append(('arc', pts))
        elif t == p.S_CURVE:
            shapes.append(('curve', []))
        else:
            shapes.append((str(t), []))
out['edge_shape_kinds'] = {}
for k, _ in shapes:
    out['edge_shape_kinds'][k] = out['edge_shape_kinds'].get(k, 0) + 1

# build outline polygon from segments (chain by endpoints)
segs = [pts for k, pts in shapes if k == 'seg']
arcs = [pts for k, pts in shapes if k == 'arc' and pts]
print('edge segs', len(segs), 'arcs', len(arcs))

for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if x.GetReference() == ref][0]
    pos = cv(f.GetPosition().x, f.GetPosition().y)
    yaw = f.GetOrientationDegrees()
    pads = []
    for pd in f.Pads():
        c = cv(pd.GetPosition().x, pd.GetPosition().y)
        pads.append(dict(num=str(pd.GetNumber()), net=pd.GetNetname(),
                         c=[round(c[0], 4), round(c[1], 4)],
                         size=[round(pd.GetSize().x / MM, 3), round(pd.GetSize().y / MM, 3)]))
    sig = [pd for pd in pads if pd['num'].isdigit()]
    # PCA on signal pad centres
    mx = sum(q['c'][0] for q in sig) / len(sig)
    my = sum(q['c'][1] for q in sig) / len(sig)
    sxx = sum((q['c'][0] - mx) ** 2 for q in sig)
    syy = sum((q['c'][1] - my) ** 2 for q in sig)
    sxy = sum((q['c'][0] - mx) * (q['c'][1] - my) for q in sig)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    axis = (math.cos(ang), math.sin(ang))
    # footprint local +X axis in board coords (KiCad: rotate by -yaw in y-down file coords;
    # report both conventions via pad axis which is frame-native)
    # body drawings of this footprint
    body = []
    for d in f.GraphicalItems():
        lay = d.GetLayerName()
        if lay in ('F.Fab', 'F.CrtYd'):
            if d.Type() == p.S_SEGMENT:
                s, e = d.GetStart(), d.GetEnd()
                body.append((lay, [cv(s.x, s.y), cv(e.x, e.y)]))
            elif d.Type() == p.S_RECT:
                s, e = d.GetStart(), d.GetEnd()
                body.append((lay, [cv(s.x, s.y), cv(e.x, e.y)]))
    out[ref] = dict(pos=[round(pos[0], 4), round(pos[1], 4)], yaw=yaw,
                    pads=pads, sig_centroid=[round(mx, 4), round(my, 4)],
                    pad_axis_angle_deg=round(math.degrees(ang), 4),
                    pad_axis=[round(axis[0], 6), round(axis[1], 6)],
                    body=body)
    print(ref, 'yaw', yaw, 'pos', pos, 'pad-axis deg', math.degrees(ang), 'npads', len(pads))

json.dump(out, open(HERE / 'stage2c-measure.json', 'w'), indent=1)
print('saved stage2c-measure.json')
