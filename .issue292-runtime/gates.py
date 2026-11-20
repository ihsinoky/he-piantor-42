"""S4 gates on the finished tree board (issue-292 re-route round)."""
import pcbnew as p, math, json
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon, box as sbox
from shapely.strtree import STRtree
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
base = p.LoadBoard(str(E/'base.kicad_pcb'))
R = {}

# outline delta vs Rev.10
rev = p.LoadBoard(str(E/'../hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb'))
def edges(bb):
    out = set()
    for d in bb.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            s, e = d.GetStart(), d.GetEnd()
            out.add((round(p.ToMM(s.x), 3), round(p.ToMM(s.y), 3), round(p.ToMM(e.x), 3), round(p.ToMM(e.y), 3)))
    return out
em, er = edges(b), edges(rev)
R['outline'] = {'mine': len(em), 'rev10': len(er), 'identical': em == er}

# via-pad audit
pads = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos = pad.GetPosition(); sz = pad.GetSize()
        pads.append({'ref': f"{f.GetReference()}.{pad.GetNumber()}", 'net': pad.GetNetname(),
                     'x': p.ToMM(pos.x), 'y': p.ToMM(pos.y),
                     'sx': p.ToMM(sz.x), 'sy': p.ToMM(sz.y), 'rot': pad.GetOrientationDegrees()})
def pad_rect_dist(px, py, pd):
    c, s = math.cos(math.radians(pd['rot'])), math.sin(math.radians(pd['rot']))
    dx, dy = px - pd['x'], py - pd['y']
    lx, ly = dx * c - dy * s, dx * s + dy * c
    ex = max(abs(lx) - pd['sx'] / 2, 0.0); ey = max(abs(ly) - pd['sy'] / 2, 0.0)
    return math.hypot(ex, ey)
worst = []
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA): continue
    pos = t.GetPosition(); vx, vy = p.ToMM(pos.x), p.ToMM(pos.y)
    vr = p.ToMM(t.GetWidth(p.F_Cu)) / 2
    vn = t.GetNetname()
    for pd in pads:
        if pd['net'] == vn: continue
        d = pad_rect_dist(vx, vy, pd) - vr
        worst.append((round(d, 4), f"via {vn} @({vx:.2f},{vy:.2f})", pd['ref'], pd['net']))
worst.sort()
R['via_pad'] = {'min': worst[0][0], 'sub_0.125': [list(w) for w in worst if w[0] < 0.125][:16]}

# keep-outs, compared against base board
def ant_items(bb):
    ANT = (70.3, 79.9, 128.9, 137.9)
    out = []
    for t in bb.GetTracks():
        if isinstance(t, p.PCB_VIA):
            pos = t.GetPosition()
            if ANT[0] <= p.ToMM(pos.x) <= ANT[1] and ANT[2] <= p.ToMM(pos.y) <= ANT[3]:
                out.append(('via', t.GetNetname()))
        else:
            s, e = t.GetStart(), t.GetEnd()
            for q in (s, e):
                if ANT[0] <= p.ToMM(q.x) <= ANT[1] and ANT[2] <= p.ToMM(q.y) <= ANT[3]:
                    out.append(('track', t.GetNetname())); break
    return out
R['antenna_keepout'] = {'final': ant_items(b), 'base': ant_items(base)}
def tp_count(bb):
    n_t = n_v = 0
    for t in bb.GetTracks():
        pos = t.GetPosition()
        d = math.hypot(p.ToMM(pos.x) - 100, p.ToMM(pos.y) - 118)
        if isinstance(t, p.PCB_VIA):
            if d < 20: n_v += 1
        else:
            s, e = t.GetStart(), t.GetEnd()
            (x1, y1), (x2, y2) = (p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))
            dx, dy = x2 - x1, y2 - y1
            tt = max(0.0, min(1.0, ((100 - x1) * dx + (118 - y1) * dy) / (dx * dx + dy * dy))) if (dx or dy) else 0.0
            if math.hypot(100 - (x1 + tt * dx), 118 - (y1 + tt * dy)) < 20: n_t += 1
    return n_t, n_v
R['trackpad_keepout'] = {'final_tracks_vias': tp_count(b), 'base_tracks_vias': tp_count(base)}

# Wing census
cen = {}
for ref in ('J2', 'J3'):
    f = [x for x in b.GetFootprints() if str(x.GetReference()) == ref][0]
    cen[ref] = {str(pad.GetNumber()): pad.GetNetname() for pad in f.Pads()}
R['wing_census'] = cen

# module GND pads
u1 = [x for x in b.GetFootprints() if str(x.GetReference()) == 'U1'][0]
R['module_gnd_pads'] = sorted(str(pad.GetNumber()) for pad in u1.Pads() if pad.GetNetname() == 'GND')

# HALL_3V3 copper identical to base?
def keyset(bb, net):
    out = set()
    for t in bb.GetTracks():
        if t.GetNetname() != net: continue
        if isinstance(t, p.PCB_VIA):
            pos = t.GetPosition(); out.add(('V', round(p.ToMM(pos.x), 3), round(p.ToMM(pos.y), 3)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            out.add(('T', t.GetLayer(), round(p.ToMM(s.x), 3), round(p.ToMM(s.y), 3), round(p.ToMM(e.x), 3), round(p.ToMM(e.y), 3)))
    return out
R['hall_3v3_identical_to_base'] = keyset(b, 'HALL_3V3') == keyset(base, 'HALL_3V3')

# ---- in-field minima + exception dependence ----
FIELD = sbox(69.3, 119.05, 80.9, 128.9)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    return Polygon([(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in
                    ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
LAYN = {p.F_Cu: 'F', p.In2_Cu: 'I2', p.B_Cu: 'B'}
objs = []  # (kind, net, layer, shape)
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        if poly.intersects(FIELD):
            objs.append(('pad', pad.GetNetname(), 'F', poly))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        shp = Point(p.ToMM(pos.x), p.ToMM(pos.y)).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2)
        if shp.intersects(FIELD):
            for L in ('F', 'I2', 'B'):
                objs.append(('via', t.GetNetname(), L, shp))
    else:
        L = LAYN.get(t.GetLayer())
        if not L: continue
        s, e = t.GetStart(), t.GetEnd()
        shp = LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth()) / 2)
        if shp.intersects(FIELD):
            objs.append(('trk', t.GetNetname(), L, shp))
minw = min(p.ToMM(t.GetWidth()) for t in b.GetTracks()
           if not isinstance(t, p.PCB_VIA) and LineString([(p.ToMM(t.GetStart().x), p.ToMM(t.GetStart().y)),
           (p.ToMM(t.GetEnd().x), p.ToMM(t.GetEnd().y))]).intersects(FIELD))
R['field_min_track_width'] = round(minw, 3)
tree = STRtree([o[3] for o in objs])
mins = {'trk-trk': 9, 'trk-pad': 9, 'pad-pad': 9, 'via-any': 9}
exc = []
for i, (k1, n1, l1, s1) in enumerate(objs):
    for j in tree.query(s1.buffer(0.13)):
        if j <= i: continue
        k2, n2, l2, s2 = objs[j]
        if n1 == n2 or l1 != l2: continue
        if not s1.intersects(FIELD) or not s2.intersects(FIELD): continue
        d = s1.distance(s2)
        cls = 'via-any' if 'via' in (k1, k2) else ('pad-pad' if k1 == k2 == 'pad' else ('trk-pad' if 'pad' in (k1, k2) else 'trk-trk'))
        if d < mins[cls]: mins[cls] = round(d, 4)
        if d < 0.0995:
            exc.append((cls, n1, n2, round(d, 4)))
R['field_min_clearances'] = mins
R['field_exception_dependent_pairs'] = {'count': len(exc), 'worst': sorted(exc, key=lambda z: z[3])[:12]}
(E/'gates-final.json').write_text(json.dumps(R, indent=1, default=str))
print(json.dumps(R, indent=1, default=str)[:2600])
